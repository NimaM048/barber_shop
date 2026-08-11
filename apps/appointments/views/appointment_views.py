"""JSON API + page views for the booking wizard."""

from __future__ import annotations

import json

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie

from apps.core.exceptions import ConflictError, DomainError, NotFoundError, ValidationError
from apps.core.services import SeoService
from apps.core.services.page_content_service import PageContentService

from apps.appointments.services import AppointmentService


def _json_error(exc: Exception, status: int = 400) -> JsonResponse:
    message = getattr(exc, "message", None) or str(exc) or "خطایی رخ داد."
    return JsonResponse({"ok": False, "error": message}, status=status)


def _status_for(exc: Exception) -> int:
    if isinstance(exc, NotFoundError):
        return 404
    if isinstance(exc, ConflictError):
        return 409
    if isinstance(exc, ValidationError):
        return 400
    if isinstance(exc, DomainError):
        return 400
    return 500


class BookingPageView(View):
    """SPA-like booking wizard shell — data loaded via API."""

    template_name = "appointments/booking.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        seo = SeoService()
        preselect = request.GET.get("service", "").strip()
        page_seo = seo.booking_meta()
        booking_page = PageContentService().get("booking")
        booking_settings = AppointmentService().get_booking_settings()
        booking_ui = PageContentService().booking_ui()
        schema = seo.breadcrumb_schema(
            [
                {"name": "خانه", "path": "/"},
                {"name": "رزرو نوبت", "path": "/appointments/new/"},
            ],
            request,
        )
        return render(
            request,
            self.template_name,
            {
                "preselect_service": preselect,
                "api_base": "/appointments/api",
                "page_seo": page_seo,
                "booking_page": booking_page,
                "booking_settings": booking_settings,
                "booking_ui": booking_ui,
                "booking_ui_json": json.dumps(booking_ui, ensure_ascii=False),
                "schema_json": seo.dumps(schema),
            },
        )


class BookingServicesAPIView(View):
    def get(self, request):
        try:
            services = AppointmentService().list_bookable_services()
            return JsonResponse({"ok": True, "services": services})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class BookingServiceDetailAPIView(View):
    def get(self, request, key):
        try:
            service = AppointmentService().get_service_detail(key)
            return JsonResponse({"ok": True, "service": service})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class BookingCalendarAPIView(View):
    def get(self, request, key):
        try:
            year = request.GET.get("year")
            month = request.GET.get("month")
            data = AppointmentService().get_calendar(
                key,
                year=int(year) if year else None,
                month=int(month) if month else None,
            )
            return JsonResponse({"ok": True, **data})
        except (TypeError, ValueError):
            return _json_error(ValidationError("پارامترهای تقویم نامعتبر است."))
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class BookingSlotsAPIView(View):
    def get(self, request, key):
        day = request.GET.get("date", "").strip()
        if not day:
            return _json_error(ValidationError("پارامتر date الزامی است."))
        try:
            data = AppointmentService().get_slots(key, day)
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class BookingCreateAPIView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return _json_error(ValidationError("درخواست نامعتبر است."))

        try:
            appointment = AppointmentService().create_guest_booking(
                service_key=payload.get("service_key", ""),
                starts_at_raw=payload.get("starts_at", ""),
                first_name=payload.get("first_name", ""),
                last_name=payload.get("last_name", ""),
                phone=payload.get("phone", ""),
                notes=payload.get("notes", ""),
                guide_acknowledged=bool(payload.get("guide_acknowledged")),
            )
            data = AppointmentService().serialize_booking(appointment)
            return JsonResponse({"ok": True, "booking": data}, status=201)
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class BookingSettingsAPIView(View):
    def get(self, request):
        settings = AppointmentService().get_booking_settings()
        page = PageContentService().get("booking")
        policy = settings.get("cancellation_policy_text") or page.get("policy_text", "")
        ui = PageContentService().booking_ui()
        return JsonResponse(
            {
                "ok": True,
                "settings": {**settings, "cancellation_policy_text": policy},
                "page": page,
                "ui": ui,
            }
        )


class BookingLookupAPIView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return _json_error(ValidationError("درخواست نامعتبر است."))
        try:
            appointment = AppointmentService().lookup_guest_booking(
                payload.get("booking_code", ""),
                payload.get("phone", ""),
            )
            data = AppointmentService().serialize_booking(appointment)
            return JsonResponse({"ok": True, "booking": data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class BookingCancelAPIView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return _json_error(ValidationError("درخواست نامعتبر است."))
        try:
            appointment = AppointmentService().cancel_guest_booking(
                payload.get("booking_code", ""),
                payload.get("phone", ""),
            )
            data = AppointmentService().serialize_booking(appointment)
            return JsonResponse({"ok": True, "booking": data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


# Backward-compatible alias used by urls
AppointmentCreateView = BookingPageView
