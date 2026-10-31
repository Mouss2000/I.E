import random
import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class EmployeeProfile(models.Model):
    class Role(models.TextChoices):
        RECEPTION = 'RECEPTION', 'Reception'
        CAO = 'CAO', 'CAO'
        FAO = 'FAO', 'FAO'
        QUALITE = 'QUALITE', 'Quality'
        COURSIER = 'COURSIER', 'Courier'

    class ContractType(models.TextChoices):
        CDI = 'CDI', 'CDI'
        CDD = 'CDD', 'CDD'
        STAGE = 'STAGE', 'Internship'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='employee_profile',
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    contract_type = models.CharField(max_length=5, choices=ContractType.choices)
    hire_date = models.DateField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['pk']


class Machine(models.Model):
    class MachineType(models.TextChoices):
        SCANNER = 'SCANNER', 'Scanner'
        USINEUSE_CNC = 'USINEUSE_CNC', 'CNC milling machine'
        FOUR_FRITTAGE = 'FOUR_FRITTAGE', 'Sintering furnace'

    class Status(models.TextChoices):
        ACTIF = 'ACTIF', 'Active'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'
        PANNE = 'PANNE', 'Out of order'

    name = models.CharField(max_length=120)
    machine_type = models.CharField(max_length=13, choices=MachineType.choices)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=11, choices=Status.choices, default=Status.ACTIF)

    class Meta:
        ordering = ['name', 'pk']
        constraints = [
            models.CheckConstraint(condition=models.Q(capacity__gte=1), name='machine_positive_capacity'),
        ]


class Inventory(models.Model):
    class Unit(models.TextChoices):
        DISQUE = 'DISQUE', 'Disc'
        GRAMMES = 'GRAMMES', 'Grams'
        UNITES = 'UNITES', 'Units'

    material_name = models.CharField(max_length=120)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=7, choices=Unit.choices)
    alert_threshold = models.FloatField(validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['material_name', 'pk']
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=0), name='inventory_nonnegative_quantity'),
            models.CheckConstraint(condition=models.Q(alert_threshold__gte=0), name='inventory_nonnegative_threshold'),
        ]

    @property
    def is_low_stock(self):
        return self.quantity <= self.alert_threshold


class PartnerClinic(models.Model):
    name = models.CharField(max_length=120)
    pickup_address = models.TextField()
    contact_phone = models.CharField(max_length=30)
    linked_dentist = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='partner_clinics',
    )

    class Meta:
        ordering = ['name', 'pk']
        constraints = [
            models.CheckConstraint(condition=~models.Q(pickup_address=''), name='clinic_required_pickup_address'),
        ]


