from django.contrib import admin

from apps.core.footer_finale import FooterFinale, FooterNavLink
from apps.core.home_page import HomeAssuranceStep, HomePage, HomeProofBullet
from apps.core.page_content import PageContent
from apps.core.site_settings import HeaderNavLink, SiteSettings


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


class HeaderNavLinkInline(admin.TabularInline):
    model = HeaderNavLink
    extra = 0
    fields = ("label", "href", "sort_order", "is_active", "show_on_mobile")
    ordering = ("sort_order",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("key", "site_name", "phone_display", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("site_name", "phone", "address")
    inlines = [HeaderNavLinkInline]
    fieldsets = (
        (None, {"fields": ("key", "is_published")}),
        (
            "برند",
            {"fields": ("site_name", "site_tagline", "site_subtitle", "logo_path", "logo_alt")},
        ),
        (
            "تماس",
            {
                "fields": (
                    ("phone", "phone_display"),
                    ("whatsapp", "email"),
                    ("instagram", "telegram", "website"),
                    "address",
                    "city",
                    ("lat", "lng", "map_zoom"),
                    "hours_text",
                    ("google_maps_url", "gbp_url"),
                )
            },
        ),
        (
            "هدر",
            {"fields": ("header_cta_short", "header_cta_full", "header_cta_href")},
        ),
        (
            "موقعیت (نقشه)",
            {
                "fields": (
                    "location_eyebrow",
                    "location_title_fa",
                    "location_badge",
                    "location_lede",
                    ("location_district", "location_street", "location_cue"),
                    "location_availability",
                    ("location_cta_directions", "location_cta_maps"),
                    ("location_cta_copy", "location_cta_gbp"),
                )
            },
        ),
        (
            "SEO پیش‌فرض",
            {"classes": ("collapse",), "fields": ("seo_title_default", "seo_description_default")},
        ),
    )


class HomeProofBulletInline(admin.TabularInline):
    model = HomeProofBullet
    extra = 0
    fields = ("text", "sort_order", "is_active")
    ordering = ("sort_order",)


class HomeAssuranceStepInline(admin.TabularInline):
    model = HomeAssuranceStep
    extra = 0
    fields = ("number_label", "title", "description", "sort_order", "is_active")
    ordering = ("sort_order",)


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ("key", "is_published", "updated_at")
    list_filter = ("is_published",)
    inlines = [HomeProofBulletInline, HomeAssuranceStepInline]
    fieldsets = (
        (None, {"fields": ("key", "is_published")}),
        (
            "هیرو",
            {
                "fields": (
                    "hero_eyebrow",
                    "hero_title",
                    "hero_tagline",
                    ("hero_cta_primary_label", "hero_cta_primary_href"),
                    ("hero_cta_secondary_label", "hero_cta_secondary_href"),
                    ("hero_image_webp", "hero_image_mobile_webp", "hero_image_fallback"),
                    "hero_logo_webp",
                    "hero_scroll_hint",
                )
            },
        ),
        (
            "تجربه (assurance)",
            {"fields": ("assurance_label", "assurance_title", "assurance_lede")},
        ),
        (
            "بخش خدمات",
            {
                "fields": (
                    "services_label",
                    "services_title",
                    "services_lede",
                    ("services_cta_label", "services_cta_href"),
                    "services_empty_message",
                    "services_card_cta_label",
                )
            },
        ),
        (
            "بخش گالری",
            {"fields": ("gallery_label", "gallery_title", "gallery_lede")},
        ),
        (
            "SEO",
            {"classes": ("collapse",), "fields": ("seo_title", "seo_description")},
        ),
    )


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("page", "section_label", "is_published", "updated_at")
    list_filter = ("page", "is_published")
    fieldsets = (
        (None, {"fields": ("page", "is_published")}),
        ("محتوا", {"fields": ("section_label", "title", "lede", "extra_label")}),
        (
            "رزرو — مراحل و نشان‌ها",
            {
                "classes": ("collapse",),
                "fields": (
                    ("assurance_1", "assurance_2"),
                    "status_text",
                    ("step_1_label", "step_2_label", "step_3_label"),
                    ("step_4_label", "step_5_label"),
                    "summary_empty",
                    "policy_text",
                ),
            },
        ),
        (
            "محتوای ساختاریافته (JSON)",
            {
                "classes": ("collapse",),
                "fields": ("content_json",),
                "description": "لیست‌ها، UI رزرو، signals مجله، journey کاتالوگ و …",
            },
        ),
        (
            "SEO",
            {"classes": ("collapse",), "fields": ("seo_title", "seo_description")},
        ),
    )
