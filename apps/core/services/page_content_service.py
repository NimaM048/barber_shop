"""Per-page content service."""

from __future__ import annotations

import copy

from apps.core.page_content import PageContent

CATALOG_JSON_DEFAULTS = {
    "assurance": ["انتخاب آگاهانه", "زمان‌بندی شفاف", "رزرو آنلاین"],
    "side_kicker": "مسیر اختصاصی شما",
    "side_copy": "خدمت مناسب را انتخاب کنید؛ زمان دلخواهتان را در مرحلهٔ بعد می‌بینید.",
    "side_cta_kicker": "شروع در کمتر از یک دقیقه",
    "side_cta_label": "شروع رزرو",
    "journey": [
        {"num": "۰۱", "label": "انتخاب خدمت"},
        {"num": "۰۲", "label": "انتخاب زمان"},
        {"num": "۰۳", "label": "تأیید نهایی"},
    ],
    "menu_eyebrow": "منوی خدمات",
    "menu_intro": "هر مسیر با زمان، هزینه و امکان رزرو فوری در دسترس شماست.",
    "menu_status": "رزرو آنلاین فعال است",
    "empty_title": "هنوز خدمتی ثبت نشده است",
    "empty_copy": "سه تخصص اصلی ما: داماد، پوست و مو",
    "empty_cta": "رزرو نوبت",
}

MAGAZINE_JSON_DEFAULTS = {
    "label_en": "Magazine",
    "signals": ["دانش تخصصی", "انتخاب تحریریه", "رزرو آگاهانه"],
}

BOOKING_UI_DEFAULTS = {
    "error_fetch": "خطا در دریافت اطلاعات",
    "error_book": "خطا در ثبت رزرو",
    "success_book": "رزرو با موفقیت ثبت شد",
    "error_guide_ack": "برای ثبت نهایی باید راهنما را تأیید کنید",
    "success_copy": "اطلاعات رزرو کپی شد",
    "error_copy": "امکان کپی وجود ندارد",
    "error_form": "لطفاً اطلاعات را اصلاح کنید",
    "success_resume": "ادامه رزرو از جایی که رها کردید",
    "capacity_changed": "ظرفیت این نوبت تغییر کرده است؛ لطفاً ساعت دیگری انتخاب کنید.",
    "loading": "در حال بارگذاری…",
    "service_label_fallback": "خدمت تخصصی",
    "service_select_cta": "انتخاب",
    "step1_title": "انتخاب خدمات",
    "step1_sub": "یکی از خدمات قابل رزرو را انتخاب کنید",
    "services_empty_title": "در حال حاضر خدمتی برای رزرو فعال نیست.",
    "services_empty_copy": "لطفاً بعداً دوباره سر بزنید.",
    "services_error": "خطا در دریافت سرویس‌ها",
    "retry": "تلاش مجدد",
    "gate_back": "بازگشت به انتخاب خدمات",
    "gate_phase_1": "خدمت انتخاب شد",
    "gate_phase_2": "راهنمای اختیاری پیش از ادامه",
}

BOOKING_DEFAULTS = {
    "section_label": "رزرو آنلاین · اصفهان",
    "title": "رزرو نوبت در",
    "lede": (
        "خدمت داماد، پوست، مو یا VIP را انتخاب کنید؛ روز و ساعت مناسب را ببینید "
        "و نوبت را بدون تماس ثبت کنید."
    ),
    "assurance_1": "تأیید آنی",
    "assurance_2": "بدون نیاز به تماس",
    "status_text": "مسیر رزرو در هر مرحله قابل بازگشت است",
    "step_1_label": "خدمات",
    "step_2_label": "تاریخ",
    "step_3_label": "زمان",
    "step_4_label": "مشخصات",
    "step_5_label": "تأیید",
    "summary_empty": "هنوز سرویسی انتخاب نشده است.",
    "policy_text": "",
    "content_json": {"ui": BOOKING_UI_DEFAULTS},
}

CATALOG_DEFAULTS = {
    "section_label": "فهرست تخصص‌ها · اصفهان",
    "title": "خدمات داماد، پوست و مو",
    "lede": (
        "کاتالوگ خدمات در اصفهان — زمان، جزئیات و مسیر مناسب را ببینید، "
        "سپس نوبت را آنلاین رزرو کنید."
    ),
    "content_json": CATALOG_JSON_DEFAULTS,
}

MAGAZINE_DEFAULTS = {
    "section_label": "مجله",
    "title": "مجله زیبایی",
    "lede": "دانشنامه تخصصی داماد، پوست، مو و استایل — خواندنی، کاربردی و هم‌تراز استاندارد برند.",
    "content_json": MAGAZINE_JSON_DEFAULTS,
}

