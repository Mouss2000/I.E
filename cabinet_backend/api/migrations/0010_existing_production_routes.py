from django.db import migrations


def preserve_routes(apps, schema_editor):
    Prescription = apps.get_model('api', 'Prescription')
    # Keep existing orders at their current stage; identify their former CNC route.
    Prescription.objects.filter(status__in=['SALLE_CAO', 'USINAGE_CNC', 'FRITTAGE_9H', 'CONTROLE_QUALITE', 'PRET_EXPEDITION', 'EN_ROUTE_CABINET', 'LIVRE']).update(production_method='CFAO', thermal_treatment='FRITTAGE')


class Migration(migrations.Migration):
    dependencies = [('api', '0009_prescription_analysis_validated_and_more')]
    operations = [migrations.RunPython(preserve_routes, migrations.RunPython.noop)]
