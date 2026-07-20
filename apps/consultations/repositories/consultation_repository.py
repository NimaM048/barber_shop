from apps.core.repositories import BaseRepository

from ..models import (
    ConsultationAlert,
    ConsultationCategory,
    ConsultationFAQ,
    ConsultationHubPage,
    ConsultationTip,
    TipGroup,
)


class ConsultationHubPageRepository(BaseRepository[ConsultationHubPage]):
    model = ConsultationHubPage

    def get_hub(self, key: str = "hub") -> ConsultationHubPage | None:
        try:
            return self.get_queryset().get(key=key, enabled=True)
        except ConsultationHubPage.DoesNotExist:
            return None


class ConsultationCategoryRepository(BaseRepository[ConsultationCategory]):
    model = ConsultationCategory

    def list_enabled(self):
        return self.get_queryset().filter(enabled=True).order_by("sort_order", "key")

    def get_by_key(self, key: str) -> ConsultationCategory | None:
        try:
            return self.get_queryset().get(key=key, enabled=True)
        except ConsultationCategory.DoesNotExist:
            return None

    def get_by_key_or_raise(self, key: str) -> ConsultationCategory:
        from apps.core.exceptions import NotFoundError

        cat = self.get_by_key(key)
        if cat is None:
            raise NotFoundError("این راهنما در دسترس نیست.")
        return cat

    def get_for_booking_service(self, service_key: str) -> ConsultationCategory | None:
        """Resolve guide for a booking service — prefer matching category key."""
        key = (service_key or "").strip()
        if not key:
            return None

        by_key = self.get_by_key(key)
        if by_key is not None:
            return by_key

        for cat in self.list_enabled():
            if key in (cat.booking_service_keys or []):
                return cat
        return None


class TipGroupRepository(BaseRepository[TipGroup]):
    model = TipGroup

    def list_for_category(self, category_id: int):
        return (
            self.get_queryset()
            .filter(category_id=category_id, enabled=True)
            .order_by("sort_order", "key")
        )


class ConsultationTipRepository(BaseRepository[ConsultationTip]):
    model = ConsultationTip

    def get_queryset(self):
        return super().get_queryset().select_related("category", "group")

    def list_for_category(self, category_id: int, *, highlights_only: bool = False):
        qs = self.get_queryset().filter(category_id=category_id, enabled=True)
        if highlights_only:
            qs = qs.filter(is_highlight=True)
        return qs.order_by("sort_order", "id")

    def search(self, category_id: int, query: str):
        return (
            self.list_for_category(category_id)
            .filter(models_q_title_or_desc(query))
        )


def models_q_title_or_desc(query: str):
    from django.db.models import Q

    q = (query or "").strip()
    if not q:
        return Q()
    return Q(title__icontains=q) | Q(description__icontains=q)


class ConsultationAlertRepository(BaseRepository[ConsultationAlert]):
    model = ConsultationAlert

    def list_for_category(self, category_id: int, *, for_booking: bool = False):
        qs = self.get_queryset().filter(category_id=category_id, enabled=True)
        if for_booking:
            qs = qs.filter(show_in_booking=True)
        return qs.order_by("sort_order", "id")


class ConsultationFAQRepository(BaseRepository[ConsultationFAQ]):
    model = ConsultationFAQ

    def list_for_category(self, category_id: int):
        return (
            self.get_queryset()
            .filter(category_id=category_id, enabled=True)
            .order_by("sort_order", "id")
        )
