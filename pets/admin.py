from django.contrib import admin

from .models import Favorite, Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "animal_type", "breed", "age", "gender", "location", "status", "created_at")
    list_filter = ("status", "animal_type", "gender")
    list_editable = ("status",)
    search_fields = ("name", "breed", "location")
    actions = ["mark_available", "mark_adopted"]

    @admin.action(description="Mark selected pets as Available")
    def mark_available(self, request, queryset):
        queryset.update(status=Pet.Status.AVAILABLE)

    @admin.action(description="Mark selected pets as Adopted")
    def mark_adopted(self, request, queryset):
        queryset.update(status=Pet.Status.ADOPTED)


admin.site.register(Favorite)
