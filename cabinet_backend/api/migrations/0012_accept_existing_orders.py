from django.db import migrations
from django.db.models import F


def accept_existing(apps, schema_editor):
    Prescription = apps.get_model('api', 'Prescription')
    Prescription.objects.exclude(status__in=['DEMANDE_RECUE', 'ANALYSE_DEMANDE']).update(accepted=True, accepted_at=F('created_at'))


class Migration(migrations.Migration):
    dependencies = [('api', '0011_prescription_accepted_prescription_accepted_at_and_more')]
    operations = [migrations.RunPython(accept_existing, migrations.RunPython.noop)]
