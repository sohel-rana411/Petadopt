from rest_framework import serializers

from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Pet
        fields = [
            "id", "name", "animal_type", "breed", "age", "gender", "location",
            "description", "image", "status", "is_available", "created_at",
        ]
        read_only_fields = ["created_at"]
