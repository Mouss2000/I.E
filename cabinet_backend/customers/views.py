import re
import secrets
import unicodedata
from functools import wraps
from django.core import signing
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_tenants.utils import schema_context
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.response import Response
from .models import Client, Domain, PlatformAccount, AccessLog, SupportTicket


def public_schema(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        with schema_context('public'):
            return view(*args, **kwargs)
    return wrapped


def login_key(name):
    text = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', text)


def current_account(request, admin=False):
    token = request.headers.get('Authorization', '').removeprefix('Bearer ')
    try:
        payload = signing.loads(token, salt='cabinet-demo', max_age=43200)
        account = PlatformAccount.objects.select_related('laboratory').get(pk=payload['id'], is_active=True)
        if payload.get('version') != (account.password_reset_at.isoformat() if account.password_reset_at else ''):
            raise ValueError('Session expired')
    except (signing.BadSignature, PlatformAccount.DoesNotExist, KeyError, ValueError, TypeError):
        raise AuthenticationFailed('Session de démonstration expirée. Reconnectez-vous.')
    if admin and account.role != 'ADMIN':
        raise PermissionDenied('Cet espace est réservé à l’administrateur.')
    return account


class AccountSerializer(serializers.ModelSerializer):
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True, default='')
    laboratory_id = serializers.CharField(source='laboratory.schema_name', read_only=True, default='')

    class Meta:
        model = PlatformAccount
        fields = ['id', 'name', 'email', 'role', 'laboratory', 'laboratory_id', 'laboratory_name', 'is_active', 'password_reset_at', 'created_at']
        read_only_fields = ['password_reset_at', 'created_at']

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', ''))
        key = login_key(name)
        if not key:
            raise serializers.ValidationError({'name': 'Renseignez un nom de connexion valide.'})
        duplicates = PlatformAccount.objects.filter(login_key=key)
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError({'name': 'Ce nom de connexion est déjà utilisé.'})
        role = attrs.get('role', getattr(self.instance, 'role', None))
        lab = attrs.get('laboratory', getattr(self.instance, 'laboratory', None))
        if role == 'LAB' and (not lab or lab.schema_name == 'public'):
            raise serializers.ValidationError({'laboratory': 'Affectez ce compte à un laboratoire.'})
        if role != 'LAB':
            attrs['laboratory'] = None
        attrs['login_key'] = key
        return attrs


class LabSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    identifier = serializers.RegexField(r'^[a-z][a-z0-9]{0,29}$', max_length=30)

    def validate_identifier(self, value):
        if value == 'public' or Client.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError('Cet identifiant existe déjà ou est réservé.')
        return value


@api_view(['POST'])
@public_schema
def demo_login(request):
    name = str(request.data.get('name', '')).strip()[:150]
    key = login_key(name)
    role = request.data.get('role')
    if role is not None and role not in {'ADMIN', 'DENTIST', 'LAB'}:
        return Response({'detail': 'Sélectionnez un espace valide.'}, status=400)
    candidates = PlatformAccount.objects.select_related('laboratory').filter(is_active=True)
    if role:
        candidates = candidates.filter(role=role)
    if role == 'LAB':
        laboratory = str(request.data.get('laboratory', ''))
        if not laboratory:
            return Response({'detail': 'Sélectionnez votre laboratoire.'}, status=400)
        candidates = candidates.filter(laboratory__schema_name=laboratory).exclude(laboratory__schema_name='public')
        matches = []
        for candidate in candidates:
            aliases = {candidate.login_key, login_key(candidate.name)}
            parts = re.split(r'\s+[-–—]\s+', candidate.name, maxsplit=1)
            if len(parts) == 2:
                aliases.add(login_key(parts[1]))
            for prefix in [candidate.laboratory.name, candidate.laboratory.schema_name]:
                prefix_key = login_key(prefix)
                if prefix_key and login_key(candidate.name).startswith(prefix_key):
                    aliases.add(login_key(candidate.name)[len(prefix_key):])
            if key and key in aliases:
                matches.append(candidate)
        account = matches[0] if len(matches) == 1 else None
    else:
        account = candidates.filter(login_key=key).first() if key else None
    if not account:
        AccessLog.objects.create(name=name, event='LOGIN', success=False, details='Compte inconnu ou désactivé')
        return Response({'detail': 'Nom inconnu ou compte désactivé. Contactez l’administrateur.'}, status=400)
    AccessLog.objects.create(account=account, name=account.name, event='LOGIN', details='Connexion de démonstration sans mot de passe')
    token = signing.dumps({'id': account.pk, 'version': account.password_reset_at.isoformat() if account.password_reset_at else ''}, salt='cabinet-demo')
    return Response({'account': AccountSerializer(account).data, 'token': token})


