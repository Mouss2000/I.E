from rest_framework import serializers
from .models import Prescription, StaffMember, Equipment, StockItem
from .workflow import workflow_steps, next_status, LABELS
from django.utils import timezone
from copy import copy


class StaffMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = '__all__'

    def validate(self, attrs):
        status = attrs.get('account_status', getattr(self.instance, 'account_status', 'A_CREER'))
        username = attrs.get('account_username', getattr(self.instance, 'account_username', ''))
        if status == 'ACTIF' and not username.strip():
            raise serializers.ValidationError({'account_username': 'Renseignez un identifiant pour un compte actif.'})
        return attrs


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = '__all__'
        read_only_fields = ['updated_at']

    def validate(self, attrs):
        received = attrs.get('received_date', getattr(self.instance, 'received_date', None))
        expiry = attrs.get('expiry_date', getattr(self.instance, 'expiry_date', None))
        if received and expiry and expiry < received:
            raise serializers.ValidationError({'expiry_date': 'La péremption doit être postérieure ou égale à la réception.'})
        return attrs


class PrescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Prescription.
    Enforces the "Verrou Sanitaire": rejects any submission where
    disinfected is False — mirroring the frontend lock.

    On CREATE: status, delivery_date, billing_stage are read-only (server defaults apply).
    On update: validate sequential workflow transitions and required checkpoints.
    Route selection is locked once technical production starts; history is server-managed.
    """

    workflow_steps = serializers.SerializerMethodField()
    next_status = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    def get_workflow_steps(self, obj):
        return workflow_steps(obj)

    def get_next_status(self, obj):
        return next_status(obj)

    def get_status_label(self, obj):
        return LABELS.get(obj.status, obj.status)

    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "delivery_pin", "workflow_history", "accepted_at", "received_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On creation (no instance yet), lock workflow fields as read-only
        if self.instance is None:
            self.fields["status"].read_only = True
            self.fields["delivery_date"].read_only = True
            self.fields["billing_stage"].read_only = True
            for field in ['production_method', 'thermal_treatment', 'analysis_validated', 'reception_validated', 'quality_validated', 'technical_notes', 'accepted', 'is_paused', 'pause_reason', 'current_issues']:
                self.fields[field].read_only = True

    def validate(self, attrs):
        if not self.instance:
            return attrs
        order = copy(self.instance)
        old_status = order.status
        for key, value in attrs.items():
            setattr(order, key, value)
        if attrs.get('impression_type', self.instance.impression_type) != self.instance.impression_type:
            raise serializers.ValidationError({'impression_type': 'Le type d’empreinte ne peut plus être modifié après l’envoi.'})
        if self.instance.accepted and not order.accepted:
            raise serializers.ValidationError({'accepted': 'Une commande acceptée ne peut pas revenir dans les nouvelles demandes.'})
        if order.is_paused and not order.pause_reason.strip():
            raise serializers.ValidationError({'pause_reason': 'Indiquez le motif de la pause.'})
        planning_stages = {'DEMANDE_RECUE', 'ANALYSE_DEMANDE', 'ATTENTE_RAMASSAGE', 'EN_ROUTE_LABO', 'A_CONFIRMER', 'CONTROLE_DOSSIER', 'PLANIFICATION'}
        if old_status not in planning_stages:
            for field in ['production_method', 'thermal_treatment']:
                if getattr(order, field) != getattr(self.instance, field):
                    raise serializers.ValidationError({field: 'Le parcours est verrouillé après le lancement de la fabrication.'})
        if order.status != old_status:
            if not order.accepted:
                raise serializers.ValidationError({'accepted': 'Acceptez la commande avant de commencer le travail.'})
            if order.is_paused:
                raise serializers.ValidationError({'is_paused': 'Reprenez la commande avant de changer d’étape.'})
            previous = copy(order)
            previous.status = old_status
            if order.status != next_status(previous):
                raise serializers.ValidationError({'status': 'Avancez uniquement vers la prochaine étape du parcours.'})
            if old_status == 'ANALYSE_DEMANDE' and not order.analysis_validated:
                raise serializers.ValidationError({'analysis_validated': 'Validez l’analyse de la demande.'})
            if old_status == 'A_CONFIRMER' and not order.reception_validated:
                raise serializers.ValidationError({'reception_validated': 'Confirmez la réception et la conformité des éléments.'})
            if old_status == 'PLANIFICATION':
                if not order.production_method:
                    raise serializers.ValidationError({'production_method': 'Choisissez une méthode de fabrication.'})
                if not order.delivery_date:
                    raise serializers.ValidationError({'delivery_date': 'Renseignez la date de livraison prévue.'})
            if old_status == 'CONTROLE_QUALITE' and not order.quality_validated:
                raise serializers.ValidationError({'quality_validated': 'Validez le contrôle qualité avant le conditionnement.'})
        return attrs

    def update(self, instance, validated_data):
        if validated_data.get('accepted') and not instance.accepted:
            validated_data['accepted_at'] = timezone.now()
        if validated_data.get('reception_validated') and not instance.reception_validated:
            validated_data['received_at'] = timezone.now()
        new_status = validated_data.get('status', instance.status)
        if new_status != instance.status:
            validated_data['workflow_history'] = [*instance.workflow_history, {'status': new_status, 'at': timezone.now().isoformat()}]
        return super().update(instance, validated_data)

    def validate_disinfected(self, value):
        if not value:
            raise serializers.ValidationError(
                "Le verrou sanitaire est obligatoire. "
                "Les empreintes doivent être désinfectées avant envoi."
            )
        return value
