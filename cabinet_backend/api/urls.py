from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, StaffMemberViewSet, EquipmentViewSet, StockItemViewSet, alerts_view
from .views import EmployeeProfileViewSet, MachineViewSet, InventoryViewSet, PartnerClinicViewSet

router = DefaultRouter()
router.register(r"prescriptions", PrescriptionViewSet, basename="prescription")
router.register(r"staff", StaffMemberViewSet, basename="staff")
router.register(r"equipment", EquipmentViewSet, basename="equipment")
router.register(r"stock", StockItemViewSet, basename="stock")
router.register(r"employee-profiles", EmployeeProfileViewSet, basename="employee-profile")
router.register(r"machines", MachineViewSet, basename="machine")
router.register(r"inventory", InventoryViewSet, basename="inventory")
router.register(r"partner-clinics", PartnerClinicViewSet, basename="partner-clinic")

urlpatterns = [
    path('alerts/', alerts_view, name='laboratory-alerts'),
    path("", include(router.urls)),
]
