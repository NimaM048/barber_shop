from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from apps.catalog.services import CatalogService
from apps.consultations.models import ConsultationFAQ, ConsultationHubPage
from apps.core.services import SeoService
from apps.core.services.home_page_service import HomePageService
from apps.core.services.page_content_service import PageContentService
from apps.portfolio.services import PortfolioService

SERVICE_IMAGES = [
    ("images/brand/service-card-1.webp", "images/brand/service-card-1.jpg"),
    ("images/brand/service-card-3.webp", "images/brand/service-card-3.jpg"),
    ("images/brand/service-card-2.webp", "images/brand/service-card-2.jpg"),
]

FALLBACK_SERVICES = [
    {
        "name": "آرایش و استایل عروسی",
        "description": "آماده‌سازی کامل داماد برای روز مهم",
        "label": "۰۱ — داماد",
        "index": "۰۱",
        "category": "داماد",
        "image_webp": SERVICE_IMAGES[0][0],
        "image_jpg": SERVICE_IMAGES[0][1],
        "slug": "groom",
        "duration": 90,
    },
    {
        "name": "مراقبت تخصصی پوست",
        "description": "پروتکل‌های اختصاصی برای پوست سالم و درخشان",
        "label": "۰۲ — پوست",
        "index": "۰۲",
        "category": "پوست",
        "image_webp": SERVICE_IMAGES[1][0],
        "image_jpg": SERVICE_IMAGES[1][1],
        "slug": "skin",
        "duration": 60,
    },
    {
        "name": "طراحی تخصصی مو",
        "description": "استایل و فرم‌دهی با استاندارد برند",
        "label": "۰۳ — مو",
        "index": "۰۳",
        "category": "مو",
        "image_webp": SERVICE_IMAGES[2][0],
        "image_jpg": SERVICE_IMAGES[2][1],
        "slug": "hair",
        "duration": 45,
    },
]

PERSIAN_INDEX = ("۰۱", "۰۲", "۰۳", "۰۴", "۰۵", "۰۶")


class HomeView(TemplateView):
    template_name = "pages/home.html"

    HOME_FAQ_DEFAULTS = {
        "enabled": True,
        "label": "پرسش‌های پرتکرار",
        "title": "پیش از مراجعه، پاسخ‌ها روشن‌اند.",
        "description": "برای جزئیات هر مسیر، راهنمای مشاوره همیشه در دسترس است.",
        "link_label": "همهٔ راهنماهای پیش از مراجعه",
    }

    @staticmethod
    def _homepage_faqs(limit: int = 4) -> list[dict[str, str]]:
        """Return a compact, category-balanced set of published FAQs."""
        candidates = list(
            ConsultationFAQ.objects.filter(enabled=True)
            .select_related("category")
            .order_by("sort_order", "id")
        )
        selected = []
        category_ids: set[int] = set()

        for faq in candidates:
            if faq.category_id in category_ids:
                continue
            selected.append(faq)
            category_ids.add(faq.category_id)
            if len(selected) == limit:
                break

        if len(selected) < limit:
            selected_ids = {faq.id for faq in selected}
            selected.extend(faq for faq in candidates if faq.id not in selected_ids)

        return [
            {
                "question": faq.question,
                "answer": faq.answer,
                "category": faq.category.title if faq.category_id else "",
            }
            for faq in selected[:limit]
        ]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        request = self.request
        seo = SeoService()
        active = list(CatalogService().list_active_services()[:6])

        if active:
            showcase = []
            for i, service in enumerate(active):
                idx = PERSIAN_INDEX[i] if i < len(PERSIAN_INDEX) else str(i + 1)
                category = service.category.name if service.category_id else "خدمت"
                cfg = getattr(service, "booking_config", None)
                webp, jpg = SERVICE_IMAGES[i % len(SERVICE_IMAGES)]
                if cfg and cfg.image_webp:
                    webp = cfg.image_webp
                if cfg and cfg.image_jpg:
                    jpg = cfg.image_jpg
                showcase.append(
                    {
                        "name": service.name,
                        "description": service.description
                        or "رزرو آنلاین با استاندارد برند",
                        "label": f"{idx} — {category}",
                        "index": idx,
                        "category": category,
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
        ctx["home_faqs"] = self._homepage_faqs()
        home_faq_section = self.HOME_FAQ_DEFAULTS.copy()
        hub = (
            ConsultationHubPage.objects.filter(key="hub", enabled=True, is_deleted=False)
            .only(
                "home_faq_enabled",
                "home_faq_label",
                "home_faq_title",
                "home_faq_description",
                "home_faq_link_label",
            )
            .first()
        )
        if hub:
            home_faq_section.update(
                {
                    "enabled": hub.home_faq_enabled,
                    "label": hub.home_faq_label or home_faq_section["label"],
                    "title": hub.home_faq_title or home_faq_section["title"],
                    "description": hub.home_faq_description or home_faq_section["description"],
                    "link_label": hub.home_faq_link_label or home_faq_section["link_label"],
                }
            )
        ctx["home_faq_section"] = home_faq_section
        home_cms = HomePageService().payload()
        ctx["home_cms"] = home_cms
        ctx["gallery_chrome"] = {
            "label": home_cms["gallery_label"],
            "title": home_cms["gallery_title"],
            "lede": home_cms["gallery_lede"],
        }
        ctx["page_seo"] = seo.home_meta()
        schemas = [
            seo.local_business_schema(request),
            seo.breadcrumb_schema(
                [{"name": "خانه", "path": "/"}],
                request,
            ),
        ]
        faq_schema = seo.faq_schema(ctx["home_faqs"])
        if faq_schema:
            schemas.append(faq_schema)
        ctx["schema_json"] = seo.dumps(schemas)
        return ctx


class RobotsTxtView(View):
    def get(self, request):
        body = SeoService().robots_txt(request)
        return HttpResponse(body, content_type="text/plain; charset=utf-8")


class SitemapXmlView(View):
    def get(self, request):
        xml = SeoService().build_sitemap_xml(request)
        return HttpResponse(xml, content_type="application/xml; charset=utf-8")


def page_not_found(request, exception):
    return render(request, "404.html", status=404)
