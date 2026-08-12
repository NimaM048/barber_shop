"""Site settings service — DB overrides with env fallbacks."""

from __future__ import annotations

from django.conf import settings
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse

from apps.core.site_settings import HeaderNavLink, SiteSettings


def _env(attr: str, default: str = "") -> str:
    return getattr(settings, attr, default) or default


def _static_path(path: str) -> str:
    if not path:
        return ""
    if path.startswith(("http://", "https://", "/media/", "/static/")):
        return path
    return static(path)


def _resolve_href(href: str) -> str:
    raw = (href or "").strip()
    if not raw:
        return ""
    hash_suffix = ""
    if "#" in raw and not raw.startswith("#"):
        name, fragment = raw.split("#", 1)
        raw = name
        hash_suffix = f"#{fragment}"
    if raw.startswith(("#", "/", "http://", "https://", "tel:", "mailto:")):
        return raw + hash_suffix
    if ":" in raw:
        try:
            return reverse(raw) + hash_suffix
        except NoReverseMatch:
            return raw + hash_suffix
    return raw + hash_suffix


class SiteSettingsService:
    def get_record(self) -> SiteSettings | None:
        return (
            SiteSettings.objects.filter(key="site", is_published=True)
            .prefetch_related("nav_links")
            .first()
        )

    def branding(self) -> dict:
        rec = self.get_record()
        return {
            "SITE_NAME": (rec.site_name if rec and rec.site_name else None) or _env(
                "SITE_NAME", "صالح ایوبی"
            ),
            "SITE_TAGLINE": (rec.site_tagline if rec else "") or _env(
                "SITE_TAGLINE", "معماری زیبایی"
            ),
            "SITE_SUBTITLE": (rec.site_subtitle if rec else "") or _env("SITE_SUBTITLE", ""),
            "SITE_PHONE": (rec.phone if rec else "") or _env("SITE_PHONE", ""),
            "SITE_PHONE_DISPLAY": (rec.phone_display if rec else "") or _env(
                "SITE_PHONE_DISPLAY", ""
            ),
            "SITE_ADDRESS": (rec.address if rec else "") or _env("SITE_ADDRESS", ""),
            "SITE_LAT": float(rec.lat if rec and rec.lat is not None else _env("SITE_LAT", 32.6412)),
            "SITE_LNG": float(rec.lng if rec and rec.lng is not None else _env("SITE_LNG", 51.6902)),
            "SITE_INSTAGRAM": (rec.instagram if rec else "") or _env("SITE_INSTAGRAM", ""),
            "SITE_WEBSITE": (rec.website if rec else "") or _env("SITE_WEBSITE", ""),
            "SITE_HOURS_TEXT": (rec.hours_text if rec else "") or _env("SITE_HOURS_TEXT", ""),
            "SITE_GOOGLE_MAPS_URL": (rec.google_maps_url if rec else "") or _env(
                "SITE_GOOGLE_MAPS_URL", ""
            ),
            "SITE_GBP_URL": (rec.gbp_url if rec else "") or _env("SITE_GBP_URL", ""),
            "SITE_WHATSAPP": (rec.whatsapp if rec else "") or _env("SITE_PHONE", ""),
            "SITE_EMAIL": (rec.email if rec else "") or "",
            "SITE_TELEGRAM": (rec.telegram if rec else "") or "",
            "SITE_CITY": (rec.city if rec else "") or "اصفهان",
            "SITE_MAP_ZOOM": rec.map_zoom if rec else int(_env("SITE_MAP_ZOOM", "16") or 16),
            "LOGO_PATH": _static_path(
                rec.logo_path if rec and rec.logo_path else "images/brand/logo-signature-800.webp"
            ),
            "LOGO_ALT": (rec.logo_alt if rec else "") or _env("SITE_NAME", "صالح ایوبی"),
        }

    def header_payload(self) -> dict:
        rec = self.get_record()
        branding = self.branding()
        links = []
        if rec:
            for link in rec.nav_links.filter(is_active=True).order_by("sort_order", "id"):
                links.append(
                    {
                        "label": link.label,
                        "href": _resolve_href(link.href),
                        "show_on_mobile": link.show_on_mobile,
                    }
                )
        if not links:
            links = [
                {"label": "خدمات", "href": reverse("core:home") + "#services", "show_on_mobile": True},
                {"label": "گالری", "href": reverse("core:home") + "#gallery", "show_on_mobile": True},
                {"label": "نظرات", "href": reverse("reviews:hub"), "show_on_mobile": True},
                {"label": "مجله", "href": reverse("magazine:hub"), "show_on_mobile": True},
                {"label": "مشاوره", "href": reverse("consultations:hub"), "show_on_mobile": True},
            ]
        cta_href = _resolve_href(
            rec.header_cta_href if rec and rec.header_cta_href else "appointments:create"
        )
        return {
            "nav_links": links,
            "cta_short": (rec.header_cta_short if rec else "") or "رزرو",
            "cta_full": (rec.header_cta_full if rec else "") or "رزرو نوبت",
            "cta_href": cta_href,
            "logo_src": branding["LOGO_PATH"],
            "logo_alt": branding["LOGO_ALT"],
        }

    def location_chrome(self) -> dict:
        rec = self.get_record()
        branding = self.branding()
        site = branding["SITE_NAME"]
        return {
            "eyebrow": (rec.location_eyebrow if rec else "") or "موقعیت در اصفهان",
            "title_fa": (rec.location_title_fa if rec else "") or f"آدرس سالن {site} در اصفهان",
            "badge": (rec.location_badge if rec else "") or "سالن تخصصی پوست و مو",
            "lede": (rec.location_lede if rec else "") or (
                f"استودیوی تخصصی داماد، پوست و مو {site} در مشتاق اول اصفهان — "
                "رزرو قبلی، مسیریابی آسان."
            ),
            "district": (rec.location_district if rec else "") or "مشتاق اول",
            "street": (rec.location_street if rec else "") or "خیابان ابوالحسن اصفهانی",
            "cue": (rec.location_cue if rec else "") or "بعد از کوچه ۲۶",
            "availability": (rec.location_availability if rec else "") or "فقط با رزرو قبلی",
            "cta_directions": (rec.location_cta_directions if rec else "") or "مسیریابی",
            "cta_maps": (rec.location_cta_maps if rec else "") or "باز کردن در نقشه",
            "cta_copy": (rec.location_cta_copy if rec else "") or "کپی آدرس",
            "cta_gbp": (rec.location_cta_gbp if rec else "") or "مشاهده در گوگل",
        }
