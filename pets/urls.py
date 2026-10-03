from django.urls import path

from . import views

app_name = "pets"

urlpatterns = [
    path("", views.home, name="home"),
    path("pets/", views.PetListView.as_view(), name="list"),
    path("pets/<int:pk>/", views.pet_detail, name="detail"),
    path("pets/<int:pk>/favorite/", views.toggle_favorite, name="favorite"),
    path("favorites/", views.favorites, name="favorites"),
]
