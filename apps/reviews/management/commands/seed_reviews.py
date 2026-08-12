"""
Seed review categories and editorial customer narratives.

Usage:
  python manage.py seed_reviews
"""

from __future__ import annotations

from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.reviews.models import Review, ReviewCategory

CATEGORIES = [
    {
        "key": "groom",
        "slug": "groom",
        "title": "داماد",
        "lede": "روایت دامادهایی که روز مهم‌شان را در استودیوی صالح ایوبی در اصفهان سپردند.",
        "seo_title": "نظرات آرایش داماد اصفهان",
        "seo_description": (
            "تجربه واقعی دامادها از آرایش داماد در صالح ایوبی اصفهان — "
            "آماده‌سازی کامل، آرامش سالن و نتیجه روز عقد."
        ),
        "booking_service_key": "groom",
        "consultation_category_key": "groom",
        "sort_order": 1,
    },
    {
        "key": "vip",
        "slug": "vip",
        "title": "VIP",
        "lede": "تجربه اختصاصی اصلاح VIP — زمان، دقت و فضای خصوصی استودیو.",
        "seo_title": "نظرات اصلاح VIP اصفهان",
        "seo_description": (
            "نظر مشتریان درباره اصلاح VIP در صالح ایوبی اصفهان — "
            "نوبت اختصاصی، دقت بالا و فضای آرام استودیو."
        ),
        "booking_service_key": "vip",
        "consultation_category_key": "vip",
        "sort_order": 2,
    },
    {
        "key": "skin",
        "slug": "skin",
        "title": "پوست",
        "lede": "مراقبت پوست مردانه در اصفهان؛ نتیجه آرام، روشن و بدون اغراق.",
        "seo_title": "نظرات مراقبت پوست مردانه اصفهان",
        "seo_description": (
            "تجربه فیشیال و مراقبت پوست در صالح ایوبی اصفهان — "
            "پروتکل شخصی، پوست آرام‌تر و نتیجه طبیعی."
        ),
        "booking_service_key": "skin",
        "consultation_category_key": "skin",
        "sort_order": 3,
    },
]


def _aware(year: int, month: int, day: int) -> datetime:
    return timezone.make_aware(datetime(year, month, day, 11, 0), timezone.get_current_timezone())