@api_view(['POST'])
@public_schema
def demo_logout(request):
    account = current_account(request)
    AccessLog.objects.create(account=account, name=account.name, event='LOGOUT', details='Déconnexion')
    return Response(status=204)


@api_view(['GET', 'POST'])
@public_schema
def laboratories(request):
    if request.method == 'POST':
        actor = current_account(request, admin=True)
        serializer = LabSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            lab = Client.objects.create(schema_name=serializer.validated_data['identifier'], name=serializer.validated_data['name'])
            Domain.objects.create(domain=f'{lab.schema_name}.localhost', tenant=lab, is_primary=True)
            AccessLog.objects.create(account=actor, name=actor.name, event='LAB_CREATED', details=f'{lab.schema_name} : {lab.name}')
        return Response({'id': lab.pk, 'identifier': lab.schema_name, 'name': lab.name}, status=201)
    return Response([{'id': lab.pk, 'identifier': lab.schema_name, 'name': lab.name} for lab in Client.objects.exclude(schema_name='public').order_by('name')])


@api_view(['GET', 'POST', 'PATCH'])
@public_schema
def accounts(request, account_id=None):
    actor = current_account(request, admin=True)
    if request.method == 'GET':
        return Response(AccountSerializer(PlatformAccount.objects.select_related('laboratory').all(), many=True).data)
    account = None
    if request.method == 'PATCH':
        account = PlatformAccount.objects.filter(pk=account_id).first()
        if not account:
            return Response({'detail': 'Compte introuvable.'}, status=404)
        if account.pk == actor.pk and (request.data.get('is_active') is False or request.data.get('role', actor.role) != 'ADMIN'):
            return Response({'detail': 'Vous ne pouvez pas désactiver votre propre accès administrateur.'}, status=400)
    serializer = AccountSerializer(account, data=request.data, partial=request.method == 'PATCH')
    serializer.is_valid(raise_exception=True)
    account = serializer.save()
    AccessLog.objects.create(account=actor, name=actor.name, event='ACCOUNT_UPDATED' if request.method == 'PATCH' else 'ACCOUNT_CREATED', details=account.name)
    return Response(AccountSerializer(account).data, status=200 if request.method == 'PATCH' else 201)


@api_view(['POST'])
@public_schema
def reset_password(request, account_id):
    actor = current_account(request, admin=True)
    account = PlatformAccount.objects.filter(pk=account_id).first()
    if not account:
        return Response({'detail': 'Compte introuvable.'}, status=404)
    password = secrets.token_urlsafe(12)
    account.password_hash = make_password(password)
    account.password_reset_at = timezone.now()
    account.save(update_fields=['password_hash', 'password_reset_at'])
    AccessLog.objects.create(account=actor, name=actor.name, event='PASSWORD_RESET', details=f'Compte : {account.name}')
    data = {'temporary_password': password, 'detail': 'Mot de passe réinitialisé. La connexion actuelle reste en mode démonstration sans mot de passe.'}
    if account.pk == actor.pk:
        data['token'] = signing.dumps({'id': account.pk, 'version': account.password_reset_at.isoformat()}, salt='cabinet-demo')
    return Response(data)


