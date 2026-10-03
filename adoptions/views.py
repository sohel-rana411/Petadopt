from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from pets.models import Pet

from .forms import AdoptionRequestForm
from .models import AdoptionRequest


@login_required
def apply(request, pk):
    pet = get_object_or_404(Pet, pk=pk)

    if not pet.is_available:
        messages.error(request, "This pet has already been adopted.")
        return redirect("pets:detail", pk=pet.pk)
    if AdoptionRequest.objects.filter(
        user=request.user, pet=pet, status=AdoptionRequest.Status.PENDING
    ).exists():
        messages.warning(request, "You already have a pending request for this pet.")
        return redirect("adoptions:my_requests")

    form = AdoptionRequestForm(
        request.POST or None, instance=AdoptionRequest(user=request.user, pet=pet)
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Your application for {pet.name} was submitted!")
        return redirect("adoptions:my_requests")
    return render(request, "adoptions/apply.html", {"form": form, "pet": pet})


@login_required
def my_requests(request):
    requests_qs = AdoptionRequest.objects.filter(user=request.user).select_related("pet")
    return render(request, "adoptions/my_requests.html", {"adoption_requests": requests_qs})
