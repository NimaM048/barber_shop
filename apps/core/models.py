"""
Shared abstract models used across domain apps.
"""

from django.db import models


class TimeStampedModel(models.Model):
    """Adds created_at / updated_at timestamps."""

    created_at = models.DateTimeField("ایجاد شده", auto_now_add=True)
    updated_at = models.DateTimeField("به‌روزرسانی", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def delete(self):
        return super().update(is_deleted=True)

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class SoftDeleteModel(models.Model):
    """Soft-delete support; default manager hides deleted rows."""

    is_deleted = models.BooleanField("حذف شده", default=False, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"] if hasattr(self, "updated_at") else ["is_deleted"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)


# Concrete CMS models (imported for Django app registry discovery)
from apps.core.brand_story import BrandStory, BrandTimelineStep, BrandValue  # noqa: E402, F401
from apps.core.footer_finale import FooterFinale, FooterNavLink  # noqa: E402, F401
