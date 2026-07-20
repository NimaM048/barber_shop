"""
Pre-visit consultation / digital guide content.
All copy and media are managed here — frontend never hardcodes tip text.
"""

from __future__ import annotations

from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedModel


class ConsultationHubPage(TimeStampedModel, SoftDeleteModel):
    """Singleton-style chrome for the consultations hub page."""

    key = models.SlugField(
        "کلید",
        max_length=40,
        unique=True,
        default="hub",
        help_text="مثلاً hub — صفحه لیست مشاوره‌ها",
    )
    enabled = models.BooleanField("فعال", default=True, db_index=True)
    section_label = models.CharField("برچسب بخش", max_length=80, blank=True)
    title = models.CharField("عنوان", max_length=160)
    subtitle = models.TextField("زیرعنوان", blank=True)
    meta_description = models.CharField("توضیح متا", max_length=255, blank=True)
    document_title = models.CharField(
        "عنوان تب مرورگر",
        max_length=160,
        blank=True,
        help_text="اگر خالی باشد از title استفاده می‌شود",
    )
    empty_message = models.CharField("پیام خالی بودن", max_length=255, blank=True)
    card_cta_label = models.CharField("متن دکمه کارت", max_length=80, blank=True)
    card_stats_template = models.CharField(
        "قالب آمار کارت",
        max_length=120,
        blank=True,
        help_text="از {tips} و {minutes} استفاده کنید",
    )

    class Meta:
        verbose_name = "صفحه هاب مشاوره"
        verbose_name_plural = "صفحه هاب مشاوره"

    def __str__(self) -> str:
        return self.title or self.key


