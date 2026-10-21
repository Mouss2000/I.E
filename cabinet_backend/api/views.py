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

    def perform_create(self, serializer):
        impression_type = self.request.data.get("impression_type", "PHYSIQUE")
        if impression_type == "NUMERIQUE":
            serializer.save(
                impression_type=impression_type,
                status=Prescription.Status.A_CONFIRMER,
            )
        else:
            serializer.save(
                impression_type="PHYSIQUE",
                status=Prescription.Status.ATTENTE_RAMASSAGE,
            )