@api_view(['GET'])
@public_schema
def overview(request):
    current_account(request, admin=True)
    from api.models import Prescription
    labs = []
    for lab in Client.objects.exclude(schema_name='public').order_by('name'):
        row = {'id': lab.pk, 'identifier': lab.schema_name, 'name': lab.name, 'account_count': PlatformAccount.objects.filter(laboratory=lab).count()}
        with schema_context(lab.schema_name):
            row['order_count'] = Prescription.objects.count()
            row['paused_count'] = Prescription.objects.filter(is_paused=True).count()
        labs.append(row)
    return Response({'laboratories': labs, 'dentist_count': PlatformAccount.objects.filter(role='DENTIST').count(), 'account_count': PlatformAccount.objects.count(), 'open_tickets': SupportTicket.objects.exclude(status='RESOLVED').count()})


@api_view(['GET'])
@public_schema
def logs(request):
    current_account(request, admin=True)
    return Response(list(AccessLog.objects.values('id', 'name', 'event', 'success', 'details', 'created_at')[:200]))


@api_view(['GET', 'POST', 'PATCH'])
@public_schema
def support(request, ticket_id=None):
    account = current_account(request)
    if request.method == 'POST':
        class TicketInput(serializers.Serializer):
            subject = serializers.CharField(max_length=150)
            message = serializers.CharField(max_length=5000)
        serializer = TicketInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = SupportTicket.objects.create(account=account, **serializer.validated_data)
        return Response({'id': ticket.pk}, status=201)
    if request.method == 'PATCH':
        if account.role != 'ADMIN':
            raise PermissionDenied('Accès administrateur requis.')
        ticket = SupportTicket.objects.filter(pk=ticket_id).first()
        if not ticket:
            return Response({'detail': 'Signalement introuvable.'}, status=404)
        choice = request.data.get('status')
        if choice not in ['OPEN', 'IN_PROGRESS', 'RESOLVED']:
            return Response({'detail': 'Statut invalide.'}, status=400)
        ticket.status = choice
        ticket.save(update_fields=['status'])
        return Response({'id': ticket.pk, 'status': ticket.status})
    items = SupportTicket.objects.select_related('account', 'account__laboratory')
    if account.role != 'ADMIN':
        items = items.filter(account=account)
    return Response([{'id': item.pk, 'name': item.account.name, 'laboratory': item.account.laboratory.name if item.account.laboratory else '', 'subject': item.subject, 'message': item.message, 'status': item.status, 'created_at': item.created_at} for item in items[:200]])


@api_view(['GET', 'POST'])
@public_schema
def dentist_orders(request):
    account = current_account(request)
    if account.role != 'DENTIST':
        raise PermissionDenied('Accès réservé aux dentistes.')
    from api.models import Prescription
    from api.serializers import PrescriptionSerializer
    if request.method == 'POST':
        lab = Client.objects.exclude(schema_name='public').filter(schema_name=request.data.get('laboratory_id')).first()
        if not lab:
            return Response({'laboratory_id': ['Choisissez un laboratoire valide.']}, status=400)
        with schema_context(lab.schema_name):
            serializer = PrescriptionSerializer(data={**request.data, 'dentist_name': account.name})
            serializer.is_valid(raise_exception=True)
            order = serializer.save(dentist_account=account)
            data = dict(PrescriptionSerializer(order).data)
        return Response({**data, 'laboratory_name': lab.name, 'laboratory_id': lab.schema_name}, status=201)
    data = []
    for lab in Client.objects.exclude(schema_name='public'):
        with schema_context(lab.schema_name):
            orders = Prescription.objects.filter(Q(dentist_account_id=account.pk) | Q(dentist_account__isnull=True, dentist_name=account.name))
            data.extend({**row, 'laboratory_name': lab.name, 'laboratory_id': lab.schema_name} for row in PrescriptionSerializer(orders, many=True).data)
    return Response(sorted(data, key=lambda row: row['created_at'], reverse=True))
