from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from .permissions import DemoTenantPermission
from rest_framework.response import Response
from .alerts import laboratory_alerts
from .models import Prescription, StaffMember, Equipment, StockItem
from .serializers import PrescriptionSerializer, StaffMemberSerializer, EquipmentSerializer, StockItemSerializer


@api_view(['GET'])
@permission_classes([DemoTenantPermission])
def alerts_view(request):
    return Response(laboratory_alerts())


class StaffMemberViewSet(viewsets.ModelViewSet):
    permission_classes = [DemoTenantPermission]
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    permission_classes = [DemoTenantPermission]
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


class StockItemViewSet(viewsets.ModelViewSet):
    permission_classes = [DemoTenantPermission]
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Prescriptions (3-portal workflow).

    list:           GET    /api/prescriptions/       — all prescriptions (newest first)
    create:         POST   /api/prescriptions/       — dentist submits a new prescription
    retrieve:       GET    /api/prescriptions/{id}/  — single prescription detail
    partial_update: PATCH  /api/prescriptions/{id}/  — lab/courier updates status or delivery_date
    """
    queryset = Prescription.objects.all()
    permission_classes = [DemoTenantPermission]
    serializer_class = PrescriptionSerializer

    def perform_create(self, serializer):
        serializer.save()
