from rest_framework.permissions import BasePermission
from customers.views import current_account


class LaboratoryResourcePermission(BasePermission):
    """Require a laboratory schema and an authenticated laboratory actor."""

    message = 'Authenticated laboratory access is required.'

    def has_permission(self, request, view):
        tenant = getattr(request, 'tenant', None)
        if tenant is None or tenant.schema_name == 'public':
            return False
        if request.headers.get('Authorization', '').startswith('Bearer '):
            account = current_account(request)
            return account.role == 'LAB' and account.laboratory_id == tenant.pk
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        from .models import EmployeeProfile
        return EmployeeProfile.objects.filter(user_id=request.user.pk).exists()


class DemoTenantPermission(BasePermission):
    message = 'Ce compte n’est pas affecté à ce laboratoire.'

    def has_permission(self, request, view):
        # Keep the existing, token-free courier prototype unchanged.
        if not request.headers.get('Authorization', '').startswith('Bearer '):
            return True
        account = current_account(request)
        return account.role == 'LAB' and account.laboratory_id == request.tenant.pk
