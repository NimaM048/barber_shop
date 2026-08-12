"""Business logic for customer reviews — serialization, SEO payloads, home teaser."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from apps.core.exceptions import NotFoundError
from apps.core.services.base import BaseService
from apps.core.services.site_settings_service import SiteSettingsService

from ..models import Review, ReviewCategory
from ..repositories import ReviewCategoryRepository, ReviewRepository

_PERSIAN_DIGITS = str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫")
_JALALI_MONTHS = (
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
)


def to_persian_digits(value: Any) -> str:
    return str(value).translate(_PERSIAN_DIGITS)


def _as_date(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.date()
    return value


def jalali_display(value: date | datetime | None) -> str:
    raw = _as_date(value)
    if raw is None:
        return ""
    try:
        import jdatetime

        j = jdatetime.date.fromgregorian(date=raw)
        month = _JALALI_MONTHS[j.month - 1]
        return to_persian_digits(f"{j.day} {month} {j.year}")
    except Exception:
        return to_persian_digits(raw.isoformat())


def rating_value_display(rating: int | float) -> str:
    if isinstance(rating, float):
        formatted = f"{rating:.1f}".rstrip("0").rstrip(".")
        return to_persian_digits(formatted)
    return to_persian_digits(int(rating))


def rating_display(rating: int | float) -> str:
    return f"{rating_value_display(rating)} از ۵"


def index_label(position: int) -> str:
    return to_persian_digits(f"{max(1, position):02d}")


def _paragraphs(body: str) -> list[str]:
    chunks = [part.strip() for part in (body or "").replace("\r\n", "\n").split("\n\n")]
    return [chunk for chunk in chunks if chunk]


def _excerpt(body: str, limit: int = 180) -> str:
    parts = _paragraphs(body)
    text = parts[0] if parts else (body or "").strip()
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _portrait_url(review: Review) -> str:
    if review.portrait:
        return review.portrait.url
    if review.portrait_static:
        path = review.portrait_static
        if path.startswith(("http://", "https://", "/media/", "/static/")):
            return path
        return static(path)
    return ""


def _booking_href(category: ReviewCategory | None) -> str:
    try:
        base = reverse("appointments:create")
    except NoReverseMatch:
        base = "/appointments/new/"
    key = (category.booking_service_key if category else "") or ""
    if key:
        return f"{base}?service={key}"
    return base


def _consultation_href(category: ReviewCategory | None) -> str:
    key = (category.consultation_category_key if category else "") or ""
    if key:
        try:
            return reverse("consultations:detail", kwargs={"key": key})
        except NoReverseMatch:
            return f"/consultations/{key}/"
    try:
        return reverse("consultations:hub")
    except NoReverseMatch:
        return "/consultations/"


class ReviewService(BaseService[ReviewRepository]):
    def __init__(
        self,
        repository: ReviewRepository | None = None,
        category_repository: ReviewCategoryRepository | None = None,
    ):
        super().__init__(repository)
        self.categories = category_repository or ReviewCategoryRepository()

    def _default_repository(self) -> ReviewRepository:
        return ReviewRepository()

    def serialize_category(self, category: ReviewCategory, *, review_count: int | None = None) -> dict[str, Any]:
        count = review_count
        if count is None:
            count = self.repository.list_published(category).count()
        return {
            "id": category.id,
            "key": category.key,
            "slug": category.slug,
            "title": category.title,
            "lede": category.lede,
            "seo_title": category.seo_title,
            "seo_description": category.seo_description,
            "url": category.get_absolute_url(),
            "booking_href": _booking_href(category),
            "consultation_href": _consultation_href(category),
            "review_count": count,
            "review_count_display": to_persian_digits(count),
        }

    def serialize_card(self, review: Review) -> dict[str, Any]:
        published = review.published_at or review.created_at
        visited = review.visited_on
        return {
            "id": review.id,
            "title": review.title,
            "slug": review.slug,
            "excerpt": _excerpt(review.body),
            "excerpt_short": _excerpt(review.body, limit=108),
            "body": review.body,
            "paragraphs": _paragraphs(review.body),
            "author_display_name": review.author_display_name,
            "author_role": review.author_role,
            "city": review.city or "اصفهان",
            "rating": review.rating,
            "rating_value_display": rating_value_display(review.rating),
            "rating_display": rating_display(review.rating),
            "service_name": review.service_name or review.category.title,
            "source_note": review.source_note or "ثبت‌شده در سالن",
            "is_featured": review.is_featured,
            "portrait": _portrait_url(review),
            "url": review.get_absolute_url(),
            "published_at": published,
            "published_display": jalali_display(published),
            "visited_on": visited,
            "visited_display": jalali_display(visited),
            "category": self.serialize_category(review.category, review_count=0),
        }

    def serialize_aggregate(self, category: ReviewCategory | None = None) -> dict[str, Any]:
        data = self.repository.aggregate_rating(category)
        count = data["review_count"]
        value = data["rating_value"]
        return {
            "rating_value": value,
            "review_count": count,
            "rating_value_display": rating_value_display(value) if count else "",
            "rating_display": rating_display(value) if count else "",
            "count_display": to_persian_digits(count),
            "has_reviews": count > 0,
        }

    def list_categories(self) -> list[dict[str, Any]]:
        return [self.serialize_category(cat) for cat in self.categories.list_published()]

    def _with_indices(self, featured: dict[str, Any] | None, archive: list[dict[str, Any]]) -> None:
        if featured is not None:
            featured["index_label"] = index_label(1)
        start = 2 if featured is not None else 1
        for i, item in enumerate(archive, start=start):
            item["index_label"] = index_label(i)

    def homepage_payload(self, limit: int = 3) -> dict[str, Any]:
        items = [self.serialize_card(review) for review in self.repository.list_featured(limit)]
        for i, item in enumerate(items, start=1):
            item["index_label"] = index_label(i)
        branding = SiteSettingsService().branding()
        return {
            "items": items,
            "aggregate": self.serialize_aggregate(),
            "gbp_url": (branding.get("SITE_GBP_URL") or "").strip(),
            "gbp_label": "مشاهده در گوگل",
        }

    def get_hub_payload(self) -> dict[str, Any]:
        reviews = [self.serialize_card(item) for item in self.repository.list_published()]
        featured = next((item for item in reviews if item["is_featured"]), None)
        if featured is None and reviews:
            featured = reviews[0]
        archive = [item for item in reviews if item is not featured]
        self._with_indices(featured, archive)
        return {
            "categories": self.list_categories(),
            "reviews": reviews,
            "featured": featured,
            "archive": archive,
            "aggregate": self.serialize_aggregate(),
            "gbp_url": (SiteSettingsService().branding().get("SITE_GBP_URL") or "").strip(),
        }

    def get_category_payload(self, slug: str) -> dict[str, Any]:
        category = self.categories.get_by_slug_or_raise(slug)
        reviews = [self.serialize_card(item) for item in self.repository.list_published(category)]
        featured = next((item for item in reviews if item["is_featured"]), None)
        if featured is None and reviews:
            featured = reviews[0]
        archive = [item for item in reviews if item is not featured]
        self._with_indices(featured, archive)
        return {
            "category": self.serialize_category(category, review_count=len(reviews)),
            "categories": self.list_categories(),
            "reviews": reviews,
            "featured": featured,
            "archive": archive,
            "aggregate": self.serialize_aggregate(category),
            "booking_href": _booking_href(category),
            "consultation_href": _consultation_href(category),
        }

    def get_detail_payload(self, category_slug: str, slug: str) -> dict[str, Any]:
        review = self.repository.get_published_or_raise(category_slug, slug)
        related = [self.serialize_card(item) for item in self.repository.list_related(review)]
        for i, item in enumerate(related, start=1):
            item["index_label"] = index_label(i)
        return {
            "review": self.serialize_card(review),
            "related": related,
            "categories": self.list_categories(),
            "booking_href": _booking_href(review.category),
            "consultation_href": _consultation_href(review.category),
        }

    def sitemap_entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for category in self.categories.list_published():
            entries.append(
                {
                    "kind": "category",
                    "slug": category.slug,
                    "path": category.get_absolute_url(),
                    "updated_at": category.updated_at,
                }
            )
        for review in self.repository.list_published():
            entries.append(
                {
                    "kind": "detail",
                    "slug": review.slug,
                    "category_slug": review.category.slug,
                    "path": review.get_absolute_url(),
                    "updated_at": review.updated_at,
                }
            )
        return entries
