from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, StaffMemberViewSet, EquipmentViewSet, StockItemViewSet, alerts_view

router = DefaultRouter()
router.register(r"prescriptions", PrescriptionViewSet, basename="prescription")
router.register(r"staff", StaffMemberViewSet, basename="staff")
router.register(r"equipment", EquipmentViewSet, basename="equipment")
router.register(r"stock", StockItemViewSet, basename="stock")

urlpatterns = [
    path('alerts/', alerts_view, name='laboratory-alerts'),
    path("", include(router.urls)),
]
