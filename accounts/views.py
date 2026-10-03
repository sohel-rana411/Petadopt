from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from adoptions.models import AdoptionRequest

from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("pets:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.username}! Your account has been created.")
        return redirect("pets:home")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    qs = AdoptionRequest.objects.filter(user=request.user)
    stats = {s: qs.filter(status=s).count() for s in AdoptionRequest.Status.values}
    return render(request, "accounts/profile.html", {"stats": stats, "total": qs.count()})
