"""Seed consultation guides for VIP, groom, and skin/hair."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.consultations.models import (
    ConsultationAlert,
    ConsultationCategory,
    ConsultationFAQ,
    ConsultationHubPage,
    ConsultationTip,
    TipGroup,
)

GATE_FIELD_KEYS = (
    "gate_eyebrow",
    "gate_title",
    "gate_body",
    "gate_primary_cta",
    "gate_primary_desc",
    "gate_primary_kicker",
    "gate_primary_cta_suffix",
    "gate_secondary_cta",
    "gate_secondary_desc",
    "gate_first_visit_title",
    "gate_first_visit_body",
    "acknowledgment_label",
    "acknowledgment_error",
    "confirm_guide_heading",
    "confirm_guide_link_label",
)


def gate_copy(**overrides: str) -> dict[str, str]:
    base = {
        "gate_eyebrow": "مشاوره قبل از رزرو",
        "gate_title": (
            "قبل از ثبت نهایی نوبت، بهتر است چند دقیقه برای دریافت مشاوره وقت بگذارید."
        ),
        "gate_body": (
            "هر فرد شرایط پوستی، مویی و سلیقه متفاوتی دارد. "
            "کارشناسان ما می‌توانند قبل از رزرو، مناسب‌ترین خدمات را به شما پیشنهاد دهند "
            "تا بهترین نتیجه را دریافت کنید."
        ),
        "gate_primary_cta": "دریافت مشاوره تخصصی",
        "gate_primary_desc": "مطالعه راهنما، نکات مهم، FAQ و ثبت تیکت برای کارشناسان",
        "gate_primary_kicker": "پیشنهادی",
        "gate_primary_cta_suffix": "ورود به مشاوره ←",
        "gate_secondary_cta": "ادامه رزرو نوبت",
        "gate_secondary_desc": (
            "اگر از سرویس موردنظر مطمئن هستید، رزرو را ادامه دهید"
        ),
        "gate_first_visit_title": "اولین بار است که از این سرویس استفاده می‌کنید؟",
        "gate_first_visit_body": (
            "پیشنهاد می‌کنیم قبل از رزرو، تنها چند دقیقه برای دریافت مشاوره تخصصی زمان بگذارید "
            "تا بهترین خدمات متناسب با شرایط شما انتخاب شود."
        ),
        "acknowledgment_label": (
            "راهنمای قبل از مراجعه را مطالعه کرده‌ام و شرایط را می‌پذیرم."
        ),
        "acknowledgment_error": "برای ثبت نهایی باید این مورد را تأیید کنید.",
        "confirm_guide_heading": "نکات مهم قبل از مراجعه",
        "confirm_guide_link_label": "مشاهده راهنمای کامل ←",
    }
    base.update(overrides)
    return base


HUB = {
    "key": "hub",
    "home_faq_enabled": True,
    "home_faq_label": "پرسش‌های پرتکرار",
    "home_faq_title": "پیش از مراجعه، پاسخ‌ها روشن‌اند.",
    "home_faq_description": "برای جزئیات هر مسیر، راهنمای مشاوره همیشه در دسترس است.",
    "home_faq_link_label": "همهٔ راهنماهای پیش از مراجعه",
    "section_label": "راهنمای تخصصی · اصفهان",
    "title": "مشاوره قبل از مراجعه",
    "subtitle": (
        "نکات، مراقبت‌ها و آمادگی‌های لازم برای داماد، پوست و VIP را بخوانید "
        "تا بهترین نتیجه را از مراجعه در اصفهان دریافت کنید."
    ),
    "meta_description": (
        "راهنمای تخصصی VIP، داماد و پوست و مو در اصفهان — آمادگی قبل از مراجعه به صالح ایوبی"
    ),
    "document_title": "مشاوره قبل از مراجعه | اصفهان",
    "empty_message": "در حال حاضر راهنمایی فعال نیست.",
    "card_cta_label": "مشاهده راهنما",
    "card_stats_template": "{tips} نکته · حدود {minutes} دقیقه",
}

CATEGORIES = [
    {
        "key": "vip",
        "title": "مشاوره VIP",
        "card_label": "مشاوره VIP",
        "short_description": "آمادگی برای تجربه اصلاح اختصاصی — پوست، فرم و سلیقه شما",
        "description": (
            "راهنمای مشاوره برای مشتریان VIP. "
            "این نکات به شما کمک می‌کند بهترین نتیجه را از جلسه اصلاح اختصاصی بگیرید."
        ),
        "icon": "👑",
        "accent_color": "#e8dfd0",
        "image_webp": "images/brand/hero-groom-1-hd.webp",
        "image_jpg": "images/brand/hero-groom-1-hd.jpg",
        "sort_order": 1,
        "estimated_read_minutes": 6,
        "booking_service_keys": ["vip"],
        "content_version": "1.0",
        **gate_copy(
            gate_title=(
                "قبل از رزرو اصلاح VIP، چند دقیقه برای مشاوره اختصاصی وقت بگذارید."
            ),
            gate_body=(
                "در سرویس VIP تمرکز روی شرایط پوست، فرم صورت و سلیقه شخصی شماست. "
                "با دریافت مشاوره کوتاه، مسیر اصلاح دقیق‌تر و نتیجه رضایت‌بخش‌تر خواهد بود."
            ),
            gate_primary_cta="دریافت مشاوره VIP",
            confirm_guide_heading="نکات مهم اصلاح VIP",
        ),
        "groups": [
            {
                "key": "before",
                "title": "قبل از مراجعه",
                "phase": "before",
                "description": "آمادگی پوست و مو پیش از جلسه VIP",
                "sort_order": 1,
            },
            {
                "key": "day",
                "title": "روز مراجعه",
                "phase": "day",
                "description": "نکات روز جلسه اصلاح اختصاصی",
                "sort_order": 2,
            },
            {
                "key": "after",
                "title": "بعد از خدمات",
                "phase": "after",
                "description": "مراقبت‌های پس از اصلاح VIP",
                "sort_order": 3,
            },
        ],
        "tips": [
            {
                "group": "before",
                "title": "وضعیت پوست را بشناسید",
                "description": (
                    "اگر پوست حساس، خشک یا مستعد التهاب دارید، قبل از جلسه اعلام کنید "
                    "تا محصولات و تکنیک متناسب انتخاب شود."
                ),
                "icon": "🧴",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 40,
            },
            {
                "group": "before",
                "title": "محصولات جدید را تست نکنید",
                "description": (
                    "۴۸ ساعت قبل، از عطر، افترشیو یا کرم‌های جدید روی صورت استفاده نکنید "
                    "تا احتمال حساسیت کمتر شود."
                ),
                "icon": "⚠",
                "is_highlight": True,
                "sort_order": 2,
                "read_seconds": 35,
            },
            {
                "group": "before",
                "title": "تصویر استایل مدنظر",
                "description": (
                    "اگر فرم ریش، خط گردن یا استایل خاصی مدنظر دارید، "
                    "۱–۲ تصویر مرجع همراه بیاورید."
                ),
                "icon": "📷",
                "is_highlight": True,
                "sort_order": 3,
                "read_seconds": 30,
            },
            {
                "group": "before",
                "title": "خواب و آب کافی",
                "description": (
                    "شب قبل خوب بخوابید و آب کافی بنوشید؛ "
                    "پوست شاداب نتیجه اصلاح را بهتر نشان می‌دهد."
                ),
                "icon": "💧",
                "sort_order": 4,
                "read_seconds": 25,
            },
            {
                "group": "day",
                "title": "صورت تمیز و بدون محصول سنگین",
                "description": (
                    "با صورت شسته و بدون ژل/واکس سنگین مراجعه کنید "
                    "تا ارزیابی و اصلاح دقیق‌تر انجام شود."
                ),
                "icon": "✨",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 30,
            },
            {
                "group": "day",
                "title": "حضور به‌موقع",
                "description": (
                    "۱۰ تا ۱۵ دقیقه زودتر بیایید تا مشاوره کوتاه ابتدای جلسه بدون عجله انجام شود."
                ),
                "icon": "⏱",
                "sort_order": 2,
                "read_seconds": 25,
            },
            {
                "group": "day",
                "title": "انتظارات را شفاف بگویید",
                "description": (
                    "میزان کوتاهی، فرم خط ریش و سبک نهایی را در ابتدای جلسه مطرح کنید."
                ),
                "icon": "🗣",
                "sort_order": 3,
                "read_seconds": 30,
            },
            {
                "group": "after",
                "title": "مراقبت ۲۴ ساعته",
                "description": (
                    "تا ۲۴ ساعت از اسکراب خشن، سونا و آفتاب شدید روی صورت پرهیز کنید."
                ),
                "icon": "🛡",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 30,
            },
            {
                "group": "after",
                "title": "مرطوب‌کننده ملایم",
                "description": (
                    "از مرطوب‌کننده سبک و بدون الکل استفاده کنید تا پوست بعد از اصلاح آرام بماند."
                ),
                "icon": "🫧",
                "sort_order": 2,
                "read_seconds": 25,
            },
        ],
        "alerts": [
            {
                "title": "اطلاع حساسیت پوستی",
                "message": "هرگونه حساسیت یا داروهای پوستی را قبل از شروع اعلام کنید.",
                "severity": "danger",
                "icon": "⚠",
                "sort_order": 1,
                "show_in_booking": True,
            },
            {
                "title": "پرهیز از محصولات جدید",
                "message": "۴۸ ساعت قبل محصولات جدید روی صورت امتحان نکنید.",
                "severity": "warning",
                "icon": "🧴",
                "sort_order": 2,
                "show_in_booking": True,
            },
            {
                "title": "مراقبت بعد از اصلاح",
                "message": "تا ۲۴ ساعت از اسکراب و آفتاب شدید خودداری کنید.",
                "severity": "info",
                "icon": "ℹ",
                "sort_order": 3,
                "show_in_booking": True,
            },
        ],
        "faqs": [
            {
                "question": "مشاوره VIP با داماد چه فرقی دارد؟",
                "answer": (
                    "مشاوره VIP مخصوص اصلاح روزمره و اختصاصی است؛ "
                    "داماد برای آمادگی مراسم و گریم روز عقد طراحی شده."
                ),
                "sort_order": 1,
            },
            {
                "question": "آیا باید ریش را از قبل اصلاح کنم؟",
                "answer": (
                    "خیر — اصلاح نهایی در جلسه انجام می‌شود تا فرم دقیق‌تر باشد."
                ),
                "sort_order": 2,
            },
            {
                "question": "اگر پوست حساس دارم چه کنم؟",
                "answer": (
                    "در رزرو یا ابتدای جلسه اعلام کنید تا محصولات سازگار انتخاب شود."
                ),
                "sort_order": 3,
            },
        ],
    },
    {
        "key": "groom",
        "title": "مشاوره داماد",
        "card_label": "مشاوره داماد",
        "short_description": "آمادگی کامل برای روز مهم — از مراقبت پوست تا زمان حضور",
        "description": (
            "راهنمای تخصصی داماد برای آرایش، گریم و اصلاح. "
            "با رعایت این نکات، نتیجه نهایی دقیق‌تر و ماندگارتر خواهد بود."
        ),
        "icon": "🤵",
        "accent_color": "#f7f4ef",
        "image_webp": "images/brand/hero-groom-1-hd.webp",
        "image_jpg": "images/brand/hero-groom-1-hd.jpg",
        "sort_order": 2,
        "estimated_read_minutes": 7,
        "booking_service_keys": ["groom"],
        "content_version": "1.0",
        **gate_copy(
            gate_title=(
                "قبل از رزرو آرایش داماد، چند دقیقه راهنمای آمادگی را ببینید."
            ),
            gate_body=(
                "روز دامادی جزئیات زیادی دارد — از اصلاح و گریم تا هماهنگی با لباس. "
                "مشاوره کوتاه کمک می‌کند بدون استرس، بهترین نتیجه را بگیرید."
            ),
            gate_primary_cta="دریافت مشاوره داماد",
            confirm_guide_heading="نکات مهم آرایش داماد",
        ),
        "groups": [
            {
                "key": "before",
                "title": "قبل از مراجعه",
                "phase": "before",
                "description": "کارهایی که روزها و ساعات قبل باید رعایت کنید",
                "sort_order": 1,
            },
            {
                "key": "day",
                "title": "روز مراجعه",
                "phase": "day",
                "description": "زمان حضور و آمادگی در روز سرویس",
                "sort_order": 2,
            },
            {
                "key": "after",
                "title": "بعد از خدمات",
                "phase": "after",
                "description": "مراقبت‌ها و محدودیت‌های پس از آرایش داماد",
                "sort_order": 3,
            },
        ],
        "tips": [
            {
                "group": "before",
                "title": "اصلاح صورت را به ما بسپارید",
                "description": (
                    "حداقل ۴۸ ساعت قبل از مراجعه، صورت خود را اصلاح نکنید. "
                    "اصلاح تازه می‌تواند پوست را تحریک کند و کیفیت گریم را کاهش دهد."
                ),
                "icon": "✂",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 40,
            },
            {
                "group": "before",
                "title": "آفتاب و سولاریوم",
                "description": (
                    "از قرار گرفتن طولانی در آفتاب یا سولاریوم در سه روز قبل خودداری کنید "
                    "تا پوست یکنواخت و بدون قرمزی باشد."
                ),
                "icon": "☀",
                "is_highlight": True,
                "sort_order": 2,
                "read_seconds": 35,
            },
            {
                "group": "before",
                "title": "آزمایش محصولات جدید",
                "description": (
                    "محصولات مراقبتی یا عطر جدید را نزدیک روز مراجعه امتحان نکنید؛ "
                    "احتمال حساسیت و التهاب وجود دارد."
                ),
                "icon": "🧴",
                "sort_order": 3,
                "read_seconds": 30,
            },
            {
                "group": "before",
                "title": "خواب کافی",
                "description": (
                    "شب قبل حداقل ۷ ساعت بخوابید. خستگی روی فرم چشم و کیفیت پوست اثر می‌گذارد."
                ),
                "icon": "🌙",
                "sort_order": 4,
                "read_seconds": 25,
            },
            {
                "group": "before",
                "title": "لباس و اکسسوری",
                "description": (
                    "کت و پیراهن نهایی را همراه داشته باشید یا رنگ و مدل یقه را مشخص کنید "
                    "تا استایل مو و گریم هماهنگ شود."
                ),
                "icon": "👔",
                "is_highlight": True,
                "sort_order": 5,
                "read_seconds": 35,
            },
            {
                "group": "day",
                "title": "زمان حضور",
                "description": (
                    "۱۵ دقیقه زودتر در محل حاضر شوید تا بدون عجله مشاوره کوتاه و آماده‌سازی انجام شود."
                ),
                "icon": "⏱",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 25,
            },
            {
                "group": "day",
                "title": "پوست تمیز و مرطوب",
                "description": (
                    "صورت را بشویید و مرطوب‌کننده سبک بزنید. از کرم‌های سنگین و براق‌کننده خودداری کنید."
                ),
                "icon": "✨",
                "sort_order": 2,
                "read_seconds": 30,
            },
            {
                "group": "day",
                "title": "مصرف کافئین و الکل",
                "description": (
                    "از مصرف زیاد قهوه و هرگونه الکل در روز مراجعه پرهیز کنید؛ "
                    "باعث کم‌آبی و تیرگی پوست می‌شود."
                ),
                "icon": "☕",
                "sort_order": 3,
                "read_seconds": 25,
            },
            {
                "group": "after",
                "title": "لمس نکردن صورت",
                "description": (
                    "تا پایان مراسم تا حد امکان صورت را لمس نکنید و از عرق کردن شدید جلوگیری کنید."
                ),
                "icon": "🤚",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 25,
            },
            {
                "group": "after",
                "title": "پاکسازی در پایان شب",
                "description": (
                    "گریم را با پاک‌کننده ملایم بردارید و پوست را مرطوب کنید. "
                    "از اسکراب خشن تا ۴۸ ساعت بعد استفاده نکنید."
                ),
                "icon": "🫧",
                "sort_order": 2,
                "read_seconds": 35,
            },
        ],
        "alerts": [
            {
                "title": "عدم اصلاح قبل از مراجعه",
                "message": "حداقل ۴۸ ساعت قبل صورت را اصلاح نکنید.",
                "severity": "danger",
                "icon": "⚠",
                "sort_order": 1,
                "show_in_booking": True,
            },
            {
                "title": "پرهیز از آفتاب شدید",
                "message": "سه روز قبل از آفتاب مستقیم و سولاریوم دوری کنید.",
                "severity": "warning",
                "icon": "☀",
                "sort_order": 2,
                "show_in_booking": True,
            },
            {
                "title": "حساسیت پوستی",
                "message": "در صورت حساسیت شناخته‌شده، حتماً قبل از شروع اطلاع دهید.",
                "severity": "info",
                "icon": "ℹ",
                "sort_order": 3,
                "show_in_booking": True,
            },
        ],
        "faqs": [
            {
                "question": "چند ساعت قبل باید بیایم؟",
                "answer": (
                    "۱۵ دقیقه زودتر کافی است. اگر تست رنگ یا مشاوره طولانی‌تر نیاز دارید، هماهنگ کنید."
                ),
                "sort_order": 1,
            },
            {
                "question": "آیا باید ریش را کامل اصلاح کنم؟",
                "answer": "خیر — اصلاح نهایی در استودیو انجام می‌شود تا فرم دقیق‌تر باشد.",
                "sort_order": 2,
            },
            {
                "question": "اگر پوست حساس دارم چه کنم؟",
                "answer": "در رزرو یا هنگام حضور اعلام کنید تا محصولات سازگار انتخاب شود.",
                "sort_order": 3,
            },
        ],
    },
    {
        "key": "skin",
        "title": "مشاوره پوست و مو",
        "card_label": "مشاوره پوست و مو",
        "short_description": "پاکسازی، فیشیال، اسکین‌کر و مراقبت قبل و بعد خدمات",
        "description": (
            "نکات تخصصی برای خدمات پوست و مو — از آمادگی قبل از فیشیال "
            "تا مراقبت‌های پس از درمان‌های زیبایی."
        ),
        "icon": "✨",
        "accent_color": "#c5d9d3",
        "image_webp": "images/brand/hero-groom-2-hd.webp",
        "image_jpg": "images/brand/hero-groom-2-hd.jpg",
        "sort_order": 3,
        "estimated_read_minutes": 8,
        "booking_service_keys": ["skin"],
        "content_version": "1.0",
        **gate_copy(
            gate_title=(
                "قبل از رزرو خدمات پوست و مو، راهنمای مراقبت را مرور کنید."
            ),
            gate_body=(
                "نتیجه فیشیال و مراقبت پوست به آمادگی قبل و بعد جلسه وابسته است. "
                "با مشاوره کوتاه، مسیر درمان مناسب‌تری انتخاب می‌کنید."
            ),
            gate_primary_cta="دریافت مشاوره پوست و مو",
            confirm_guide_heading="نکات مهم پوست و مو",
        ),
        "groups": [
            {
                "key": "before",
                "title": "قبل از مراجعه",
                "phase": "before",
                "description": "آمادگی پوست و مو پیش از پاکسازی و فیشیال",
                "sort_order": 1,
            },
            {
                "key": "day",
                "title": "روز مراجعه",
                "phase": "day",
                "description": "توصیه‌های روز سرویس",
                "sort_order": 2,
            },
            {
                "key": "after",
                "title": "بعد از خدمات",
                "phase": "after",
                "description": "مراقبت‌ها و محدودیت‌های پس از درمان",
                "sort_order": 3,
            },
        ],
        "tips": [
            {
                "group": "before",
                "title": "قطع اسکراب و لایه‌بردار",
                "description": (
                    "حداقل ۳ روز قبل از فیشیال یا پاکسازی، از اسکراب، اسید و لایه‌بردارهای قوی استفاده نکنید."
                ),
                "icon": "🛑",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 40,
            },
            {
                "group": "before",
                "title": "اصلاح یا اپیلاسیون",
                "description": (
                    "۴۸ ساعت قبل از خدمات پوست، اصلاح یا اپیلاسیون ناحیه درمان را انجام ندهید."
                ),
                "icon": "✂",
                "is_highlight": True,
                "sort_order": 2,
                "read_seconds": 35,
            },
            {
                "group": "before",
                "title": "آفتاب و برنزه",
                "description": (
                    "از برنزه کردن و آفتاب شدید یک هفته قبل خودداری کنید تا پوست برای درمان آماده باشد."
                ),
                "icon": "☀",
                "is_highlight": True,
                "sort_order": 3,
                "read_seconds": 30,
            },
            {
                "group": "before",
                "title": "داروها و محصولات تجویزی",
                "description": (
                    "اگر از رتینوئید، آنتی‌بیوتیک پوستی یا داروهای خاص استفاده می‌کنید، "
                    "قبل از رزرو اطلاع دهید."
                ),
                "icon": "💊",
                "sort_order": 4,
                "read_seconds": 40,
            },
            {
                "group": "before",
                "title": "موی تمیز برای خدمات مو",
                "description": (
                    "برای خدمات مو، با موی شسته‌شده و بدون محصولات سنگین (ژل/واکس) مراجعه کنید."
                ),
                "icon": "💇",
                "sort_order": 5,
                "read_seconds": 30,
            },
            {
                "group": "day",
                "title": "بدون آرایش سنگین",
                "description": (
                    "آرایش صورت را به حداقل برسانید یا کاملاً پاک کنید تا پاکسازی دقیق‌تر انجام شود."
                ),
                "icon": "🪞",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 25,
            },
            {
                "group": "day",
                "title": "هیدراته بمانید",
                "description": "آب کافی بنوشید و از مصرف الکل در روز مراجعه پرهیز کنید.",
                "icon": "💧",
                "sort_order": 2,
                "read_seconds": 20,
            },
            {
                "group": "day",
                "title": "عکس مرجع استایل",
                "description": (
                    "اگر استایل مو مدنظر دارید، ۲–۳ تصویر مرجع همراه بیاورید."
                ),
                "icon": "📷",
                "sort_order": 3,
                "read_seconds": 25,
            },
            {
                "group": "after",
                "title": "ضدآفتاب الزامی",
                "description": (
                    "تا ۷۲ ساعت بعد از فیشیال/پاکسازی، ضدآفتاب مناسب بزنید و از آفتاب مستقیم دوری کنید."
                ),
                "icon": "🛡",
                "is_highlight": True,
                "sort_order": 1,
                "read_seconds": 35,
            },
            {
                "group": "after",
                "title": "پرهیز از سونا و استخر",
                "description": (
                    "۴۸ ساعت از سونا، استخر کلردار و ورزش خیلی شدید خودداری کنید."
                ),
                "icon": "🏊",
                "sort_order": 2,
                "read_seconds": 30,
            },
            {
                "group": "after",
                "title": "محصولات فعال",
                "description": (
                    "۳ تا ۵ روز از اسید، رتینول و اسکراب استفاده نکنید مگر اینکه متخصص توصیه کند."
                ),
                "icon": "🧴",
                "is_highlight": True,
                "sort_order": 3,
                "read_seconds": 35,
            },
        ],
        "alerts": [
            {
                "title": "قطع لایه‌بردارها",
                "message": "۳ روز قبل اسکراب و اسیدهای قوی را متوقف کنید.",
                "severity": "danger",
                "icon": "⚠",
                "sort_order": 1,
                "show_in_booking": True,
            },
            {
                "title": "عدم آفتاب مستقیم",
                "message": "قبل و بعد از خدمات پوست، از آفتاب شدید دوری کنید.",
                "severity": "warning",
                "icon": "☀",
                "sort_order": 2,
                "show_in_booking": True,
            },
            {
                "title": "اطلاع‌رسانی حساسیت",
                "message": "حساسیت‌ها و داروهای پوستی را قبل از شروع اعلام کنید.",
                "severity": "info",
                "icon": "ℹ",
                "sort_order": 3,
                "show_in_booking": True,
            },
        ],
        "faqs": [
            {
                "question": "بعد از فیشیال پوستم قرمز می‌شود؟",
                "answer": (
                    "قرمزی خفیف طبیعی است و معمولاً طی چند ساعت تا یک روز کاهش می‌یابد."
                ),
                "sort_order": 1,
            },
            {
                "question": "آیا می‌توانم همان روز آرایش کنم؟",
                "answer": (
                    "ترجیحاً ۲۴ ساعت صبر کنید؛ اگر لازم بود فقط محصولات سبک و غیرکومدوژنیک."
                ),
                "sort_order": 2,
            },
            {
                "question": "فاصله بین جلسات پاکسازی چقدر باشد؟",
                "answer": (
                    "بسته به نوع پوست معمولاً ۳ تا ۶ هفته؛ متخصص پس از ارزیابی دقیق اعلام می‌کند."
                ),
                "sort_order": 3,
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed pre-visit consultation categories, tips, alerts, FAQs"

    @transaction.atomic
    def handle(self, *args, **options):
        ConsultationHubPage.objects.update_or_create(
            key=HUB["key"],
            defaults={
                "enabled": True,
                "section_label": HUB["section_label"],
                "title": HUB["title"],
                "subtitle": HUB["subtitle"],
                "meta_description": HUB["meta_description"],
                "document_title": HUB["document_title"],
                "empty_message": HUB["empty_message"],
                "card_cta_label": HUB["card_cta_label"],
                "card_stats_template": HUB["card_stats_template"],
                "home_faq_enabled": HUB["home_faq_enabled"],
                "home_faq_label": HUB["home_faq_label"],
                "home_faq_title": HUB["home_faq_title"],
                "home_faq_description": HUB["home_faq_description"],
                "home_faq_link_label": HUB["home_faq_link_label"],
            },
        )
        self.stdout.write("  - seeded hub page")

        for item in CATEGORIES:
            defaults = {
                "title": item["title"],
                "card_label": item["card_label"],
                "short_description": item["short_description"],
                "description": item["description"],
                "icon": item["icon"],
                "accent_color": item["accent_color"],
                "image_webp": item["image_webp"],
                "image_jpg": item["image_jpg"],
                "sort_order": item["sort_order"],
                "enabled": True,
                "estimated_read_minutes": item["estimated_read_minutes"],
                "booking_service_keys": item["booking_service_keys"],
                "content_version": item["content_version"],
            }
            for field in GATE_FIELD_KEYS:
                defaults[field] = item[field]

            cat, _ = ConsultationCategory.objects.update_or_create(
                key=item["key"],
                defaults=defaults,
            )

            group_map = {}
            for g in item["groups"]:
                group, _ = TipGroup.objects.update_or_create(
                    category=cat,
                    key=g["key"],
                    defaults={
                        "title": g["title"],
                        "phase": g["phase"],
                        "description": g["description"],
                        "sort_order": g["sort_order"],
                        "enabled": True,
                    },
                )
                group_map[g["key"]] = group

            ConsultationTip.objects.filter(category=cat).delete()
            for t in item["tips"]:
                ConsultationTip.objects.create(
                    category=cat,
                    group=group_map.get(t["group"]),
                    title=t["title"],
                    description=t["description"],
                    icon=t.get("icon", ""),
                    is_highlight=t.get("is_highlight", False),
                    sort_order=t["sort_order"],
                    enabled=True,
                    read_seconds=t.get("read_seconds", 30),
                )

            ConsultationAlert.objects.filter(category=cat).delete()
            for a in item["alerts"]:
                ConsultationAlert.objects.create(
                    category=cat,
                    title=a["title"],
                    message=a["message"],
                    severity=a["severity"],
                    icon=a.get("icon", "⚠"),
                    sort_order=a["sort_order"],
                    enabled=True,
                    show_in_booking=a.get("show_in_booking", True),
                )

            ConsultationFAQ.objects.filter(category=cat).delete()
            for f in item["faqs"]:
                ConsultationFAQ.objects.create(
                    category=cat,
                    question=f["question"],
                    answer=f["answer"],
                    sort_order=f["sort_order"],
                    enabled=True,
                )

            self.stdout.write(f"  - seeded category: {cat.key}")

        self.stdout.write(self.style.SUCCESS("Consultation guides seeded."))
