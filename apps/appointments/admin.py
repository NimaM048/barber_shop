from django.contrib import admin, messages

from .models import (
    Appointment,
    BookingBreak,
    BookingHoliday,
    BookingServiceConfig,
    BookingSettings,
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
        "barber",
        "starts_at",
        "status",
        "guide_acknowledged",
        "price_at_booking",
    )
    list_filter = ("status", "booking_config", "service", "barber", "guide_acknowledged")
    search_fields = (
        "booking_code",
        "first_name",
        "last_name",
        "phone",
        "notes",
    )
    date_hierarchy = "starts_at"
    readonly_fields = ("booking_code", "created_at", "updated_at")
    list_editable = ("status",)
    actions = (
        "action_confirm",
        "action_cancel",
        "action_complete",
        "action_no_show",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "booking_code",
                    "status",
                    ("first_name", "last_name"),
                    "phone",
                    ("service", "booking_config"),
                    "barber",
                    ("starts_at", "ends_at"),
                    "price_at_booking",
                    "guide_acknowledged",
                    "notes",
                )
            },
        ),
        (
            "سیستم",
            {"classes": ("collapse",), "fields": ("customer", "created_at", "updated_at")},
        ),
    )

    @admin.display(description="نام")
    def full_name_display(self, obj):
        return obj.full_name

    @admin.action(description="تأیید نوبت‌های انتخاب‌شده")
    def action_confirm(self, request, queryset):
        updated = queryset.exclude(status=Appointment.Status.CONFIRMED).update(
            status=Appointment.Status.CONFIRMED
        )
        self.message_user(request, f"{updated} نوبت تأیید شد.", messages.SUCCESS)

    @admin.action(description="لغو نوبت‌های انتخاب‌شده")
    def action_cancel(self, request, queryset):
        updated = queryset.exclude(status=Appointment.Status.CANCELLED).update(
            status=Appointment.Status.CANCELLED
        )
        self.message_user(request, f"{updated} نوبت لغو شد.", messages.WARNING)

    @admin.action(description="انجام شد")
    def action_complete(self, request, queryset):
        updated = queryset.update(status=Appointment.Status.COMPLETED)
        self.message_user(request, f"{updated} نوبت انجام‌شده ثبت شد.", messages.SUCCESS)

    @admin.action(description="حاضر نشد")
    def action_no_show(self, request, queryset):
        updated = queryset.update(status=Appointment.Status.NO_SHOW)
        self.message_user(request, f"{updated} نوبت «حاضر نشد» ثبت شد.", messages.WARNING)


@admin.register(BookingSettings)
class BookingSettingsAdmin(admin.ModelAdmin):
    list_display = ("key", "auto_confirm", "allow_customer_cancel", "is_active", "updated_at")
    fieldsets = (
        (None, {"fields": ("key", "is_active")}),
        (
            "قوانین رزرو",
            {
                "fields": (
                    "auto_confirm",
                    "cancel_before_hours",
                    ("allow_customer_cancel", "allow_customer_lookup"),
                    "max_bookings_per_phone_per_day",
                    ("default_booking_lead_hours", "default_booking_window_days"),
                )
            },
        ),
        (
            "پیام‌ها",
            {
                "fields": (
                    "confirmation_message",
                    "pending_message",
                    "cancellation_policy_text",
                    "staff_notification_email",
                )
            },
        ),
    )
