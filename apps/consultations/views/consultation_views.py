"""Page + JSON API for pre-visit consultation guides."""

from __future__ import annotations

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from django.conf import settings

from apps.core.exceptions import DomainError, NotFoundError, ValidationError
from apps.core.services import SeoService
from apps.core.services.page_content_service import PageContentService

from apps.consultations.services import ConsultationService


def _json_error(exc: Exception, status: int = 400) -> JsonResponse:
    message = getattr(exc, "message", None) or str(exc) or "خطایی رخ داد."
    return JsonResponse({"ok": False, "error": message}, status=status)


def _status_for(exc: Exception) -> int:
    if isinstance(exc, NotFoundError):
        return 404
    if isinstance(exc, ValidationError):
        return 400
    if isinstance(exc, DomainError):
        return 400
    return 500


class ConsultationHubView(View):
    template_name = "consultations/hub.html"

    def get(self, request):
        seo = SeoService()
        payload = ConsultationService().list_categories()
        hub = payload.get("hub") or {}
        page_content = PageContentService().get("consultations")
        page_seo = seo.consultation_hub_meta(hub)
        schema = seo.breadcrumb_schema(
            [
                {"name": "خانه", "path": "/"},
                {"name": "مشاوره", "path": "/consultations/"},
            ],
            request,
        )
        return render(
            request,
            self.template_name,
            {
                "api_base": "/consultations/api",
                "page_seo": page_seo,
                "page_content": page_content,
                "schema_json": seo.dumps(schema),
            },
        )


class ConsultationDetailView(View):
    template_name = "consultations/detail.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, key):
        seo = SeoService()
        site = getattr(settings, "SITE_NAME", "صالح ایوبی")
        try:
            detail = ConsultationService().get_category_detail(key)
            category = detail["category"]
            page_seo = seo.consultation_detail_meta(category)
            schemas = [
                seo.breadcrumb_schema(
                    [
                        {"name": "خانه", "path": "/"},
                        {"name": "مشاوره", "path": "/consultations/"},
                        {
                            "name": category.get("title") or "راهنما",
                            "path": f"/consultations/{key}/",
                        },
                    ],
                    request,
                ),
            ]
            faq_schema = seo.faq_schema(detail.get("faqs") or [])
            if faq_schema:
                schemas.append(faq_schema)
            schema_json = seo.dumps(schemas)
        except DomainError:
            page_seo = {
                "title": f"راهنما | {site}",
                "description": f"راهنمای تخصصی قبل از مراجعه در {site}",
                "og_title": f"راهنما | {site}",
                "og_description": f"راهنمای تخصصی قبل از مراجعه در {site}",
            }
            schema_json = ""

        return render(
            request,
            self.template_name,
            {
                "category_key": key,
                "api_base": "/consultations/api",
                "ticket_url": "/consultations/api/tickets/",
                "from_booking": request.GET.get("from") == "booking",
                "booking_service": request.GET.get("service", ""),
                "page_seo": page_seo,
                "schema_json": schema_json,
            },
        )


class ConsultationCategoriesAPIView(View):
    def get(self, request):
        try:
            payload = ConsultationService().list_categories()
            return JsonResponse({"ok": True, **payload})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class ConsultationDetailAPIView(View):
    def get(self, request, key):
        try:
            data = ConsultationService().get_category_detail(
                key,
                q=request.GET.get("q", ""),
                group=request.GET.get("group", ""),
                highlights=request.GET.get("highlights") in ("1", "true", "yes"),
            )
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class ConsultationBookingSummaryAPIView(View):
    """Highlights + alerts for a booking service_key (used in confirm step)."""

    def get(self, request, service_key):
        try:
            summary = ConsultationService().get_booking_summary(service_key)
            if summary is None:
                return JsonResponse(
                    {
                        "ok": True,
                        "summary": None,
                        "acknowledgment_required": False,
                        "gate_required": False,
                    }
                )
            return JsonResponse({"ok": True, "summary": summary})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class ConsultationTicketCreateAPIView(View):
    def post(self, request):
        try:
            # Support multipart (with file) and JSON
            if request.content_type and "multipart/form-data" in request.content_type:
                payload = request.POST
                attachment = request.FILES.get("attachment")
                appointment_id = payload.get("appointment_id") or None
                if appointment_id:
                    try:
                        appointment_id = int(appointment_id)
                    except (TypeError, ValueError):
                        appointment_id = None
                data = ConsultationService().create_ticket(
                    category_key=payload.get("category_key", ""),
                    first_name=payload.get("first_name", ""),
                    last_name=payload.get("last_name", ""),
                    phone=payload.get("phone", ""),
                    message=payload.get("message", ""),
                    booking_service_key=payload.get("booking_service_key", ""),
                    source=payload.get("source", "direct"),
                    appointment_id=appointment_id,
                    attachment=attachment,
                )
            else:
                import json

                body = json.loads(request.body.decode("utf-8") or "{}")
                data = ConsultationService().create_ticket(
                    category_key=body.get("category_key", ""),
                    first_name=body.get("first_name", ""),
                    last_name=body.get("last_name", ""),
                    phone=body.get("phone", ""),
                    message=body.get("message", ""),
                    booking_service_key=body.get("booking_service_key", ""),
                    source=body.get("source", "direct"),
                    appointment_id=body.get("appointment_id"),
                )
            return JsonResponse({"ok": True, "ticket": data}, status=201)
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))
        except Exception:
            return _json_error(ValidationError("درخواست نامعتبر است."))
