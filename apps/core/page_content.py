"""Per-page editorial chrome — catalog, magazine, booking, barbers."""

from __future__ import annotations

from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedModel


class PageContent(TimeStampedModel, SoftDeleteModel):
    class PageKey(models.TextChoices):
        CATALOG = "catalog", "کاتالوگ خدمات"
        MAGAZINE = "magazine", "مجله"
        BOOKING = "booking", "رزرو نوبت"
        BARBERS = "barbers", "آرایشگران"
        CONSULTATIONS = "consultations", "مشاوره"

    page = models.CharField(
        "صفحه",
        max_length=40,
        choices=PageKey.choices,
        unique=True,
    )
    is_published = models.BooleanField("منتشر شده", default=True, db_index=True)
    section_label = models.CharField("برچسب بخش", max_length=120, blank=True)
    title = models.TextField("عنوان", blank=True)
    lede = models.TextField("توضیح", blank=True)

    # Booking-specific flat fields
    extra_label = models.CharField("برچسب جانبی", max_length=120, blank=True)
    assurance_1 = models.CharField("نشان ۱", max_length=120, blank=True)
    assurance_2 = models.CharField("نشان ۲", max_length=120, blank=True)
    status_text = models.CharField("وضعیت مسیر", max_length=200, blank=True)
    step_1_label = models.CharField("مرحله ۱", max_length=80, blank=True)
    step_2_label = models.CharField("مرحله ۲", max_length=80, blank=True)
    step_3_label = models.CharField("مرحله ۳", max_length=80, blank=True)
    step_4_label = models.CharField("مرحله ۴", max_length=80, blank=True)
    step_5_label = models.CharField("مرحله ۵", max_length=80, blank=True)
    summary_empty = models.CharField("خلاصه خالی", max_length=200, blank=True)
    policy_text = models.TextField("متن قوانین / لغو", blank=True)

    content_json = models.JSONField(
        "محتوای ساختاریافته",
        default=dict,
        blank=True,
        help_text="JSON برای لیست‌ها، UI رزرو، نشان‌ها و متن‌های جانبی",
    )

    seo_title = models.CharField("SEO عنوان", max_length=160, blank=True)
    seo_description = models.CharField("SEO توضیح", max_length=300, blank=True)

    class Meta:
        verbose_name = "محتوای صفحه"
        verbose_name_plural = "محتوای صفحات"

    def __str__(self) -> str:
        return self.get_page_display()
