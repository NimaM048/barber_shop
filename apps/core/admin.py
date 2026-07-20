from django.contrib import admin

from apps.core.brand_story import BrandStory, BrandTimelineStep, BrandValue
from apps.core.footer_finale import FooterFinale, FooterNavLink


class BrandTimelineStepInline(admin.TabularInline):
    model = BrandTimelineStep
    extra = 0
    fields = (
        "number_label",
        "title",
        "description",
        "portrait_effect",
        "sort_order",
        "is_active",
    )
    ordering = ("sort_order",)


class BrandValueInline(admin.TabularInline):
    model = BrandValue
    extra = 0
    fields = ("title", "subtitle", "sort_order", "is_active")
    ordering = ("sort_order",)


@admin.register(BrandStory)
class BrandStoryAdmin(admin.ModelAdmin):
    list_display = ("key", "section_label", "founder_name", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("key", "headline", "quote_text", "founder_name")
    inlines = [BrandTimelineStepInline, BrandValueInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "key",
                    "is_published",
                    "edition_label",
                    "section_label",
                )
            },
        ),
        (
            "فلسفه",
            {
                "fields": (
                    "headline",
                    "subtitle",
                    "story_body",
                )
            },
        ),
        (
            "نقل‌قول و امضا",
            {
                "fields": (
                    "quote_text",
                    "founder_name",
                    "founder_title",
                    "quote_signature",
                )
            },
        ),
        (
            "تایپوگرافی پس‌زمینه",
            {
                "fields": (
                    "bg_word_1",
                    "bg_word_2",
                    "bg_word_3",
                    "bg_word_4",
                )
            },
        ),
        (
            "پرتره",
            {
                "fields": (
                    "portrait",
                    "portrait_static",
                    "portrait_webp_static",
                    "portrait_lqip_static",
                    "portrait_alt",
                    "portrait_caption",
                    "portrait_index",
                )
            },
        ),
        (
            "برچسب‌ها و CTA",
            {
                "fields": (
                    "timeline_label",
                    "values_label",
                    "cta_primary_label",
                    "cta_primary_href",
                    "cta_secondary_label",
                    "cta_secondary_href",
                )
            },
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("seo_title", "seo_description"),
            },
        ),
    )


@admin.register(BrandTimelineStep)
class BrandTimelineStepAdmin(admin.ModelAdmin):
    list_display = (
        "number_label",
        "title",
        "story",
        "portrait_effect",
        "sort_order",
        "is_active",
    )
    list_filter = ("is_active", "portrait_effect", "story")
    search_fields = ("title", "description", "number_label")
    ordering = ("story", "sort_order")


@admin.register(BrandValue)
class BrandValueAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "story", "sort_order", "is_active")
    list_filter = ("is_active", "story")
    search_fields = ("title", "subtitle")
    ordering = ("story", "sort_order")


class FooterNavLinkInline(admin.TabularInline):
    model = FooterNavLink
    extra = 0
    fields = ("label", "href", "sort_order", "is_active", "open_in_new_tab")
    ordering = ("sort_order",)


@admin.register(FooterFinale)
class FooterFinaleAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "section_label",
        "bg_word",
        "founder_name",
        "is_published",
        "updated_at",
    )
    list_filter = ("is_published", "show_founder", "show_navigation")
    search_fields = ("key", "philosophy", "cta_statement", "founder_name", "signature")
    inlines = [FooterNavLinkInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "key",
                    "is_published",
                    "edition_label",
                    "section_label",
                    "aria_label",
                )
            },
        ),
        (
            "فصل اول — تأمل",
            {
                "fields": (
                    "philosophy",
                    "philosophy_caption",
                    "bg_word",
                )
            },
        ),
        (
            "فصل دوم — تصمیم",
            {
                "fields": (
                    "cta_statement",
                    "cta_prompt",
                    "cta_primary_label",
                    "cta_primary_href",
                    "cta_secondary_label",
                    "cta_secondary_href",
                )
            },
        ),
        (
            "فصل سوم — ارتباط",
            {
                "fields": (
                    "contact_caption",
                    ("show_phone", "phone", "phone_display", "phone_label"),
                    ("show_whatsapp", "whatsapp", "whatsapp_label"),
                    ("show_instagram", "instagram", "instagram_label"),
                    ("show_telegram", "telegram", "telegram_label"),
                    ("show_email", "email", "email_label"),
                    ("show_website", "website", "website_label"),
                    ("show_address", "address", "address_label"),
                    ("show_hours", "working_hours", "hours_label"),
                )
            },
        ),
        (
            "امضای برند",
            {
                "fields": (
                    "logo",
                    "logo_static",
                    "logo_alt",
                    "signature",
                    "show_founder",
                    "founder_name",
                    "founder_title",
                    "founded_year",
                    "copyright_text",
                    "show_navigation",
                )
            },
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("seo_title", "seo_description"),
            },
        ),
    )


@admin.register(FooterNavLink)
class FooterNavLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "href", "footer", "sort_order", "is_active")
    list_filter = ("is_active", "footer")
    search_fields = ("label", "href")
    ordering = ("footer", "sort_order")
