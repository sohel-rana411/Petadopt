import django_filters as filters
from django.db.models import Q

from .models import Pet


class PetFilter(filters.FilterSet):
    q = filters.CharFilter(method="filter_q", label="Search")
    name = filters.CharFilter(lookup_expr="icontains")
    breed = filters.CharFilter(lookup_expr="icontains")
    location = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Pet
        fields = ["animal_type", "gender", "status"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(animal_type__icontains=value)
            | Q(breed__icontains=value)
            | Q(location__icontains=value)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.form.fields.values():
            css = "form-select" if hasattr(field, "choices") else "form-control"
            field.widget.attrs["class"] = css
