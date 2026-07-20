"""
Service catalog: haircuts, beard trims, packages, etc.

Named `catalog` (not `services`) to avoid clashing with the service layer.
"""

from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedModel


class ServiceCategory(TimeStampedModel, SoftDeleteModel):
    name = models.CharField("نام", max_length=100)
    slug = models.SlugField("اسلاگ", unique=True, allow_unicode=True)
    description = models.TextField("توضیحات", blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "دسته‌بندی خدمت"
        verbose_name_plural = "دسته‌بندی خدمات"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class ServiceItem(TimeStampedModel, SoftDeleteModel):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="دسته‌بندی",
        null=True,
        blank=True,
    )
    name = models.CharField("نام خدمت", max_length=150)
    slug = models.SlugField("اسلاگ", unique=True, allow_unicode=True)
    description = models.TextField("توضیحات", blank=True)
    duration_minutes = models.PositiveSmallIntegerField("مدت (دقیقه)", default=30)
    price = models.DecimalField("قیمت", max_digits=12, decimal_places=0)
    is_active = models.BooleanField("فعال", default=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "خدمت"
        verbose_name_plural = "خدمات"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name
