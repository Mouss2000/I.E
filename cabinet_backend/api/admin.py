from django.contrib import admin
from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ["patient_ref", "tooth_number", "shade", "material", "is_fast_track", "total_price", "status", "created_at"]
    list_filter = ["status", "material", "disinfected", "is_fast_track"]
    search_fields = ["patient_ref"]
