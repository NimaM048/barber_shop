import re

from django.shortcuts import render
from django.views import View

from apps.core.services import SeoService
from apps.core.services.page_content_service import PageContentService

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


def _clean_label(raw: str, fallback: str) -> str:
    text = EMOJI_RE.sub("", raw or "").strip(" ·-–—")
    text = re.sub(r"\s+", " ", text).strip()
    return text or fallback


class ServiceListView(View):
    template_name = "catalog/list.html"

    def get(self, request):
        seo = SeoService()
        services = list(CatalogService().list_active_services())
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
                "schema_json": seo.dumps(schemas),
            },
        )
