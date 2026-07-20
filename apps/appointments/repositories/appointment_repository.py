"""Repositories for appointment booking domain."""

from __future__ import annotations

from datetime import date, datetime

from django.db.models import Count, Q
from django.utils import timezone

from apps.core.repositories import BaseRepository

from ..models import (
    Appointment,
    BookingBreak,
    BookingHoliday,
    BookingServiceConfig,
    BookingSpecialDate,
    DisabledTimeSlot,
)


class BookingServiceConfigRepository(BaseRepository[BookingServiceConfig]):
    model = BookingServiceConfig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("service", "service__category")
            .prefetch_related("breaks")
        )

    def list_enabled(self):
        return (
            self.get_queryset()
            .filter(enabled=True, service__is_active=True)
            .order_by("sort_order", "key")
        )

    def get_by_key(self, key: str) -> BookingServiceConfig | None:
        try:
            return self.get_queryset().get(key=key, enabled=True)
        except BookingServiceConfig.DoesNotExist:
            return None

    def get_by_key_or_raise(self, key: str) -> BookingServiceConfig:
        from apps.core.exceptions import NotFoundError

        config = self.get_by_key(key)
        if config is None:
            raise NotFoundError("این سرویس رزرو در دسترس نیست.")
        return config


class BookingHolidayRepository(BaseRepository[BookingHoliday]):
    model = BookingHoliday

    def list_for_range(
        self,
        *,
        start: date,
        end: date,
        config_id: int | None = None,
    ):
        qs = self.get_queryset().filter(
            date__gte=start,
            date__lte=end,
            is_closed=True,
        )
        return qs.filter(Q(config_id=config_id) | Q(config__isnull=True))


class BookingSpecialDateRepository(BaseRepository[BookingSpecialDate]):
    model = BookingSpecialDate

    def get_for_date(self, config_id: int, day: date) -> BookingSpecialDate | None:
        return self.get_queryset().filter(config_id=config_id, date=day).first()

    def list_for_month(self, config_id: int, start: date, end: date):
        return self.get_queryset().filter(
            config_id=config_id,
            date__gte=start,
            date__lte=end,
        )


class DisabledTimeSlotRepository(BaseRepository[DisabledTimeSlot]):
    model = DisabledTimeSlot

    def list_for_date(self, config_id: int, day: date):
        return self.get_queryset().filter(
            config_id=config_id,
            date=day,
            is_active=True,
        )


class BookingBreakRepository(BaseRepository[BookingBreak]):
    model = BookingBreak

    def list_active_for_config(self, config_id: int):
        return self.get_queryset().filter(config_id=config_id, is_active=True)


class AppointmentRepository(BaseRepository[Appointment]):
    model = Appointment

    ACTIVE_STATUSES = (
        Appointment.Status.PENDING,
        Appointment.Status.CONFIRMED,
    )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("customer", "barber", "service", "booking_config")
        )

    def list_for_customer(self, customer_id):
        return self.get_queryset().filter(customer_id=customer_id)

    def list_for_barber(self, barber_id):
        return self.get_queryset().filter(barber_id=barber_id)

    def list_upcoming(self):
        return self.get_queryset().filter(
            starts_at__gte=timezone.now(),
            status__in=self.ACTIVE_STATUSES,
        )

    def has_overlap(self, *, barber_id, starts_at, ends_at, exclude_id=None) -> bool:
        qs = (
            self.get_queryset()
            .filter(
                barber_id=barber_id,
                status__in=self.ACTIVE_STATUSES,
            )
            .filter(Q(starts_at__lt=ends_at) & Q(ends_at__gt=starts_at))
        )
        if exclude_id is not None:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    def count_for_slot(self, *, config_id: int, starts_at: datetime) -> int:
        return (
            self.get_queryset()
            .filter(
                booking_config_id=config_id,
                starts_at=starts_at,
                status__in=self.ACTIVE_STATUSES,
            )
            .count()
        )

    def occupancy_map_for_day(
        self,
        *,
        config_id: int,
        day_start: datetime,
        day_end: datetime,
    ) -> dict[datetime, int]:
        rows = (
            self.get_queryset()
            .filter(
                booking_config_id=config_id,
                starts_at__gte=day_start,
                starts_at__lt=day_end,
                status__in=self.ACTIVE_STATUSES,
            )
            .values("starts_at")
            .annotate(taken=Count("id"))
        )
        return {row["starts_at"]: row["taken"] for row in rows}

    def daily_booked_counts(
        self,
        *,
        config_id: int,
        range_start: datetime,
        range_end: datetime,
    ) -> dict[date, int]:
        rows = (
            self.get_queryset()
            .filter(
                booking_config_id=config_id,
                starts_at__gte=range_start,
                starts_at__lt=range_end,
                status__in=self.ACTIVE_STATUSES,
            )
            .extra(select={"day": "date(starts_at)"})
            .values("day")
            .annotate(taken=Count("id"))
        )
        result: dict[date, int] = {}
        for row in rows:
            day = row["day"]
            if isinstance(day, str):
                day = date.fromisoformat(day)
            result[day] = row["taken"]
        return result
