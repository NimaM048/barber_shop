"""ORM access for review models."""

from __future__ import annotations

from django.db.models import Avg, Count, QuerySet
from django.utils import timezone

from apps.core.exceptions import NotFoundError
from apps.core.repositories.base import BaseRepository

from ..models import Review, ReviewCategory


class ReviewCategoryRepository(BaseRepository[ReviewCategory]):
    model = ReviewCategory

    def list_published(self) -> QuerySet[ReviewCategory]:
        return (
            self.get_queryset()
            .filter(is_published=True)
            .order_by("sort_order", "title")
        )

    def get_by_slug(self, slug: str) -> ReviewCategory | None:
        try:
            return self.get_queryset().get(slug=slug, is_published=True)
        except ReviewCategory.DoesNotExist:
            return None

    def get_by_slug_or_raise(self, slug: str) -> ReviewCategory:
        category = self.get_by_slug(slug)
        if category is None:
            raise NotFoundError("دسته نظر یافت نشد.")
        return category


class ReviewRepository(BaseRepository[Review]):
    model = Review

    def published_qs(self) -> QuerySet[Review]:
        now = timezone.now()
        return (
            self.get_queryset()
            .select_related("category")
            .filter(
                status=Review.Status.PUBLISHED,
                published_at__isnull=False,
                published_at__lte=now,
                category__is_published=True,
                category__is_deleted=False,
            )
        )

    def list_published(self, category: ReviewCategory | None = None) -> QuerySet[Review]:
        qs = self.published_qs()
        if category is not None:
            qs = qs.filter(category=category)
        return qs.order_by("sort_order", "-published_at", "-id")

    def list_featured(self, limit: int = 3) -> list[Review]:
        featured = list(
            self.published_qs()
            .filter(is_featured=True)
            .order_by("sort_order", "-published_at", "-id")[:limit]
        )
        if len(featured) >= limit:
            return featured
        seen = {item.pk for item in featured}
        extras = (
            self.published_qs()
            .exclude(pk__in=seen)
            .order_by("-published_at", "-id")[: limit - len(featured)]
        )
        return featured + list(extras)

    def get_published(self, category_slug: str, slug: str) -> Review | None:
        try:
            return self.published_qs().get(category__slug=category_slug, slug=slug)
        except Review.DoesNotExist:
            return None

    def get_published_or_raise(self, category_slug: str, slug: str) -> Review:
        review = self.get_published(category_slug, slug)
        if review is None:
            raise NotFoundError("نظر یافت نشد.")
        return review

    def list_related(self, review: Review, limit: int = 3) -> QuerySet[Review]:
        return (
            self.published_qs()
            .filter(category=review.category)
            .exclude(pk=review.pk)
            .order_by("sort_order", "-published_at", "-id")[:limit]
        )

    def aggregate_rating(self, category: ReviewCategory | None = None) -> dict:
        qs = self.published_qs()
        if category is not None:
            qs = qs.filter(category=category)
        data = qs.aggregate(avg=Avg("rating"), count=Count("id"))
        count = int(data["count"] or 0)
        avg = float(data["avg"] or 0)
        return {
            "rating_value": round(avg, 1) if count else 0,
            "review_count": count,
        }
