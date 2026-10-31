from django_tenants.test.cases import TenantTestCase
from rest_framework.test import APIClient
from datetime import date, timedelta
from .alerts import laboratory_alerts
from .models import StockItem, StaffMember, Equipment


class ConfigurationTests(TenantTestCase):
    @classmethod
    def setup_tenant(cls, tenant):
        tenant.name = 'Test laboratory'

    def setUp(self):
        self.client = APIClient(HTTP_HOST=self.get_test_tenant_domain())

    def test_resource_lifecycle(self):
        resources = {
            'staff': {'reference': 'P-1', 'name': 'Technicien test', 'role': 'CFAO'},
            'equipment': {'reference': 'E-1', 'name': 'Four test', 'capacity': 12, 'tasks': 'Frittage'},
            'stock': {'reference': 'S-1', 'name': 'Disque test', 'quantity': '3.50', 'received_date': '2026-10-26'},
        }
        for endpoint, payload in resources.items():
            with self.subTest(endpoint=endpoint):
                url = f'/api/{endpoint}/'
                created = self.client.post(url, payload, format='json')
                self.assertEqual(created.status_code, 201, created.data)
                detail = f'{url}{created.data["id"]}/'
                self.assertEqual(self.client.get(detail).data['reference'], payload['reference'])
                duplicate = self.client.post(url, payload, format='json')
                self.assertEqual(duplicate.status_code, 400)
                self.assertIn('reference', duplicate.data)
                changed = self.client.patch(detail, {'name': 'Modifié'}, format='json')
                self.assertEqual(changed.status_code, 200, changed.data)
                self.assertEqual(self.client.get(detail).data['name'], 'Modifié')
                self.assertEqual(self.client.delete(detail).status_code, 204)
                self.assertEqual(self.client.get(detail).status_code, 404)

    def test_stock_rejects_negative_quantities_and_invalid_dates(self):
        base = {'reference': 'S-1', 'name': 'Disque', 'quantity': '2', 'received_date': '2026-10-26'}
        for change, field in [({'quantity': '-1'}, 'quantity'), ({'minimum_quantity': '-1'}, 'minimum_quantity'), ({'expiry_date': '2026-10-25'}, 'expiry_date')]:
            response = self.client.post('/api/stock/', {**base, **change}, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)
        created = self.client.post('/api/stock/', base, format='json')
        response = self.client.patch(f'/api/stock/{created.data["id"]}/', {'expiry_date': '2026-10-25'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_equipment_requires_positive_capacity(self):
        response = self.client.post('/api/equipment/', {'reference': 'E-1', 'name': 'Four', 'capacity': 0, 'tasks': 'Frittage'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('capacity', response.data)

    def test_active_account_requires_identifier(self):
        response = self.client.post('/api/staff/', {'reference': 'P-1', 'name': 'Test', 'role': 'CFAO', 'account_status': 'ACTIF'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('account_username', response.data)

    def test_unknown_tenant_cannot_access_configuration(self):
        response = self.client.get('/api/staff/', HTTP_HOST='unknown.localhost')
        self.assertEqual(response.status_code, 404)

    def test_alert_boundaries_and_resolution(self):
        today = date(2026, 10, 26)
        stock = StockItem.objects.create(reference='S-1', name='Zircone', quantity=5, minimum_quantity=5, received_date=today)
        machine = Equipment.objects.create(reference='E-1', name='Four', capacity=12, tasks='Frittage', maintenance_date=today + timedelta(days=7))
        staff = StaffMember.objects.create(reference='P-1', name='Technicien', role='CFAO', contract_end_date=today + timedelta(days=7), qualification_expiry_date=today - timedelta(days=1))
        alerts = laboratory_alerts(today)
        self.assertEqual({alert['type'] for alert in alerts}, {'stock', 'maintenance', 'contract', 'qualification'})
        self.assertTrue(next(alert for alert in alerts if alert['type'] == 'qualification')['overdue'])
        self.assertEqual(next(alert for alert in alerts if alert['type'] == 'maintenance')['resource_id'], machine.pk)
        machine.maintenance_date = today + timedelta(days=8)
        machine.save()
        staff.contract_end_date = None
        staff.qualification_expiry_date = today + timedelta(days=8)
        staff.save()
        stock.quantity = 6
        stock.save()
        self.assertEqual(laboratory_alerts(today), [])
        machine.maintenance_date = today
        machine.save()
        self.assertIn('aujourd’hui', laboratory_alerts(today)[0]['message'])

    def test_alert_endpoint_uses_tenant_and_reports_expired_stock(self):
        StockItem.objects.create(reference='S-1', name='Résine', quantity=10, minimum_quantity=2, received_date=date(2020, 1, 1), expiry_date=date(2020, 1, 2))
        response = self.client.get('/api/alerts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['type'], 'expiry')
        self.assertEqual(response.data[0]['section'], 'stock')
        self.assertEqual(self.client.get('/api/alerts/', HTTP_HOST='unknown.localhost').status_code, 404)

    def create_order(self, impression='NUMERIQUE'):
        response = self.client.post('/api/prescriptions/', {
            'patient_ref': 'QA-PROCESS', 'dentist_name': 'Cabinet test', 'tooth_number': 11,
            'shade': 'A2', 'material': 'Zircone', 'disinfected': True, 'impression_type': impression,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        order = response.data
        self.assertEqual(order['status'], 'DEMANDE_RECUE')
        accepted = self.client.patch(f'/api/prescriptions/{order["id"]}/', {'accepted': True}, format='json')
        self.assertEqual(accepted.status_code, 200, accepted.data)
        return accepted.data

    def test_complete_method_specific_workflows(self):
        for method, impression, required, absent in [
            ('CFAO', 'PHYSIQUE', 'USINAGE_CNC', 'IMPRESSION_3D'),
            ('IMPRESSION_3D', 'NUMERIQUE', 'POST_POLYMERISATION', 'USINAGE_CNC'),
            ('CONVENTIONNEL', 'NUMERIQUE', 'MODELAGE', 'SALLE_CAO'),
        ]:
            with self.subTest(method=method):
                order = self.create_order(impression)
                self.assertEqual(order['status'], 'DEMANDE_RECUE')
                self.assertEqual(len(order['delivery_pin']), 4)
                url = f'/api/prescriptions/{order["id"]}/'
                visited = []
                while order['next_status']:
                    visited.append(order['status'])
                    payload = {'status': order['next_status']}
                    if order['status'] == 'ANALYSE_DEMANDE':
                        payload['analysis_validated'] = True
                    if order['status'] == 'A_CONFIRMER':
                        payload['reception_validated'] = True
                    if order['status'] == 'PLANIFICATION':
                        payload.update(production_method=method, delivery_date='2026-11-10', thermal_treatment='FRITTAGE' if method == 'CFAO' else 'AUCUN', status='MODELE_TRAVAIL' if method == 'CONVENTIONNEL' else 'SALLE_CAO')
                    if order['status'] == 'CONTROLE_QUALITE':
                        payload['quality_validated'] = True
                    response = self.client.patch(url, payload, format='json')
                    self.assertEqual(response.status_code, 200, response.data)
                    order = response.data
                self.assertEqual(order['status'], 'LIVRE')
                self.assertIn(required, visited)
                self.assertNotIn(absent, visited)
                self.assertEqual(len(order['workflow_history']), len(visited) + 1)
                self.assertEqual('ATTENTE_RAMASSAGE' in visited, impression == 'PHYSIQUE')

    def test_workflow_guards(self):
        order = self.create_order()
        url = f'/api/prescriptions/{order["id"]}/'
        self.assertEqual(self.client.patch(url, {'status': 'ANALYSE_DEMANDE'}, format='json').status_code, 200)
        self.assertEqual(self.client.patch(url, {'status': 'USINAGE_CNC'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'status': 'A_CONFIRMER'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'status': 'A_CONFIRMER', 'analysis_validated': True}, format='json').status_code, 200)
        self.assertEqual(self.client.patch(url, {'status': 'CONTROLE_DOSSIER'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'status': 'CONTROLE_DOSSIER', 'reception_validated': True}, format='json').status_code, 200)
        self.assertEqual(self.client.patch(url, {'status': 'PLANIFICATION'}, format='json').status_code, 200)
        self.assertEqual(self.client.patch(url, {'status': 'SALLE_CAO', 'production_method': 'CFAO'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'status': 'SALLE_CAO', 'production_method': 'CFAO', 'delivery_date': '2026-11-10'}, format='json').status_code, 200)
        self.assertEqual(self.client.patch(url, {'production_method': 'IMPRESSION_3D'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'status': 'IMPRESSION_3D'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'impression_type': 'PHYSIQUE'}, format='json').status_code, 400)

    def test_no_thermal_treatment_when_not_planned(self):
        from .models import Prescription
        from .workflow import workflow_steps
        order = Prescription(production_method='CFAO', thermal_treatment='AUCUN')
        self.assertNotIn('TRAITEMENT_THERMIQUE', [step['key'] for step in workflow_steps(order)])

    def test_acceptance_and_pause_controls(self):
        order = self.create_order()
        url = f'/api/prescriptions/{order["id"]}/'
        self.assertIsNotNone(order['accepted_at'])
        self.assertEqual(self.client.patch(url, {'accepted': False}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'is_paused': True}, format='json').status_code, 400)
        response = self.client.patch(url, {'is_paused': True, 'pause_reason': 'Attente du cabinet', 'current_issues': 'Fichier incomplet'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.client.patch(url, {'status': 'ANALYSE_DEMANDE'}, format='json').status_code, 400)
        resumed = self.client.patch(url, {'is_paused': False, 'status': 'ANALYSE_DEMANDE'}, format='json')
        self.assertEqual(resumed.status_code, 200, resumed.data)
        persisted = self.client.get(url).data
        self.assertEqual(persisted['current_issues'], 'Fichier incomplet')
        self.assertFalse(persisted['is_paused'])

    def test_unaccepted_order_cannot_start(self):
        from .models import Prescription
        order = Prescription.objects.create(patient_ref='QA-RECEIVED', dentist_name='Cabinet', tooth_number=11, shade='A2', material='Zircone', disinfected=True)
        response = self.client.patch(f'/api/prescriptions/{order.pk}/', {'status': 'ANALYSE_DEMANDE'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('accepted', response.data)
