from rest_framework import permissions, viewsets

from .models import AdoptionRequest
from .serializers import AdoptionRequestSerializer


class AdoptionRequestViewSet(viewsets.ModelViewSet):
    """Users can only see and manage their own adoption requests."""

    serializer_class = AdoptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]  # no DELETE
    filterset_fields = ["status", "pet"]
    search_fields = ["pet__name", "reason"]

    def get_queryset(self):
        return AdoptionRequest.objects.filter(user=self.request.user).select_related("pet", "user")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
