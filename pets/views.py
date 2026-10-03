from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from adoptions.models import AdoptionRequest

from .filters import PetFilter
from .models import Favorite, Pet


def home(request):
    return render(request, "home.html", {
        "latest_pets": Pet.objects.filter(status=Pet.Status.AVAILABLE)[:6],
        "available_count": Pet.objects.filter(status=Pet.Status.AVAILABLE).count(),
        "adopted_count": Pet.objects.filter(status=Pet.Status.ADOPTED).count(),
    })


class PetListView(ListView):
    model = Pet
    template_name = "pets/pet_list.html"
    context_object_name = "pets"
    paginate_by = 9

    def get_queryset(self):
        self.filterset = PetFilter(self.request.GET or None, queryset=Pet.objects.all())
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["filter"] = self.filterset
        ctx["querystring"] = params.urlencode()
        if self.request.user.is_authenticated:
            ctx["favorite_ids"] = set(
                Favorite.objects.filter(user=self.request.user).values_list("pet_id", flat=True)
            )
        return ctx


def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    has_pending = is_favorite = False
    if request.user.is_authenticated:
        has_pending = AdoptionRequest.objects.filter(
            user=request.user, pet=pet, status=AdoptionRequest.Status.PENDING
        ).exists()
        is_favorite = Favorite.objects.filter(user=request.user, pet=pet).exists()
    return render(request, "pets/pet_detail.html", {
        "pet": pet, "has_pending": has_pending, "is_favorite": is_favorite,
    })


@login_required
@require_POST
def toggle_favorite(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, pet=pet)
    if created:
        messages.success(request, f"{pet.name} added to your favorites.")
    else:
        fav.delete()
        messages.info(request, f"{pet.name} removed from your favorites.")
    next_url = request.POST.get("next")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("pets:detail", pk=pk)


@login_required
def favorites(request):
    pets = Pet.objects.filter(favorited_by__user=request.user)
    return render(request, "pets/favorites.html", {
        "pets": pets, "favorite_ids": set(pets.values_list("id", flat=True)),
    })
