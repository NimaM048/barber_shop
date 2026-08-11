"""Booking global settings service."""

from __future__ import annotations

from apps.appointments.models import BookingSettings


class BookingSettingsService:
    def get_record(self) -> BookingSettings | None:
        return BookingSettings.objects.filter(key="site", is_active=True).first()

    def payload(self) -> dict:
        rec = self.get_record()
        if not rec:
            return {
                "auto_confirm": True,
                "cancel_before_hours": 24,
                "allow_customer_cancel": False,
                "allow_customer_lookup": True,
                "max_bookings_per_phone_per_day": 3,
                "default_booking_lead_hours": 2,
                "default_booking_window_days": 45,
                "cancellation_policy_text": "",
                "confirmation_message": "نوبت شما با موفقیت ثبت شد.",
                "pending_message": "نوبت شما ثبت شد و در انتظار تأیید است.",
            }
        return {
            "auto_confirm": rec.auto_confirm,
            "cancel_before_hours": rec.cancel_before_hours,
            "allow_customer_cancel": rec.allow_customer_cancel,
            "allow_customer_lookup": rec.allow_customer_lookup,
            "max_bookings_per_phone_per_day": rec.max_bookings_per_phone_per_day,
            "default_booking_lead_hours": rec.default_booking_lead_hours,
            "default_booking_window_days": rec.default_booking_window_days,
            "cancellation_policy_text": rec.cancellation_policy_text,
            "confirmation_message": rec.confirmation_message,
            "pending_message": rec.pending_message,
            "staff_notification_email": rec.staff_notification_email,
        }
