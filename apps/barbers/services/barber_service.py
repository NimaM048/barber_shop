from apps.core.services import BaseService

from ..repositories import BarberRepository


class BarberService(BaseService[BarberRepository]):
    def _default_repository(self) -> BarberRepository:
        return BarberRepository()

    def list_active_barbers(self):
        return self.repository.list_active()

    def get_barber(self, barber_id):
        return self.repository.get_or_raise(barber_id)