class StaffMember(models.Model):
    reference = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=80)
    qualifications = models.TextField(blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    qualification_expiry_date = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    account_username = models.CharField(max_length=100, blank=True)
    account_status = models.CharField(max_length=20, choices=[('A_CREER', 'À créer'), ('ACTIF', 'Actif'), ('SUSPENDU', 'Suspendu')], default='A_CREER')
    availability = models.CharField(max_length=20, choices=[('DISPONIBLE', 'Disponible'), ('OCCUPE', 'Occupé'), ('ABSENT', 'Absent')], default='DISPONIBLE')
    schedule = models.CharField(max_length=255, blank=True)
    available_from = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']


class Equipment(models.Model):
    reference = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    availability = models.CharField(max_length=20, choices=[('DISPONIBLE', 'Disponible'), ('EN_SERVICE', 'En service'), ('MAINTENANCE', 'Maintenance'), ('HORS_SERVICE', 'Hors service')], default='DISPONIBLE')
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    capacity_unit = models.CharField(max_length=60, default='éléments / cycle')
    tasks = models.TextField()
    available_from = models.DateField(null=True, blank=True)
    maintenance_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']


class StockItem(models.Model):
    reference = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    unit = models.CharField(max_length=30, default='pièces')
    minimum_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    lot_number = models.CharField(max_length=80, blank=True)
    received_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']


class Prescription(models.Model):
    """
    Represents a dental prescription order sent from a dentist to a lab.
    Patient identity is anonymised (patient_ref = PAT-XXXX) before reaching the lab,
    in compliance with Loi 09-08 / CNDP.

    Two-Way Courier + CFAO Technician Pipeline:
      PHYSIQUE:   Dentist → ATTENTE_RAMASSAGE → EN_ROUTE_LABO → A_CONFIRMER
      NUMERIQUE:  Dentist → A_CONFIRMER (bypass courier)
      Lab:        SALLE_CAO → USINAGE_CNC → FRITTAGE_9H → CONTROLE_QUALITE → PRET_EXPEDITION
      Courier:    EN_ROUTE_CABINET → LIVRE
    """

    class Status(models.TextChoices):
        DEMANDE_RECUE = 'DEMANDE_RECUE', 'Demande reçue'
        ANALYSE_DEMANDE = 'ANALYSE_DEMANDE', 'Analyse de la demande'
        CONTROLE_DOSSIER = 'CONTROLE_DOSSIER', 'Contrôle du dossier'
        PLANIFICATION = 'PLANIFICATION', 'Planification'
        PREPARATION_CNC = 'PREPARATION_CNC', 'Préparation FAO'
        TRAITEMENT_THERMIQUE = 'TRAITEMENT_THERMIQUE', 'Traitement thermique'
        PREPARATION_3D = 'PREPARATION_3D', 'Préparation impression 3D'
        IMPRESSION_3D = 'IMPRESSION_3D', 'Impression 3D'
        LAVAGE_SECHAGE = 'LAVAGE_SECHAGE', 'Lavage et séchage'
        POST_POLYMERISATION = 'POST_POLYMERISATION', 'Post-polymérisation'
        MODELE_TRAVAIL = 'MODELE_TRAVAIL', 'Modèle de travail'
        MODELAGE = 'MODELAGE', 'Modelage'
        FABRICATION_MANUELLE = 'FABRICATION_MANUELLE', 'Fabrication conventionnelle'
        FINITION = 'FINITION', 'Finition'
        CONDITIONNEMENT = 'CONDITIONNEMENT', 'Conditionnement'
        # --- Pre-Lab Courier Phase (Physical Impressions Only) ---
        ATTENTE_RAMASSAGE = "ATTENTE_RAMASSAGE", "En attente de ramassage coursier"
        EN_ROUTE_LABO     = "EN_ROUTE_LABO",     "Coursier en route vers le labo"
        # --- Lab CFAO Pipeline ---
        A_CONFIRMER       = "A_CONFIRMER",       "Réception / Modèle"
        SALLE_CAO         = "SALLE_CAO",         "Conception Exocad / Fichier Construction"
        USINAGE_CNC       = "USINAGE_CNC",       "Calcul CNC & Usinage"
        FRITTAGE_9H       = "FRITTAGE_9H",       "Four de Frittage 9h & Refroidissement"
        CONTROLE_QUALITE  = "CONTROLE_QUALITE",  "Phase de Contrôle & Glaçage"
        PRET_EXPEDITION   = "PRET_EXPEDITION",   "Prêt pour Coursier"
        # --- Final Delivery Phase ---
        EN_ROUTE_CABINET  = "EN_ROUTE_CABINET",  "En livraison vers le cabinet"
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
    dentist_account = models.ForeignKey('customers.PlatformAccount', null=True, blank=True, on_delete=models.PROTECT)
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
        default=Status.DEMANDE_RECUE,
    )
    delivery_date = models.DateField(null=True, blank=True, help_text="Delivery date set by the lab")
    production_method = models.CharField(max_length=20, blank=True, choices=[('CFAO', 'CFAO / usinage CNC'), ('IMPRESSION_3D', 'Impression 3D'), ('CONVENTIONNEL', 'Fabrication conventionnelle')])
    thermal_treatment = models.CharField(max_length=20, default='AUCUN', choices=[('AUCUN', 'Aucun'), ('FRITTAGE', 'Frittage'), ('CRISTALLISATION', 'Cristallisation'), ('CUISSON', 'Cuisson')])
    technical_notes = models.TextField(blank=True)
    analysis_validated = models.BooleanField(default=False)
    reception_validated = models.BooleanField(default=False)
    quality_validated = models.BooleanField(default=False)
    workflow_history = models.JSONField(default=list, blank=True)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    is_paused = models.BooleanField(default=False)
    pause_reason = models.TextField(blank=True)
    current_issues = models.TextField(blank=True)

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
        if self._state.adding:
            # Auto-generate delivery PIN
            if not self.delivery_pin:
                self.delivery_pin = str(random.randint(1000, 9999))
            self.status = self.Status.DEMANDE_RECUE
            from django.utils import timezone
            self.workflow_history = [{'status': self.status, 'at': timezone.now().isoformat()}]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_ref} | Dent {self.tooth_number} | {self.material} | {self.status}"
