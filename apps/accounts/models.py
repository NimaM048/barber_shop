"""
Custom user model for barbershop customers and staff.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "مشتری"
        BARBER = "barber", "آرایشگر"
        ADMIN = "admin", "مدیر"

    phone = models.CharField("شماره موبایل", max_length=15, blank=True, db_index=True)
    role = models.CharField(
        "نقش",
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    @property
    def is_customer(self) -> bool:
        return self.role == self.Role.CUSTOMER

    @property
    def is_barber(self) -> bool:
        return self.role == self.Role.BARBER
