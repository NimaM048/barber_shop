from django.views.generic import TemplateView

from apps.catalog.services import CatalogService
from apps.core.services.brand_story_service import BrandStoryService
from apps.portfolio.services import PortfolioService

SERVICE_IMAGES = [
    ("images/brand/hero-groom-1-hd.webp", "images/brand/hero-groom-1-hd.jpg"),
    ("images/brand/hero-groom-3-hd.webp", "images/brand/hero-groom-3-hd.jpg"),
    ("images/brand/hero-groom-2-hd.webp", "images/brand/hero-groom-2-hd.jpg"),
]

FALLBACK_SERVICES = [
    {
        "name": "آرایش و استایل عروسی",
        "description": "آماده‌سازی کامل داماد برای روز مهم",
        "label": "۰۱ — داماد",
        "image_webp": SERVICE_IMAGES[0][0],
        "image_jpg": SERVICE_IMAGES[0][1],
        "slug": "groom",
    },
    {
        "name": "مراقبت تخصصی پوست",
        "description": "پروتکل‌های اختصاصی برای پوست سالم و درخشان",
        "label": "۰۲ — پوست",
        "image_webp": SERVICE_IMAGES[1][0],
        "image_jpg": SERVICE_IMAGES[1][1],
        "slug": "skin",
    },
    {
        "name": "طراحی تخصصی مو",
        "description": "استایل و فرم‌دهی با استاندارد برند",
        "label": "۰۳ — مو",
        "image_webp": SERVICE_IMAGES[2][0],
        "image_jpg": SERVICE_IMAGES[2][1],
        "slug": "hair",
    },
]

PERSIAN_INDEX = ("۰۱", "۰۲", "۰۳", "۰۴", "۰۵", "۰۶")


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active = list(CatalogService().list_active_services()[:6])

        if active:
            showcase = []
            for i, service in enumerate(active):
                idx = PERSIAN_INDEX[i] if i < len(PERSIAN_INDEX) else str(i + 1)
                category = service.category.name if service.category_id else "خدمت"
                webp, jpg = SERVICE_IMAGES[i % len(SERVICE_IMAGES)]
                showcase.append(
                    {
                        "name": service.name,
                        "description": service.description
                        or "رزرو آنلاین با استاندارد برند",
                        "label": f"{idx} — {category}",
                        "image_webp": webp,
                        "image_jpg": jpg,
                        "slug": service.slug,
                        "price": service.price,
                        "duration": service.duration_minutes,
                    }
                )
            ctx["showcase_services"] = showcase
        else:
            ctx["showcase_services"] = FALLBACK_SERVICES

        gallery = PortfolioService().homepage_payload()
        ctx["gallery_categories"] = gallery["categories"]
        ctx["gallery_items"] = gallery["items"]
        ctx["brand_story"] = BrandStoryService().homepage_payload()
        return ctx
