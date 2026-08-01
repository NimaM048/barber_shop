"""
Seed luxury portfolio gallery items from brand static assets.

Usage:
  python manage.py seed_portfolio
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import ServiceItem
from apps.portfolio.models import GalleryCategory, GalleryImage, GalleryItem, GalleryTag


CATEGORIES = [
    {"title": "داماد", "slug": "groom", "sort_order": 1},
    {"title": "VIP", "slug": "vip", "sort_order": 2},
    {"title": "مو", "slug": "hair", "sort_order": 3},
    {"title": "پوست", "slug": "skin", "sort_order": 4},
    {"title": "فیس", "slug": "facial", "sort_order": 5},
    {"title": "پشت صحنه", "slug": "bts", "sort_order": 6},
]

TAGS = [
    {"title": "عروسی", "slug": "wedding"},
    {"title": "استودیو", "slug": "studio"},
    {"title": "لوکس", "slug": "luxury"},
]

ITEMS = [
    {
        "title": "آماده‌سازی داماد — روز عهد",
        "subtitle": "استایل کامل برای مهم‌ترین حضور",
        "slug": "groom-ceremony",
        "description": "طراحی مو، پوست و جزئیات نهایی با استاندارد برند برای روز عروسی.",
        "category": "groom",
        "tags": ["wedding", "luxury"],
        "cover_image_static": "images/brand/hero-groom-1-hd.jpg",
        "cover_webp_static": "images/brand/hero-groom-1-hd.webp",
        "cover_lqip_static": "images/brand/hero-groom-1-lqip.jpg",
        "alt_text": "آرایش داماد — نتیجه نهایی استودیو",
        "service_slug": "groom",
        "featured": True,
        "sort_order": 1,
        "location": "اصفهان",
        "completed_at": date(2026, 3, 14),
        "problem": "نیاز به حضوری آرام، دقیق و هماهنگ با لباس و نور مراسم.",
        "solution": "پروتکل سه‌مرحله‌ای مشاوره، طراحی و اجرای نهایی در استودیو.",
        "services_text": "آرایش داماد · مراقبت پوست · فرم‌دهی مو",
        "duration_text": "۱۲۰ دقیقه",
        "result": "نتیجه‌ای ماندگار که در عکس‌ها و نور طبیعی یکدست می‌ماند.",
        "customer_review": "دقت و آرامش تیم، دقیقاً همان چیزی بود که برای آن روز می‌خواستم.",
        "has_before_after": True,
        "before_image_static": "images/brand/hero-groom-2-hd.jpg",
        "after_image_static": "images/brand/hero-groom-1-hd.jpg",
        "gallery": [
            {
                "image_static": "images/brand/hero-groom-1-hd.jpg",
                "webp_static": "images/brand/hero-groom-1-hd.webp",
                "lqip_static": "images/brand/hero-groom-1-lqip.jpg",
                "caption": "جزئیات نهایی",
                "alt_text": "جزئیات آرایش داماد",
            },
            {
                "image_static": "images/brand/hero-cinematic.jpg",
                "webp_static": "images/brand/hero-cinematic.webp",
                "caption": "نمای سینمایی",
                "alt_text": "نمای سینمایی استودیو",
            },
        ],
    },
    {
        "title": "اصلاح VIP — تجربه اختصاصی",
        "subtitle": "تمرکز کامل روی شما",
        "slug": "vip-signature",
        "description": "جلسه اختصاصی با ریتم آرام و دقت حداکثری روی فرم و بافت.",
        "category": "vip",
        "tags": ["luxury", "studio"],
        "cover_image_static": "images/brand/hero-groom-3-hd.jpg",
        "cover_webp_static": "images/brand/hero-groom-3-hd.webp",
        "cover_lqip_static": "images/brand/hero-groom-3-lqip.jpg",
        "alt_text": "اصلاح VIP در استودیو",
        "service_slug": "vip",
        "featured": True,
        "sort_order": 2,
        "location": "اصفهان",
        "completed_at": date(2026, 2, 20),
        "problem": "جست‌وجوی تجربه‌ای خصوصی بدون عجله و با جزئیات دقیق.",
        "solution": "نوبت تک‌نفره با پروتکل VIP و کنترل نور و فرم.",
        "services_text": "اصلاح VIP · استایل مو",
        "duration_text": "۹۰ دقیقه",
        "result": "فرم تمیز، بافت طبیعی و حضوری که احساس لوکس بودن می‌دهد.",
        "customer_review": "حس یک استودیوی خصوصی واقعی بود.",
        "has_before_after": False,
        "gallery": [
            {
                "image_static": "images/brand/hero-groom-3-hd.jpg",
                "webp_static": "images/brand/hero-groom-3-hd.webp",
                "lqip_static": "images/brand/hero-groom-3-lqip.jpg",
                "caption": "نتیجه VIP",
                "alt_text": "نتیجه اصلاح VIP",
            },
        ],
    },
    {
        "title": "طراحی مو — معماری فرم",
        "subtitle": "فرم‌دهی با استاندارد برند",
        "slug": "hair-architecture",
        "description": "استایل مو بر اساس فرم چهره، بافت و هویت بصری شما.",
        "category": "hair",
        "tags": ["studio"],
        "cover_image_static": "images/brand/hero-groom-2-hd.jpg",
        "cover_webp_static": "images/brand/hero-groom-2-hd.webp",
        "cover_lqip_static": "images/brand/hero-groom-2-lqip.jpg",
        "alt_text": "طراحی تخصصی مو",
        "service_slug": "skin",
        "featured": False,
        "sort_order": 3,
        "location": "اصفهان",
        "completed_at": date(2026, 1, 28),
        "problem": "استایل قبلی با فرم چهره هماهنگ نبود.",
        "solution": "بازطراحی خطوط و حجم با تمرکز روی تعادل بصری.",
        "services_text": "طراحی مو · فرم‌دهی",
        "duration_text": "۶۰ دقیقه",
        "result": "فرمی که هم در روزمره و هم در عکس‌ها ماندگار است.",
        "customer_review": "",
        "has_before_after": True,
        "before_image_static": "images/brand/hero-groom-3-hd.jpg",
        "after_image_static": "images/brand/hero-groom-2-hd.jpg",
        "gallery": [
            {
                "image_static": "images/brand/hero-groom-2-hd.jpg",
                "webp_static": "images/brand/hero-groom-2-hd.webp",
                "lqip_static": "images/brand/hero-groom-2-lqip.jpg",
                "caption": "فرم نهایی",
                "alt_text": "فرم نهایی مو",
            },
        ],
    },
    {
        "title": "مراقبت پوست — درخشش آرام",
        "subtitle": "پروتکل اختصاصی استودیو",
        "slug": "skin-glow",
        "description": "مراقبت پوست با تمرکز روی بافت، شفافیت و آماده‌سازی برای مناسبت.",
        "category": "skin",
        "tags": ["luxury"],
        "cover_image_static": "images/brand/hero-cinematic.jpg",
        "cover_webp_static": "images/brand/hero-cinematic.webp",
        "cover_lqip_static": "images/brand/hero-groom-1-lqip.jpg",
        "alt_text": "مراقبت تخصصی پوست",
        "service_slug": "skin",
        "featured": False,
        "sort_order": 4,
        "location": "اصفهان",
        "completed_at": date(2025, 12, 10),
        "problem": "پوست خسته و ناهمگون قبل از یک رویداد مهم.",
        "solution": "پروتکل آرامش‌محور با لایه‌بندی مراقبت و فینیش طبیعی.",
        "services_text": "مراقبت پوست · فیس",
        "duration_text": "۷۵ دقیقه",
        "result": "بافت یکدست‌تر و درخششی که مصنوعی به‌نظر نمی‌رسد.",
        "customer_review": "پوستم آرام‌تر و روشن‌تر شد؛ بدون حس ماسک.",
        "has_before_after": False,
        "gallery": [
            {
                "image_static": "images/brand/hero-cinematic.jpg",
                "webp_static": "images/brand/hero-cinematic.webp",
                "lqip_static": "images/brand/hero-groom-1-lqip.jpg",
                "caption": "نتیجه مراقبت پوست",
                "alt_text": "نتیجه مراقبت پوست استودیو",
            },
        ],
    },
    {
        "title": "فیس — جزئیات دقیق",
        "subtitle": "تمرکز روی بافت و خطوط",
        "slug": "facial-detail",
        "description": "جلسه فیس با دقت روی جزئیاتی که در نور نزدیک دیده می‌شوند.",
        "category": "facial",
        "tags": ["studio", "luxury"],
        "cover_image_static": "images/brand/hero-cinematic.jpg",
        "cover_webp_static": "images/brand/hero-cinematic.webp",
        "cover_lqip_static": "images/brand/hero-groom-1-lqip.jpg",
        "alt_text": "جلسه فیس استودیو",
        "service_slug": "skin",
        "featured": False,
        "sort_order": 5,
        "location": "اصفهان",
        "completed_at": date(2026, 4, 2),
        "problem": "",
        "solution": "",
        "services_text": "فیس · مراقبت پوست",
        "duration_text": "۴۵ دقیقه",
        "result": "پایانی تمیز و طبیعی برای پوست.",
        "customer_review": "",
        "has_before_after": False,
        "gallery": [],
    },
    {
        "title": "پشت صحنه استودیو",
        "subtitle": "فضای کار و معماری زیبایی",
        "slug": "studio-bts",
        "description": "نگاهی به فضای استودیو، نور و ریتم کاری پشت هر نتیجه.",
        "category": "bts",
        "tags": ["studio"],
        "cover_image_static": "images/brand/hero-groom-1-hd.jpg",
        "cover_webp_static": "images/brand/hero-groom-1-hd.webp",
        "cover_lqip_static": "images/brand/hero-groom-1-lqip.jpg",
        "alt_text": "پشت صحنه استودیو صالح ایوبی",
        "service_slug": None,
        "featured": False,
        "sort_order": 6,
        "location": "اصفهان",
        "completed_at": None,
        "problem": "",
        "solution": "",
        "services_text": "",
        "duration_text": "",
        "result": "هر نتیجه از یک فرآیند دقیق ساخته می‌شود.",
        "customer_review": "",
        "has_before_after": False,
        "gallery": [
            {
                "image_static": "images/brand/hero-groom-2-hd.jpg",
                "webp_static": "images/brand/hero-groom-2-hd.webp",
                "lqip_static": "images/brand/hero-groom-2-lqip.jpg",
                "caption": "جزئیات اجرا",
                "alt_text": "جزئیات اجرای استودیو",
            },
            {
                "image_static": "images/brand/hero-groom-3-hd.jpg",
                "webp_static": "images/brand/hero-groom-3-hd.webp",
                "lqip_static": "images/brand/hero-groom-3-lqip.jpg",
                "caption": "نتیجه نهایی",
                "alt_text": "نتیجه نهایی استودیو",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed portfolio gallery categories, tags, and items"

    @transaction.atomic
    def handle(self, *args, **options):
        cat_map = {}
        for data in CATEGORIES:
            cat, _ = GalleryCategory.all_objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "sort_order": data["sort_order"],
                    "is_active": True,
                    "is_deleted": False,
                },
            )
            cat_map[data["slug"]] = cat

        tag_map = {}
        for data in TAGS:
            tag, _ = GalleryTag.objects.update_or_create(
                slug=data["slug"],
                defaults={"title": data["title"]},
            )
            tag_map[data["slug"]] = tag

        created = 0
        updated = 0
        for data in ITEMS:
            service = None
            if data.get("service_slug"):
                service = ServiceItem.objects.filter(slug=data["service_slug"]).first()

            item, was_created = GalleryItem.all_objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "subtitle": data["subtitle"],
                    "description": data["description"],
                    "category": cat_map.get(data["category"]),
                    "cover_image_static": data["cover_image_static"],
                    "cover_webp_static": data.get("cover_webp_static", ""),
                    "cover_lqip_static": data.get("cover_lqip_static", ""),
                    "alt_text": data["alt_text"],
                    "has_before_after": data.get("has_before_after", False),
                    "before_image_static": data.get("before_image_static", ""),
                    "after_image_static": data.get("after_image_static", ""),
                    "problem": data.get("problem", ""),
                    "solution": data.get("solution", ""),
                    "services_text": data.get("services_text", ""),
                    "duration_text": data.get("duration_text", ""),
                    "result": data.get("result", ""),
                    "customer_review": data.get("customer_review", ""),
                    "location": data.get("location", ""),
                    "completed_at": data.get("completed_at"),
                    "is_published": True,
                    "is_featured": data.get("featured", False),
                    "sort_order": data["sort_order"],
                    "related_service": service,
                    "is_deleted": False,
                },
            )
            item.tags.set([tag_map[s] for s in data.get("tags", []) if s in tag_map])

            item.images.all().delete()
            for i, g in enumerate(data.get("gallery", [])):
                GalleryImage.objects.create(
                    item=item,
                    image_static=g.get("image_static", ""),
                    webp_static=g.get("webp_static", ""),
                    lqip_static=g.get("lqip_static", ""),
                    caption=g.get("caption", ""),
                    alt_text=g.get("alt_text", ""),
                    sort_order=i,
                )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Portfolio seeded — categories={len(cat_map)}, "
                f"items created={created}, updated={updated}"
            )
        )
