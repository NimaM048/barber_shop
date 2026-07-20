from __future__ import annotations

from django.urls import reverse
from django.templatetags.static import static

from apps.core.services import BaseService

from ..repositories import GalleryCategoryRepository, GalleryItemRepository


def _static_or_empty(path: str) -> str:
    if not path:
        return ""
    if path.startswith(("http://", "https://", "/media/", "/static/")):
        return path
    return static(path)


class PortfolioService(BaseService[GalleryItemRepository]):
    def _default_repository(self) -> GalleryItemRepository:
        return GalleryItemRepository()

    def __init__(self, repository=None, category_repository=None):
        super().__init__(repository)
        self.category_repository = category_repository or GalleryCategoryRepository()

    def list_published_items(self):
        return self.repository.list_published()

    def list_active_categories(self):
        return self.category_repository.list_active()

    def serialize_item(self, item) -> dict:
        images = []
        if item.cover_image:
            cover_src = item.cover_image.url
        else:
            cover_src = _static_or_empty(item.cover_image_static)

        cover = {
            "src": cover_src,
            "webp": _static_or_empty(item.cover_webp_static),
            "avif": _static_or_empty(item.cover_avif_static),
            "lqip": _static_or_empty(item.cover_lqip_static),
            "alt": item.alt_text or item.title,
        }

        if cover["src"]:
            images.append(
                {
                    "src": cover["src"],
                    "webp": cover["webp"],
                    "avif": cover["avif"],
                    "lqip": cover["lqip"],
                    "alt": cover["alt"],
                    "caption": item.title,
                    "kind": "cover",
                }
            )

        for img in item.images.all():
            src = img.image.url if img.image else _static_or_empty(img.image_static)
            if not src:
                continue
            images.append(
                {
                    "src": src,
                    "webp": _static_or_empty(img.webp_static),
                    "avif": _static_or_empty(img.avif_static),
                    "lqip": _static_or_empty(img.lqip_static),
                    "alt": img.alt_text or item.alt_text or item.title,
                    "caption": img.caption,
                    "kind": "gallery",
                }
            )

        video_src = ""
        if item.video:
            video_src = item.video.url
        elif item.video_url:
            video_src = item.video_url

        before_src = ""
        after_src = ""
        if item.has_before_after:
            if item.before_image:
                before_src = item.before_image.url
            elif item.before_image_static:
                before_src = _static_or_empty(item.before_image_static)
            if item.after_image:
                after_src = item.after_image.url
            elif item.after_image_static:
                after_src = _static_or_empty(item.after_image_static)

        booking_url = reverse("appointments:create")
        if item.related_service_id and item.related_service:
            booking_url = f"{booking_url}?service={item.related_service.slug}"

        consultation_url = reverse("consultations:hub")

        completed = ""
        if item.completed_at:
            completed = item.completed_at.isoformat()

        return {
            "id": item.pk,
            "slug": item.slug,
            "title": item.title,
            "subtitle": item.subtitle,
            "description": item.description,
            "category": item.category.slug if item.category_id else "all",
            "category_title": item.category.title if item.category_id else "",
            "tags": [t.title for t in item.tags.all()],
            "cover": cover,
            "images": images,
            "has_video": bool(video_src),
            "video_src": video_src,
            "video_poster": _static_or_empty(item.video_poster_static) or cover["src"],
            "has_before_after": bool(item.has_before_after and before_src and after_src),
            "before": {
                "src": before_src,
                "alt": item.before_alt or f"قبل — {item.title}",
            },
            "after": {
                "src": after_src,
                "alt": item.after_alt or f"بعد — {item.title}",
            },
            "story": {
                "problem": item.problem,
                "solution": item.solution,
                "services": item.services_text,
                "duration": item.duration_text,
                "result": item.result,
                "review": item.customer_review,
            },
            "location": item.location,
            "completed_at": completed,
            "featured": item.is_featured,
            "cta": {
                "title": item.cta_title or "از این نتیجه خوشتان آمد؟",
                "consultation_label": item.cta_consultation_label or "دریافت مشاوره",
                "booking_label": item.cta_booking_label or "رزرو این خدمت",
                "consultation_url": consultation_url,
                "booking_url": booking_url,
            },
        }

    def homepage_payload(self) -> dict:
        items = list(self.list_published_items())
        categories = list(self.list_active_categories())
        return {
            "categories": [
                {"slug": "all", "title": "همه"},
                *[{"slug": c.slug, "title": c.title} for c in categories],
            ],
            "items": [self.serialize_item(item) for item in items],
        }