class ConsultationCategory(TimeStampedModel, SoftDeleteModel):
    """Top-level guides: vip / groom / skin."""

    key = models.SlugField("کلید", max_length=40, unique=True)
    title = models.CharField("عنوان", max_length=120)
    short_description = models.CharField("توضیح کوتاه", max_length=255, blank=True)
    description = models.TextField("توضیحات", blank=True)
    card_label = models.CharField("برچسب کارت", max_length=80, blank=True)
    icon = models.CharField("آیکون", max_length=80, blank=True, help_text="نام آیکون یا ایموجی")
    accent_color = models.CharField(
        "رنگ اختصاصی",
        max_length=20,
        blank=True,
        default="#f7f4ef",
        help_text="مثل #f7f4ef",
    )
    image_webp = models.CharField("تصویر WebP", max_length=255, blank=True)
    image_jpg = models.CharField("تصویر JPG", max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    enabled = models.BooleanField("فعال", default=True, db_index=True)
    estimated_read_minutes = models.PositiveSmallIntegerField(
        "مدت تقریبی مطالعه (دقیقه)",
        default=5,
    )
    booking_service_keys = models.JSONField(
        "کلیدهای سرویس رزرو مرتبط",
        default=list,
        blank=True,
        help_text='یک‌به‌یک با سرویس رزرو — مثلاً ["vip"] یا ["groom"] یا ["skin"]',
    )
    pdf_guide = models.FileField(
        "PDF راهنمای کامل",
        upload_to="consultations/guides/",
        blank=True,
        null=True,
    )
    content_version = models.CharField("نسخه محتوا", max_length=20, default="1.0")

    # ── Booking gate copy (per category) ──
    gate_eyebrow = models.CharField("برچسب گیت رزرو", max_length=120, blank=True)
    gate_title = models.TextField("عنوان گیت رزرو", blank=True)
    gate_body = models.TextField("متن گیت رزرو", blank=True)
    gate_primary_cta = models.CharField("دکمه اصلی گیت", max_length=120, blank=True)
    gate_primary_desc = models.CharField("توضیح دکمه اصلی", max_length=255, blank=True)
    gate_primary_kicker = models.CharField("برچسب پیشنهادی دکمه", max_length=80, blank=True)
    gate_primary_cta_suffix = models.CharField(
        "پسوند CTA اصلی",
        max_length=80,
        blank=True,
    )
    gate_secondary_cta = models.CharField("دکمه فرعی گیت", max_length=120, blank=True)
    gate_secondary_desc = models.CharField("توضیح دکمه فرعی", max_length=255, blank=True)
    gate_first_visit_title = models.CharField(
        "عنوان اولین مراجعه",
        max_length=200,
        blank=True,
    )
    gate_first_visit_body = models.TextField("متن اولین مراجعه", blank=True)
    acknowledgment_label = models.CharField(
        "متن تأیید راهنما",
        max_length=255,
        blank=True,
    )
    acknowledgment_error = models.CharField(
        "خطای عدم تأیید",
        max_length=255,
        blank=True,
    )
    confirm_guide_heading = models.CharField(
        "عنوان خلاصه در تأیید رزرو",
        max_length=160,
        blank=True,
    )
    confirm_guide_link_label = models.CharField(
        "لینک راهنمای کامل در تأیید",
        max_length=120,
        blank=True,
    )

    class Meta:
        verbose_name = "دسته مشاوره"
        verbose_name_plural = "دسته‌های مشاوره"
        ordering = ["sort_order", "key"]

    def __str__(self) -> str:
        return self.title


class TipGroup(TimeStampedModel):
    """Logical grouping inside a category (before / day / after)."""

    class Phase(models.TextChoices):
        BEFORE = "before", "قبل از مراجعه"
        DAY = "day", "روز مراجعه"
        AFTER = "after", "بعد از خدمات"

    category = models.ForeignKey(
        ConsultationCategory,
        on_delete=models.CASCADE,
        related_name="tip_groups",
        verbose_name="دسته",
    )
    key = models.SlugField("کلید", max_length=40)
    title = models.CharField("عنوان", max_length=120)
    phase = models.CharField(
        "فاز",
        max_length=20,
        choices=Phase.choices,
        default=Phase.BEFORE,
        db_index=True,
    )
    description = models.CharField("توضیح", max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    enabled = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "گروه نکات"
        verbose_name_plural = "گروه‌های نکات"
        ordering = ["sort_order", "key"]
        unique_together = ("category", "key")

    def __str__(self) -> str:
        return f"{self.category.key} / {self.title}"


class ConsultationTip(TimeStampedModel, SoftDeleteModel):
    category = models.ForeignKey(
        ConsultationCategory,
        on_delete=models.CASCADE,
        related_name="tips",
        verbose_name="دسته",
    )
    group = models.ForeignKey(
        TipGroup,
        on_delete=models.SET_NULL,
        related_name="tips",
        verbose_name="گروه",
        null=True,
        blank=True,
    )
    title = models.CharField("عنوان", max_length=180)
    description = models.TextField("توضیح")
    icon = models.CharField("آیکون", max_length=80, blank=True)
    image = models.ImageField(
        "تصویر آموزشی",
        upload_to="consultations/tips/",
        blank=True,
        null=True,
    )
    image_static = models.CharField(
        "مسیر تصویر استاتیک",
        max_length=255,
        blank=True,
        help_text="اگر ImageField خالی باشد، از این مسیر static استفاده می‌شود",
    )
    sort_order = models.PositiveSmallIntegerField("ترتیب / اولویت", default=0)
    enabled = models.BooleanField("فعال", default=True, db_index=True)
    is_highlight = models.BooleanField("نکته مهم (هایلایت)", default=False)
    video_url = models.URLField("لینک ویدئو", blank=True)
    pdf_file = models.FileField(
        "فایل PDF",
        upload_to="consultations/pdfs/",
        blank=True,
        null=True,
    )
    audio_file = models.FileField(
        "فایل صوتی",
        upload_to="consultations/audio/",
        blank=True,
        null=True,
    )
    external_link = models.URLField("لینک مطالعه بیشتر", blank=True)
    content_version = models.CharField("نسخه محتوا", max_length=20, default="1.0")
    read_seconds = models.PositiveSmallIntegerField(
        "مدت مطالعه تقریبی (ثانیه)",
        default=30,
    )

    class Meta:
        verbose_name = "نکته مشاوره"
        verbose_name_plural = "نکات مشاوره"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title


class ConsultationAlert(TimeStampedModel, SoftDeleteModel):
    class Severity(models.TextChoices):
        INFO = "info", "اطلاع"
        WARNING = "warning", "هشدار"
        DANGER = "danger", "بحرانی"

    category = models.ForeignKey(
        ConsultationCategory,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="دسته",
    )
    title = models.CharField("عنوان", max_length=180)
    message = models.TextField("متن هشدار")
    severity = models.CharField(
        "شدت",
        max_length=20,
        choices=Severity.choices,
        default=Severity.WARNING,
    )
    icon = models.CharField("آیکون", max_length=80, blank=True, default="⚠")
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    enabled = models.BooleanField("فعال", default=True, db_index=True)
    show_in_booking = models.BooleanField(
        "نمایش در خلاصه رزرو",
        default=True,
        help_text="در مرحله تأیید رزرو نمایش داده شود",
    )

    class Meta:
        verbose_name = "هشدار مهم"
        verbose_name_plural = "هشدارهای مهم"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title


class ConsultationFAQ(TimeStampedModel, SoftDeleteModel):
    category = models.ForeignKey(
        ConsultationCategory,
        on_delete=models.CASCADE,
        related_name="faqs",
        verbose_name="دسته",
    )
    question = models.CharField("سوال", max_length=255)
    answer = models.TextField("پاسخ")
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    enabled = models.BooleanField("فعال", default=True, db_index=True)

    class Meta:
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.question


class ConsultationTicket(TimeStampedModel, SoftDeleteModel):
    """Expert consultation request — often opened from the booking gate."""

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار پاسخ"
        ANSWERED = "answered", "پاسخ داده شده"
        CLOSED = "closed", "بسته"

    category = models.ForeignKey(
        ConsultationCategory,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="دسته مشاوره",
    )
    booking_service_key = models.SlugField(
        "کلید سرویس رزرو",
        max_length=40,
        blank=True,
        db_index=True,
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        related_name="consultation_tickets",
        verbose_name="رزرو مرتبط",
        null=True,
        blank=True,
    )
    first_name = models.CharField("نام", max_length=80)
    last_name = models.CharField("نام خانوادگی", max_length=80)
    phone = models.CharField("شماره تماس", max_length=15, db_index=True)
    message = models.TextField("پیام / سوال")
    attachment = models.FileField(
        "فایل پیوست",
        upload_to="consultations/tickets/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    source = models.CharField(
        "منبع",
        max_length=40,
        default="direct",
        help_text="booking | direct",
    )
    staff_notes = models.TextField("یادداشت داخلی", blank=True)

    class Meta:
        verbose_name = "تیکت مشاوره"
        verbose_name_plural = "تیکت‌های مشاوره"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} — {self.category.key}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
