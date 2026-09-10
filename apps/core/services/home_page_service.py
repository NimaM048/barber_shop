"""Homepage CMS payload with fallbacks matching current production copy."""

from __future__ import annotations

from django.templatetags.static import static
from django.urls import reverse

from apps.core.home_page import HomeAssuranceStep, HomePage, HomeProofBullet


def _static(path: str) -> str:
    if not path:
        return ""
    if path.startswith(("http://", "https://", "/media/", "/static/")):
        return path
    return static(path)


DEFAULTS = {
    "hero_eyebrow": "استودیوی تخصصی داماد، پوست و مو در اصفهان",
    "hero_title": "استایل داماد، پوست و مو؛ دقیق، شخصی و آماده برای روز مهم.",
    "hero_tagline": (
        "از مشاوره تا اجرای نهایی، هر خدمت متناسب با چهره، "
        "زمان و نتیجه‌ای که می‌خواهید طراحی می‌شود."
    ),
    "hero_cta_primary_label": "رزرو آنلاین",
    "hero_cta_secondary_label": "راهنمای پیش از مراجعه",
    # Lossless WebP from the 2250px master; avoids showing a visibly
    # over-compressed image in the desktop LCP slot.
    "hero_image_webp": "images/brand/hero-cinematic-frame-hq.webp",
    # A dedicated 2560px portrait crop prevents the phone hero from enlarging
    # the old 960px landscape derivative until it looks soft.
    "hero_image_mobile_webp": "images/brand/hero-cinematic.webp",
    "hero_image_fallback": "images/brand/hero-cinematic-frame-fallback.jpg",
    "hero_logo_webp": "images/brand/logo-signature-800.webp",
    "hero_scroll_hint": "Scroll",
    "assurance_label": "تجربه‌ای حساب‌شده",
    "assurance_title": "از تصمیم تا نتیجه، هیچ مرحله‌ای مبهم نمی‌ماند.",
    "assurance_lede": "مسیر مراجعه کوتاه، روشن و متناسب با نیاز واقعی شما طراحی شده است.",
    "services_label": "خدمات منتخب",
    "services_title": "خدمتی که می‌خواهید؛ با جزئیات شفاف و رزرو مستقیم.",
    "services_lede": "هر مسیر با زمان، قیمت و نتیجه‌ای که انتظار دارید مشخص است.",
    "services_cta_label": "کاتالوگ کامل",
    "services_empty_message": "به‌زودی خدمات جدید اضافه می‌شود.",
    "services_card_cta_label": "رزرو این خدمت",
    "gallery_label": "نمونه کار",
    "gallery_title": "گالری",
    "gallery_lede": "نمونه‌های منتخب از اجرای خدمات در استودیو.",
    "reviews_label": "روایت مشتریان",
    "reviews_title": "آن‌چه بعد از مراجعه می‌ماند.",
    "reviews_lede": "تجربه داماد، VIP و پوست در استودیوی اصفهان — به روایت کسانی که آمده‌اند.",
    "reviews_cta_label": "همه روایت‌ها",
}

# Keep deployments that already ran `seed_cms` on the improved assets without
# overwriting a genuinely custom image selected from the CMS.
LEGACY_HERO_ASSETS = {
    "hero_image_webp": "images/brand/hero-cinematic-frame.webp",
    "hero_image_mobile_webp": "images/brand/hero-cinematic-frame-mobile.webp",
}

DEFAULT_PROOF = [
    "مشاوره پیش از اجرا",
    "رزرو مرحله‌به‌مرحله",
    "انتخاب شفاف خدمت",
]

DEFAULT_ASSURANCE = [
    {
        "number_label": "۰۱",
        "title": "انتخاب آگاهانه",
        "description": "خدمات، زمان اجرا و جزئیات هر مسیر را پیش از رزرو بررسی کنید.",
    },
    {
        "number_label": "۰۲",
        "title": "مشاوره شخصی",
        "description": "پیشنهاد نهایی بر اساس چهره، سبک و موقعیت شما شکل می‌گیرد.",
    },
    {
        "number_label": "۰۳",
        "title": "رزرو بدون اصطکاک",
        "description": "خدمت و زمان مناسب را آنلاین انتخاب کنید و آماده مراجعه شوید.",
    },
]


class HomePageService:
    def get_record(self) -> HomePage | None:
        return (
            HomePage.objects.filter(key="home", is_published=True, is_deleted=False)
            .prefetch_related("proof_bullets", "assurance_steps")
            .first()
        )

    def payload(self) -> dict:
        rec = self.get_record()
        data = DEFAULTS.copy()
        if rec:
            for field in DEFAULTS:
                val = getattr(rec, field, "")
                if val:
                    data[field] = val
            data["hero_cta_primary_href"] = rec.hero_cta_primary_href or "appointments:create"
            data["hero_cta_secondary_href"] = rec.hero_cta_secondary_href or "consultations:hub"
            data["services_cta_href"] = rec.services_cta_href or "catalog:list"
        else:
            data["hero_cta_primary_href"] = "appointments:create"
            data["hero_cta_secondary_href"] = "consultations:hub"
            data["services_cta_href"] = "catalog:list"

        for field, legacy_path in LEGACY_HERO_ASSETS.items():
            if data[field] == legacy_path:
                data[field] = DEFAULTS[field]

        data["hero_image_webp"] = _static(data["hero_image_webp"])
        data["hero_image_mobile_webp"] = _static(data["hero_image_mobile_webp"])
        data["hero_image_fallback"] = _static(data["hero_image_fallback"])
        data["hero_logo_webp"] = _static(data["hero_logo_webp"])

        proof = []
        if rec:
            proof = [
                b.text
                for b in rec.proof_bullets.filter(is_active=True).order_by("sort_order", "id")
            ]
        data["proof_bullets"] = proof or DEFAULT_PROOF

        steps = []
        if rec:
            steps = [
                {
                    "number_label": s.number_label,
                    "title": s.title,
                    "description": s.description,
                }
                for s in rec.assurance_steps.filter(is_active=True).order_by("sort_order", "id")
            ]
        data["assurance_steps"] = steps or DEFAULT_ASSURANCE

        def _href(raw: str) -> str:
            if raw.startswith(("/", "#", "http")):
                return raw
            if ":" in raw:
                from django.urls import NoReverseMatch, reverse

                try:
                    return reverse(raw)
                except NoReverseMatch:
                    return raw
            return raw

        data["hero_cta_primary_href"] = _href(data["hero_cta_primary_href"])
        data["hero_cta_secondary_href"] = _href(data["hero_cta_secondary_href"])
        data["services_cta_href"] = _href(data["services_cta_href"])

        return data
