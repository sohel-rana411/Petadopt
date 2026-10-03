from django.urls import path

from . import views

app_name = "adoptions"

urlpatterns = [
    path("my-requests/", views.my_requests, name="my_requests"),
    path("apply/<int:pk>/", views.apply, name="apply"),
]
