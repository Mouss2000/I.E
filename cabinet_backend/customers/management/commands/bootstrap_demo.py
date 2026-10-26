from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from customers.models import Client, Domain, PlatformAccount
from customers.views import login_key


class Command(BaseCommand):
    help = 'Create the public platform, three laboratories and demo accounts without changing existing accounts.'

    def handle(self, *args, **options):
        with schema_context('public'):
            public, _ = Client.objects.get_or_create(schema_name='public', defaults={'name': 'Administration Cabinet 2.0'})
            for host in ['localhost', '127.0.0.1']:
                Domain.objects.get_or_create(domain=host, defaults={'tenant': public, 'is_primary': host == 'localhost'})
            PlatformAccount.objects.get_or_create(login_key='admin', defaults={'name': 'Admin', 'role': 'ADMIN'})
            for number in range(1, 4):
                lab, _ = Client.objects.get_or_create(schema_name=f'labo{number}', defaults={'name': f'Labo {number}'})
                Domain.objects.get_or_create(domain=f'labo{number}.localhost', defaults={'tenant': lab, 'is_primary': True})
                name = f'Labo {number} - Mohamed'
                PlatformAccount.objects.get_or_create(login_key=login_key(name), defaults={'name': name, 'role': 'LAB', 'laboratory': lab})
                name = f'Dentiste {number}'
                PlatformAccount.objects.get_or_create(login_key=login_key(name), defaults={'name': name, 'role': 'DENTIST'})
        self.stdout.write(self.style.SUCCESS('Demo ready: Admin; Dentiste 1, 2, 3; Labo 1 - Mohamed, Labo 2 - Mohamed, Labo 3 - Mohamed.'))
