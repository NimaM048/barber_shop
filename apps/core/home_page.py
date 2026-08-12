"""Homepage CMS — hero, assurance, section chrome."""

from __future__ import annotations

from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedModel


class HomePage(TimeStampedModel, SoftDeleteModel):
    key = models.SlugField("کلید", max_length=40, unique=True, default="home")
    is_published = models.BooleanField("منتشر شده", default=True, db_index=True)

    hero_eyebrow = models.CharField("هیرو — برچسب", max_length=200, blank=True)
    hero_title = models.TextField("هیرو — عنوان", blank=True)
    hero_tagline = models.TextField("هیرو — توضیح", blank=True)
    hero_cta_primary_label = models.CharField("هیرو — CTA اصلی", max_length=80, blank=True)
    hero_cta_primary_href = models.CharField("هیرو — لینک CTA اصلی", max_length=255, blank=True)
    hero_cta_secondary_label = models.CharField("هیرو — CTA فرعی", max_length=80, blank=True)
    hero_cta_secondary_href = models.CharField("هیرو — لینک CTA فرعی", max_length=255, blank=True)
    hero_image_webp = models.CharField("هیرو — WebP", max_length=255, blank=True)
    hero_image_mobile_webp = models.CharField("هیرو — WebP موبایل", max_length=255, blank=True)
    hero_image_fallback = models.CharField("هیرو — JPG fallback", max_length=255, blank=True)
    hero_logo_webp = models.CharField("هیرو — لوگو", max_length=255, blank=True)
    hero_scroll_hint = models.CharField("هیرو — اسکرول", max_length=80, blank=True)

    assurance_label = models.CharField("تجربه — برچسب", max_length=120, blank=True)
    assurance_title = models.TextField("تجربه — عنوان", blank=True)
    assurance_lede = models.TextField("تجربه — توضیح", blank=True)

    services_label = models.CharField("خدمات — برچسب", max_length=120, blank=True)
    services_title = models.TextField("خدمات — عنوان", blank=True)
    services_lede = models.TextField("خدمات — توضیح", blank=True)
    services_cta_label = models.CharField("خدمات — CTA", max_length=80, blank=True)
    services_cta_href = models.CharField("خدمات — لینک CTA", max_length=255, blank=True)
    services_empty_message = models.CharField("خدمات — خالی", max_length=200, blank=True)
    services_card_cta_label = models.CharField("خدمات — رزرو کارت", max_length=80, blank=True)

    gallery_label = models.CharField("گالری — برچسب", max_length=120, blank=True)
    gallery_title = models.CharField("گالری — عنوان", max_length=200, blank=True)
    gallery_lede = models.TextField("گالری — توضیح", blank=True)

    reviews_label = models.CharField("نظرات — برچسب", max_length=120, blank=True)
    reviews_title = models.CharField("نظرات — عنوان", max_length=200, blank=True)
    reviews_lede = models.TextField("نظرات — توضیح", blank=True)
    reviews_cta_label = models.CharField("نظرات — CTA", max_length=80, blank=True)

    seo_title = models.CharField("SEO عنوان", max_length=160, blank=True)
    seo_description = models.CharField("SEO توضیح", max_length=300, blank=True)

    class Meta:
        verbose_name = "صفحه اصلی"
        verbose_name_plural = "صفحه اصلی"

    def __str__(self) -> str:
        return f"Home ({self.key})"


class HomeProofBullet(models.Model):
    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name="proof_bullets",
        verbose_name="صفحه اصلی",
    )
    text = models.CharField("متن", max_length=200)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "نشان هیرو"
        verbose_name_plural = "نشان‌های هیرو"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.text


class HomeAssuranceStep(models.Model):
    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name="assurance_steps",
        verbose_name="صفحه اصلی",
    )
    number_label = models.CharField("شماره", max_length=10, blank=True)
    title = models.CharField("عنوان", max_length=120)
    description = models.TextField("توضیح", blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "مرحله تجربه"
        verbose_name_plural = "مراحل تجربه"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title
