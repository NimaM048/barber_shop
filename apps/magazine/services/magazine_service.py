"""Magazine / encyclopedia business logic."""

from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import quote

from django.conf import settings
from django.db import transaction
from django.utils import timezone

import jdatetime

from apps.core.exceptions import NotFoundError, ValidationError
from apps.core.services import BaseService

from ..models import Article, ArticleInteraction, ArticleVersion
from ..repositories import (
    ArticleCommentRepository,
    ArticleImageRepository,
    ArticleInteractionRepository,
    ArticleRepository,
    ArticleVersionRepository,
    MagazineAuthorRepository,
    MagazineCategoryRepository,
    MagazineTagRepository,
)

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
HEADING_RE = re.compile(
    r"<h([2-3])[^>]*(?:id=[\"']([^\"']+)[\"'])?[^>]*>(.*?)</h\1>",
    re.IGNORECASE | re.DOTALL,
)


def to_fa(value) -> str:
    return str(value).translate(PERSIAN_DIGITS)


def jalali_date(dt) -> str:
    if not dt:
        return ""
    local = timezone.localtime(dt)
    j = jdatetime.datetime.fromgregorian(datetime=local)
    months = (
        "",
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
    return f"{to_fa(j.day)} {months[j.month]} {to_fa(j.year)}"


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html or "").strip()


def _slugify_heading(text: str) -> str:
    clean = _strip_html(text)
    slug = re.sub(r"\s+", "-", clean.strip())[:80]
    return slug or "section"


