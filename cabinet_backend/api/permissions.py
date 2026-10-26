from rest_framework.permissions import BasePermission
from customers.views import current_account


class DemoTenantPermission(BasePermission):
    message = 'Ce compte n’est pas affecté à ce laboratoire.'

    def has_permission(self, request, view):
        # Keep the existing, token-free courier prototype unchanged.
        if not request.headers.get('Authorization', '').startswith('Bearer '):
            return True
        account = current_account(request)
        return account.role == 'LAB' and account.laboratory_id == request.tenant.pk
