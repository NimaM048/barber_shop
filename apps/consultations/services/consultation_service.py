"""Consultation / pre-visit guide business logic."""

from __future__ import annotations

from typing import Any

from django.utils import timezone

import jdatetime

from apps.core.services import BaseService

from ..models import ConsultationCategory, ConsultationHubPage, ConsultationTip
from ..repositories import (
    ConsultationAlertRepository,
    ConsultationCategoryRepository,
    ConsultationFAQRepository,
    ConsultationHubPageRepository,
    ConsultationTipRepository,
    TipGroupRepository,
)

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def to_fa(value) -> str:
    return str(value).translate(PERSIAN_DIGITS)


def jalali_updated(dt) -> str:
    if not dt:
        return ""
    local = timezone.localtime(dt)
    j = jdatetime.datetime.fromgregorian(datetime=local)
    months = (
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
    return f"{to_fa(j.day)} {months[j.month]} {to_fa(j.year)}"


class ConsultationService(BaseService[ConsultationCategoryRepository]):
    def __init__(
        self,
        repository: ConsultationCategoryRepository | None = None,
        tip_repo: ConsultationTipRepository | None = None,
        group_repo: TipGroupRepository | None = None,
        alert_repo: ConsultationAlertRepository | None = None,
        faq_repo: ConsultationFAQRepository | None = None,
        hub_repo: ConsultationHubPageRepository | None = None,
    ):
        super().__init__(repository)
        self.tips = tip_repo or ConsultationTipRepository()
        self.groups = group_repo or TipGroupRepository()
        self.alerts = alert_repo or ConsultationAlertRepository()
        self.faqs = faq_repo or ConsultationFAQRepository()
        self.hub_pages = hub_repo or ConsultationHubPageRepository()

    def _default_repository(self) -> ConsultationCategoryRepository:
        return ConsultationCategoryRepository()

    def list_categories(self) -> dict[str, Any]:
        result = []
        for cat in self.repository.list_enabled():
            tip_count = self.tips.list_for_category(cat.id).count()
            result.append(self._serialize_category(cat, tip_count=tip_count))
        return {
            "hub": self._serialize_hub(self.hub_pages.get_hub()),
            "categories": result,
        }

    def get_category_detail(
        self,
        key: str,
        *,
        q: str = "",
        group: str = "",
        highlights: bool = False,
    ) -> dict[str, Any]:
        cat = self.repository.get_by_key_or_raise(key)
        groups = list(self.groups.list_for_category(cat.id))
        tips_qs = self.tips.list_for_category(cat.id, highlights_only=highlights)
        if q:
            from ..repositories.consultation_repository import models_q_title_or_desc

            tips_qs = tips_qs.filter(models_q_title_or_desc(q))
        if group:
            tips_qs = tips_qs.filter(group__key=group)

        tips = list(tips_qs)
        tip_count = self.tips.list_for_category(cat.id).count()

        grouped: dict[str, dict[str, Any]] = {}
        for g in groups:
            grouped[g.key] = {
                "key": g.key,
                "title": g.title,
                "phase": g.phase,
                "phase_label": g.get_phase_display(),
                "description": g.description,
                "sort_order": g.sort_order,
                "tips": [],
            }

        ungrouped: list[dict[str, Any]] = []
        for tip in tips:
            payload = self._serialize_tip(tip)
            if tip.group_id and tip.group and tip.group.key in grouped:
                grouped[tip.group.key]["tips"].append(payload)
            else:
                ungrouped.append(payload)

        return {
            "category": self._serialize_category(cat, tip_count=tip_count),
            "groups": [g for g in grouped.values()],
            "ungrouped_tips": ungrouped,
            "alerts": [
                self._serialize_alert(a)
                for a in self.alerts.list_for_category(cat.id)
            ],
            "faqs": [
                self._serialize_faq(f) for f in self.faqs.list_for_category(cat.id)
            ],
            "filters": {
                "q": q,
                "group": group,
                "highlights": highlights,
            },
            "result_count": len(tips),
        }

    def get_booking_summary(self, service_key: str) -> dict[str, Any] | None:
        cat = self.repository.get_for_booking_service(service_key)
        if cat is None:
            return None

        highlights = list(
            self.tips.list_for_category(cat.id, highlights_only=True)[:6]
        )
        if not highlights:
            highlights = list(self.tips.list_for_category(cat.id)[:4])

        alerts = list(
            self.alerts.list_for_category(cat.id, for_booking=True)[:4]
        )

        return {
            "category": self._serialize_category(
                cat,
                tip_count=self.tips.list_for_category(cat.id).count(),
            ),
            "highlights": [self._serialize_tip(t) for t in highlights],
            "alerts": [self._serialize_alert(a) for a in alerts],
            "guide_url": f"/consultations/{cat.key}/",
            "gate_required": True,
            "gate": self._serialize_gate(cat),
            "acknowledgment_required": True,
            "acknowledgment_label": cat.acknowledgment_label,
            "acknowledgment_error": cat.acknowledgment_error,
            "confirm_guide_heading": cat.confirm_guide_heading,
            "confirm_guide_link_label": cat.confirm_guide_link_label,
        }

    def create_ticket(
        self,
        *,
        category_key: str,
        first_name: str,
        last_name: str,
        phone: str,
        message: str,
        booking_service_key: str = "",
        source: str = "direct",
        appointment_id: int | None = None,
        attachment=None,
    ):
        import re

        from apps.core.exceptions import ValidationError

        from ..models import ConsultationTicket

        cat = self.repository.get_by_key_or_raise(category_key)
        first_name = (first_name or "").strip()
        last_name = (last_name or "").strip()
        message = (message or "").strip()
        phone = self._normalize_phone(phone)

        if len(first_name) < 2:
            raise ValidationError("نام باید حداقل ۲ حرف باشد.")
        if len(last_name) < 2:
            raise ValidationError("نام خانوادگی باید حداقل ۲ حرف باشد.")
        if not re.match(r"^09\d{9}$", phone):
            raise ValidationError("شماره موبایل معتبر نیست.")
        if len(message) < 10:
            raise ValidationError("پیام باید حداقل ۱۰ کاراکتر باشد.")

        appointment = None
        if appointment_id:
            from apps.appointments.models import Appointment

            appointment = Appointment.objects.filter(pk=appointment_id).first()

        ticket = ConsultationTicket.objects.create(
            category=cat,
            booking_service_key=booking_service_key or "",
            appointment=appointment,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            message=message,
            attachment=attachment,
            source=source or "direct",
        )
        return {
            "id": ticket.id,
            "status": ticket.status,
            "category_key": cat.key,
            "booking_service_key": ticket.booking_service_key,
            "full_name": ticket.full_name,
            "phone": ticket.phone,
            "message": "تیکت شما ثبت شد. کارشناسان به‌زودی پاسخ می‌دهند.",
        }

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        import re

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

    def _serialize_hub(self, hub: ConsultationHubPage | None) -> dict[str, Any]:
        if hub is None:
            return {}
        return {
            "section_label": hub.section_label,
            "title": hub.title,
            "subtitle": hub.subtitle,
            "meta_description": hub.meta_description,
            "document_title": hub.document_title or hub.title,
            "empty_message": hub.empty_message,
            "card_cta_label": hub.card_cta_label,
            "card_stats_template": hub.card_stats_template,
        }

    def _serialize_gate(self, cat: ConsultationCategory) -> dict[str, Any]:
        return {
            "eyebrow": cat.gate_eyebrow,
            "title": cat.gate_title,
            "body": cat.gate_body,
            "primary_cta": cat.gate_primary_cta,
            "primary_desc": cat.gate_primary_desc,
            "primary_kicker": cat.gate_primary_kicker,
            "primary_cta_suffix": cat.gate_primary_cta_suffix,
            "secondary_cta": cat.gate_secondary_cta,
            "secondary_desc": cat.gate_secondary_desc,
            "first_visit_title": cat.gate_first_visit_title,
            "first_visit_body": cat.gate_first_visit_body,
        }

    def _serialize_category(
        self,
        cat: ConsultationCategory,
        *,
        tip_count: int = 0,
    ) -> dict[str, Any]:
        pdf_url = cat.pdf_guide.url if cat.pdf_guide else ""
        return {
            "key": cat.key,
            "title": cat.title,
            "short_description": cat.short_description,
            "description": cat.description,
            "card_label": cat.card_label or cat.title,
            "icon": cat.icon,
            "accent_color": cat.accent_color or "#f7f4ef",
            "image_webp": cat.image_webp,
            "image_jpg": cat.image_jpg,
            "tip_count": tip_count,
            "tip_count_display": to_fa(tip_count),
            "estimated_read_minutes": cat.estimated_read_minutes,
            "estimated_read_display": to_fa(cat.estimated_read_minutes),
            "booking_service_keys": cat.booking_service_keys or [],
            "pdf_url": pdf_url,
            "content_version": cat.content_version,
            "updated_at": cat.updated_at.isoformat() if cat.updated_at else "",
            "updated_at_display": jalali_updated(cat.updated_at),
            "sort_order": cat.sort_order,
        }

    def _serialize_tip(self, tip: ConsultationTip) -> dict[str, Any]:
        image_url = ""
        if tip.image:
            image_url = tip.image.url
        elif tip.image_static:
            image_url = tip.image_static

        return {
            "id": tip.id,
            "title": tip.title,
            "description": tip.description,
            "icon": tip.icon,
            "image": image_url,
            "group_key": tip.group.key if tip.group_id else "",
            "group_title": tip.group.title if tip.group_id else "",
            "phase": tip.group.phase if tip.group_id else "",
            "is_highlight": tip.is_highlight,
            "video_url": tip.video_url,
            "pdf_url": tip.pdf_file.url if tip.pdf_file else "",
            "audio_url": tip.audio_file.url if tip.audio_file else "",
            "external_link": tip.external_link,
            "content_version": tip.content_version,
            "read_seconds": tip.read_seconds,
            "updated_at_display": jalali_updated(tip.updated_at),
            "sort_order": tip.sort_order,
        }

    def _serialize_alert(self, alert) -> dict[str, Any]:
        return {
            "id": alert.id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "icon": alert.icon or "⚠",
            "sort_order": alert.sort_order,
        }

    def _serialize_faq(self, faq) -> dict[str, Any]:
        return {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "sort_order": faq.sort_order,
        }
