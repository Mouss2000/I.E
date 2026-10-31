from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)

    auto_create_schema = True

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass


class PlatformAccount(models.Model):
    name = models.CharField(max_length=120)
    login_key = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=20, choices=[('ADMIN', 'Administrateur'), ('DENTIST', 'Dentiste'), ('LAB', 'Laboratoire')])
    laboratory = models.ForeignKey(Client, null=True, blank=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    password_hash = models.CharField(max_length=255, blank=True)
    password_reset_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']


class AccessLog(models.Model):
    account = models.ForeignKey(PlatformAccount, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=150)
    event = models.CharField(max_length=30)
    success = models.BooleanField(default=True)
    details = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class SupportTicket(models.Model):
    account = models.ForeignKey(PlatformAccount, on_delete=models.PROTECT)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('OPEN', 'Ouvert'), ('IN_PROGRESS', 'En cours'), ('RESOLVED', 'Résolu')], default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
