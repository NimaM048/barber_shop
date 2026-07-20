from apps.core.services import BaseService

from ..repositories import ServiceItemRepository


class CatalogService(BaseService[ServiceItemRepository]):
    def _default_repository(self) -> ServiceItemRepository:
        return ServiceItemRepository()

    def list_active_services(self):
        return self.repository.list_active()

    def get_service(self, service_id):
        return self.repository.get_or_raise(service_id)
