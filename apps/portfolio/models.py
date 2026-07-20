"""
Luxury portfolio / gallery CMS.

Every homepage gallery card is driven from these models —
no hardcoded slides on the frontend.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import SoftDeleteModel, TimeStampedModel


class GalleryCategory(TimeStampedModel, SoftDeleteModel):
    """Filter chips above the gallery (داماد، VIP، مو، …)."""

    title = models.CharField("عنوان", max_length=100)
    slug = models.SlugField("اسلاگ", max_length=120, unique=True, allow_unicode=True)
    description = models.TextField("توضیحات", blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True, db_index=True)

    class Meta:
        verbose_name = "دسته‌بندی گالری"
        verbose_name_plural = "دسته‌بندی‌های گالری"
        ordering = ["sort_order", "title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = (
                slugify(self.title, allow_unicode=True)
                or f"cat-{timezone.now().timestamp():.0f}"
            )
        super().save(*args, **kwargs)


class GalleryTag(TimeStampedModel):
    title = models.CharField("عنوان", max_length=80)
    slug = models.SlugField("اسلاگ", max_length=100, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = "برچسب گالری"
        verbose_name_plural = "برچسب‌های گالری"
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = (
                slugify(self.title, allow_unicode=True)
                or f"tag-{timezone.now().timestamp():.0f}"
            )
        super().save(*args, **kwargs)


class GalleryItem(TimeStampedModel, SoftDeleteModel):
    """A premium portfolio case — cover, story, media, and conversion CTAs."""

    title = models.CharField("عنوان", max_length=200)
    subtitle = models.CharField("زیرعنوان", max_length=255, blank=True)
    slug = models.SlugField("اسلاگ", max_length=220, unique=True, allow_unicode=True)
    description = models.TextField("توضیح کوتاه", blank=True)
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="دسته‌بندی",
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(
        GalleryTag,
        related_name="items",
        blank=True,
        verbose_name="برچسب‌ها",
    )

    # Cover media (upload or static path for seeded brand assets)
    cover_image = models.ImageField(
        "تصویر کاور",
        upload_to="portfolio/covers/",
        blank=True,
        null=True,
    )
    cover_image_static = models.CharField("مسیر کاور JPG/PNG", max_length=255, blank=True)
    cover_webp_static = models.CharField("مسیر کاور WebP", max_length=255, blank=True)
    cover_avif_static = models.CharField("مسیر کاور AVIF", max_length=255, blank=True)
    cover_lqip_static = models.CharField("مسیر LQIP", max_length=255, blank=True)
    alt_text = models.CharField("متن جایگزین", max_length=220, blank=True)

    # Optional video
    video = models.FileField(
        "ویدئو",
        upload_to="portfolio/videos/",
        blank=True,
        null=True,
    )
    video_url = models.URLField("لینک ویدئو", blank=True)
    video_poster_static = models.CharField("پوستر ویدئو (static)", max_length=255, blank=True)

    # Before / After
    has_before_after = models.BooleanField("مقایسه قبل و بعد", default=False)
    before_image = models.ImageField(
        "تصویر قبل",
        upload_to="portfolio/before_after/",
        blank=True,
        null=True,
    )
    after_image = models.ImageField(
        "تصویر بعد",
        upload_to="portfolio/before_after/",
        blank=True,
        null=True,
    )
    before_image_static = models.CharField("قبل (static)", max_length=255, blank=True)
    after_image_static = models.CharField("بعد (static)", max_length=255, blank=True)
    before_alt = models.CharField("متن جایگزین قبل", max_length=200, blank=True)
    after_alt = models.CharField("متن جایگزین بعد", max_length=200, blank=True)

    # Storytelling
    problem = models.TextField("مشکل / نیاز", blank=True)
    solution = models.TextField("راه‌حل", blank=True)
    services_text = models.CharField("خدمات انجام‌شده", max_length=255, blank=True)
    duration_text = models.CharField("مدت زمان", max_length=80, blank=True)
    result = models.TextField("نتیجه", blank=True)
    customer_review = models.TextField("نظر مشتری", blank=True)

    # Meta
    location = models.CharField("مکان", max_length=120, blank=True)
    completed_at = models.DateField("تاریخ اتمام", null=True, blank=True)

    # Flags & ordering
    is_published = models.BooleanField("منتشر شده", default=True, db_index=True)
    is_featured = models.BooleanField("ویژه", default=False, db_index=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0, db_index=True)

    # Conversion
    related_service = models.ForeignKey(
        "catalog.ServiceItem",
        on_delete=models.SET_NULL,
        related_name="gallery_items",
        verbose_name="خدمت مرتبط",
        null=True,
        blank=True,
    )
    cta_title = models.CharField(
        "عنوان CTA",
        max_length=180,
        blank=True,
        default="از این نتیجه خوشتان آمد؟",
    )
    cta_consultation_label = models.CharField(
        "برچسب مشاوره",
        max_length=100,
        blank=True,
        default="دریافت مشاوره",
    )
    cta_booking_label = models.CharField(
        "برچسب رزرو",
        max_length=100,
        blank=True,
        default="رزرو این خدمت",
    )

    # SEO
    meta_title = models.CharField("Meta Title", max_length=70, blank=True)
    meta_description = models.CharField("Meta Description", max_length=170, blank=True)
    meta_keywords = models.CharField("Meta Keywords", max_length=255, blank=True)

    class Meta:
        verbose_name = "آیتم گالری"
        verbose_name_plural = "آیتم‌های گالری"
        ordering = ["sort_order", "-is_featured", "-created_at"]
        indexes = [
            models.Index(fields=["is_published", "sort_order"]),
            models.Index(fields=["is_featured", "is_published"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base = slugify(self.title, allow_unicode=True) or "gallery"
            candidate = base
            n = 1
            while (
                GalleryItem.all_objects.filter(slug=candidate)
                .exclude(pk=self.pk)
                .exists()
            ):
                n += 1
                candidate = f"{base}-{n}"
            self.slug = candidate
        if not self.alt_text:
            self.alt_text = self.title
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.meta_description and self.description:
            self.meta_description = self.description[:170]
        super().save(*args, **kwargs)

    def _media_url(self, uploaded, static_path: str) -> str:
        if uploaded:
            return uploaded.url
        return static_path or ""

    @property
    def cover_src(self) -> str:
        return self._media_url(self.cover_image, self.cover_image_static)

    @property
    def before_src(self) -> str:
        return self._media_url(self.before_image, self.before_image_static)

    @property
    def after_src(self) -> str:
        return self._media_url(self.after_image, self.after_image_static)

    @property
    def has_video(self) -> bool:
        return bool(self.video or self.video_url)


class GalleryImage(TimeStampedModel):
    """Additional images for a portfolio project (lightbox strip)."""

    item = models.ForeignKey(
        GalleryItem,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="آیتم",
    )
    image = models.ImageField(
        "تصویر",
        upload_to="portfolio/gallery/",
        blank=True,
        null=True,
    )
    image_static = models.CharField("مسیر static", max_length=255, blank=True)
    webp_static = models.CharField("WebP static", max_length=255, blank=True)
    avif_static = models.CharField("AVIF static", max_length=255, blank=True)
    lqip_static = models.CharField("LQIP static", max_length=255, blank=True)
    caption = models.CharField("کپشن", max_length=255, blank=True)
    alt_text = models.CharField("متن جایگزین", max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "تصویر گالری"
        verbose_name_plural = "تصاویر گالری"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.caption or f"{self.item_id} / {self.pk}"

    @property
    def src(self) -> str:
        if self.image:
            return self.image.url
        return self.image_static or ""
