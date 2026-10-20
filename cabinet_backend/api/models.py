import random
import uuid
from django.db import models


class Prescription(models.Model):
    """
    Represents a dental prescription order sent from a dentist to a lab.
    Patient identity is anonymised (patient_ref = PAT-XXXX) before reaching the lab,
    in compliance with Loi 09-08 / CNDP.

    CFAO Technician Pipeline:
      Dentist  → A_CONFIRMER
      Lab      → SALLE_CAO → USINAGE_CNC → FRITTAGE_9H → CONTROLE_QUALITE → PRET_EXPEDITION
      Courier  → EN_ROUTE → LIVRE
    """

    class Status(models.TextChoices):
        A_CONFIRMER       = "A_CONFIRMER",       "Réception / Modèle"
        SALLE_CAO         = "SALLE_CAO",         "Conception Exocad / Fichier Construction"
        USINAGE_CNC       = "USINAGE_CNC",       "Calcul CNC & Usinage"
        FRITTAGE_9H       = "FRITTAGE_9H",       "Four de Frittage 9h & Refroidissement"
        CONTROLE_QUALITE  = "CONTROLE_QUALITE",  "Phase de Contrôle & Glaçage"
        PRET_EXPEDITION   = "PRET_EXPEDITION",   "Prêt pour Coursier"
        EN_ROUTE          = "EN_ROUTE",          "En livraison"
        LIVRE             = "LIVRE",             "Livré au Cabinet"

    class ImpressionType(models.TextChoices):
        PHYSIQUE  = "PHYSIQUE",  "Empreinte Physique (Coursier)"
        NUMERIQUE = "NUMERIQUE", "Fichier Numérique (.STL)"

    class BillingStage(models.TextChoices):
        COMMANDE  = "COMMANDE",  "Bon de Commande"
        SITUATION = "SITUATION", "En Situation (Relevé)"
        FACTURE   = "FACTURE",   "Facturé & Payé"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_ref = models.CharField(max_length=50, help_text="Anonymised patient reference (e.g. PAT-4829)")
    dentist_name = models.CharField(max_length=100, help_text="Name of the dentist who created the order")
    tooth_number = models.IntegerField()
    shade = models.CharField(max_length=10)
    material = models.CharField(max_length=50)
    disinfected = models.BooleanField(default=False)
    is_fast_track = models.BooleanField(default=False, help_text="Priority delivery option (+200 MAD)")
    total_price = models.IntegerField(null=True, blank=True, help_text="Calculated quote in MAD")

    impression_type = models.CharField(
        max_length=20,
        choices=ImpressionType.choices,
        default=ImpressionType.PHYSIQUE,
        help_text="Type d'empreinte : physique (coursier) ou numérique (.STL)",
    )
    stl_file_name = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Nom du fichier .STL téléversé (mock) si empreinte numérique",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.A_CONFIRMER,
    )
    delivery_date = models.DateField(null=True, blank=True, help_text="Delivery date set by the lab")

    billing_stage = models.CharField(
        max_length=20,
        choices=BillingStage.choices,
        default=BillingStage.COMMANDE,
        help_text="Étape financière : Commande → Situation → Facture",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
