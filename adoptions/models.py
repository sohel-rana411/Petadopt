from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models, transaction

from pets.models import Pet

phone_validator = RegexValidator(
    r"^\+?[0-9\s\-]{7,20}$", "Enter a valid phone number (digits, spaces, dashes, optional leading +)."
)


class AdoptionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="adoption_requests")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="adoption_requests")
    phone = models.CharField(max_length=20, validators=[phone_validator])
    address = models.TextField()
    reason = models.TextField(verbose_name="Reason for adoption")
    previous_pet_experience = models.BooleanField(default=False, verbose_name="Has owned a pet before")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            # Rule 2 (DB-level safety net): one pending request per user per pet.
            models.UniqueConstraint(
                fields=["user", "pet"],
                condition=models.Q(status="Pending"),
                name="one_pending_request_per_user_and_pet",
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.pet.name} [{self.status}]"

    def clean(self):
        if not self.pet_id or not self.user_id:
            return
        if self._state.adding:
            # Rule 1: only available pets can be adopted.
            if not self.pet.is_available:
                raise ValidationError("This pet has already been adopted.")
            # Rule 2: no duplicate active (pending) requests for the same pet.
            if AdoptionRequest.objects.filter(
                user_id=self.user_id, pet_id=self.pet_id, status=self.Status.PENDING
            ).exists():
                raise ValidationError("You already have a pending request for this pet.")
        # Only one request can ever be approved for a pet.
        if self.status == self.Status.APPROVED and (
            AdoptionRequest.objects.filter(pet_id=self.pet_id, status=self.Status.APPROVED)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("Another request for this pet has already been approved.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            # Rule 3: approval marks the pet as adopted and closes other pending requests.
            if self.status == self.Status.APPROVED:
                Pet.objects.filter(pk=self.pet_id).update(status=Pet.Status.ADOPTED)
                AdoptionRequest.objects.filter(
                    pet_id=self.pet_id, status=self.Status.PENDING
                ).exclude(pk=self.pk).update(status=self.Status.REJECTED)
