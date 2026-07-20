from django.contrib import admin

from .models import (
    ConsultationAlert,
    ConsultationCategory,
    ConsultationFAQ,
    ConsultationHubPage,
    ConsultationTicket,
    ConsultationTip,
    TipGroup,
)


class TipGroupInline(admin.TabularInline):
    model = TipGroup
    extra = 0


class ConsultationTipInline(admin.StackedInline):
    model = ConsultationTip
    extra = 0
    fields = (
        "group",
        "title",
        "description",
        "icon",
        "sort_order",
        "enabled",
        "is_highlight",
        "video_url",
        "external_link",
    )


class ConsultationAlertInline(admin.TabularInline):
    model = ConsultationAlert
    extra = 0


class ConsultationFAQInline(admin.TabularInline):
    model = ConsultationFAQ
    extra = 0


@admin.register(ConsultationHubPage)
class ConsultationHubPageAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "enabled", "updated_at")
    list_filter = ("enabled",)
    search_fields = ("key", "title", "subtitle")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "key",
                    "enabled",
                    "section_label",
                    "title",
                    "subtitle",
                    "document_title",
                    "meta_description",
                )
            },
        ),
        (
            "کارت‌ها و پیام‌ها",
            {
                "fields": (
                    "empty_message",
                    "card_cta_label",
                    "card_stats_template",
                )
            },
        ),
    )


@admin.register(ConsultationCategory)
class ConsultationCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "title",
        "enabled",
        "sort_order",
        "estimated_read_minutes",
        "content_version",
    )
    list_filter = ("enabled",)
    search_fields = ("key", "title", "short_description")
    inlines = [
        TipGroupInline,
        ConsultationAlertInline,
        ConsultationFAQInline,
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "key",
                    "title",
                    "card_label",
                    "short_description",
                    "description",
                    "enabled",
                    "sort_order",
                )
            },
        ),
        (
            "نمایش",
            {
                "fields": (
                    "icon",
                    "accent_color",
                    "image_webp",
                    "image_jpg",
                    "estimated_read_minutes",
                )
            },
        ),
        (
            "گیت رزرو (متن‌های داینامیک)",
            {
                "fields": (
                    "gate_eyebrow",
                    "gate_title",
                    "gate_body",
                    "gate_primary_kicker",
                    "gate_primary_cta",
                    "gate_primary_desc",
                    "gate_primary_cta_suffix",
                    "gate_secondary_cta",
                    "gate_secondary_desc",
                    "gate_first_visit_title",
                    "gate_first_visit_body",
                )
            },
        ),
        (
            "تأیید نهایی رزرو",
            {
                "fields": (
                    "confirm_guide_heading",
                    "confirm_guide_link_label",
                    "acknowledgment_label",
                    "acknowledgment_error",
                )
            },
        ),
        (
            "یکپارچگی و فایل",
            {
                "fields": (
                    "booking_service_keys",
                    "pdf_guide",
                    "content_version",
                )
            },
        ),
    )


@admin.register(TipGroup)
class TipGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "phase", "key", "sort_order", "enabled")
    list_filter = ("category", "phase", "enabled")


@admin.register(ConsultationTip)
class ConsultationTipAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "group",
        "is_highlight",
        "enabled",
        "sort_order",
    )
    list_filter = ("category", "group", "is_highlight", "enabled")
    search_fields = ("title", "description")


@admin.register(ConsultationAlert)
class ConsultationAlertAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "severity",
        "show_in_booking",
        "enabled",
        "sort_order",
    )
    list_filter = ("category", "severity", "show_in_booking", "enabled")


@admin.register(ConsultationFAQ)
class ConsultationFAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "enabled", "sort_order")
    list_filter = ("category", "enabled")
    search_fields = ("question", "answer")


@admin.register(ConsultationTicket)
class ConsultationTicketAdmin(admin.ModelAdmin):
    list_display = (
        "full_name_display",
        "phone",
        "category",
        "booking_service_key",
        "status",
        "source",
        "created_at",
    )
    list_filter = ("status", "source", "category")
    search_fields = ("first_name", "last_name", "phone", "message")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="نام")
    def full_name_display(self, obj):
        return obj.full_name
