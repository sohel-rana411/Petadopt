from rest_framework import permissions, viewsets

from .filters import PetFilter
from .models import Pet
from .serializers import PetSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Anyone can read pets; only staff can create/update/delete."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = PetFilter
    search_fields = ["name", "animal_type", "breed", "location", "description"]
    ordering = ["-created_at"]
