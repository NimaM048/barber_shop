"""
Footer Finale CMS — the closing chapter of the brand experience.

All philosophy, CTAs, contact, signature, and navigation are data-driven.
"""

from __future__ import annotations

from django.db import models
from django.urls import NoReverseMatch, reverse

from apps.core.models import SoftDeleteModel, TimeStampedModel


class FooterFinale(TimeStampedModel, SoftDeleteModel):
    """Singleton-style footer payload keyed for site-wide use."""

    key = models.SlugField(
        "کلید",
        max_length=60,
        unique=True,
        default="site",
        help_text="مثلاً site — فوتر سراسری",
    )
    is_published = models.BooleanField("منتشر شده", default=True, db_index=True)

    # Editorial meta
    edition_label = models.CharField("برچسب نسخه", max_length=80, blank=True)
    section_label = models.CharField("برچسب بخش", max_length=80, blank=True)
    aria_label = models.CharField(
        "برچسب دسترس‌پذیری",
        max_length=120,
        blank=True,
        help_text="برای screen reader — مثلاً پایان تجربه برند",
    )

    # ── Act I — Reflection ──
    philosophy = models.TextField(
        "فلسفه برند",
        help_text="هر خط را با Enter جدا کنید — تایپوگرافی موزه‌ای.",
    )
    philosophy_caption = models.CharField("کپشن فلسفه", max_length=120, blank=True)
    bg_word = models.CharField(
        "واژه پس‌زمینه",
        max_length=40,
        blank=True,
        help_text="مثلاً ARCHITECTURE — شفافیت ۲ تا ۴٪",
    )

    # ── Act II — Decision ──
    cta_statement = models.TextField(
        "بیانیه تصمیم",
        blank=True,
        help_text="مثلاً: هر دگرگونی با یک تصمیم آغاز می‌شود.",
    )
    cta_prompt = models.CharField(
        "دعوت به اقدام",
        max_length=120,
        blank=True,
        help_text="مثلاً: سفر خود را آغاز کنید.",
    )
    cta_primary_label = models.CharField("متن دکمه اصلی", max_length=80, blank=True)
    cta_primary_href = models.CharField(
        "لینک دکمه اصلی",
        max_length=255,
        blank=True,
        help_text="مسیر مطلق، #anchor، یا نام URL مثل consultations:hub",
    )
    cta_secondary_label = models.CharField("متن دکمه فرعی", max_length=80, blank=True)
    cta_secondary_href = models.CharField(
        "لینک دکمه فرعی",
        max_length=255,
        blank=True,
        help_text="مسیر مطلق، #anchor، یا نام URL مثل appointments:create",
    )

    # ── Act III — Connection ──
    show_phone = models.BooleanField("نمایش تلفن", default=True)
    phone = models.CharField("تلفن (لینک)", max_length=40, blank=True)
    phone_display = models.CharField("تلفن (نمایش)", max_length=60, blank=True)
    phone_label = models.CharField("برچسب تلفن", max_length=40, blank=True, default="تلفن")

    show_whatsapp = models.BooleanField("نمایش واتساپ", default=True)
    whatsapp = models.CharField(
        "واتساپ",
        max_length=40,
        blank=True,
        help_text="شماره با کد کشور بدون + — مثلاً 989132270519",
    )
    whatsapp_label = models.CharField(
        "برچسب واتساپ", max_length=40, blank=True, default="واتساپ"
    )

    show_instagram = models.BooleanField("نمایش اینستاگرام", default=True)
    instagram = models.CharField("اینستاگرام", max_length=80, blank=True)
    instagram_label = models.CharField(
        "برچسب اینستاگرام", max_length=40, blank=True, default="اینستاگرام"
    )

    show_telegram = models.BooleanField("نمایش تلگرام", default=False)
    telegram = models.CharField("تلگرام", max_length=80, blank=True)
    telegram_label = models.CharField(
        "برچسب تلگرام", max_length=40, blank=True, default="تلگرام"
    )

    show_email = models.BooleanField("نمایش ایمیل", default=False)
    email = models.EmailField("ایمیل", blank=True)
    email_label = models.CharField("برچسب ایمیل", max_length=40, blank=True, default="ایمیل")

    show_website = models.BooleanField("نمایش وب‌سایت", default=True)
    website = models.CharField("وب‌سایت", max_length=120, blank=True)
    website_label = models.CharField(
        "برچسب وب‌سایت", max_length=40, blank=True, default="وب‌سایت"
    )

    show_address = models.BooleanField("نمایش آدرس", default=True)
    address = models.TextField("آدرس", blank=True)
    address_label = models.CharField("برچسب آدرس", max_length=40, blank=True, default="آدرس")

    show_hours = models.BooleanField("نمایش ساعات کاری", default=True)
    working_hours = models.CharField("ساعات کاری", max_length=160, blank=True)
    hours_label = models.CharField(
        "برچسب ساعات", max_length=40, blank=True, default="ساعات کاری"
    )

    contact_caption = models.CharField("کپشن ارتباط", max_length=120, blank=True)

    # ── Brand Signature ──
    logo = models.ImageField("لوگو", upload_to="footer/", blank=True, null=True)
    logo_static = models.CharField(
        "لوگو (static)",
        max_length=255,
        blank=True,
        default="images/brand/logo-signature.webp",
    )
    logo_alt = models.CharField("متن جایگزین لوگو", max_length=160, blank=True)
    signature = models.CharField(
        "امضای برند",
        max_length=160,
        blank=True,
        help_text="مثلاً Architecture of Beauty",
    )
    show_founder = models.BooleanField("نمایش بنیان‌گذار", default=True)
    founder_name = models.CharField("نام بنیان‌گذار", max_length=120, blank=True)
    founder_title = models.CharField("عنوان بنیان‌گذار", max_length=120, blank=True)
    founded_year = models.CharField("سال تأسیس", max_length=20, blank=True)
    copyright_text = models.CharField(
        "متن کپی‌رایت",
        max_length=200,
        blank=True,
        help_text="خالی بگذارید تا به‌صورت خودکار ساخته شود.",
    )

    # Visibility / SEO
    show_navigation = models.BooleanField("نمایش ناوبری", default=True)
    seo_title = models.CharField("عنوان SEO", max_length=160, blank=True)
    seo_description = models.TextField("توضیح SEO", blank=True)

    class Meta:
        verbose_name = "فوتر نهایی"
        verbose_name_plural = "فوترهای نهایی"
        ordering = ["key"]

    def __str__(self) -> str:
        return f"Footer Finale · {self.key}"

    @staticmethod
    def resolve_href(raw: str) -> str:
        if not raw:
            return ""
        value = raw.strip()
        if value.startswith(("#", "/", "http://", "https://", "tel:", "mailto:")):
            return value
        if ":" in value:
            try:
                return reverse(value)
            except NoReverseMatch:
                return value
        return value


class FooterNavLink(TimeStampedModel, SoftDeleteModel):
    """Editorial navigation links in the closing signature zone."""

    footer = models.ForeignKey(
        FooterFinale,
        on_delete=models.CASCADE,
        related_name="nav_links",
        verbose_name="فوتر",
    )
    label = models.CharField("عنوان", max_length=80)
    href = models.CharField(
        "لینک",
        max_length=255,
        help_text="مسیر مطلق، #anchor، یا نام URL",
    )
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0, db_index=True)
    is_active = models.BooleanField("فعال", default=True, db_index=True)
    open_in_new_tab = models.BooleanField("تب جدید", default=False)

    class Meta:
        verbose_name = "لینک ناوبری فوتر"
        verbose_name_plural = "لینک‌های ناوبری فوتر"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.label

    @property
    def resolved_href(self) -> str:
        return FooterFinale.resolve_href(self.href)
