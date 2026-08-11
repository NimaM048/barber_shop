"""
Appointment booking domain: guest bookings, per-service schedule config, slots.
"""

from __future__ import annotations

import secrets
import string

from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedModel

WEEKDAY_KEYS = (
    "saturday",
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
)

WEEKDAY_LABELS_FA = {
    "saturday": "شنبه",
    "sunday": "یکشنبه",
    "monday": "دوشنبه",
    "tuesday": "سه‌شنبه",
    "wednesday": "چهارشنبه",
    "thursday": "پنجشنبه",
    "friday": "جمعه",
}

# Python datetime.weekday(): Mon=0 … Sun=6
WEEKDAY_TO_PYTHON = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

PYTHON_TO_WEEKDAY = {v: k for k, v in WEEKDAY_TO_PYTHON.items()}


def default_working_days():
    return list(WEEKDAY_KEYS)


def generate_booking_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "SA-" + "".join(secrets.choice(alphabet) for _ in range(6))


class BookingServiceConfig(TimeStampedModel, SoftDeleteModel):
    """Dynamic schedule settings for each bookable service flow."""

    service = models.OneToOneField(
        "catalog.ServiceItem",
        on_delete=models.CASCADE,
        related_name="booking_config",
        verbose_name="خدمت کاتالوگ",
    )
    key = models.SlugField(
        "کلید سرویس",
        max_length=40,
        unique=True,
        help_text="مثلاً vip، skin، groom — برای API و فرانت",
    )
    enabled = models.BooleanField("فعال", default=True, db_index=True)
    working_days = models.JSONField(
        "روزهای کاری",
        default=default_working_days,
        help_text="لیست کلیدها: saturday … friday",
    )
    start_time = models.TimeField("ساعت شروع")
    end_time = models.TimeField("ساعت پایان")
    slot_duration = models.PositiveSmallIntegerField(
        "فاصله نوبت (دقیقه)",
        help_text="مدت هر Slot — فرانت فقط نمایش می‌دهد",
    )
    capacity = models.PositiveSmallIntegerField(
        "ظرفیت هر بازه",
        default=1,
        help_text="تعداد مراجعه‌کننده همزمان در هر Slot",
    )
    short_description = models.CharField("توضیح کوتاه کارت", max_length=255, blank=True)
    card_label = models.CharField("برچسب کارت", max_length=80, blank=True)
    image_webp = models.CharField("مسیر تصویر WebP", max_length=255, blank=True)
    image_jpg = models.CharField("مسیر تصویر JPG", max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    booking_lead_hours = models.PositiveSmallIntegerField(
        "حداقل فاصله تا نوبت (ساعت)",
        default=2,
    )
    booking_window_days = models.PositiveSmallIntegerField(
        "بازه رزرو آینده (روز)",
        default=45,
    )

    class Meta:
        verbose_name = "تنظیمات رزرو سرویس"
        verbose_name_plural = "تنظیمات رزرو سرویس‌ها"
        ordering = ["sort_order", "key"]

    def __str__(self) -> str:
        return f"{self.service.name} ({self.key})"

    @property
    def display_duration(self) -> int:
        return self.slot_duration


class BookingBreak(TimeStampedModel):
    """Rest / closed windows inside working hours (e.g. lunch)."""

    config = models.ForeignKey(
        BookingServiceConfig,
        on_delete=models.CASCADE,
        related_name="breaks",
        verbose_name="سرویس",
    )
    start_time = models.TimeField("شروع استراحت")
    end_time = models.TimeField("پایان استراحت")
    label = models.CharField("عنوان", max_length=100, blank=True)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "استراحت کاری"
        verbose_name_plural = "استراحت‌های کاری"
        ordering = ["start_time"]

    def __str__(self) -> str:
        return f"{self.config.key}: {self.start_time}–{self.end_time}"


class BookingHoliday(TimeStampedModel):
    """Closed dates — global (config=null) or per-service."""

    config = models.ForeignKey(
        BookingServiceConfig,
        on_delete=models.CASCADE,
        related_name="holidays",
        verbose_name="سرویس",
        null=True,
        blank=True,
        help_text="خالی = تعطیلی عمومی برای همه سرویس‌ها",
    )
    date = models.DateField("تاریخ", db_index=True)
    title = models.CharField("عنوان", max_length=150, blank=True)
    is_closed = models.BooleanField("تعطیل", default=True)

    class Meta:
        verbose_name = "تعطیلی"
        verbose_name_plural = "تعطیلات"
        ordering = ["date"]
        unique_together = ("config", "date")

    def __str__(self) -> str:
        scope = self.config.key if self.config_id else "عمومی"
        return f"{self.date} ({scope})"


class BookingSpecialDate(TimeStampedModel):
    """Override schedule for a specific calendar date."""

    config = models.ForeignKey(
        BookingServiceConfig,
        on_delete=models.CASCADE,
        related_name="special_dates",
        verbose_name="سرویس",
    )
    date = models.DateField("تاریخ", db_index=True)
    is_closed = models.BooleanField("تعطیل در این روز", default=False)
    start_time = models.TimeField("ساعت شروع جایگزین", null=True, blank=True)
    end_time = models.TimeField("ساعت پایان جایگزین", null=True, blank=True)
    slot_duration = models.PositiveSmallIntegerField(
        "فاصله نوبت جایگزین",
        null=True,
        blank=True,
    )
    capacity = models.PositiveSmallIntegerField("ظرفیت جایگزین", null=True, blank=True)
    note = models.CharField("یادداشت", max_length=200, blank=True)

    class Meta:
        verbose_name = "تاریخ خاص"
        verbose_name_plural = "تاریخ‌های خاص"
        ordering = ["date"]
        unique_together = ("config", "date")

    def __str__(self) -> str:
        return f"{self.config.key} @ {self.date}"


class DisabledTimeSlot(TimeStampedModel):
    """Disable one or more time ranges on a given date."""

    config = models.ForeignKey(
        BookingServiceConfig,
        on_delete=models.CASCADE,
        related_name="disabled_slots",
        verbose_name="سرویس",
    )
    date = models.DateField("تاریخ", db_index=True)
    start_time = models.TimeField("شروع بازه")
    end_time = models.TimeField("پایان بازه")
    reason = models.CharField("دلیل", max_length=200, blank=True)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "بازه غیرفعال"
        verbose_name_plural = "بازه‌های غیرفعال"
        ordering = ["date", "start_time"]

    def __str__(self) -> str:
        return f"{self.config.key} {self.date} {self.start_time}–{self.end_time}"


class Appointment(TimeStampedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار تأیید"
        CONFIRMED = "confirmed", "تأیید شده"
        CANCELLED = "cancelled", "لغو شده"
        COMPLETED = "completed", "انجام شده"
        NO_SHOW = "no_show", "حاضر نشد"

    booking_code = models.CharField(
        "کد رزرو",
        max_length=20,
        unique=True,
        db_index=True,
        blank=True,
        editable=False,
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="appointments",
        verbose_name="مشتری",
        null=True,
        blank=True,
    )
    barber = models.ForeignKey(
        "barbers.Barber",
        on_delete=models.SET_NULL,
        related_name="appointments",
        verbose_name="آرایشگر",
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        "catalog.ServiceItem",
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="خدمت",
    )
    booking_config = models.ForeignKey(
        BookingServiceConfig,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="تنظیمات رزرو",
        null=True,
        blank=True,
    )
    first_name = models.CharField("نام", max_length=80)
    last_name = models.CharField("نام خانوادگی", max_length=80)
    phone = models.CharField("شماره تماس", max_length=15, db_index=True)
    starts_at = models.DateTimeField("شروع نوبت", db_index=True)
    ends_at = models.DateTimeField("پایان نوبت")
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
        db_index=True,
    )
    notes = models.TextField("یادداشت", blank=True)
    guide_acknowledged = models.BooleanField(
        "تأیید مطالعه راهنما",
        default=False,
        help_text="کاربر راهنمای قبل از مراجعه را پذیرفته است",
    )
    price_at_booking = models.DecimalField(
        "قیمت در زمان رزرو",
        max_digits=12,
        decimal_places=0,
        default=0,
    )

    class Meta:
        verbose_name = "نوبت"
        verbose_name_plural = "نوبت‌ها"
        ordering = ["-starts_at"]
        indexes = [
            models.Index(fields=["service", "starts_at"]),
            models.Index(fields=["phone", "starts_at"]),
            models.Index(fields=["booking_config", "starts_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.booking_code} — {self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if not self.booking_code:
            for _ in range(8):
                code = generate_booking_code()
                if not Appointment.all_objects.filter(booking_code=code).exists():
                    self.booking_code = code
                    break
            else:
                self.booking_code = generate_booking_code()
        super().save(*args, **kwargs)


class BookingSettings(TimeStampedModel):
    """Global booking policy — singleton (key=site)."""

    key = models.SlugField("کلید", max_length=40, unique=True, default="site")
    is_active = models.BooleanField("فعال", default=True)

    auto_confirm = models.BooleanField(
        "تأیید خودکار نوبت",
        default=True,
        help_text="اگر غیرفعال باشد نوبت با وضعیت «در انتظار» ثبت می‌شود.",
    )
    cancel_before_hours = models.PositiveSmallIntegerField(
        "حداقل فاصله لغو (ساعت)",
        default=24,
    )
    allow_customer_cancel = models.BooleanField("لغو توسط مشتری", default=False)
    allow_customer_lookup = models.BooleanField("جستجوی نوبت توسط مشتری", default=True)
    max_bookings_per_phone_per_day = models.PositiveSmallIntegerField(
        "حداکثر نوبت روزانه هر شماره",
        default=3,
    )
    default_booking_lead_hours = models.PositiveSmallIntegerField(
        "پیش‌فرض فاصله تا نوبت (ساعت)",
        default=2,
        help_text="برای سرویس‌هایی که مقدار خاص ندارند.",
    )
    default_booking_window_days = models.PositiveSmallIntegerField(
        "پیش‌فرض بازه رزرو (روز)",
        default=45,
    )
    staff_notification_email = models.EmailField("ایمیل اطلاع‌رسانی", blank=True)
    cancellation_policy_text = models.TextField("متن قوانین لغو", blank=True)
    confirmation_message = models.CharField("پیام تأیید", max_length=300, blank=True)
    pending_message = models.CharField("پیام در انتظار", max_length=300, blank=True)

    class Meta:
        verbose_name = "تنظیمات رزرو"
        verbose_name_plural = "تنظیمات رزرو"

    def __str__(self) -> str:
        return f"Booking settings ({self.key})"
