"""
Base repository — data access only.

Rules:
- Talk to the ORM / database
- No business rules, no HTTP, no templates
- Return model instances or querysets
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from django.db import models

ModelT = TypeVar("ModelT", bound=models.Model)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD repository for a Django model."""

    model: type[ModelT]

    def get_queryset(self) -> models.QuerySet[ModelT]:
        return self.model.objects.all()

    def get_by_id(self, pk: Any) -> ModelT | None:
        try:
            return self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def get_or_raise(self, pk: Any) -> ModelT:
        from apps.core.exceptions import NotFoundError

        instance = self.get_by_id(pk)
        if instance is None:
            raise NotFoundError(f"{self.model.__name__} با شناسه {pk} یافت نشد.")
        return instance

    def list(self, **filters: Any) -> models.QuerySet[ModelT]:
        return self.get_queryset().filter(**filters)

    def create(self, **data: Any) -> ModelT:
        return self.model.objects.create(**data)

    def update(self, instance: ModelT, **data: Any) -> ModelT:
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save(update_fields=list(data.keys()) or None)
        return instance

    def delete(self, instance: ModelT) -> None:
        instance.delete()

    def exists(self, **filters: Any) -> bool:
        return self.get_queryset().filter(**filters).exists()

    def count(self, **filters: Any) -> int:
        return self.get_queryset().filter(**filters).count()
