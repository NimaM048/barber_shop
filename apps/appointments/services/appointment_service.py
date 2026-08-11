"""
Appointment booking business logic.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

import jdatetime

from apps.core.exceptions import ConflictError, ValidationError
from apps.core.services import BaseService

from ..models import (
    PYTHON_TO_WEEKDAY,
    WEEKDAY_LABELS_FA,
    Appointment,
    generate_booking_code,
)
from ..repositories import (
    AppointmentRepository,
    BookingServiceConfigRepository,
)
from .booking_settings_service import BookingSettingsService
from .slot_engine import JALALI_MONTHS, SlotEngine, format_time_fa, to_persian_digits

PHONE_RE = re.compile(r"^09\d{9}$")


class AppointmentService(BaseService[AppointmentRepository]):
    def __init__(
        self,
        repository: AppointmentRepository | None = None,
        config_repository: BookingServiceConfigRepository | None = None,
        slot_engine: SlotEngine | None = None,
    ):
        super().__init__(repository)
        self.config_repository = config_repository or BookingServiceConfigRepository()
        self.slot_engine = slot_engine or SlotEngine(appointment_repo=self.repository)
        self.booking_settings = BookingSettingsService()

    def get_booking_settings(self) -> dict:
        return self.booking_settings.payload()

    def _default_repository(self) -> AppointmentRepository:
        return AppointmentRepository()

    def list_customer_appointments(self, customer_id):
        return self.repository.list_for_customer(customer_id)

    def list_bookable_services(self) -> list[dict[str, Any]]:
        configs = self.config_repository.list_enabled()
        return [self.slot_engine.serialize_config(c) for c in configs]

    def get_service_detail(self, key: str) -> dict[str, Any]:
        config = self.config_repository.get_by_key_or_raise(key)
        return self.slot_engine.serialize_config(config)

    def get_calendar(
        self,
        key: str,
        *,
        year: int | None = None,
        month: int | None = None,
    ) -> dict[str, Any]:
        config = self.config_repository.get_by_key_or_raise(key)
        today_j = jdatetime.date.today()
        jy = year or today_j.year
        jm = month or today_j.month
        if not (1 <= jm <= 12) or jy < 1300 or jy > 1500:
            raise ValidationError("ماه یا سال تقویم نامعتبر است.")
        calendar = self.slot_engine.build_calendar_month(
            config,
            jalali_year=jy,
            jalali_month=jm,
        )
        calendar["service"] = self.slot_engine.serialize_config(config)
        return calendar

    def get_slots(self, key: str, day_iso: str) -> dict[str, Any]:
        config = self.config_repository.get_by_key_or_raise(key)
        try:
            day = datetime.strptime(day_iso, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValidationError("تاریخ نامعتبر است.") from exc

        schedule = self.slot_engine.resolve_day_schedule(config, day)
        slots = self.slot_engine.build_slots_for_day(config, day)
        jday = jdatetime.date.fromgregorian(date=day)
        weekday_key = PYTHON_TO_WEEKDAY[day.weekday()]

        return {
            "service": self.slot_engine.serialize_config(config),
            "date": day.isoformat(),
            "date_display": (
                f"{to_persian_digits(jday.day)} "
                f"{JALALI_MONTHS[jday.month]} "
                f"{to_persian_digits(jday.year)}"
            ),
            "weekday_label": WEEKDAY_LABELS_FA[weekday_key],
            "is_bookable": schedule.is_bookable,
            "reason": schedule.reason,
            "slot_duration": schedule.slot_duration,
            "capacity": schedule.capacity,
            "slots": slots,
            "available_count": sum(1 for s in slots if s["status"] == "available"),
        }

    def create_guest_booking(
        self,
        *,
        service_key: str,
        starts_at_raw: str,
        first_name: str,
        last_name: str,
        phone: str,
        notes: str = "",
        guide_acknowledged: bool = False,
    ) -> Appointment:
        config = self.config_repository.get_by_key_or_raise(service_key)

        first_name = (first_name or "").strip()
        last_name = (last_name or "").strip()
        phone = self._normalize_phone(phone)
        notes = (notes or "").strip()

        if len(first_name) < 2:
            raise ValidationError("نام باید حداقل ۲ حرف باشد.")
        if len(last_name) < 2:
            raise ValidationError("نام خانوادگی باید حداقل ۲ حرف باشد.")
        if not PHONE_RE.match(phone):
            raise ValidationError("شماره موبایل معتبر نیست (مثال: ۰۹۱۳xxxxxxx).")

        # Require guide acknowledgment when a linked consultation exists
        try:
            from apps.consultations.services import ConsultationService

            guide = ConsultationService().get_booking_summary(service_key)
            if guide and guide.get("acknowledgment_required") and not guide_acknowledged:
                raise ValidationError(
                    "برای ثبت نهایی باید راهنمای قبل از مراجعه را تأیید کنید."
                )
        except ImportError:
            pass

        starts_at = parse_datetime(starts_at_raw)
        if starts_at is None:
            raise ValidationError("زمان نوبت نامعتبر است.")
        if timezone.is_naive(starts_at):
            starts_at = timezone.make_aware(
                starts_at, timezone.get_current_timezone()
            )

        day = timezone.localtime(starts_at).date()
        slot_time = timezone.localtime(starts_at).time().replace(second=0, microsecond=0)

        slots = self.slot_engine.build_slots_for_day(config, day)
        matched = next(
            (
                s
                for s in slots
                if s["start"] == slot_time.strftime("%H:%M")
                and s["status"] == "available"
            ),
            None,
        )
        if matched is None:
            raise ConflictError("این بازه زمانی دیگر در دسترس نیست.")

        settings = self.booking_settings.payload()
        today = timezone.localdate()
        taken_today = self.repository.count_for_phone_on_day(phone=phone, day=today)
        max_daily = settings["max_bookings_per_phone_per_day"]
        if max_daily and taken_today >= max_daily:
            raise ConflictError("حداکثر نوبت روزانه برای این شماره تکمیل شده است.")

        ends_at = parse_datetime(matched["ends_at"])
        if ends_at and timezone.is_naive(ends_at):
            ends_at = timezone.make_aware(ends_at, timezone.get_current_timezone())

        with transaction.atomic():
            taken = self.repository.count_for_slot(
                config_id=config.id,
                starts_at=starts_at,
            )
            if taken >= matched["capacity"]:
                raise ConflictError("ظرفیت این نوبت تکمیل شده است.")

            initial_status = (
                Appointment.Status.CONFIRMED
                if settings["auto_confirm"]
                else Appointment.Status.PENDING
            )

            return self.repository.create(
                booking_code=generate_booking_code(),
                service=config.service,
                booking_config=config,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                starts_at=starts_at,
                ends_at=ends_at,
                notes=notes,
                guide_acknowledged=bool(guide_acknowledged),
                price_at_booking=config.service.price,
                status=initial_status,
            )

    def lookup_guest_booking(self, booking_code: str, phone: str) -> Appointment:
        phone = self._normalize_phone(phone)
        code = (booking_code or "").strip().upper()
        if not code:
            raise ValidationError("کد رزرو الزامی است.")
        settings = self.booking_settings.payload()
        if not settings["allow_customer_lookup"]:
            raise ValidationError("جستجوی نوبت در حال حاضر غیرفعال است.")
        appointment = self.repository.get_by_code_and_phone(code, phone)
        if appointment is None:
            raise ValidationError("نوبتی با این مشخصات پیدا نشد.")
        return appointment

    def cancel_guest_booking(self, booking_code: str, phone: str) -> Appointment:
        settings = self.booking_settings.payload()
        if not settings["allow_customer_cancel"]:
            raise ValidationError("لغو نوبت توسط مشتری در حال حاضر غیرفعال است.")

        appointment = self.lookup_guest_booking(booking_code, phone)
        if appointment.status in (
            Appointment.Status.CANCELLED,
            Appointment.Status.COMPLETED,
            Appointment.Status.NO_SHOW,
        ):
            raise ValidationError("این نوبت قابل لغو نیست.")

        local_start = timezone.localtime(appointment.starts_at)
        hours_until = (local_start - timezone.localtime()).total_seconds() / 3600
        if hours_until < settings["cancel_before_hours"]:
            raise ValidationError(
                f"لغو نوبت حداقل {settings['cancel_before_hours']} ساعت قبل از زمان نوبت مجاز است."
            )

        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])
        return appointment

    def serialize_booking(self, appointment: Appointment) -> dict[str, Any]:
        local_start = timezone.localtime(appointment.starts_at)
        local_end = timezone.localtime(appointment.ends_at)
        jday = jdatetime.date.fromgregorian(date=local_start.date())

        duration = (
            appointment.booking_config.slot_duration
            if appointment.booking_config_id
            else appointment.service.duration_minutes
        )

        return {
            "booking_code": appointment.booking_code,
            "booking_code_display": to_persian_digits(appointment.booking_code),
            "service_key": (
                appointment.booking_config.key if appointment.booking_config_id else ""
            ),
            "service_name": appointment.service.name,
            "first_name": appointment.first_name,
            "last_name": appointment.last_name,
            "full_name": appointment.full_name,
            "phone": appointment.phone,
            "phone_display": to_persian_digits(appointment.phone),
            "notes": appointment.notes,
            "date": local_start.date().isoformat(),
            "date_display": (
                f"{to_persian_digits(jday.day)} "
                f"{JALALI_MONTHS[jday.month]} "
                f"{to_persian_digits(jday.year)}"
            ),
            "start_time": local_start.strftime("%H:%M"),
            "end_time": local_end.strftime("%H:%M"),
            "start_time_display": format_time_fa(local_start.time()),
            "end_time_display": format_time_fa(local_end.time()),
            "duration_minutes": duration,
            "status": appointment.status,
            "price": int(appointment.price_at_booking),
        }

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        if not phone:
            return ""
        persian = "۰۱۲۳۴۵۶۷۸۹"
        english = "0123456789"
        table = str.maketrans(persian + "٠١٢٣٤٥٦٧٨٩", english + english)
        cleaned = phone.translate(table)
        cleaned = re.sub(r"[\s\-()]", "", cleaned)
        if cleaned.startswith("+98"):
            cleaned = "0" + cleaned[3:]
        if cleaned.startswith("98") and len(cleaned) == 12:
            cleaned = "0" + cleaned[2:]
        return cleaned
