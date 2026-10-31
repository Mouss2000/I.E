from django.contrib.auth.hashers import check_password
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import schema_context
from rest_framework.test import APIClient
from .models import Domain, PlatformAccount, AccessLog


class PlatformTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Laboratoire test'

    def setUp(self):
        self.client = APIClient(HTTP_HOST=self.get_test_tenant_domain())
        self.admin = PlatformAccount.objects.create(name='Admin', login_key='admin', role='ADMIN')
        self.dentist = PlatformAccount.objects.create(name='Dentiste 1', login_key='dentiste1', role='DENTIST')
        self.other = PlatformAccount.objects.create(name='Dentiste 2', login_key='dentiste2', role='DENTIST')
        self.worker = PlatformAccount.objects.create(name='Labo 1 - Mohamed', login_key='labo1mohamed', role='LAB', laboratory=self.tenant)

    def login(self, name):
        response = self.client.post('/platform/login/', {'name': name}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["token"]}')
        return response.data

    def test_name_routing_and_login_logs(self):
        login = self.login('  LABO 1 – Mohamed ')
        self.assertEqual(login['account']['laboratory_id'], self.tenant.schema_name)
        self.assertEqual(login['account']['role'], 'LAB')
        self.assertEqual(self.client.get('/api/prescriptions/').status_code, 200)
        self.assertEqual(self.client.post('/platform/logout/').status_code, 204)
        self.assertEqual(self.client.post('/platform/login/', {'name': 'unknown'}, format='json').status_code, 400)
        self.assertTrue(AccessLog.objects.filter(event='LOGIN', success=False).exists())
        self.assertTrue(AccessLog.objects.filter(event='LOGOUT', account=self.worker).exists())

    def test_portal_login_accepts_short_name_in_selected_laboratory(self):
        response = self.client.post('/platform/login/', {
            'name': '  Mohamed  ', 'role': 'LAB', 'laboratory': self.tenant.schema_name,
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['account']['id'], self.worker.pk)
        self.assertEqual(response.data['account']['laboratory_id'], self.tenant.schema_name)
        self.worker.is_active = False
        self.worker.save()
        response = self.client.post('/platform/login/', {
            'name': 'Mohamed', 'role': 'LAB', 'laboratory': self.tenant.schema_name,
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_portal_login_enforces_role_and_laboratory(self):
        invalid = [
            {'name': 'Mohamed', 'role': 'LAB'},
            {'name': self.worker.name, 'role': 'LAB', 'laboratory': 'unknown'},
            {'name': self.worker.name, 'role': 'DENTIST'},
            {'name': 'Admin', 'role': 'DENTIST'},
            {'name': 'Admin', 'role': 'INVALID'},
            {'name': '', 'role': 'LAB', 'laboratory': self.tenant.schema_name},
        ]
        for payload in invalid:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post('/platform/login/', payload, format='json').status_code, 400)
        response = self.client.post('/platform/login/', {'name': 'Dentiste 1', 'role': 'DENTIST'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['account']['id'], self.dentist.pk)

    def test_portal_login_rejects_ambiguous_short_names(self):
        PlatformAccount.objects.create(name='Mohamed', login_key='mohamed', role='LAB', laboratory=self.tenant)
        response = self.client.post('/platform/login/', {
            'name': 'Mohamed', 'role': 'LAB', 'laboratory': self.tenant.schema_name,
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_admin_permissions_account_assignment_and_deactivation(self):
        self.assertIn(self.client.get('/platform/accounts/').status_code, [401, 403])
        self.login('Dentiste 1')
        self.assertEqual(self.client.get('/platform/accounts/').status_code, 403)
        self.assertEqual(self.client.post('/platform/laboratories/', {'name': 'Forbidden', 'identifier': 'forbidden'}, format='json').status_code, 403)
        self.login('Admin')
        response = self.client.post('/platform/accounts/', {'name': 'Labo test - Sara', 'role': 'LAB', 'laboratory': self.tenant.pk}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        account_id = response.data['id']
        self.assertNotIn('password_hash', response.data)
        self.assertEqual(self.client.post('/platform/accounts/', {'name': 'Labo test Sara', 'role': 'LAB', 'laboratory': self.tenant.pk}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/platform/accounts/', {'name': 'No lab', 'role': 'LAB'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(f'/platform/accounts/{account_id}/', {'is_active': False}, format='json').status_code, 200)
        self.assertEqual(self.client.post('/platform/login/', {'name': 'Labo test - Sara'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(f'/platform/accounts/{self.admin.pk}/', {'is_active': False}, format='json').status_code, 400)

    def test_password_reset_hash_and_session_expiry(self):
        old_token = self.login('Dentiste 1')['token']
        self.login('Admin')
        response = self.client.post(f'/platform/accounts/{self.dentist.pk}/reset-password/')
        self.assertEqual(response.status_code, 200, response.data)
        self.dentist.refresh_from_db()
        self.assertTrue(check_password(response.data['temporary_password'], self.dentist.password_hash))
        self.assertNotIn(response.data['temporary_password'], str(list(AccessLog.objects.values())))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {old_token}')
        self.assertIn(self.client.get('/platform/dentist/orders/').status_code, [401, 403])
        self.login('Dentiste 1')
        self.assertEqual(self.client.get('/platform/dentist/orders/').status_code, 200)

    def test_lab_creation_and_order_isolation(self):
        self.login('Admin')
        created = self.client.post('/platform/laboratories/', {'name': 'Autre labo', 'identifier': 'otherlab'}, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        self.assertTrue(Domain.objects.filter(domain='otherlab.localhost').exists())
        self.assertEqual(self.client.post('/platform/laboratories/', {'name': 'Duplicate', 'identifier': 'otherlab'}, format='json').status_code, 400)
        self.login('Labo 1 - Mohamed')
        self.assertEqual(self.client.get('/api/prescriptions/', HTTP_HOST='otherlab.localhost').status_code, 403)
        self.login('Dentiste 1')
        payload = {'laboratory_id': 'otherlab', 'patient_ref': 'QA-ROUTING', 'dentist_name': 'Spoofed', 'tooth_number': 11, 'shade': 'A2', 'material': 'Zircone', 'disinfected': True}
        order = self.client.post('/platform/dentist/orders/', payload, format='json')
        self.assertEqual(order.status_code, 201, order.data)
        self.assertEqual(order.data['dentist_name'], self.dentist.name)
        self.assertEqual(order.data['laboratory_id'], 'otherlab')
        from api.models import Prescription
        self.assertEqual(Prescription.objects.count(), 0)
        with schema_context('otherlab'):
            self.assertEqual(Prescription.objects.get().dentist_account_id, self.dentist.pk)
        self.assertEqual(len(self.client.get('/platform/dentist/orders/').data), 1)
        self.login('Dentiste 2')
        self.assertEqual(self.client.get('/platform/dentist/orders/').data, [])
        self.assertEqual(self.client.get('/api/prescriptions/').status_code, 403)

    def test_technical_support_and_overview(self):
        self.login('Dentiste 1')
        created = self.client.post('/platform/support/', {'subject': 'Test technique', 'message': 'Description du problème'}, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        self.login('Dentiste 2')
        self.assertEqual(self.client.get('/platform/support/').data, [])
        self.assertEqual(self.client.patch(f'/platform/support/{created.data["id"]}/', {'status': 'RESOLVED'}, format='json').status_code, 403)
        self.login('Admin')
        self.assertEqual(len(self.client.get('/platform/support/').data), 1)
        self.assertEqual(self.client.get('/platform/overview/').data['open_tickets'], 1)
        self.assertEqual(self.client.patch(f'/platform/support/{created.data["id"]}/', {'status': 'RESOLVED'}, format='json').status_code, 200)
        self.assertEqual(self.client.get('/platform/overview/').data['open_tickets'], 0)
        self.assertEqual(self.client.get('/platform/logs/').status_code, 200)