class MagazineService(BaseService[ArticleRepository]):
    def __init__(
        self,
        repository: ArticleRepository | None = None,
        category_repo: MagazineCategoryRepository | None = None,
        tag_repo: MagazineTagRepository | None = None,
        author_repo: MagazineAuthorRepository | None = None,
        image_repo: ArticleImageRepository | None = None,
        version_repo: ArticleVersionRepository | None = None,
        interaction_repo: ArticleInteractionRepository | None = None,
        comment_repo: ArticleCommentRepository | None = None,
    ):
        super().__init__(repository)
        self.categories = category_repo or MagazineCategoryRepository()
        self.tags = tag_repo or MagazineTagRepository()
        self.authors = author_repo or MagazineAuthorRepository()
        self.images = image_repo or ArticleImageRepository()
        self.versions = version_repo or ArticleVersionRepository()
        self.interactions = interaction_repo or ArticleInteractionRepository()
        self.comments = comment_repo or ArticleCommentRepository()

    def _default_repository(self) -> ArticleRepository:
        return ArticleRepository()

    # ── Hub / listing ──────────────────────────────────────────────

    def get_hub_payload(self) -> dict[str, Any]:
        self.repository.publish_scheduled()
        hero = self.repository.get_hero()
        if hero is None:
            hero = self.repository.list_latest(limit=1).first()

        featured = list(self.repository.list_featured(limit=6))
        if hero:
            featured = [a for a in featured if a.id != hero.id][:4]

        latest, latest_total = self.repository.filter_articles(limit=9)
        popular = list(self.repository.list_popular(metric="views", limit=6))
        most_read = list(self.repository.list_popular(metric="reads", limit=4))
        editors = list(self.repository.list_editors_picks(limit=4))

        return {
            "hero": self._serialize_card(hero) if hero else None,
            "categories": [self._serialize_category(c) for c in self.categories.list_active()],
            "featured": [self._serialize_card(a) for a in featured],
            "latest": [self._serialize_card(a) for a in latest],
            "latest_total": latest_total,
            "popular": [self._serialize_card(a) for a in popular],
            "most_read": [self._serialize_card(a) for a in most_read],
            "editors_picks": [self._serialize_card(a) for a in editors],
            "tags": [self._serialize_tag(t) for t in self.tags.list_popular(16)],
            "conversion": {
                "title": "از مطالعه تا تجربه حضوری",
                "consultation_label": "مشاوره تخصصی",
                "booking_label": "رزرو نوبت",
                "consultation_url": "/consultations/",
                "booking_url": "/appointments/new/",
                "services_url": "/services/",
            },
            "masthead": {
                "label_en": "Magazine",
                "label_fa": f"مجله {getattr(settings, 'SITE_NAME', 'صالح ایوبی')}",
            },
        }

    def list_articles(
        self,
        *,
        category: str = "",
        tag: str = "",
        author: str = "",
        q: str = "",
        sort: str = "newest",
        reading_min: int | None = None,
        reading_max: int | None = None,
        page: int = 1,
        page_size: int = 12,
    ) -> dict[str, Any]:
        page = max(1, page)
        page_size = min(max(1, page_size), 24)
        offset = (page - 1) * page_size
        articles, total = self.repository.filter_articles(
            category=category,
            tag=tag,
            author=author,
            q=q,
            sort=sort,
            reading_min=reading_min,
            reading_max=reading_max,
            offset=offset,
            limit=page_size,
        )
        pages = max(1, (total + page_size - 1) // page_size)
        return {
            "articles": [self._serialize_card(a) for a in articles],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1,
            },
            "filters": {
                "category": category,
                "tag": tag,
                "author": author,
                "q": q,
                "sort": sort,
                "reading_min": reading_min,
                "reading_max": reading_max,
            },
        }

    def search_autocomplete(self, q: str) -> dict[str, Any]:
        raw = self.repository.search_autocomplete(q, limit=6)
        return {
            "query": q,
            "articles": [self._serialize_card(a) for a in raw["articles"]],
            "categories": [self._serialize_category(c) for c in raw["categories"]],
            "tags": [self._serialize_tag(t) for t in raw["tags"]],
        }

    def list_categories(self) -> list[dict[str, Any]]:
        return [self._serialize_category(c) for c in self.categories.list_active()]

    def list_filter_meta(self) -> dict[str, Any]:
        authors = [
            {"name": a.name, "slug": a.slug}
            for a in self.authors.get_queryset().filter(is_active=True)
        ]
        return {
            "categories": self.list_categories(),
            "tags": [self._serialize_tag(t) for t in self.tags.list_popular(24)],
            "authors": authors,
            "sorts": [
                {"key": "newest", "label": "جدیدترین"},
                {"key": "popular", "label": "محبوب‌ترین"},
                {"key": "reads", "label": "بیشترین مطالعه"},
                {"key": "reading_asc", "label": "کوتاه‌ترین"},
                {"key": "reading_desc", "label": "بلندترین"},
            ],
        }

    # ── Article detail ─────────────────────────────────────────────

    def get_article_detail(self, slug: str, *, session_key: str = "") -> dict[str, Any]:
        article = self.repository.get_by_slug_or_raise(slug)
        body, toc = self._prepare_body_and_toc(article.body)
        related = self.repository.related_for(article, limit=4)
        images = list(self.images.list_for_article(article.id))
        comments = []
        if article.allow_comments:
            comments = [
                self._serialize_comment(c)
                for c in self.comments.list_approved(article.id)[:30]
            ]

        liked = False
        bookmarked = False
        user_rating = None
        if session_key:
            liked = self.interactions.has(article.id, ArticleInteraction.Kind.LIKE, session_key)
            bookmarked = self.interactions.has(
                article.id, ArticleInteraction.Kind.BOOKMARK, session_key
            )
            rating = self.interactions.get_rating(article.id, session_key)
            if rating:
                user_rating = rating.rating_value

        return {
            "article": self._serialize_detail(article, body=body, toc=toc, images=images),
            "related": [self._serialize_card(a) for a in related],
            "conversion": self._serialize_conversion(article),
            "comments": comments,
            "engagement": {
                "liked": liked,
                "bookmarked": bookmarked,
                "user_rating": user_rating,
            },
            "share": self._share_links(article),
        }

    def record_view(self, slug: str, *, session_key: str, ip: str = "") -> dict[str, Any]:
        article = self.repository.get_by_slug_or_raise(slug)
        if not session_key:
            raise ValidationError("نشست نامعتبر است.")
        already = self.interactions.has(article.id, ArticleInteraction.Kind.VIEW, session_key)
        if not already:
            self.interactions.create(
                article=article,
                kind=ArticleInteraction.Kind.VIEW,
                session_key=session_key,
                ip_hash=self._hash_ip(ip),
            )
            self.repository.increment_counter(article.id, "view_count")
            article.refresh_from_db(fields=["view_count"])
        return {"view_count": article.view_count, "counted": not already}

    def toggle_like(self, slug: str, *, session_key: str) -> dict[str, Any]:
        return self._toggle_flag(
            slug,
            session_key=session_key,
            kind=ArticleInteraction.Kind.LIKE,
            counter="like_count",
            on_label="liked",
        )

    def toggle_bookmark(self, slug: str, *, session_key: str) -> dict[str, Any]:
        return self._toggle_flag(
            slug,
            session_key=session_key,
            kind=ArticleInteraction.Kind.BOOKMARK,
            counter="bookmark_count",
            on_label="bookmarked",
        )

    def record_share(self, slug: str, *, session_key: str, channel: str = "") -> dict[str, Any]:
        article = self.repository.get_by_slug_or_raise(slug)
        if not session_key:
            raise ValidationError("نشست نامعتبر است.")
        self.interactions.create(
            article=article,
            kind=ArticleInteraction.Kind.SHARE,
            session_key=session_key,
            share_channel=(channel or "")[:40],
        )
        self.repository.increment_counter(article.id, "share_count")
        article.refresh_from_db(fields=["share_count"])
        return {"share_count": article.share_count}

    def record_complete_read(self, slug: str, *, session_key: str) -> dict[str, Any]:
        article = self.repository.get_by_slug_or_raise(slug)
        if not session_key:
            raise ValidationError("نشست نامعتبر است.")
        if self.interactions.has(article.id, ArticleInteraction.Kind.COMPLETE_READ, session_key):
            return {"complete_read_count": article.complete_read_count, "counted": False}
        self.interactions.create(
            article=article,
            kind=ArticleInteraction.Kind.COMPLETE_READ,
            session_key=session_key,
        )
        self.repository.increment_counter(article.id, "complete_read_count")
        article.refresh_from_db(fields=["complete_read_count"])
        return {"complete_read_count": article.complete_read_count, "counted": True}

    def rate_article(self, slug: str, *, session_key: str, value: int) -> dict[str, Any]:
        """Editorial feedback: 5 = helpful, 1 = needs improvement (legacy 2–4 still accepted)."""
        if value < 1 or value > 5:
            raise ValidationError("بازخورد نامعتبر است.")
        if not session_key:
            raise ValidationError("نشست نامعتبر است.")
        article = self.repository.get_by_slug_or_raise(slug)
        existing = self.interactions.get_rating(article.id, session_key)
        with transaction.atomic():
            if existing:
                old = existing.rating_value or 0
                existing.rating_value = value
                existing.save(update_fields=["rating_value", "updated_at"])
                Article.objects.filter(pk=article.id).update(
                    rating_sum=article.rating_sum - old + value
                )
            else:
                self.interactions.create(
                    article=article,
                    kind=ArticleInteraction.Kind.RATING,
                    session_key=session_key,
                    rating_value=value,
                )
                Article.objects.filter(pk=article.id).update(
                    rating_sum=article.rating_sum + value,
                    rating_count=article.rating_count + 1,
                )
        article.refresh_from_db(fields=["rating_sum", "rating_count"])
        sentiment = "helpful" if value >= 4 else "needs_improvement" if value <= 2 else "neutral"
        return {
            "average_rating": article.average_rating,
            "rating_count": article.rating_count,
            "user_rating": value,
            "sentiment": sentiment,
        }

    def create_comment(
        self,
        slug: str,
        *,
        author_name: str,
        body: str,
        author_phone: str = "",
    ) -> dict[str, Any]:
        article = self.repository.get_by_slug_or_raise(slug)
        if not article.allow_comments:
            raise ValidationError("نظرات برای این مقاله فعال نیست.")
        name = (author_name or "").strip()
        text = (body or "").strip()
        if len(name) < 2:
            raise ValidationError("نام معتبر وارد کنید.")
        if len(text) < 8:
            raise ValidationError("متن نظر کوتاه است.")
        comment = self.comments.create(
            article=article,
            author_name=name[:80],
            author_phone=(author_phone or "")[:20],
            body=text[:2000],
            is_approved=False,
        )
        return self._serialize_comment(comment)

    # ── Versioning (admin-facing helpers) ──────────────────────────

    def snapshot_version(
        self,
        article: Article,
        *,
        changed_by: str = "",
        change_note: str = "",
    ) -> ArticleVersion:
        number = self.versions.next_version_number(article.id)
        return self.versions.create(
            article=article,
            version_number=number,
            title=article.title,
            subtitle=article.subtitle,
            excerpt=article.excerpt,
            body=article.body,
            meta_title=article.meta_title,
            meta_description=article.meta_description,
            changed_by=changed_by[:120],
            change_note=change_note[:255],
            snapshot={
                "title": article.title,
                "subtitle": article.subtitle,
                "excerpt": article.excerpt,
                "body": article.body,
                "meta_title": article.meta_title,
                "meta_description": article.meta_description,
                "status": article.status,
            },
        )

    def restore_version(self, article_id: int, version_number: int) -> Article:
        article = self.repository.get_or_raise(article_id)
        version = self.versions.get_version(article_id, version_number)
        if version is None:
            raise NotFoundError("نسخه یافت نشد.")
        self.snapshot_version(article, changed_by="system", change_note="قبل از بازگردانی")
        article.title = version.title
        article.subtitle = version.subtitle
        article.excerpt = version.excerpt
        article.body = version.body
        article.meta_title = version.meta_title
        article.meta_description = version.meta_description
        article.save()
        return article

    def sitemap_entries(self) -> list[dict[str, Any]]:
        self.repository.publish_scheduled()
        entries = []
        for a in self.repository.published_qs().order_by("-published_at"):
            entries.append(
                {
                    "slug": a.slug,
                    "updated_at": a.updated_at,
                    "published_at": a.published_at,
                }
            )
        return entries

    def rss_entries(self, limit: int = 20) -> list[dict[str, Any]]:
        return [
            self._serialize_card(a)
            for a in self.repository.list_latest(limit=limit)
        ]

    # ── Internals ──────────────────────────────────────────────────

    def _toggle_flag(
        self,
        slug: str,
        *,
        session_key: str,
        kind: str,
        counter: str,
        on_label: str,
    ) -> dict[str, Any]:
        if not session_key:
            raise ValidationError("نشست نامعتبر است.")
        article = self.repository.get_by_slug_or_raise(slug)
        existing = (
            self.interactions.get_queryset()
            .filter(article_id=article.id, kind=kind, session_key=session_key)
            .first()
        )
        if existing:
            existing.delete()
            from django.db.models import F, Value
            from django.db.models.functions import Greatest

            Article.objects.filter(pk=article.id).update(
                **{counter: Greatest(F(counter) - 1, Value(0))}
            )
            active = False
        else:
            self.interactions.create(article=article, kind=kind, session_key=session_key)
            self.repository.increment_counter(article.id, counter)
            active = True
        article.refresh_from_db(fields=[counter])
        return {on_label: active, "count": getattr(article, counter)}

    def _prepare_body_and_toc(self, body: str) -> tuple[str, list[dict[str, str]]]:
        toc: list[dict[str, str]] = []
        used: set[str] = set()

        def replacer(match: re.Match) -> str:
            level = match.group(1)
            existing_id = match.group(2)
            inner = match.group(3)
            text = _strip_html(inner)
            hid = existing_id or _slugify_heading(text)
            base = hid
            n = 1
            while hid in used:
                n += 1
                hid = f"{base}-{n}"
            used.add(hid)
            toc.append({"id": hid, "text": text, "level": f"h{level}"})
            return f'<h{level} id="{hid}">{inner}</h{level}>'

        processed = HEADING_RE.sub(replacer, body or "")
        return processed, toc

    def _serialize_conversion(self, article: Article) -> dict[str, Any]:
        cat = article.category
        service_keys = cat.booking_service_keys or []
        primary_service = service_keys[0] if service_keys else ""
        booking_url = "/appointments/new/"
        if primary_service:
            booking_url = f"/appointments/new/?service={primary_service}"
        consult_url = ""
        if cat.consultation_category_key:
            consult_url = f"/consultations/{cat.consultation_category_key}/"
        else:
            consult_url = "/consultations/"
        return {
            "title": cat.cta_title or "آماده دریافت مشاوره هستید؟",
            "consultation_label": cat.cta_consultation_label or "دریافت مشاوره تخصصی",
            "booking_label": cat.cta_booking_label or "رزرو نوبت",
            "consultation_url": consult_url,
            "booking_url": booking_url,
            "ticket_url": "/consultations/",
            "service_keys": service_keys,
            "category_title": cat.title,
        }

    def _share_links(self, article: Article) -> dict[str, str]:
        site = getattr(settings, "SITE_WEBSITE", "") or "https://example.com"
        url = f"{site.rstrip('/')}/magazine/{article.slug}/"
        encoded = quote(url, safe="")
        title = quote(article.title, safe="")
        return {
            "url": url,
            "twitter": f"https://twitter.com/intent/tweet?url={encoded}&text={title}",
            "telegram": f"https://t.me/share/url?url={encoded}&text={title}",
            "whatsapp": f"https://wa.me/?text={title}%20{encoded}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded}",
        }

    # Category → editorial cover fallbacks (brand photography, mood-matched)
    CATEGORY_COVER_FALLBACKS = {
        "groom": "images/brand/hero-cinematic.webp",
        "skin": "images/brand/hero-groom-2-hd.webp",
        "hair": "images/brand/hero-groom-3-hd.webp",
        "shave": "images/brand/hero-groom-3-hd.webp",
        "style": "images/brand/hero-cinematic.webp",
        "facial": "images/brand/hero-groom-2-hd.webp",
        "pre-care": "images/brand/hero-cinematic.webp",
        "after-care": "images/brand/hero-groom-2-hd.webp",
        "products": "images/brand/hero-wide.webp",
        "trends": "images/brand/hero-cinematic.webp",
        "education": "images/brand/hero-groom-3-hd.webp",
        "news": "images/brand/hero-wide.webp",
        "services-guide": "images/brand/hero-cinematic.webp",
    }
    DEFAULT_COVER_FALLBACK = "images/brand/hero-cinematic.webp"

    # Mood-matched LQIP for brand static covers (never a generic grey box)
    COVER_LQIP_MAP = {
        "images/brand/hero-groom-1-plate.webp": "images/brand/hero-groom-1-lqip.jpg",
        "images/brand/hero-groom-1-plate.jpg": "images/brand/hero-groom-1-lqip.jpg",
        "images/brand/hero-groom-1-hd.webp": "images/brand/hero-groom-1-lqip.jpg",
        "images/brand/hero-groom-1-hd.jpg": "images/brand/hero-groom-1-lqip.jpg",
        "images/brand/hero-groom-2-hd.webp": "images/brand/hero-groom-2-lqip.jpg",
        "images/brand/hero-groom-2-hd.jpg": "images/brand/hero-groom-2-lqip.jpg",
        "images/brand/hero-groom-3-hd.webp": "images/brand/hero-groom-3-lqip.jpg",
        "images/brand/hero-groom-3-hd.jpg": "images/brand/hero-groom-3-lqip.jpg",
        "images/brand/hero-cinematic.webp": "images/brand/hero-cinematic-lqip.jpg",
        "images/brand/hero-cinematic.jpg": "images/brand/hero-cinematic-lqip.jpg",
        "images/brand/hero-wide.webp": "images/brand/hero-wide-lqip.jpg",
        "images/brand/hero-wide.jpg": "images/brand/hero-wide-lqip.jpg",
        "images/brand/hero-ambient.webp": "images/brand/hero-ambient-lqip.jpg",
        "images/brand/hero-ambient.jpg": "images/brand/hero-ambient-lqip.jpg",
    }

    def _normalize_static_path(self, path: str) -> str:
        path = (path or "").lstrip("/")
        if path.startswith("static/"):
            path = path[7:]
        # Prefer full-resolution cinematic plate over undersized legacy assets
        path = path.replace("hero-groom-1-plate.webp", "hero-cinematic.webp")
        path = path.replace("hero-groom-1-plate.jpg", "hero-cinematic.jpg")
        path = path.replace("hero-groom-1-hd.webp", "hero-cinematic.webp")
        path = path.replace("hero-groom-1-hd.jpg", "hero-cinematic.jpg")
        path = path.replace("hero-groom-1.webp", "hero-cinematic.webp")
        path = path.replace("hero-groom-2.webp", "hero-groom-2-hd.webp")
        path = path.replace("hero-groom-3.webp", "hero-groom-3-hd.webp")
        return path

    def _cover_static_path(self, article: Article) -> str:
        if article.cover_image:
            return ""
        if article.cover_image_static:
            return self._normalize_static_path(article.cover_image_static)
        cat_slug = getattr(getattr(article, "category", None), "slug", "") or ""
        return self.CATEGORY_COVER_FALLBACKS.get(cat_slug, self.DEFAULT_COVER_FALLBACK)

    def _cover_url(self, article: Article, request_static: str = "/static/") -> str:
        if article.cover_image:
            return article.cover_image.url
        path = self._cover_static_path(article)
        return f"{request_static}{path}" if path else ""

    def _cover_lqip_url(self, article: Article, request_static: str = "/static/") -> str:
        """Resolve LQIP blur placeholder for progressive image reveal."""
        path = self._cover_static_path(article)
        if not path:
            return ""
        lqip = self.COVER_LQIP_MAP.get(path, "")
        if not lqip:
            # Derive: hero-foo-hd.webp / hero-foo.webp → hero-foo-lqip.jpg
            stem = path.rsplit("/", 1)[-1]
            stem = stem.replace("-hd.webp", "").replace("-hd.jpg", "")
            stem = stem.replace(".webp", "").replace(".jpg", "").replace(".png", "")
            candidate = f"images/brand/{stem}-lqip.jpg"
            lqip = candidate if candidate in self.COVER_LQIP_MAP.values() else ""
            # Also accept derived path even if not in map (file may exist on disk)
            if not lqip and stem.startswith("hero-"):
                lqip = f"images/brand/{stem}-lqip.jpg"
        return f"{request_static}{lqip}" if lqip else ""

    def _cover_webp_url(self, article: Article, request_static: str = "/static/") -> str:
        path = self._cover_static_path(article)
        if not path:
            return ""
        if path.endswith(".webp"):
            return f"{request_static}{path}"
        if path.endswith((".jpg", ".jpeg", ".png")):
            webp = path.rsplit(".", 1)[0] + ".webp"
            return f"{request_static}{webp}"
        return ""

    def _author_avatar(self, author, request_static: str = "/static/") -> str:
        if author.avatar:
            return author.avatar.url
        if author.avatar_static:
            path = author.avatar_static.lstrip("/")
            if path.startswith("static/"):
                path = path[7:]
            return f"{request_static}{path}"
        return ""

    def _serialize_author(self, author) -> dict[str, Any]:
        return {
            "name": author.name,
            "slug": author.slug,
            "role": author.role,
            "bio": author.bio,
            "avatar": self._author_avatar(author),
        }

    def _serialize_category(self, cat) -> dict[str, Any]:
        count = (
            self.repository.published_qs().filter(category_id=cat.id).count()
            if hasattr(cat, "id")
            else 0
        )
        return {
            "title": cat.title,
            "slug": cat.slug,
            "description": cat.description,
            "icon": cat.icon,
            "accent_color": cat.accent_color,
            "image_webp": cat.image_webp,
            "image_jpg": cat.image_jpg,
            "article_count": count,
            "article_count_fa": to_fa(count),
        }

    def _serialize_tag(self, tag) -> dict[str, Any]:
        return {"title": tag.title, "slug": tag.slug}

    def _serialize_card(self, article: Article) -> dict[str, Any]:
        return {
            "id": article.id,
            "title": article.title,
            "subtitle": article.subtitle,
            "slug": article.slug,
            "excerpt": article.excerpt,
            "cover": self._cover_url(article),
            "cover_webp": self._cover_webp_url(article),
            "cover_lqip": self._cover_lqip_url(article),
            "cover_alt": article.cover_image_alt or article.title,
            "reading_minutes": article.reading_minutes,
            "reading_minutes_fa": to_fa(article.reading_minutes),
            "published_at": article.published_at.isoformat() if article.published_at else "",
            "published_at_fa": jalali_date(article.published_at),
            "updated_at_fa": jalali_date(article.updated_at),
            "is_featured": article.is_featured,
            "is_editors_pick": article.is_editors_pick,
            "is_hero": article.is_hero,
            "view_count": article.view_count,
            "view_count_fa": to_fa(article.view_count),
            "like_count": article.like_count,
            "category": {
                "title": article.category.title,
                "slug": article.category.slug,
            },
            "author": self._serialize_author(article.author),
            "tags": [self._serialize_tag(t) for t in article.tags.all()],
            "url": f"/magazine/{article.slug}/",
        }

    def _serialize_detail(
        self,
        article: Article,
        *,
        body: str,
        toc: list[dict[str, str]],
        images: list,
    ) -> dict[str, Any]:
        card = self._serialize_card(article)
        seo = {
            "meta_title": article.meta_title or article.title,
            "meta_description": article.meta_description or article.excerpt,
            "meta_keywords": article.meta_keywords,
            "og_title": article.og_title or article.meta_title or article.title,
            "og_description": article.og_description or article.meta_description or article.excerpt,
            "og_image": article.og_image.url if article.og_image else card["cover"],
            "twitter_title": article.twitter_title or article.title,
            "twitter_description": article.twitter_description or article.excerpt,
            "canonical_url": article.canonical_url or card["url"],
            "robots": "noindex,nofollow" if article.robots_noindex else "index,follow",
            "schema": article.schema_json or self._default_schema(article, card),
        }
        return {
            **card,
            "body": body,
            "toc": toc,
            "video_url": article.video_url,
            "audio_url": article.audio_file.url if article.audio_file else "",
            "pdf_url": article.pdf_file.url if article.pdf_file else "",
            "allow_comments": article.allow_comments,
            "complete_read_count": article.complete_read_count,
            "share_count": article.share_count,
            "bookmark_count": article.bookmark_count,
            "average_rating": article.average_rating,
            "rating_count": article.rating_count,
            "rating_count_fa": to_fa(article.rating_count),
            "images": [
                {
                    "url": img.image.url,
                    "caption": img.caption,
                    "alt": img.alt_text or img.caption,
                }
                for img in images
            ],
            "seo": seo,
            "author_bio": article.author.bio,
        }

    def _default_schema(self, article: Article, card: dict) -> dict[str, Any]:
        site = getattr(settings, "SITE_NAME", "صالح ایوبی")
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article.title,
            "description": article.excerpt,
            "image": card.get("cover") or None,
            "datePublished": article.published_at.isoformat() if article.published_at else None,
            "dateModified": article.updated_at.isoformat() if article.updated_at else None,
            "author": {
                "@type": "Person",
                "name": article.author.name,
            },
            "publisher": {
                "@type": "Organization",
                "name": site,
            },
            "mainEntityOfPage": card.get("url"),
            "wordCount": len(_strip_html(article.body).split()),
            "timeRequired": f"PT{article.reading_minutes}M",
        }

    def _serialize_comment(self, comment) -> dict[str, Any]:
        return {
            "id": comment.id,
            "author_name": comment.author_name,
            "body": comment.body,
            "created_at_fa": jalali_date(comment.created_at),
            "is_approved": comment.is_approved,
        }

    @staticmethod
    def _hash_ip(ip: str) -> str:
        if not ip:
            return ""
        return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:64]
