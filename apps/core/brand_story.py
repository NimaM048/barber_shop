"""
Brand Story CMS — the emotional heart of the homepage.

All copy, portrait, timeline, values, and CTAs are data-driven.
"""

from __future__ import annotations

from django.db import models
from django.urls import NoReverseMatch, reverse

from apps.core.models import SoftDeleteModel, TimeStampedModel


class BrandStory(TimeStampedModel, SoftDeleteModel):
    """Singleton-style section payload keyed for homepage (and future pages)."""

    key = models.SlugField(
        "کلید",
        max_length=60,
        unique=True,
        default="home",
        help_text="مثلاً home — برای صفحه اصلی",
    )
    is_published = models.BooleanField("منتشر شده", default=True, db_index=True)

    # Editorial meta
    edition_label = models.CharField("برچسب نسخه", max_length=80, blank=True)
    section_label = models.CharField("برچسب بخش", max_length=80, blank=True)

    # Philosophy
    headline = models.TextField(
        "تیتر اصلی",
        help_text="هر خط را با Enter جدا کنید — خطوط به صورت بصری شکسته می‌شوند.",
    )
    subtitle = models.TextField("زیرتیتر", blank=True)
    story_body = models.TextField("داستان برند", blank=True)

    # Signature quote
    quote_text = models.TextField("نقل‌قول", blank=True)
    founder_name = models.CharField("نام بنیان‌گذار", max_length=120, blank=True)
    founder_title = models.CharField("عنوان بنیان‌گذار", max_length=120, blank=True)
    quote_signature = models.CharField("امضای نقل‌قول", max_length=160, blank=True)

    # Background typography (2–5% opacity words)
    bg_word_1 = models.CharField("واژه پس‌زمینه ۱", max_length=40, blank=True)
    bg_word_2 = models.CharField("واژه پس‌زمینه ۲", max_length=40, blank=True)
    bg_word_3 = models.CharField("واژه پس‌زمینه ۳", max_length=40, blank=True)
    bg_word_4 = models.CharField("واژه پس‌زمینه ۴", max_length=40, blank=True)

    # Portrait
    portrait = models.ImageField(
        "پرتره",
        upload_to="brand_story/",
        blank=True,
        null=True,
    )
    portrait_static = models.CharField("پرتره JPG (static)", max_length=255, blank=True)
    portrait_webp_static = models.CharField("پرتره WebP (static)", max_length=255, blank=True)
    portrait_lqip_static = models.CharField("پرتره LQIP (static)", max_length=255, blank=True)
    portrait_alt = models.CharField("متن جایگزین پرتره", max_length=220, blank=True)
    portrait_caption = models.CharField("کپشن پرتره", max_length=160, blank=True)
    portrait_index = models.CharField(
        "شماره نمایش پرتره",
        max_length=12,
        blank=True,
        default="01",
        help_text="مثلاً 01 — میکرو‌تایپوگرافی کنار کپشن",
    )

    # Timeline / values labels
    timeline_label = models.CharField("برچسب مسیر", max_length=80, blank=True)
    values_label = models.CharField("برچسب ارزش‌ها", max_length=80, blank=True)

    # CTAs
    cta_primary_label = models.CharField("متن دکمه اصلی", max_length=80, blank=True)
    cta_primary_href = models.CharField(
        "لینک دکمه اصلی",
        max_length=255,
        blank=True,
        help_text="مسیر مطلق، #anchor، یا نام URL مثل appointments:create",
    )
    cta_secondary_label = models.CharField("متن دکمه فرعی", max_length=80, blank=True)
    cta_secondary_href = models.CharField(
        "لینک دکمه فرعی",
        max_length=255,
        blank=True,
        help_text="مسیر مطلق، #anchor، یا نام URL",
    )

    # SEO / future
    seo_title = models.CharField("عنوان SEO", max_length=160, blank=True)
    seo_description = models.TextField("توضیح SEO", blank=True)

    class Meta:
        verbose_name = "داستان برند"
        verbose_name_plural = "داستان‌های برند"
        ordering = ["key"]

    def __str__(self) -> str:
        return f"Brand Story · {self.key}"

    @staticmethod
    def resolve_href(raw: str) -> str:
        if not raw:
            return ""
        value = raw.strip()
        if value.startswith(("#", "/", "http://", "https://")):
            return value
        if ":" in value:
            try:
                return reverse(value)
            except NoReverseMatch:
                return value
        return value


class BrandTimelineStep(TimeStampedModel, SoftDeleteModel):
    """Vertical philosophy journey — activates on scroll."""

    class PortraitEffect(models.TextChoices):
        FOCUS = "focus", "تمرکز چهره"
        LIGHT = "light", "تغییر نور"
        HAIR = "hair", "تأکید مو"
        BRIGHT = "bright", "روشنایی کامل"
        SOFT = "soft", "نرمی"
        NONE = "none", "بدون اثر"

    story = models.ForeignKey(
        BrandStory,
        on_delete=models.CASCADE,
        related_name="timeline_steps",
        verbose_name="داستان برند",
    )
    number_label = models.CharField("شماره", max_length=8)
    title = models.CharField("عنوان", max_length=80)
    description = models.TextField("توضیح", blank=True)
    portrait_effect = models.CharField(
        "اثر پرتره",
        max_length=20,
        choices=PortraitEffect.choices,
        default=PortraitEffect.NONE,
    )
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0, db_index=True)
    is_active = models.BooleanField("فعال", default=True, db_index=True)

    class Meta:
        verbose_name = "گام مسیر"
        verbose_name_plural = "گام‌های مسیر"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.number_label} — {self.title}"


class BrandValue(TimeStampedModel, SoftDeleteModel):
    """Brand values strip — softly animates into view."""

    story = models.ForeignKey(
        BrandStory,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name="داستان برند",
    )
    title = models.CharField("عنوان", max_length=60)
    subtitle = models.CharField("زیرعنوان", max_length=120, blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0, db_index=True)
    is_active = models.BooleanField("فعال", default=True, db_index=True)

    class Meta:
        verbose_name = "ارزش برند"
        verbose_name_plural = "ارزش‌های برند"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title