CONSULTATIONS_DEFAULTS = {
    "section_label": "راهنمای تخصصی · اصفهان",
    "title": "مشاوره قبل از مراجعه",
    "lede": "راهنمای VIP، داماد و پوست و مو — قبل از رزرو نوبت بخوانید تا نتیجه بهتری بگیرید.",
    "content_json": {
        "header_cta_kicker": "برای شروع آماده‌اید؟",
        "header_cta_label": "رزرو نوبت",
    },
}

BARBERS_DEFAULTS = {
    "section_label": "آرایشگران",
    "title": "تیم استودیو",
    "lede": "آرایشگران و متخصصان استودیو.",
    "content_json": {
        "empty_title": "هنوز آرایشگری ثبت نشده است",
        "empty_copy": "به‌زودی معرفی تیم اینجا قرار می‌گیرد.",
    },
}

REVIEWS_JSON_DEFAULTS = {
    "label_en": "Reviews",
    "signals": ["روایت واقعی", "امتیاز شفاف", "استودیوی اصفهان"],
    "empty_title": "هنوز روایتی منتشر نشده است",
    "empty_copy": "به‌زودی تجربه مشتریان اینجا قرار می‌گیرد.",
    "journey_label": "گام بعدی",
    "journey_title": "نوبت خود را با اطمینان رزرو کنید.",
    "cta_booking": "رزرو نوبت",
    "cta_consult": "راهنمای پیش از مراجعه",
    "gbp_label": "مشاهده در گوگل",
}

REVIEWS_DEFAULTS = {
    "section_label": "نظرات",
    "title": "روایت کسانی که به استودیو آمده‌اند",
    "lede": (
        "تجربه داماد، اصلاح VIP و مراقبت پوست در صالح ایوبی اصفهان — "
        "به زبان مشتری، با امتیاز مشخص."
    ),
    "content_json": REVIEWS_JSON_DEFAULTS,
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], val)
        elif val is not None and val != "" and val != []:
            result[key] = val
    return result


class PageContentService:
    JSON_DEFAULTS = {
        PageContent.PageKey.CATALOG: CATALOG_JSON_DEFAULTS,
        PageContent.PageKey.MAGAZINE: MAGAZINE_JSON_DEFAULTS,
        PageContent.PageKey.BOOKING: {"ui": BOOKING_UI_DEFAULTS},
        PageContent.PageKey.CONSULTATIONS: CONSULTATIONS_DEFAULTS["content_json"],
        PageContent.PageKey.BARBERS: BARBERS_DEFAULTS["content_json"],
        PageContent.PageKey.REVIEWS: REVIEWS_JSON_DEFAULTS,
    }

    DEFAULTS = {
        PageContent.PageKey.CATALOG: CATALOG_DEFAULTS,
        PageContent.PageKey.MAGAZINE: MAGAZINE_DEFAULTS,
        PageContent.PageKey.BOOKING: BOOKING_DEFAULTS,
        PageContent.PageKey.BARBERS: BARBERS_DEFAULTS,
        PageContent.PageKey.CONSULTATIONS: CONSULTATIONS_DEFAULTS,
        PageContent.PageKey.REVIEWS: REVIEWS_DEFAULTS,
    }

    def get(self, page: str) -> dict:
        defaults = copy.deepcopy(self.DEFAULTS.get(page, {}))
        json_defaults = copy.deepcopy(self.JSON_DEFAULTS.get(page, {}))
        defaults["content_json"] = json_defaults

        rec = PageContent.objects.filter(
            page=page, is_published=True, is_deleted=False
        ).first()
        if not rec:
            return defaults

        mapping = {
            "section_label": rec.section_label,
            "title": rec.title,
            "lede": rec.lede,
            "extra_label": rec.extra_label,
            "assurance_1": rec.assurance_1,
            "assurance_2": rec.assurance_2,
            "status_text": rec.status_text,
            "step_1_label": rec.step_1_label,
            "step_2_label": rec.step_2_label,
            "step_3_label": rec.step_3_label,
            "step_4_label": rec.step_4_label,
            "step_5_label": rec.step_5_label,
            "summary_empty": rec.summary_empty,
            "policy_text": rec.policy_text,
            "seo_title": rec.seo_title,
            "seo_description": rec.seo_description,
        }
        for key, val in mapping.items():
            if val:
                defaults[key] = val

        if rec.content_json:
            defaults["content_json"] = _deep_merge(
                defaults.get("content_json", {}), rec.content_json
            )
        return defaults

    def booking_ui(self) -> dict:
        page = self.get(PageContent.PageKey.BOOKING)
        return page.get("content_json", {}).get("ui", BOOKING_UI_DEFAULTS)
