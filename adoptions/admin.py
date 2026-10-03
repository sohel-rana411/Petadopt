from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import AdoptionRequest


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "pet", "created_at", "phone", "short_reason", "status")
    list_filter = ("status", "pet__animal_type", "created_at")
    search_fields = ("user__username", "pet__name", "phone")
    readonly_fields = ("created_at",)
    actions = ["approve_requests", "reject_requests"]

    @admin.display(description="Reason")
    def short_reason(self, obj):
        return (obj.reason[:60] + "…") if len(obj.reason) > 60 else obj.reason

    def _set_status(self, request, queryset, new_status):
        done = 0
        # Loop + save() (not queryset.update) so the approval business logic runs.
        for req in queryset.filter(status=AdoptionRequest.Status.PENDING):
            req.status = new_status
            try:
                req.clean()
            except ValidationError as exc:
                self.message_user(request, f"{req}: {exc.messages[0]}", messages.ERROR)
                continue
            req.save()
            done += 1
        self.message_user(request, f"{done} request(s) marked {new_status}.", messages.SUCCESS)

    @admin.action(description="Approve selected pending requests (pet becomes Adopted)")
    def approve_requests(self, request, queryset):
        self._set_status(request, queryset, AdoptionRequest.Status.APPROVED)

    @admin.action(description="Reject selected pending requests")
    def reject_requests(self, request, queryset):
        self._set_status(request, queryset, AdoptionRequest.Status.REJECTED)
