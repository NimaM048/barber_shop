"""
Customer reviews CMS — admin-curated, SEO-first editorial voices.
"""

from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import SoftDeleteModel, TimeStampedModel


class ReviewCategory(TimeStampedModel, SoftDeleteModel):
    """Service-aligned review collections (داماد، VIP، پوست)."""

    key = models.SlugField(
        "کلید",
        max_length=40,
        unique=True,
        help_text="شناسه برنامه‌ای — vip، groom، skin",
    )
    title = models.CharField("عنوان", max_length=120)
    slug = models.SlugField("اسلاگ", max_length=140, unique=True, allow_unicode=True)
    lede = models.TextField("توضیح", blank=True)
    seo_title = models.CharField("SEO عنوان", max_length=160, blank=True)
    seo_description = models.CharField("SEO توضیح", max_length=300, blank=True)
    booking_service_key = models.SlugField(
        "کلید سرویس رزرو",
        max_length=40,
        blank=True,
        help_text="برای لینک رزرو: /appointments/new/?service=",
    )
    consultation_category_key = models.SlugField(
        "کلید دسته مشاوره",
        max_length=40,
        blank=True,
        help_text="برای لینک به /consultations/<key>/",
    )
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0, db_index=True)
    is_published = models.BooleanField("منتشر شده", default=True, db_index=True)

    class Meta:
        verbose_name = "دسته نظر"
        verbose_name_plural = "دسته‌های نظرات"
        ordering = ["sort_order", "title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.key or slugify(self.title, allow_unicode=True) or self.key
        if not self.booking_service_key:
            self.booking_service_key = self.key
        if not self.consultation_category_key:
            self.consultation_category_key = self.key
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("reviews:category", kwargs={"category": self.slug})


class Review(TimeStampedModel, SoftDeleteModel):
    """A published customer narrative — unique URL, visible rating, full body."""

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشر شده"

    title = models.CharField("عنوان", max_length=220)
    slug = models.SlugField("اسلاگ", max_length=240, allow_unicode=True)
    body = models.TextField(
        "متن نظر",
        help_text="۲ تا ۴ پاراگراف. پاراگراف‌ها را با خط خالی جدا کنید.",
    )
    author_display_name = models.CharField("نام نمایشی", max_length=120)
    author_role = models.CharField(
        "نقش / نسبت",
        max_length=80,
        blank=True,
        help_text="مثلاً داماد، مراجعه پوست، مهمان VIP",
    )
    city = models.CharField("شهر", max_length=80, default="اصفهان", blank=True)
    rating = models.PositiveSmallIntegerField(
        "امتیاز",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="۱ تا ۵ — روی صفحه به‌صورت «۵ از ۵» دیده می‌شود",
    )
    category = models.ForeignKey(
        ReviewCategory,
        on_delete=models.PROTECT,
        related_name="reviews",
        verbose_name="دسته",
    )
    service_name = models.CharField(
        "نام خدمت",
        max_length=120,
        blank=True,
        help_text="برچسب نمایشی خدمت، مثلاً آرایش داماد",
    )
    visited_on = models.DateField("تاریخ مراجعه", null=True, blank=True)
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    is_featured = models.BooleanField("ویژه صفحه اصلی", default=False, db_index=True)
    published_at = models.DateTimeField("تاریخ انتشار", null=True, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0, db_index=True)
    seo_title = models.CharField("SEO عنوان", max_length=160, blank=True)
    seo_description = models.CharField("SEO توضیح", max_length=300, blank=True)
    portrait = models.ImageField(
        "پرتره",
        upload_to="reviews/portraits/",
        blank=True,
        null=True,
    )
    portrait_static = models.CharField(
        "مسیر پرتره استاتیک",
        max_length=255,
        blank=True,
        help_text="اگر ImageField خالی باشد از این مسیر static استفاده می‌شود",
    )
    source_note = models.CharField(
        "منبع",
        max_length=120,
        blank=True,
        default="ثبت‌شده در سالن",
    )

    class Meta:
        verbose_name = "نظر مشتری"
        verbose_name_plural = "نظرات مشتریان"
        ordering = ["sort_order", "-published_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"],
                name="reviews_unique_category_slug",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "is_featured", "-published_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.author_display_name} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = (
                slugify(self.title, allow_unicode=True)
                or f"review-{timezone.now().timestamp():.0f}"
            )
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse(
            "reviews:detail",
            kwargs={"category": self.category.slug, "slug": self.slug},
        )
