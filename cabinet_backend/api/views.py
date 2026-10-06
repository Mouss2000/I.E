from rest_framework import viewsets
from .models import Prescription
from .serializers import PrescriptionSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Prescriptions (3-portal workflow).

    list:           GET    /api/prescriptions/       — all prescriptions (newest first)
    create:         POST   /api/prescriptions/       — dentist submits a new prescription
    retrieve:       GET    /api/prescriptions/{id}/  — single prescription detail
    partial_update: PATCH  /api/prescriptions/{id}/  — lab/courier updates status or delivery_date
    """
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
