"""ORM access for magazine models."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, F, Q, QuerySet
from django.utils import timezone

from apps.core.exceptions import NotFoundError
from apps.core.repositories.base import BaseRepository

from ..models import (
    Article,
    ArticleComment,
    ArticleImage,
    ArticleInteraction,
    ArticleVersion,
    MagazineAuthor,
    MagazineCategory,
    MagazineTag,
)


class MagazineAuthorRepository(BaseRepository[MagazineAuthor]):
    model = MagazineAuthor

    def get_by_slug(self, slug: str) -> MagazineAuthor | None:
        try:
            return self.get_queryset().get(slug=slug, is_active=True)
        except MagazineAuthor.DoesNotExist:
            return None


class MagazineCategoryRepository(BaseRepository[MagazineCategory]):
    model = MagazineCategory

    def list_active(self) -> QuerySet[MagazineCategory]:
        return self.get_queryset().filter(is_active=True).order_by("sort_order", "title")

    def get_by_slug(self, slug: str) -> MagazineCategory | None:
        try:
            return self.get_queryset().get(slug=slug, is_active=True)
        except MagazineCategory.DoesNotExist:
            return None

    def get_by_slug_or_raise(self, slug: str) -> MagazineCategory:
        cat = self.get_by_slug(slug)
        if cat is None:
            raise NotFoundError("دسته‌بندی یافت نشد.")
        return cat


class MagazineTagRepository(BaseRepository[MagazineTag]):
    model = MagazineTag

    def get_by_slug(self, slug: str) -> MagazineTag | None:
        try:
            return self.get_queryset().get(slug=slug)
        except MagazineTag.DoesNotExist:
            return None

    def list_popular(self, limit: int = 20) -> QuerySet[MagazineTag]:
        return (
            self.get_queryset()
            .annotate(article_count=Count("articles"))
            .filter(article_count__gt=0)
            .order_by("-article_count", "title")[:limit]
        )


class ArticleRepository(BaseRepository[Article]):
    model = Article

    def published_qs(self) -> QuerySet[Article]:
        now = timezone.now()
        return (
            self.get_queryset()
            .filter(
                is_active=True,
                status=Article.Status.PUBLISHED,
            )
            .filter(Q(published_at__isnull=True) | Q(published_at__lte=now))
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def get_by_slug(self, slug: str, *, published_only: bool = True) -> Article | None:
        qs = self.published_qs() if published_only else self.get_queryset().select_related(
            "category", "author"
        ).prefetch_related("tags", "images")
        try:
            return qs.get(slug=slug)
        except Article.DoesNotExist:
            return None

    def get_by_slug_or_raise(self, slug: str) -> Article:
        article = self.get_by_slug(slug)
        if article is None:
            raise NotFoundError("مقاله یافت نشد.")
        return article

    def get_hero(self) -> Article | None:
        return self.published_qs().filter(is_hero=True).order_by(
            "-display_priority", "-published_at"
        ).first()

    def list_featured(self, limit: int = 6) -> QuerySet[Article]:
        return self.published_qs().filter(is_featured=True).order_by(
            "-display_priority", "-published_at"
        )[:limit]

    def list_editors_picks(self, limit: int = 4) -> QuerySet[Article]:
        return self.published_qs().filter(is_editors_pick=True).order_by(
            "-display_priority", "-published_at"
        )[:limit]

    def list_latest(self, limit: int = 12, offset: int = 0) -> QuerySet[Article]:
        return self.published_qs().order_by("-published_at", "-id")[offset : offset + limit]

    def list_popular(
        self,
        *,
        metric: str = "views",
        limit: int = 8,
    ) -> QuerySet[Article]:
        qs = self.published_qs()
        if metric == "reads":
            return qs.order_by("-complete_read_count", "-view_count")[:limit]
        if metric == "shares":
            return qs.order_by("-share_count", "-view_count")[:limit]
        return qs.order_by("-view_count", "-like_count")[:limit]

    def filter_articles(
        self,
        *,
        category: str = "",
        tag: str = "",
        author: str = "",
        q: str = "",
        sort: str = "newest",
        reading_min: int | None = None,
        reading_max: int | None = None,
        offset: int = 0,
        limit: int = 12,
    ) -> tuple[QuerySet[Article], int]:
        qs = self.published_qs()
        if category:
            qs = qs.filter(category__slug=category)
        if tag:
            qs = qs.filter(tags__slug=tag)
        if author:
            qs = qs.filter(author__slug=author)
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(subtitle__icontains=q)
                | Q(excerpt__icontains=q)
                | Q(body__icontains=q)
                | Q(tags__title__icontains=q)
                | Q(category__title__icontains=q)
            ).distinct()
        if reading_min is not None:
            qs = qs.filter(reading_minutes__gte=reading_min)
        if reading_max is not None:
            qs = qs.filter(reading_minutes__lte=reading_max)

        if sort == "popular":
            qs = qs.order_by("-view_count", "-published_at")
        elif sort == "reads":
            qs = qs.order_by("-complete_read_count", "-published_at")
        elif sort == "reading_asc":
            qs = qs.order_by("reading_minutes", "-published_at")
        elif sort == "reading_desc":
            qs = qs.order_by("-reading_minutes", "-published_at")
        else:
            qs = qs.order_by("-published_at", "-id")

        total = qs.count()
        return qs[offset : offset + limit], total

    def search_autocomplete(self, q: str, limit: int = 8) -> dict[str, Any]:
        if not q or len(q.strip()) < 2:
            return {"articles": [], "categories": [], "tags": []}
        term = q.strip()
        articles = list(
            self.published_qs()
            .filter(Q(title__icontains=term) | Q(excerpt__icontains=term) | Q(tags__title__icontains=term))
            .distinct()
            .order_by("-view_count")[:limit]
        )
        categories = list(
            MagazineCategory.objects.filter(is_active=True, is_deleted=False, title__icontains=term)[:4]
        )
        tags = list(MagazineTag.objects.filter(title__icontains=term)[:4])
        return {
            "articles": articles,
            "categories": categories,
            "tags": tags,
        }

    def related_for(self, article: Article, limit: int = 4) -> list[Article]:
        related = list(article.related_articles.filter(
            is_active=True,
            status=Article.Status.PUBLISHED,
            is_deleted=False,
        )[:limit])
        if len(related) >= limit:
            return related
        needed = limit - len(related)
        exclude_ids = {article.id, *[a.id for a in related]}
        tag_ids = list(article.tags.values_list("id", flat=True))
        extras = list(
            self.published_qs()
            .exclude(id__in=exclude_ids)
            .filter(Q(category_id=article.category_id) | Q(tags__id__in=tag_ids))
            .distinct()
            .order_by("-view_count", "-published_at")[:needed]
        )
        return related + extras

    def increment_counter(self, article_id: int, field: str, amount: int = 1) -> None:
        Article.objects.filter(pk=article_id).update(**{field: F(field) + amount})

    def publish_scheduled(self) -> int:
        now = timezone.now()
        return (
            Article.objects.filter(
                status=Article.Status.SCHEDULED,
                scheduled_at__lte=now,
                is_deleted=False,
            ).update(status=Article.Status.PUBLISHED, published_at=now)
        )


class ArticleImageRepository(BaseRepository[ArticleImage]):
    model = ArticleImage

    def list_for_article(self, article_id: int) -> QuerySet[ArticleImage]:
        return self.get_queryset().filter(article_id=article_id)


class ArticleVersionRepository(BaseRepository[ArticleVersion]):
    model = ArticleVersion

    def list_for_article(self, article_id: int) -> QuerySet[ArticleVersion]:
        return self.get_queryset().filter(article_id=article_id)

    def next_version_number(self, article_id: int) -> int:
        last = (
            self.get_queryset()
            .filter(article_id=article_id)
            .order_by("-version_number")
            .values_list("version_number", flat=True)
            .first()
        )
        return (last or 0) + 1

    def get_version(self, article_id: int, version_number: int) -> ArticleVersion | None:
        try:
            return self.get_queryset().get(article_id=article_id, version_number=version_number)
        except ArticleVersion.DoesNotExist:
            return None


class ArticleInteractionRepository(BaseRepository[ArticleInteraction]):
    model = ArticleInteraction

    def has(self, article_id: int, kind: str, session_key: str) -> bool:
        return self.get_queryset().filter(
            article_id=article_id, kind=kind, session_key=session_key
        ).exists()

    def get_rating(self, article_id: int, session_key: str) -> ArticleInteraction | None:
        return (
            self.get_queryset()
            .filter(article_id=article_id, kind=ArticleInteraction.Kind.RATING, session_key=session_key)
            .first()
        )


class ArticleCommentRepository(BaseRepository[ArticleComment]):
    model = ArticleComment

    def list_approved(self, article_id: int) -> QuerySet[ArticleComment]:
        return self.get_queryset().filter(article_id=article_id, is_approved=True)
