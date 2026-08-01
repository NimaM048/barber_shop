from django.contrib import admin

from .models import Barber, WorkingHour


class WorkingHourInline(admin.TabularInline):
    model = WorkingHour
    extra = 1


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "is_active", "experience_years")
    list_filter = ("is_active",)
    search_fields = ("display_name", "user__username")
    fields = (
        "user",
        "display_name",
        "bio",
        "avatar",
        "avatar_static",
        "avatar_webp_static",
        "experience_years",
        "is_active",
    )
    inlines = [WorkingHourInline]


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ("barber", "weekday", "start_time", "end_time", "is_active")
    list_filter = ("weekday", "is_active")
