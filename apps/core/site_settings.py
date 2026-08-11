"""Site-wide branding and contact — admin-manageable singleton."""

from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampedModel


class SiteSettings(TimeStampedModel):
    """Singleton site configuration (key=site)."""

    key = models.SlugField("کلید", max_length=40, unique=True, default="site")
    is_published = models.BooleanField("فعال", default=True, db_index=True)

    site_name = models.CharField("نام برند", max_length=120, blank=True)
    site_tagline = models.CharField("تگ‌لاین", max_length=160, blank=True)
    site_subtitle = models.CharField("زیرعنوان", max_length=200, blank=True)

    phone = models.CharField("تلفن (لینک)", max_length=40, blank=True)
    phone_display = models.CharField("تلفن (نمایش)", max_length=60, blank=True)
    whatsapp = models.CharField("واتساپ", max_length=40, blank=True)
    email = models.EmailField("ایمیل", blank=True)
    instagram = models.CharField("اینستاگرام", max_length=80, blank=True)
    telegram = models.CharField("تلگرام", max_length=80, blank=True)
    website = models.CharField("وب‌سایت", max_length=120, blank=True)

    address = models.CharField("آدرس کامل", max_length=255, blank=True)
    city = models.CharField("شهر", max_length=80, blank=True, default="اصفهان")
    lat = models.DecimalField("عرض جغرافیایی", max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField("طول جغرافیایی", max_digits=9, decimal_places=6, null=True, blank=True)
    map_zoom = models.PositiveSmallIntegerField("زوم نقشه", default=16)
    hours_text = models.CharField("ساعات کاری", max_length=200, blank=True)
    google_maps_url = models.URLField("لینک گوگل مپ", blank=True)
    gbp_url = models.URLField("لینک Google Business", blank=True)

    logo_path = models.CharField(
        "مسیر لوگو",
        max_length=255,
        blank=True,
        help_text="مثلاً images/brand/logo-signature-800.webp",
    )
    logo_alt = models.CharField("متن alt لوگو", max_length=120, blank=True)

    header_cta_short = models.CharField("دکمه هدر (کوتاه)", max_length=40, blank=True, default="رزرو")
    header_cta_full = models.CharField("دکمه هدر (کامل)", max_length=80, blank=True, default="رزرو نوبت")
    header_cta_href = models.CharField(
        "لینک دکمه هدر",
        max_length=255,
        blank=True,
        default="appointments:create",
    )

    location_eyebrow = models.CharField("موقعیت — برچسب", max_length=80, blank=True)
    location_title_fa = models.CharField("موقعیت — عنوان", max_length=200, blank=True)
    location_badge = models.CharField("موقعیت — نشان", max_length=80, blank=True)
    location_lede = models.TextField("موقعیت — توضیح", blank=True)
    location_district = models.CharField("محله", max_length=120, blank=True)
    location_street = models.CharField("خیابان", max_length=120, blank=True)
    location_cue = models.CharField("راهنمای آدرس", max_length=120, blank=True)
    location_availability = models.CharField("نوبت‌دهی", max_length=120, blank=True)
    location_cta_directions = models.CharField("CTA مسیریابی", max_length=80, blank=True)
    location_cta_maps = models.CharField("CTA نقشه", max_length=80, blank=True)
    location_cta_copy = models.CharField("CTA کپی آدرس", max_length=80, blank=True)
    location_cta_gbp = models.CharField("CTA گوگل", max_length=80, blank=True)

    seo_title_default = models.CharField("SEO عنوان پیش‌فرض", max_length=160, blank=True)
    seo_description_default = models.CharField("SEO توضیح پیش‌فرض", max_length=300, blank=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self) -> str:
        return self.site_name or self.key


class HeaderNavLink(models.Model):
    """Primary navigation links — managed in admin."""

    settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="nav_links",
        verbose_name="تنظیمات",
    )
    label = models.CharField("عنوان", max_length=80)
    href = models.CharField(
        "لینک",
        max_length=255,
        help_text="مسیر، #anchor، یا نام URL مثل magazine:hub",
    )
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)
    show_on_mobile = models.BooleanField("نمایش در موبایل", default=True)

    class Meta:
        verbose_name = "لینک منو"
        verbose_name_plural = "لینک‌های منو"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.label
