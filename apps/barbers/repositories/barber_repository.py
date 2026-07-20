from apps.core.repositories import BaseRepository

from ..models import Barber, WorkingHour


class BarberRepository(BaseRepository[Barber]):
    model = Barber

    def get_queryset(self):
        return super().get_queryset().select_related("user")

    def list_active(self):
        return self.get_queryset().filter(is_active=True)


class WorkingHourRepository(BaseRepository[WorkingHour]):
    model = WorkingHour

    def list_for_barber(self, barber_id):
        return self.get_queryset().filter(barber_id=barber_id, is_active=True)
