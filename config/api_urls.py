from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from adoptions.api import AdoptionRequestViewSet
from pets.api import PetViewSet

router = DefaultRouter()
router.register("pets", PetViewSet, basename="pet")
router.register("adoptions", AdoptionRequestViewSet, basename="adoption")

urlpatterns = [
    path("token/", obtain_auth_token, name="api-token"),
    path("", include(router.urls)),
]
