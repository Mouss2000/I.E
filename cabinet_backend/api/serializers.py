from rest_framework import serializers
from .models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Prescription.
    Enforces the "Verrou Sanitaire": rejects any submission where
    disinfected is False — mirroring the frontend lock.

    On CREATE: status and delivery_date are read-only (server defaults apply).
    On PATCH:  status and delivery_date become writable so Lab/Courier can update.
    """

    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "delivery_pin"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On creation (no instance yet), lock status & delivery_date as read-only
        if self.instance is None:
            self.fields["status"].read_only = True
            self.fields["delivery_date"].read_only = True

    def validate_disinfected(self, value):
        if not value:
            raise serializers.ValidationError(
                "Le verrou sanitaire est obligatoire. "
                "Les empreintes doivent être désinfectées avant envoi."
            )
        return value
