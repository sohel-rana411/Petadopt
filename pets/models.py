from django.conf import settings
from django.db import models


class Pet(models.Model):
    class AnimalType(models.TextChoices):
        DOG = "Dog", "Dog"
        CAT = "Cat", "Cat"
        BIRD = "Bird", "Bird"
        RABBIT = "Rabbit", "Rabbit"
        OTHER = "Other", "Other"

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    class Status(models.TextChoices):
        AVAILABLE = "Available", "Available"
        ADOPTED = "Adopted", "Adopted"

    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=20, choices=AnimalType.choices, default=AnimalType.DOG)
    breed = models.CharField(max_length=100, blank=True)
    age = models.PositiveSmallIntegerField(help_text="Age in years (0 = under 1 year)")
    gender = models.CharField(max_length=10, choices=Gender.choices)
    location = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="pets/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.name} ({self.animal_type})"

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE

    @property
    def age_display(self):
        if self.age == 0:
            return "Under 1 year"
        return f"{self.age} year" + ("" if self.age == 1 else "s")


class Favorite(models.Model):
    """Bonus: users can save pets to favorites."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "pet"], name="unique_favorite")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.pet}"
