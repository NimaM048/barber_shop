import re

from django.shortcuts import render
from django.views import View

from apps.core.services import SeoService
from apps.core.services.page_content_service import PageContentService
from apps.appointments.models import BookingSettings

from ..services import CatalogService

FALLBACK_IMAGES = [
    ("images/brand/hero-groom-1-hd.webp", "images/brand/hero-groom-1-hd.jpg"),
    ("images/brand/hero-groom-3-hd.webp", "images/brand/hero-groom-3-hd.jpg"),
    ("images/brand/hero-groom-2-hd.webp", "images/brand/hero-groom-2-hd.jpg"),
]

PERSIAN_INDEX = ("۰۱", "۰۲", "۰۳", "۰۴", "۰۵", "۰۶", "۰۷", "۰۸")
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0000FE0F"
    "]+",
    flags=re.UNICODE,
)
CATEGORY_LABELS = {
    "vip": "تجربه اختصاصی",
    "skin": "مراقبت تخصصی",
    "groom": "تشریفات داماد",
    "hair": "طراحی مو",
}

SERVICE_DETAILS = {
    "vip": {
        "includes": "بررسی کوتاه استایل، اصلاح و فرم‌دهی مو و ریش، و پرداخت نهایی جزئیات.",
        "suitable_for": "برای اصلاح اختصاصی، جلسه مهم یا زمانی که به نتیجه دقیق‌تر نیاز دارید.",
        "provider": "صالح ایوبی یا یکی از اعضای تخصصی تیم، متناسب با زمان و نوع خدمت.",
        "consultation": "مشاوره پیش از رزرو پیشنهاد می‌شود؛ برای انتخاب اولیه الزامی نیست.",
    },
    "skin": {
        "includes": "ارزیابی پوست، پاکسازی و مراقبت پوست سر، همراه با طراحی و استایل مو.",
        "suitable_for": "برای رسیدگی پوست و مو، پیش از قرار مهم یا یک نوبت مراقبتی کامل.",
        "provider": "عضو تخصصی تیم در حوزه پوست و مو؛ در صورت نیاز با هماهنگی صالح.",
        "consultation": "اگر پوست حساس یا هدف مشخصی دارید، مشاوره پیش از رزرو توصیه می‌شود.",
    },
    "groom": {
        "includes": "هماهنگی استایل، طراحی مو و ریش، آماده‌سازی پوست و جزئیات نهایی داماد.",
        "suitable_for": "برای داماد و مراسمی که زمان‌بندی و نتیجه نهایی در آن اهمیت دارد.",
        "provider": "صالح ایوبی با همراهی تیم تخصصی، پس از هماهنگی برنامه مراسم.",
        "consultation": "مشاوره پیش از رزرو لازم است تا زمان‌بندی و جزئیات مراسم هماهنگ شود.",
    },
}


def _clean_label(raw: str, fallback: str) -> str:
    text = EMOJI_RE.sub("", raw or "").strip(" ·-–—")
    text = re.sub(r"\s+", " ", text).strip()
    return text or fallback


class ServiceListView(View):
    template_name = "catalog/list.html"

    def get(self, request):
        seo = SeoService()
        services = list(CatalogService().list_active_services())
        booking_settings = BookingSettings.objects.filter(key="site", is_active=True).first()
        booking_status = (
            "رزرو پس از انتخاب زمان قطعی است."
            if not booking_settings or booking_settings.auto_confirm
            else "رزرو ثبت می‌شود و برای قطعی‌شدن نیاز به هماهنگی دارد."
        )
        cards = []
        for i, service in enumerate(services):
            cfg = getattr(service, "booking_config", None)
            webp, jpg = FALLBACK_IMAGES[i % len(FALLBACK_IMAGES)]
            if cfg and cfg.image_webp:
                webp = cfg.image_webp
            if cfg and cfg.image_jpg:
                jpg = cfg.image_jpg
            idx = PERSIAN_INDEX[i] if i < len(PERSIAN_INDEX) else str(i + 1)
            category = service.category.name if service.category_id else "خدمت"
            slug_key = (cfg.key if cfg else "") or service.slug
            preferred = CATEGORY_LABELS.get(slug_key, category)
            raw_label = preferred if slug_key in CATEGORY_LABELS else (
                cfg.card_label if cfg and cfg.card_label else preferred
            )
            details = SERVICE_DETAILS.get(
                slug_key,
                {
                    "includes": "جزئیات مراحل این خدمت هنگام رزرو به شما نمایش داده می‌شود.",
                    "suitable_for": "برای انتخاب دقیق، هدف و زمان مراجعه خود را با ما در میان بگذارید.",
                    "provider": "توسط عضو تخصصی تیم و با هماهنگی سالن اجرا می‌شود.",
                    "consultation": "در صورت نیاز می‌توانید پیش از رزرو درخواست مشاوره ثبت کنید.",
                },
            )
            cards.append(
                {
                    "name": service.name,
                    "description": service.description
                    or (cfg.short_description if cfg else "")
                    or "رزرو آنلاین با استاندارد برند",
                    "label": f"{idx} — {_clean_label(raw_label, preferred)}",
                    "slug": service.slug,
                    "price": f"{int(service.price):,}",
                    "duration": service.duration_minutes,
                    "image_webp": webp,
                    "image_jpg": jpg,
                    "category": category,
                    "details": details,
                    "booking_status": booking_status,
                }
            )
        page_seo = seo.catalog_meta()
        page_content = PageContentService().get("catalog")
        schemas = [
            seo.breadcrumb_schema(
                [
                    {"name": "خانه", "path": "/"},
                    {"name": "خدمات", "path": "/services/"},
                ],
                request,
            ),
        ]
        if cards:
            schemas.append(seo.service_catalog_schema(cards, request))
        return render(
            request,
            self.template_name,
            {
                "services": cards,
                "page_seo": page_seo,
                "page_content": page_content,
                "booking_status": booking_status,
                "schema_json": seo.dumps(schemas),
            },
        )
