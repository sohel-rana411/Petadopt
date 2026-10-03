from rest_framework import serializers

from .models import AdoptionRequest
from pets.models import Pet


class AdoptionRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    pet = serializers.PrimaryKeyRelatedField(queryset=Pet.objects.all())
    pet_name = serializers.CharField(source="pet.name", read_only=True)

    class Meta:
        model = AdoptionRequest
        fields = [
            "id", "user", "pet", "pet_name", "phone", "address", "reason",
            "previous_pet_experience", "message", "status", "created_at",
        ]
        # Status is changed by admins (Django Admin), never by the applicant.
        read_only_fields = ["status", "created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None and not isinstance(self.instance, (list, tuple)) \
                and hasattr(self.instance, "pk"):
            self.fields["pet"].required = False

    def validate(self, attrs):
        # Updating an existing request
        if self.instance is not None:
            if "pet" in attrs and attrs["pet"] != self.instance.pet:
                raise serializers.ValidationError({"pet": "The pet of an existing request cannot be changed."})
            if self.instance.status != AdoptionRequest.Status.PENDING:
                raise serializers.ValidationError("Only pending requests can be edited.")
            return attrs

        # Creating a new request
        user = self.context["request"].user
        pet = attrs["pet"]
        if not pet.is_available:  # Rule 1
            raise serializers.ValidationError({"pet": "This pet has already been adopted."})
        if AdoptionRequest.objects.filter(  # Rule 2
            user=user, pet=pet, status=AdoptionRequest.Status.PENDING
        ).exists():
            raise serializers.ValidationError({"pet": "You already have a pending request for this pet."})
        return attrs
