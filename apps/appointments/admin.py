from django.contrib import admin

from .models import (
    Appointment,
    BookingBreak,
    BookingHoliday,
    BookingServiceConfig,
    BookingSpecialDate,
    DisabledTimeSlot,
)


class BookingBreakInline(admin.TabularInline):
    model = BookingBreak
    extra = 0


class BookingSpecialDateInline(admin.TabularInline):
    model = BookingSpecialDate
    extra = 0
    fields = (
        "date",
        "is_closed",
        "start_time",
        "end_time",
        "slot_duration",
        "capacity",
        "note",
    )


class DisabledTimeSlotInline(admin.TabularInline):
    model = DisabledTimeSlot
    extra = 0


@admin.register(BookingServiceConfig)
class BookingServiceConfigAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "service",
        "enabled",
        "start_time",
        "end_time",
        "slot_duration",
        "capacity",
        "sort_order",
    )
    list_filter = ("enabled",)
    search_fields = ("key", "service__name", "card_label")
    inlines = [BookingBreakInline, BookingSpecialDateInline, DisabledTimeSlotInline]
    fieldsets = (
        (
            "سرویس",
            {
                "fields": (
                    "service",
                    "key",
                    "enabled",
                    "sort_order",
                    "card_label",
                    "short_description",
                    "image_webp",
                    "image_jpg",
                )
            },
        ),
        (
            "زمان‌بندی",
            {
                "fields": (
                    "working_days",
                    "start_time",
                    "end_time",
                    "slot_duration",
                    "capacity",
                    "booking_lead_hours",
                    "booking_window_days",
                )
            },
        ),
    )


@admin.register(BookingHoliday)
class BookingHolidayAdmin(admin.ModelAdmin):
    list_display = ("date", "title", "config", "is_closed")
    list_filter = ("is_closed", "config")
    date_hierarchy = "date"


@admin.register(BookingSpecialDate)
class BookingSpecialDateAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "config",
        "is_closed",
        "start_time",
        "end_time",
        "slot_duration",
        "capacity",
    )
    list_filter = ("config", "is_closed")
    date_hierarchy = "date"


@admin.register(DisabledTimeSlot)
class DisabledTimeSlotAdmin(admin.ModelAdmin):
    list_display = ("date", "config", "start_time", "end_time", "is_active", "reason")
    list_filter = ("config", "is_active")
    date_hierarchy = "date"


@admin.register(BookingBreak)
class BookingBreakAdmin(admin.ModelAdmin):
    list_display = ("config", "start_time", "end_time", "label", "is_active")
    list_filter = ("config", "is_active")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "booking_code",
        "full_name_display",
        "phone",
        "service",
        "starts_at",
        "status",
        "guide_acknowledged",
        "price_at_booking",
    )
    list_filter = ("status", "booking_config", "service", "guide_acknowledged")
    search_fields = (
        "booking_code",
        "first_name",
        "last_name",
        "phone",
        "notes",
    )
    date_hierarchy = "starts_at"
    readonly_fields = ("booking_code", "created_at", "updated_at")

    @admin.display(description="نام")
    def full_name_display(self, obj):
        return obj.full_name
