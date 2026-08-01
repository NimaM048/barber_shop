from apps.core.repositories import BaseRepository

from ..models import ServiceCategory, ServiceItem


class ServiceCategoryRepository(BaseRepository[ServiceCategory]):
    model = ServiceCategory


class ServiceItemRepository(BaseRepository[ServiceItem]):
    model = ServiceItem

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "booking_config")
        )

    def list_active(self):
        return self.get_queryset().filter(is_active=True)