REVIEWS = [
    {
        "slug": "damad-aramesh-rooz-aghd",
        "category": "groom",
        "title": "آرایش داماد در اصفهان؛ روز عقد بدون عجله",
        "author_display_name": "امیرحسین ر.",
        "author_role": "داماد",
        "city": "اصفهان",
        "rating": 5,
        "service_name": "آرایش داماد",
        "visited_on": date(2026, 4, 18),
        "published_at": _aware(2026, 4, 22),
        "is_featured": True,
        "sort_order": 1,
        "seo_title": "نظر داماد: آرایش داماد در صالح ایوبی اصفهان",
        "seo_description": (
            "تجربه امیرحسین از آرایش داماد در استودیوی صالح ایوبی اصفهان — "
            "زمان‌بندی دقیق، آرامش سالن و نتیجه طبیعی برای روز عقد."
        ),
        "body": (
            "برای روز عقد دنبال سالنی در اصفهان بودم که شلوغی و عجله نداشته باشد. "
            "در صالح ایوبی از همان مشاوره اول مشخص بود مسیر کار حساب‌شده است؛ "
            "زمان نوبت، فرم چهره و استایل لباس را جداگانه بررسی کردند.\n\n"
            "روز مراجعه فضای استودیو آرام بود و هیچ مرحله‌ای سرسری انجام نشد. "
            "اصلاح، پوست و مو هماهنگ با هم پیش رفت و نتیجه در عکس‌ها طبیعی ماند؛ "
            "نه براق اغراق‌شده و نه خشک.\n\n"
            "اگر داماد هستید و می‌خواهید صبح مراسم فقط روی خودتان تمرکز کنید، "
            "این استودیو در مشتاق اول همان جایی است که باید رزرو کنید."
        ),
    },
    {
        "slug": "vip-nobaat-ekhtesasi",
        "category": "vip",
        "title": "اصلاح VIP؛ حس یک استودیوی خصوصی",
        "author_display_name": "کیان م.",
        "author_role": "مهمان VIP",
        "city": "اصفهان",
        "rating": 5,
        "service_name": "اصلاح VIP",
        "visited_on": date(2026, 3, 9),
        "published_at": _aware(2026, 3, 12),
        "is_featured": True,
        "sort_order": 2,
        "seo_title": "نظر مشتری: اصلاح VIP در صالح ایوبی",
        "seo_description": (
            "تجربه اصلاح VIP در صالح ایوبی اصفهان — نوبت اختصاصی، دقت بالا "
            "و فضایی که شبیه سالن شلوغ نیست."
        ),
        "body": (
            "اصلاح VIP را بیشتر به‌خاطر زمان اختصاصی انتخاب کردم، نه فقط عنوان. "
            "نوبت دقیقاً مال خودم بود؛ کسی پشت در منتظر نبود و گفت‌وگو درباره فرم صورت "
            "قبل از شروع تیغ انجام شد.\n\n"
            "نتیجه تمیز و دقیق بود، بدون قرمزی اضافه. بعد از کار هم مراقبت پوست کوتاهی "
            "پیشنهاد شد که همان روز اثرش را دیدم.\n\n"
            "برای کسی که در اصفهان دنبال تجربه آرام و لوکس است، این مسیر ارزش رزرو دارد."
        ),
    },
    {
        "slug": "facial-post-aram",
        "category": "skin",
        "title": "فیشیال مردانه؛ پوست آرام‌تر بدون ماسک سنگین",
        "author_display_name": "سهراب ن.",
        "author_role": "مراجعه پوست",
        "city": "اصفهان",
        "rating": 5,
        "service_name": "مراقبت پوست",
        "visited_on": date(2026, 2, 21),
        "published_at": _aware(2026, 2, 25),
        "is_featured": True,
        "sort_order": 3,
        "seo_title": "نظر مشتری: فیشیال مردانه در اصفهان",
        "seo_description": (
            "تجربه مراقبت پوست در صالح ایوبی اصفهان — پروتکل شخصی، "
            "پوست روشن‌تر و بدون حس ماسک سنگین."
        ),
        "body": (
            "پوستم معمولاً بعد از فیشیال قرمز و حساس می‌ماند. اینجا اول نوع پوست "
            "و روتین خانگی را پرسیدند و پروتکل را همان جلسه تنظیم کردند.\n\n"
            "جلسه سنگین و سوزناک نبود. همان شب پوست آرام‌تر بود و تا چند روز بعد "
            "رنگ یکدست‌تری داشتم. هیچ محصولی را بدون دلیل روی صورت نگذاشتند.\n\n"
            "اگر در اصفهان دنبال مراقبت پوست مردانه با نتیجه طبیعی هستید، این استودیو را جدی بگیرید."
        ),
    },
    {
        "slug": "damad-moshaver-gabl-az-roz",
        "category": "groom",
        "title": "مشاوره قبل از داماد، روز مراسم را ساده کرد",
        "author_display_name": "محمدجواد ک.",
        "author_role": "داماد",
        "city": "اصفهان",
        "rating": 5,
        "service_name": "آرایش داماد",
        "visited_on": date(2026, 1, 30),
        "published_at": _aware(2026, 2, 3),
        "is_featured": False,
        "sort_order": 4,
        "seo_title": "نظر داماد: مشاوره و آرایش داماد اصفهان",
        "seo_description": (
            "چطور مشاوره قبل از مراجعه در صالح ایوبی، روز عقد را بدون استرس کرد."
        ),
        "body": (
            "اول راهنمای مشاوره سایت را خواندم و بعد نوبت داماد را رزرو کردم. "
            "همان هماهنگی قبلی باعث شد روز مراسم چیزی برای حدس زدن نماند.\n\n"
            "ساعت ورود، فرم مو و حتی میزان برق پوست از قبل مشخص بود. "
            "تیم بدون عجله کار کرد و من سر وقت به محل عقد رسیدم.\n\n"
            "برای دامادهای اصفهان که برنامه فشرده دارند، این نظم از خود آرایش مهم‌تر است."
        ),
    },
    {
        "slug": "vip-daqiq-va-bi-sor-seda",
        "category": "vip",
        "title": "اصلاح دقیق، بدون شلوغی سالن",
        "author_display_name": "آرین ش.",
        "author_role": "مهمان VIP",
        "city": "اصفهان",
        "rating": 4,
        "service_name": "اصلاح VIP",
        "visited_on": date(2025, 12, 14),
        "published_at": _aware(2025, 12, 18),
        "is_featured": False,
        "sort_order": 5,
        "seo_title": "نظر اصلاح VIP صالح ایوبی اصفهان",
        "seo_description": (
            "تجربه اصلاح VIP در استودیوی صالح ایوبی — دقت بالا و فضای آرام، "
            "با نوبت رزرو قبلی."
        ),
        "body": (
            "سالن‌های شلوغ را دوست ندارم؛ برای همین VIP را انتخاب کردم. "
            "ورود با رزرو قبلی بود و فضا بیشتر شبیه استودیو بود تا آرایشگاه پررفت‌وآمد.\n\n"
            "اصلاح خط ریش خیلی دقیق انجام شد. تنها نکته این بود که برای نوبت‌های شلوغ هفته "
            "باید زودتر رزرو کرد؛ ظرفیت واقعاً محدود است.\n\n"
            "اگر کیفیت برایتان از سرعت مهم‌تر است، مسیر درستی است."
        ),
    },
    {
        "slug": "post-roshan-bedone-aghragh",
        "category": "skin",
        "title": "پوست روشن‌تر، بدون نتیجه مصنوعی",
        "author_display_name": "نیما ف.",
        "author_role": "مراجعه پوست",
        "city": "اصفهان",
        "rating": 5,
        "service_name": "مراقبت پوست",
        "visited_on": date(2025, 11, 8),
        "published_at": _aware(2025, 11, 12),
        "is_featured": False,
        "sort_order": 6,
        "seo_title": "نظر مراقبت پوست مردانه صالح ایوبی",
        "seo_description": (
            "نتیجه طبیعی فیشیال در صالح ایوبی اصفهان — روشن‌تر، آرام‌تر، بدون اغراق."
        ),
        "body": (
            "دنبال براق شدن اغراق‌شده نبودم؛ فقط می‌خواستم پوست خسته بعد از سفر "
            "به حالت عادی برگردد. توضیح دادند چه کاری همان جلسه لازم است و چه چیزی را نباید کرد.\n\n"
            "بعد از کار، پوستم آرام و کمی روشن‌تر بود. آرایش یا پوشش سنگینی روی صورت نبود "
            "و همان شب می‌شد در جمع حاضر شد.\n\n"
            "برای مراقبت پوست مردانه در اصفهان، این رویکرد شخصی را کمتر جایی دیده‌ام."
        ),
    },
    {
        "slug": "damad-ax-tabiee",
        "category": "groom",
        "title": "در عکس‌های عقد همان چهره‌ای بودم که می‌خواستم",
        "author_display_name": "حسین ع.",
        "author_role": "داماد",
        "city": "اصفهان",
        "rating": 5,
        "service_name": "آرایش داماد",
        "visited_on": date(2025, 10, 2),
        "published_at": _aware(2025, 10, 6),
        "is_featured": False,
        "sort_order": 7,
        "seo_title": "نظر داماد اصفهان: نتیجه طبیعی در عکس عقد",
        "seo_description": (
            "تجربه آرایش داماد در صالح ایوبی — استایل هماهنگ با لباس و نتیجه طبیعی در عکس."
        ),
        "body": (
            "نگران بودم آرایش داماد در عکس‌ها مصنوعی دیده شود. "
            "اینجا اول نور، رنگ پوست و یقه لباس را دیدند و بعد سراغ مو و پوست رفتند.\n\n"
            "در سالن عقد چند نفر گفتند چهره خسته نیست و در عین حال گریم‌شده هم به نظر نمی‌رسم. "
            "همان تعادل را می‌خواستم.\n\n"
            "اگر استودیوی داماد در اصفهان می‌خواهید که عکس را خراب نکند، رزرو این‌جا منطقی است."
        ),
    },
    {
        "slug": "vip-zaman-bandi",
        "category": "vip",
        "title": "نوبت VIP سر ساعت شروع شد",
        "author_display_name": "پارسا د.",
        "author_role": "مهمان VIP",
        "city": "اصفهان",
        "rating": 5,
        "service_name": "اصلاح VIP",
        "visited_on": date(2025, 9, 19),
        "published_at": _aware(2025, 9, 23),
        "is_featured": False,
        "sort_order": 8,
        "seo_title": "نظر مشتری VIP: رزرو آنلاین صالح ایوبی",
        "seo_description": (
            "رزرو آنلاین اصلاح VIP در صالح ایوبی اصفهان — شروع سر ساعت و کار بدون عجله."
        ),
        "body": (
            "رزرو را آنلاین انجام دادم و همان ساعتی که انتخاب کرده بودم کار شروع شد. "
            "این برای من از هر چیز دیگری مهم‌تر بود.\n\n"
            "در طول نوبت کسی وارد فضا نشد و تمرکز روی فرم صورت کامل بود. "
            "خروج هم با توضیح کوتاه مراقبت بعد از اصلاح همراه بود.\n\n"
            "برای جلسات کاری در اصفهان که باید مرتب و سر وقت حاضر شد، VIP انتخاب درستی است."
        ),
    },
    {
        "slug": "skin-protocol-shakhsi",
        "category": "skin",
        "title": "پروتکل پوست را برای من ساختند، نه از روی منو",
        "author_display_name": "علیرضا ب.",
        "author_role": "مراجعه پوست",
        "city": "اصفهان",
        "rating": 4,
        "service_name": "مراقبت پوست",
        "visited_on": date(2025, 8, 11),
        "published_at": _aware(2025, 8, 15),
        "is_featured": False,
        "sort_order": 9,
        "seo_title": "نظر فیشیال شخصی‌سازی‌شده در اصفهان",
        "seo_description": (
            "تجربه پروتکل پوست شخصی در صالح ایوبی اصفهان — بدون پکیج آماده و با توضیح شفاف."
        ),
        "body": (
            "قبلاً پکیج‌های آماده فیشیال را تجربه کرده بودم که برای پوست من تند بود. "
            "اینجا چند سؤال مشخص پرسیدند و همان جلسه تصمیم گرفتند چه مرحله‌ای حذف شود.\n\n"
            "نتیجه ملایم‌تر از چیزی بود که عادت داشتم؛ قرمزی کمتر و بافت یکدست‌تر. "
            "فقط انتظار داشتم روتین خانگی را کمی مفصل‌تر روی کاغذ بدهند.\n\n"
            "با این حال برای پوست حساس در اصفهان، این دقت را توصیه می‌کنم."
        ),
    },
    {
        "slug": "damad-team-hamahang",
        "category": "groom",
        "title": "مو، پوست و اصلاح داماد یک‌دست پیش رفت",
        "author_display_name": "رضا س.",
        "author_role": "داماد",
        "city": "اصفهان",
        "rating": 5,
        "service_name": "آرایش داماد",
        "visited_on": date(2025, 7, 5),
        "published_at": _aware(2025, 7, 9),
        "is_featured": False,
        "sort_order": 10,
        "seo_title": "نظر داماد: آماده‌سازی کامل در صالح ایوبی",
        "seo_description": (
            "آماده‌سازی کامل داماد در صالح ایوبی اصفهان — هماهنگی مو، پوست و اصلاح در یک نوبت."
        ),
        "body": (
            "نمی‌خواستم صبح عقد بین چند جا رفت‌وآمد کنم. "
            "اینجا مو، پوست و اصلاح در یک نوبت هماهنگ شد و هیچ بخشی جدا از بقیه دیده نمی‌شد.\n\n"
            "تیم کم‌حرف و دقیق کار کرد. زمان‌بندی طوری بود که برای عکاسی قبل از عقد هم جا ماند.\n\n"
            "اگر داماد اصفهان هستید و یک مسیر کامل می‌خواهید، رزرو این استودیو را عقب نیندازید."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed review categories and sample customer narratives"

    @transaction.atomic
    def handle(self, *args, **options):
        categories: dict[str, ReviewCategory] = {}
        for data in CATEGORIES:
            obj, _ = ReviewCategory.objects.update_or_create(
                key=data["key"],
                defaults={
                    "title": data["title"],
                    "slug": data["slug"],
                    "lede": data["lede"],
                    "seo_title": data["seo_title"],
                    "seo_description": data["seo_description"],
                    "booking_service_key": data["booking_service_key"],
                    "consultation_category_key": data["consultation_category_key"],
                    "sort_order": data["sort_order"],
                    "is_published": True,
                    "is_deleted": False,
                },
            )
            categories[data["key"]] = obj
        self.stdout.write(f"Categories seeded: {len(categories)}")

        created = 0
        updated = 0
        for data in REVIEWS:
            category = categories[data["category"]]
            defaults = {
                "title": data["title"],
                "body": data["body"],
                "author_display_name": data["author_display_name"],
                "author_role": data["author_role"],
                "city": data["city"],
                "rating": data["rating"],
                "service_name": data["service_name"],
                "visited_on": data["visited_on"],
                "status": Review.Status.PUBLISHED,
                "is_featured": data["is_featured"],
                "published_at": data["published_at"],
                "sort_order": data["sort_order"],
                "seo_title": data["seo_title"],
                "seo_description": data["seo_description"],
                "source_note": "ثبت‌شده در سالن",
                "is_deleted": False,
            }
            obj, was_created = Review.objects.update_or_create(
                category=category,
                slug=data["slug"],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Reviews seeded — created={created}, updated={updated}"
            )
        )
