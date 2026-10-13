import random
import uuid
from django.db import models


class Prescription(models.Model):
    """
    Represents a dental prescription order sent from a dentist to a lab.
    Patient identity is anonymised (patient_ref = PAT-XXXX) before reaching the lab,
    in compliance with Loi 09-08 / CNDP.

    3-Portal Workflow:
      Dentist  → EN_ATTENTE
      Lab      → EN_PRODUCTION → PRET_EXPEDITION
      Courier  → EN_ROUTE → LIVRE
    """

    class Status(models.TextChoices):
        EN_ATTENTE      = "EN_ATTENTE",      "En Attente"
        EN_PRODUCTION   = "EN_PRODUCTION",   "En Production"
        PRET_EXPEDITION = "PRET_EXPEDITION", "Prêt pour Expédition"
        EN_ROUTE        = "EN_ROUTE",        "En Route"
        LIVRE           = "LIVRE",           "Livré"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_ref = models.CharField(max_length=50, help_text="Anonymised patient reference (e.g. PAT-4829)")
    dentist_name = models.CharField(max_length=100, help_text="Name of the dentist who created the order")
    tooth_number = models.IntegerField()
    shade = models.CharField(max_length=10)
    material = models.CharField(max_length=50)
    disinfected = models.BooleanField(default=False)
    is_fast_track = models.BooleanField(default=False, help_text="Priority delivery option (+200 MAD)")
    total_price = models.IntegerField(null=True, blank=True, help_text="Calculated quote in MAD")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EN_ATTENTE,
    )
    delivery_date = models.DateField(null=True, blank=True, help_text="Delivery date set by the lab")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('EN_ATTENTE', 'En attente'), ('PAYE', 'Payé')],
        default='EN_ATTENTE',
    )
    delivery_pin = models.CharField(
        max_length=4, blank=True,
        help_text="Code PIN à 4 chiffres généré automatiquement",
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk is None and not self.delivery_pin:
            self.delivery_pin = str(random.randint(1000, 9999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_ref} | Dent {self.tooth_number} | {self.material} | {self.status}"
