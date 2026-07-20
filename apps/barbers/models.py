"""
Barber staff profiles and working schedules (structure only).
"""

from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedModel


class Barber(TimeStampedModel, SoftDeleteModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="barber_profile",
        verbose_name="کاربر",
    )
    display_name = models.CharField("نام نمایشی", max_length=120)
    bio = models.TextField("بیوگرافی", blank=True)
    avatar = models.ImageField("تصویر", upload_to="barbers/", blank=True)
    is_active = models.BooleanField("فعال", default=True)
    experience_years = models.PositiveSmallIntegerField("سابقه (سال)", default=0)

    class Meta:
        verbose_name = "آرایشگر"
        verbose_name_plural = "آرایشگران"
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name


class WorkingHour(TimeStampedModel):
    class WeekDay(models.IntegerChoices):
        SATURDAY = 0, "شنبه"
        SUNDAY = 1, "یکشنبه"
        MONDAY = 2, "دوشنبه"
        TUESDAY = 3, "سه‌شنبه"
        WEDNESDAY = 4, "چهارشنبه"
        THURSDAY = 5, "پنجشنبه"
        FRIDAY = 6, "جمعه"

    barber = models.ForeignKey(
        Barber,
        on_delete=models.CASCADE,
        related_name="working_hours",
        verbose_name="آرایشگر",
    )
    weekday = models.PositiveSmallIntegerField("روز هفته", choices=WeekDay.choices)
    start_time = models.TimeField("شروع")
    end_time = models.TimeField("پایان")
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "ساعت کاری"
        verbose_name_plural = "ساعات کاری"
        ordering = ["weekday", "start_time"]
        unique_together = ("barber", "weekday", "start_time")

    def __str__(self) -> str:
        return f"{self.barber} — {self.get_weekday_display()}"
