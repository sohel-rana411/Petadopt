from django import forms

from .models import AdoptionRequest


class AdoptionRequestForm(forms.ModelForm):
    previous_pet_experience = forms.TypedChoiceField(
        label="Have you owned a pet before?",
        choices=[(True, "Yes"), (False, "No")],
        coerce=lambda v: v in (True, "True", "true"),
        widget=forms.RadioSelect,
        initial=False,
    )

    class Meta:
        model = AdoptionRequest
        fields = ["address", "phone", "reason", "previous_pet_experience", "message"]
        labels = {
            "reason": "Why do you want this pet?",
            "message": "Additional message (optional)",
        }
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+8801XXXXXXXXX"}),
            "reason": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "message": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }
