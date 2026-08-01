"""Seed magazine categories, authors, tags, and sample articles."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.magazine.models import Article, MagazineAuthor, MagazineCategory, MagazineTag


CATEGORIES = [
    {
        "title": "داماد",
        "slug": "groom",
        "description": "راهنمای جامع آمادگی، استایل و مراقبت داماد",
        "sort_order": 1,
        "booking_service_keys": ["groom"],
        "consultation_category_key": "groom",
        "cta_title": "آماده دریافت مشاوره داماد هستید؟",
        "cta_consultation_label": "مشاوره تخصصی داماد",
        "cta_booking_label": "رزرو نوبت داماد",
    },
    {
        "title": "پوست",
        "slug": "skin",
        "description": "مراقبت پوست، فیشیال و روتین‌های حرفه‌ای",
        "sort_order": 2,
        "booking_service_keys": ["skin"],
        "consultation_category_key": "skin",
        "cta_title": "آماده دریافت مشاوره پوست هستید؟",
        "cta_consultation_label": "مشاوره پوست و مو",
        "cta_booking_label": "رزرو خدمات پوست",
    },
    {
        "title": "مو",
        "slug": "hair",
        "description": "اصلاح، کوتاهی، رنگ و سلامت مو",
        "sort_order": 3,
        "booking_service_keys": ["vip", "skin"],
        "consultation_category_key": "skin",
        "cta_booking_label": "رزرو خدمات مو",
    },
    {
        "title": "اصلاح",
        "slug": "shave",
        "description": "تکنیک‌ها و مراقبت‌های اصلاح حرفه‌ای",
        "sort_order": 4,
        "booking_service_keys": ["vip"],
    },
    {
        "title": "استایل",
        "slug": "style",
        "description": "ترندها و راهنمای استایل مردانه",
        "sort_order": 5,
        "booking_service_keys": ["groom", "vip"],
    },
    {
        "title": "فیشیال",
        "slug": "facial",
        "description": "انواع فیشیال و مراقبت‌های تخصصی صورت",
        "sort_order": 6,
        "booking_service_keys": ["skin"],
        "consultation_category_key": "skin",
    },
    {
        "title": "مراقبت قبل از مراجعه",
        "slug": "pre-care",
        "description": "آمادگی‌های ضروری قبل از خدمات",
        "sort_order": 7,
        "booking_service_keys": ["groom", "skin", "vip"],
        "consultation_category_key": "groom",
    },
    {
        "title": "مراقبت بعد از مراجعه",
        "slug": "after-care",
        "description": "نگهداری نتیجه خدمات پس از مراجعه",
        "sort_order": 8,
        "booking_service_keys": ["groom", "skin"],
    },
    {
        "title": "محصولات",
        "slug": "products",
        "description": "معرفی محصولات مراقبتی پیشنهادی",
        "sort_order": 9,
    },
    {
        "title": "ترندهای روز",
        "slug": "trends",
        "description": "ترندهای جهانی زیبایی مردانه",
        "sort_order": 10,
    },
    {
        "title": "آموزش",
        "slug": "education",
        "description": "آموزش‌های حرفه‌ای مراقبت و استایل",
        "sort_order": 11,
    },
    {
        "title": "اخبار",
        "slug": "news",
        "description": "اخبار و رویدادهای مجموعه",
        "sort_order": 12,
    },
    {
        "title": "معرفی خدمات",
        "slug": "services-guide",
        "description": "راهنمای انتخاب و شناخت خدمات",
        "sort_order": 13,
        "booking_service_keys": ["groom", "skin", "vip"],
    },
]

TAGS = [
    ("مراقبت پوست", "skin-care"),
    ("داماد", "groom-tag"),
    ("ریش", "beard"),
    ("کوتاهی مو", "haircut"),
    ("فیشیال", "facial-tag"),
    ("ترند ۲۰۲۶", "trend-2026"),
    ("روتین روزانه", "daily-routine"),
    ("موی چرب", "oily-hair"),
]

ARTICLES = [
    {
        "title": "راهنمای کامل آمادگی داماد؛ از سه ماه قبل تا روز مراسم",
        "subtitle": "چک‌لیست حرفه‌ای برای ظاهری بی‌نقص در مهم‌ترین روز زندگی",
        "slug": "groom-preparation-complete-guide",
        "excerpt": "آمادگی داماد فقط یک اصلاح ساده نیست؛ فرآیندی برنامه‌ریزی‌شده برای پوست، مو، ریش و استایل است که نتیجه نهایی را تعیین می‌کند.",
        "category": "groom",
        "tags": ["groom-tag", "skin-care", "daily-routine"],
        "reading_minutes": 9,
        "is_hero": True,
        "is_featured": True,
        "is_editors_pick": True,
        "display_priority": 100,
        "cover_image_static": "images/brand/hero-cinematic.jpg",
        "cover_image_alt": "آماده‌سازی حرفه‌ای داماد — اصلاح نهایی پیش از مراسم",
        "body": """
<p>روز مراسم، نقطه اوج ماه‌ها برنامه‌ریزی است. ظاهر داماد باید آرام، مرتب و هماهنگ با استایل مراسم باشد — نه عجولانه و نه تصادفی.</p>
<h2>سه ماه قبل: پایه‌گذاری مراقبت</h2>
<p>در این مرحله تمرکز روی سلامت پوست و تثبیت فرم مو است. اگر پوست حساس دارید، روتین ملایم را زودتر شروع کنید تا در روز مراسم غافلگیر نشوید.</p>
<ul>
  <li>مشاوره تخصصی پوست و مو</li>
  <li>انتخاب فرم کوتاهی متناسب با فرم صورت</li>
  <لی>تست محصولات جدید — حداقل شش هفته قبل</li>
</ul>
<div class="mag-callout"><strong>نکته کلیدی:</strong> هیچ محصول یا رنگ جدیدی را در دو هفته آخر امتحان نکنید.</div>
<h2>یک ماه قبل: تثبیت استایل</h2>
<p>جلسه آزمایشی کوتاهی و اصلاح، بهترین راه برای اطمینان از هماهنگی استایل با کت و شلوار و نور عکاسی است.</p>
<blockquote class="mag-quote">ظاهر داماد باید «طبیعیِ کامل» به نظر برسد؛ نه مصنوعی و نه فراموش‌شده.</blockquote>
<h2>هفته آخر و روز مراسم</h2>
<p>خواب کافی، آب‌رسانی پوست، و مراجعه به‌موقع برای اصلاح نهایی، سه اصل غیرقابل مذاکره هستند.</p>
<h3>چک‌لیست صبح مراسم</h3>
<ol>
  <li>شستشوی ملایم صورت</li>
  <li>مرطوب‌کننده سبک</li>
  <li>فرم‌دهی مو بدون زیاده‌روی در محصول</li>
</ol>
<p>اگر به راهنمایی شخصی‌سازی‌شده نیاز دارید، تیم مشاوره مجموعه آماده طراحی برنامه اختصاصی برای شماست.</p>
""".replace("<لی>", "<li>"),
    },
    {
        "title": "روتین مراقبت پوست مردانه در چهار قدم",
        "subtitle": "ساده، مؤثر و قابل تداوم برای پوست شهری",
        "slug": "mens-skincare-routine-four-steps",
        "excerpt": "مراقبت پوست مردانه نیازی به پیچیدگی ندارد؛ ثبات در چهار قدم پایه‌ای، تفاوت واقعی ایجاد می‌کند.",
        "category": "skin",
        "tags": ["skin-care", "daily-routine"],
        "reading_minutes": 6,
        "is_featured": True,
        "display_priority": 80,
        "cover_image_static": "images/brand/hero-groom-2-hd.jpg",
        "body": """
<p>پوست مردانه معمولاً ضخیم‌تر است و به دلیل اصلاح، بیشتر در معرض تحریک قرار می‌گیرد. روتین درست، التهاب را کم و بافت پوست را یکدست می‌کند.</p>
<h2>۱. پاکسازی</h2>
<p>شوینده ملایم صبح و شب کافی است. از اسکراب‌های خشن روزانه پرهیز کنید.</p>
<h2>۲. آبرسانی</h2>
<p>تونر الکلی پوست را خشک می‌کند؛ سرم هیالورونیک یا تونر ملایم انتخاب بهتری است.</p>
<h2>۳. مرطوب‌کننده</h2>
<p>حتی پوست چرب به مرطوب‌کننده سبک نیاز دارد تا سد دفاعی پوست حفظ شود.</p>
<h2>۴. ضدآفتاب</h2>
<p>مهم‌ترین قدم ضدپیری. در فضای باز، SPF مناسب را فراموش نکنید.</p>
<div class="mag-callout">برای انتخاب محصول متناسب با نوع پوست، مشاوره پوست مجموعه را رزرو کنید.</div>
""",
    },
    {
        "title": "ترند کوتاهی موی مردانه ۲۰۲۶",
        "subtitle": "از بافت طبیعی تا فرم‌های ساختاریافته",
        "slug": "mens-haircut-trends-2026",
        "excerpt": "امسال تعادل بین نظم و بافت طبیعی، محور استایل مو است؛ فرم‌هایی که هم رسمی می‌مانند و هم روزمره.",
        "category": "trends",
        "tags": ["trend-2026", "haircut"],
        "reading_minutes": 5,
        "is_featured": True,
        "is_editors_pick": True,
        "display_priority": 70,
        "cover_image_static": "images/brand/hero-cinematic.jpg",
        "body": """
<p>ترندهای ۲۰۲۶ از افراط فاصله گرفته‌اند. تمرکز روی تناسب با فرم صورت، بافت مو و سبک زندگی است.</p>
<h2>بافت کنترل‌شده</h2>
<p>کوتاهی‌هایی که حجم دارند اما شلخته نیستند؛ مناسب جلسات کاری و مراسم.</p>
<h2>خطوط تمیز در کناره‌ها</h2>
<p>فید نرم و خط گردن دقیق، هنوز پایه‌ی یک اصلاح حرفه‌ای است.</p>
<blockquote class="mag-quote">بهترین ترند، آن است که روی شما طبیعی به نظر برسد.</blockquote>
""",
    },
    {
        "title": "مراقبت بعد از فیشیال؛ ۷۲ ساعت طلایی",
        "subtitle": "چگونه نتیجه فیشیال را حفظ کنیم",
        "slug": "facial-aftercare-72-hours",
        "excerpt": "نتیجه فیشیال به همان اندازه که به جلسه درمان وابسته است، به مراقبت‌های بعد از آن هم بستگی دارد.",
        "category": "after-care",
        "tags": ["facial-tag", "skin-care"],
        "reading_minutes": 4,
        "is_editors_pick": True,
        "display_priority": 60,
        "cover_image_static": "images/brand/hero-groom-2-hd.jpg",
        "body": """
<p>پس از فیشیال، پوست در فاز بازسازی است. مراقبت اشتباه می‌تواند التهاب ایجاد کند.</p>
<h2>۲۴ ساعت اول</h2>
<ul>
  <لی>از آرایش و محصولات فعال (رتینول، اسید) پرهیز کنید</li>
  <li>آب فراوان بنوشید</li>
  <li>از گرمای شدید سونا و ورزش سنگین دوری کنید</li>
</ul>
<h2>تا ۷۲ ساعت</h2>
<p>ضدآفتاب و مرطوب‌کننده ملایم را جدی بگیرید. اگر قرمزی غیرعادی دیدید، با کارشناس تماس بگیرید.</p>
""".replace("<لی>", "<li>"),
    },
    {
        "title": "چگونه سرویس VIP را برای خود انتخاب کنیم؟",
        "subtitle": "راهنمای انتخاب هوشمند خدمات",
        "slug": "how-to-choose-vip-service",
        "excerpt": "انتخاب سرویس مناسب، ترکیبی از هدف زیبایی، زمان در دسترس و سطح مراقبت مورد نیاز است.",
        "category": "services-guide",
        "tags": ["haircut", "beard"],
        "reading_minutes": 5,
        "display_priority": 50,
        "cover_image_static": "images/brand/hero-cinematic.jpg",
        "cover_image_alt": "فضای آرام سالن — انتخاب هوشمند خدمات زیبایی",
        "body": """
<p>سرویس VIP برای کسانی طراحی شده که می‌خواهند در یک مراجعه، اصلاح، استایل و مراقبت را یکجا دریافت کنند.</p>
<h2>چه زمانی VIP؟</h2>
<p>اگر برای مراسم، جلسه مهم یا ریست کامل ظاهر آمده‌اید، VIP انتخاب دقیق‌تری است.</p>
<h2>تفاوت با سرویس‌های تخصصی</h2>
<p>داماد و پوست تمرکز عمقی‌تری دارند؛ VIP جامعیت و هماهنگی ظاهر را هدف می‌گیرد.</p>
""",
    },
    {
        "title": "اصلاح ریش حرفه‌ای بدون تحریک پوست",
        "subtitle": "تکنیک و مراقبت برای پوست حساس",
        "slug": "professional-beard-shave-sensitive-skin",
        "excerpt": "تحریک بعد از اصلاح معمولاً نتیجه عجله، تیغ نامناسب یا نبود مراقبت پس از اصلاح است.",
        "category": "shave",
        "tags": ["beard", "skin-care"],
        "reading_minutes": 7,
        "is_featured": True,
        "display_priority": 55,
        "cover_image_static": "images/brand/hero-groom-3-hd.jpg",
        "body": """
<p>اصلاح خوب با آماده‌سازی پوست شروع می‌شود: گرم‌کردن، رطوبت و روغن مناسب.</p>
<h2>اصول اصلاح بدون سوزش</h2>
<ol>
  <li>پوست را مرطوب و گرم کنید</li>
  <li>در جهت رشد مو اصلاح کنید</li>
  <li>فشار تیغ را به حداقل برسانید</li>
  <li>بالم یا سرم تسکین‌دهنده استفاده کنید</li>
</ol>
<div class="mag-callout">اگر پوستتان مستعد فولیکولیت است، جلسه مشاوره پوست قبل از اصلاح منظم پیشنهاد می‌شود.</div>
""",
    },
]


class Command(BaseCommand):
    help = "Seed magazine authors, categories, tags, and sample articles"

    def handle(self, *args, **options):
        author, _ = MagazineAuthor.objects.update_or_create(
            slug="saleh-ayoubi-editorial",
            defaults={
                "name": "هیئت تحریریه صالح ایوبی",
                "role": "سردبیر دانشنامه زیبایی",
                "bio": "محتوای این دانشنامه توسط تیم تخصصی مجموعه صالح ایوبی با تمرکز بر استانداردهای حرفه‌ای داماد، پوست و مو تدوین می‌شود.",
                "avatar_static": "images/brand/hero-groom-1-hd.jpg",
                "is_active": True,
            },
        )

        cat_map = {}
        for item in CATEGORIES:
            obj, _ = MagazineCategory.objects.update_or_create(
                slug=item["slug"],
                defaults={k: v for k, v in item.items() if k != "slug"},
            )
            cat_map[item["slug"]] = obj

        tag_map = {}
        for title, slug in TAGS:
            obj, _ = MagazineTag.objects.update_or_create(
                slug=slug, defaults={"title": title}
            )
            tag_map[slug] = obj

        now = timezone.now()
        created = 0
        for item in ARTICLES:
            cat = cat_map[item["category"]]
            article, was_created = Article.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "subtitle": item.get("subtitle", ""),
                    "excerpt": item["excerpt"],
                    "body": item["body"].strip(),
                    "category": cat,
                    "author": author,
                    "reading_minutes": item["reading_minutes"],
                    "status": Article.Status.PUBLISHED,
                    "is_active": True,
                    "published_at": now,
                    "is_hero": item.get("is_hero", False),
                    "is_featured": item.get("is_featured", False),
                    "is_editors_pick": item.get("is_editors_pick", False),
                    "display_priority": item.get("display_priority", 0),
                    "cover_image_static": item.get("cover_image_static", ""),
                    "cover_image_alt": item.get("cover_image_alt") or item["title"],
                    "meta_title": item["title"][:70],
                    "meta_description": item["excerpt"][:170],
                    "meta_keywords": "، ".join(
                        tag_map[t].title for t in item.get("tags", []) if t in tag_map
                    ),
                    "view_count": 40 + created * 17,
                    "complete_read_count": 8 + created * 3,
                    "like_count": 5 + created,
                },
            )
            article.tags.set([tag_map[t] for t in item.get("tags", []) if t in tag_map])
            created += 1 if was_created else 0

        # Wire related articles
        by_slug = {a.slug: a for a in Article.objects.filter(is_deleted=False)}
        if "groom-preparation-complete-guide" in by_slug:
            a = by_slug["groom-preparation-complete-guide"]
            related = [
                by_slug[s]
                for s in (
                    "mens-skincare-routine-four-steps",
                    "how-to-choose-vip-service",
                    "professional-beard-shave-sensitive-skin",
                )
                if s in by_slug
            ]
            a.related_articles.set(related)

        self.stdout.write(
            self.style.SUCCESS(
                f"Magazine seeded: {len(CATEGORIES)} categories, {len(TAGS)} tags, {len(ARTICLES)} articles"
            )
        )
