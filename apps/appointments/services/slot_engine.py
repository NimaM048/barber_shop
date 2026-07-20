"""
Slot generation engine — all availability logic lives here.

Frontend never invents slots; it only renders what this module returns.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

import jdatetime
from django.utils import timezone

from apps.appointments.models import (
    PYTHON_TO_WEEKDAY,
    WEEKDAY_LABELS_FA,
    BookingServiceConfig,
)
from apps.appointments.repositories import (
    AppointmentRepository,
    BookingHolidayRepository,
    BookingSpecialDateRepository,
    DisabledTimeSlotRepository,
)

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

JALALI_MONTHS = (
    "",
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
)


def to_persian_digits(value: str | int) -> str:
    return str(value).translate(PERSIAN_DIGITS)


def format_time_fa(t: time) -> str:
    return to_persian_digits(f"{t.hour:02d}:{t.minute:02d}")


def _combine_local(day: date, t: time) -> datetime:
    tz = timezone.get_current_timezone()
    naive = datetime.combine(day, t)
    return timezone.make_aware(naive, tz)


def _time_overlaps(a_start: time, a_end: time, b_start: time, b_end: time) -> bool:
    return a_start < b_end and a_end > b_start


@dataclass
class DaySchedule:
    start_time: time
    end_time: time
    slot_duration: int
    capacity: int
    is_bookable: bool
    reason: str = ""


class SlotEngine:
    def __init__(
        self,
        appointment_repo: AppointmentRepository | None = None,
        holiday_repo: BookingHolidayRepository | None = None,
        special_repo: BookingSpecialDateRepository | None = None,
        disabled_repo: DisabledTimeSlotRepository | None = None,
    ):
        self.appointments = appointment_repo or AppointmentRepository()
        self.holidays = holiday_repo or BookingHolidayRepository()
        self.specials = special_repo or BookingSpecialDateRepository()
        self.disabled = disabled_repo or DisabledTimeSlotRepository()

    def resolve_day_schedule(
        self,
        config: BookingServiceConfig,
        day: date,
    ) -> DaySchedule:
        special = self.specials.get_for_date(config.id, day)
        if special and special.is_closed:
            return DaySchedule(
                start_time=config.start_time,
                end_time=config.end_time,
                slot_duration=config.slot_duration,
                capacity=config.capacity,
                is_bookable=False,
                reason="special_closed",
            )

        holiday = (
            self.holidays.list_for_range(start=day, end=day, config_id=config.id)
            .filter(is_closed=True)
            .first()
        )
        if holiday:
            return DaySchedule(
                start_time=config.start_time,
                end_time=config.end_time,
                slot_duration=config.slot_duration,
                capacity=config.capacity,
                is_bookable=False,
                reason="holiday",
            )

        weekday_key = PYTHON_TO_WEEKDAY[day.weekday()]
        working_days = config.working_days or []
        if weekday_key not in working_days:
            return DaySchedule(
                start_time=config.start_time,
                end_time=config.end_time,
                slot_duration=config.slot_duration,
                capacity=config.capacity,
                is_bookable=False,
                reason="closed_weekday",
            )

        start_t = config.start_time
        end_t = config.end_time
        duration = config.slot_duration
        capacity = config.capacity

        if special:
            if special.start_time:
                start_t = special.start_time
            if special.end_time:
                end_t = special.end_time
            if special.slot_duration:
                duration = special.slot_duration
            if special.capacity:
                capacity = special.capacity

        return DaySchedule(
            start_time=start_t,
            end_time=end_t,
            slot_duration=duration,
            capacity=capacity,
            is_bookable=True,
        )

    def generate_raw_slots(
        self,
        *,
        day: date,
        start_time: time,
        end_time: time,
        slot_duration: int,
    ) -> list[tuple[time, time]]:
        if slot_duration <= 0:
            return []

        slots: list[tuple[time, time]] = []
        cursor = datetime.combine(day, start_time)
        day_end = datetime.combine(day, end_time)
        delta = timedelta(minutes=slot_duration)

        while cursor + delta <= day_end:
            slot_start = cursor.time()
            slot_end = (cursor + delta).time()
            slots.append((slot_start, slot_end))
            cursor += delta

        return slots

    def _is_in_break(
        self,
        config: BookingServiceConfig,
        slot_start: time,
        slot_end: time,
    ) -> bool:
        for br in config.breaks.all():
            if not br.is_active:
                continue
            if _time_overlaps(slot_start, slot_end, br.start_time, br.end_time):
                return True
        return False

    def _is_disabled(
        self,
        config: BookingServiceConfig,
        day: date,
        slot_start: time,
        slot_end: time,
    ) -> bool:
        for block in self.disabled.list_for_date(config.id, day):
            if _time_overlaps(slot_start, slot_end, block.start_time, block.end_time):
                return True
        return False

    def build_slots_for_day(
        self,
        config: BookingServiceConfig,
        day: date,
    ) -> list[dict[str, Any]]:
        schedule = self.resolve_day_schedule(config, day)
        if not schedule.is_bookable:
            return []

        now = timezone.now()
        lead = timedelta(hours=config.booking_lead_hours)
        earliest = now + lead
        window_end = (now + timedelta(days=config.booking_window_days)).date()

        if day < now.date() or day > window_end:
            return []

        day_start = _combine_local(day, time.min)
        day_end = _combine_local(day + timedelta(days=1), time.min)
        occupancy = self.appointments.occupancy_map_for_day(
            config_id=config.id,
            day_start=day_start,
            day_end=day_end,
        )

        # Normalize keys to aware datetimes for lookup
        occ_by_time: dict[time, int] = {}
        for starts_at, taken in occupancy.items():
            local = timezone.localtime(starts_at)
            occ_by_time[local.time().replace(second=0, microsecond=0)] = taken

        raw = self.generate_raw_slots(
            day=day,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            slot_duration=schedule.slot_duration,
        )

        result: list[dict[str, Any]] = []
        for slot_start, slot_end in raw:
            starts_at = _combine_local(day, slot_start)
            ends_at = _combine_local(day, slot_end)

            if self._is_in_break(config, slot_start, slot_end):
                status = "disabled"
                remaining = 0
            elif self._is_disabled(config, day, slot_start, slot_end):
                status = "disabled"
                remaining = 0
            elif starts_at < earliest:
                status = "disabled"
                remaining = 0
            else:
                taken = occ_by_time.get(slot_start.replace(second=0, microsecond=0), 0)
                remaining = max(schedule.capacity - taken, 0)
                if remaining <= 0:
                    status = "reserved"
                else:
                    status = "available"

            result.append(
                {
                    "start": slot_start.strftime("%H:%M"),
                    "end": slot_end.strftime("%H:%M"),
                    "start_display": format_time_fa(slot_start),
                    "end_display": format_time_fa(slot_end),
                    "starts_at": starts_at.isoformat(),
                    "ends_at": ends_at.isoformat(),
                    "capacity": schedule.capacity,
                    "remaining": remaining,
                    "status": status,
                }
            )

        return result

    def build_calendar_month(
        self,
        config: BookingServiceConfig,
        *,
        jalali_year: int,
        jalali_month: int,
    ) -> dict[str, Any]:
        j_first = jdatetime.date(jalali_year, jalali_month, 1)
        if jalali_month == 12:
            next_month = jdatetime.date(jalali_year + 1, 1, 1)
        else:
            next_month = jdatetime.date(jalali_year, jalali_month + 1, 1)
        days_in_month = (next_month - jdatetime.timedelta(days=1)).day

        now = timezone.now()
        today = timezone.localdate()
        window_end = (now + timedelta(days=config.booking_window_days)).date()

        days: list[dict[str, Any]] = []
        for day_num in range(1, days_in_month + 1):
            jday = jdatetime.date(jalali_year, jalali_month, day_num)
            gday = jday.togregorian()
            schedule = self.resolve_day_schedule(config, gday)
            slots = self.build_slots_for_day(config, gday) if schedule.is_bookable else []
            available_count = sum(1 for s in slots if s["status"] == "available")
            total_capacity = sum(s["capacity"] for s in slots) if slots else 0
            remaining_capacity = sum(s["remaining"] for s in slots) if slots else 0

            if gday < today or gday > window_end:
                state = "past" if gday < today else "out_of_range"
                selectable = False
            elif not schedule.is_bookable:
                state = "closed"
                selectable = False
            elif available_count == 0:
                state = "full"
                selectable = False
            elif remaining_capacity <= max(total_capacity * 0.25, 1) and total_capacity > 1:
                state = "limited"
                selectable = True
            else:
                state = "available"
                selectable = True

            weekday_key = PYTHON_TO_WEEKDAY[gday.weekday()]
            days.append(
                {
                    "jalali_day": day_num,
                    "jalali_day_display": to_persian_digits(day_num),
                    "date": gday.isoformat(),
                    "weekday": weekday_key,
                    "weekday_label": WEEKDAY_LABELS_FA[weekday_key],
                    "state": state,
                    "selectable": selectable,
                    "available_slots": available_count,
                    "remaining_capacity": remaining_capacity,
                    "is_today": gday == today,
                }
            )

        # Previous / next month for navigation
        if jalali_month == 1:
            prev_y, prev_m = jalali_year - 1, 12
        else:
            prev_y, prev_m = jalali_year, jalali_month - 1

        if jalali_month == 12:
            next_y, next_m = jalali_year + 1, 1
        else:
            next_y, next_m = jalali_year, jalali_month + 1

        # First weekday of month for grid offset (Saturday = 0 in Iranian calendars)
        first_weekday_py = j_first.togregorian().weekday()
        # Convert Python Mon=0 to Sat=0 index
        iran_offset = (first_weekday_py + 2) % 7

        return {
            "year": jalali_year,
            "month": jalali_month,
            "year_display": to_persian_digits(jalali_year),
            "month_label": JALALI_MONTHS[jalali_month],
            "title": f"{JALALI_MONTHS[jalali_month]} {to_persian_digits(jalali_year)}",
            "weekdays": [WEEKDAY_LABELS_FA[k] for k in (
                "saturday", "sunday", "monday", "tuesday",
                "wednesday", "thursday", "friday",
            )],
            "offset": iran_offset,
            "days": days,
            "prev": {"year": prev_y, "month": prev_m},
            "next": {"year": next_y, "month": next_m},
        }

    def serialize_config(self, config: BookingServiceConfig) -> dict[str, Any]:
        service = config.service
        return {
            "key": config.key,
            "enabled": config.enabled,
            "name": service.name,
            "slug": service.slug,
            "description": config.short_description or service.description,
            "card_label": config.card_label,
            "duration_minutes": config.slot_duration,
            "duration_display": to_persian_digits(config.slot_duration),
            "capacity": config.capacity,
            "price": int(service.price),
            "price_display": to_persian_digits(f"{int(service.price):,}"),
            "working_days": config.working_days,
            "working_days_labels": [
                WEEKDAY_LABELS_FA.get(d, d) for d in (config.working_days or [])
            ],
            "start_time": config.start_time.strftime("%H:%M"),
            "end_time": config.end_time.strftime("%H:%M"),
            "start_time_display": format_time_fa(config.start_time),
            "end_time_display": format_time_fa(config.end_time),
            "slot_duration": config.slot_duration,
            "image_webp": config.image_webp,
            "image_jpg": config.image_jpg,
            "booking_lead_hours": config.booking_lead_hours,
            "booking_window_days": config.booking_window_days,
            "sort_order": config.sort_order,
        }
