from django.shortcuts import render
from django.views import View

from ..services import CatalogService

FALLBACK_IMAGES = [
    ("images/brand/hero-groom-1-hd.webp", "images/brand/hero-groom-1-hd.jpg"),
    ("images/brand/hero-groom-3-hd.webp", "images/brand/hero-groom-3-hd.jpg"),
    ("images/brand/hero-groom-2-hd.webp", "images/brand/hero-groom-2-hd.jpg"),
]

PERSIAN_INDEX = ("۰۱", "۰۲", "۰۳", "۰۴", "۰۵", "۰۶", "۰۷", "۰۸")


class ServiceListView(View):
    template_name = "catalog/list.html"

    def get(self, request):
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
            cards.append(
                {
                    "name": service.name,
                    "description": service.description
                    or (cfg.short_description if cfg else "")
                    or "رزرو آنلاین با استاندارد برند",
                    "label": (cfg.card_label if cfg and cfg.card_label else f"{idx} — {category}"),
                    "slug": service.slug,
                    "price": service.price,
                    "duration": service.duration_minutes,
                    "image_webp": webp,
                    "image_jpg": jpg,
                    "category": category,
                }
            )
        return render(request, self.template_name, {"services": cards})
