# چک‌لیست SEO هنگام دیپلوی

اقداماتی که **سمت شما** باید بعد از بالا آمدن سایت روی دامنهٔ واقعی انجام شود.  
کد سایت از قبل `robots.txt`، `sitemap.xml`، meta و Schema را دارد؛ این سند فقط کارهای دستی/خارجی است.

دامنهٔ مرجع در این سند: `https://salehayoubi.com`  
اگر دامنه فرق دارد، همهٔ URLها را با دامنهٔ خودتان جایگزین کنید.

---

## ۱) قبل از دیپلوی — متغیرهای محیطی

در `.env` پروداکشن این مقادیر را تنظیم کنید:

```env
SITE_PUBLIC_URL=https://salehayoubi.com
SITE_WEBSITE=salehayoubi.com
SITE_NAME=صالح ایوبی
SITE_PHONE=09132270519
SITE_PHONE_DISPLAY=۰۹۱۳ ۲۲۷ ۰۵۱۹
SITE_ADDRESS=اصفهان، مشتاق اول، خیابان ابوالحسن اصفهانی، بعد از کوچه ۲۶
SITE_LAT=32.6412
SITE_LNG=51.6902
SITE_INSTAGRAM=saleh_ayoobi_academy
SITE_HOURS_TEXT=شنبه تا پنج‌شنبه · ۱۰ تا ۲۱
DEFAULT_OG_IMAGE=images/brand/hero-cinematic-frame.jpg
GOOGLE_SITE_VERIFICATION=
# بعد از ساخت/ادعا GBP این دو را پر کنید:
SITE_GOOGLE_MAPS_URL=
SITE_GBP_URL=
ALLOWED_HOSTS=salehayoubi.com,www.salehayoubi.com
```

نکات مهم:

- `SITE_PUBLIC_URL` باید با `https://` باشد (بدون اسلش انتهایی).
- مختصات (`SITE_LAT` / `SITE_LNG`) را با پین دقیق ورودی سالن روی نقشه چک و اصلاح کنید.
- نام، تلفن، آدرس و ساعات باید **دقیقاً** با Google Business Profile یکی باشد (NAP + Hours).
- `SITE_GOOGLE_MAPS_URL`: لینک دائمی مکان در Google Maps (Share → Copy link).
- `SITE_GBP_URL`: لینک پروفایل کسب‌وکار در گوگل (اگر جدا از Maps است).
- بعد از گرفتن کد تأیید Search Console، مقدار `GOOGLE_SITE_VERIFICATION` را پر کنید و دوباره دیپلوی کنید.

### بعد از بالا آمدن سایت، این URLها را در مرورگر باز کنید

| URL | انتظار |
|-----|--------|
| `https://salehayoubi.com/robots.txt` | متن plain با خط `Sitemap: …` |
| `https://salehayoubi.com/sitemap.xml` | XML شامل خانه، خدمات، رزرو، مشاوره، مقالات |
| `https://salehayoubi.com/` | در View Source: `BeautySalon` داخل `application/ld+json` |
| صفحهٔ خانه | `og:image` با URL مطلق `https://…` |

اگر `www` هم دارید، یکی را canonical کنید (ترجیحاً بدون www یا با www — فقط یکی) و دیگری را ۳۰۱ ریدایرکت کنید.

---

## ۲) Google Search Console

### ثبت و تأیید مالکیت

1. بروید به [Google Search Console](https://search.google.com/search-console).
2. **Add property** → ترجیحاً نوع **URL prefix**: `https://salehayoubi.com`
   - اگر هم `www` و هم بدون `www` دارید، همان نسخه‌ای را ثبت کنید که canonical است؛ نسخهٔ دیگر را هم می‌توانید جداگانه اضافه کنید.
3. روش تأیید پیشنهادی برای این پروژه: **HTML tag**
   - کد شبیه این می‌گیرید:  
     `<meta name="google-site-verification" content="XXXX" />`
   - فقط مقدار `XXXX` را در `.env` بگذارید:

```env
GOOGLE_SITE_VERIFICATION=XXXX
```

4. اپ/سرور را ریستارت کنید تا meta در `<head>` ظاهر شود.
5. در Search Console روی **Verify** بزنید.

روش‌های جایگزین (اگر ترجیح می‌دهید): DNS TXT در دامنه، یا آپلود فایل HTML در root — برای این پروژه meta tag ساده‌ترین است.

### ارسال Sitemap

1. در همان property → منوی **Sitemaps**
2. این آدرس را Submit کنید:

```text
https://salehayoubi.com/sitemap.xml
```

3. وضعیت را بعد از چند ساعت/روز چک کنید (`Success` / تعداد URL کشف‌شده).

### درخواست ایندکس صفحات کلیدی (اختیاری ولی مفید)

در **URL Inspection** این صفحات را یکی‌یکی Inspect و در صورت امکان **Request indexing** کنید:

- `/`
- `/services/`
- `/appointments/new/`
- `/consultations/`
- `/magazine/`
- ۲–۳ مقالهٔ مهم مجله

---

## ۳) Bing Webmaster Tools (پیشنهادی)

1. [Bing Webmaster Tools](https://www.bing.com/webmasters)
2. سایت را اضافه کنید (می‌توانید با ایمپورت از Google تأیید کنید).
3. Sitemap را Submit کنید: `https://salehayoubi.com/sitemap.xml`

---

## ۴) Google Business Profile (خیلی مهم برای کسب‌وکار محلی)

برای SEO محلی اصفهان، این بخش اغلب از خود سایت هم اثرگذارتر است.

### چه چیزی از قبل در سایت آماده است؟

- Schema از نوع `BeautySalon` با آدرس، تلفن، geo، ساعات، `hasMap`، `sameAs` (اینستاگرام + GBP/Maps در صورت پر بودن env)
- بلوک موقعیت در فوتر با مسیریابی Google Maps
- دکمهٔ «مشاهده در گوگل» وقتی `SITE_GBP_URL` ست شده باشد
- محتوای محلی (اصفهان / داماد / پوست و مو) در خانه، خدمات، رزرو، مشاوره و مجله

### کارهای دستی شما در Google

1. بروید به [Google Business Profile](https://business.google.com/)
2. کسب‌وکار را بسازید/ادعا کنید: **صالح ایوبی**
3. دستهٔ اصلی مناسب مثل **آرایشگاه مردانه / Beauty salon** را انتخاب کنید.
4. این فیلدها را **عین سایت / `.env`** پر کنید:
   - نام
   - آدرس
   - تلفن
   - ساعات کاری (`SITE_HOURS_TEXT`)
   - وب‌سایت: `https://salehayoubi.com`
5. ساعات کاری، عکس‌های واقعی سالن، و خدمات را اضافه کنید.
6. لینک اینستاگرام را هم در پروفایل بگذارید.
7. بعد از تأیید مکان:
   - لینک Maps را کپی کنید → `SITE_GOOGLE_MAPS_URL`
   - لینک پروفایل کسب‌وکار را کپی کنید → `SITE_GBP_URL`
   - دیپلوی/ریستارت کنید تا در Schema و دکمهٔ فوتر ظاهر شود
8. مرتب نظرات بگیرید و به پرسش‌ها جواب دهید.

### هم‌خوانی NAP (اجباری)

هر بار آدرس یا تلفن عوض شد، **هم‌زمان** این سه جا را به‌روز کنید:

1. `.env` / settings سایت  
2. Google Business Profile  
3. فوتر و بلوک موقعیت سایت (از همان env خوانده می‌شود)

---

## ۵) شبکه‌های اجتماعی و اشتراک‌گذاری (Open Graph)

بعد از دیپلوی، یک بار این ابزارها را روی URL خانه و یک مقاله تست کنید:

- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) (در صورت نیاز)

اگر کش قدیمی دیدید، در همان ابزار **Scrape Again** بزنید.

انتظار: تصویر `hero-cinematic-frame.jpg` با URL مطلق لود شود.

---

## ۶) ریدایرکت و HTTPS

روی سرور/CDN مطمئن شوید:

- [ ] فقط HTTPS فعال است (HTTP → HTTPS با ۳۰۱)
- [ ] یکی از `www` / بدون `www` canonical است؛ دیگری ۳۰۱ می‌شود
- [ ] `ALLOWED_HOSTS` هر دو host را دارد (اگر هر دو استفاده می‌شوند)
- [ ] گواهی SSL معتبر است

---

## ۷) مانیتورینگ بعد از لانچ (هفتهٔ اول تا ماه اول)

| کار | زمان تقریبی |
|-----|-------------|
| چک وضعیت Sitemap در Search Console | ۲۴–۷۲ ساعت بعد |
| بررسی Coverage / Pages (ایندکس / خطا) | هفتگی |
| جستجوی `site:salehayoubi.com` در گوگل | بعد از چند روز |
| بررسی Core Web Vitals در Search Console (در صورت فعال شدن) | ماهانه |
| هم‌خوانی NAP سایت با Google Business | هر بار تغییر آدرس/تلفن |

---

## ۸) چک‌لیست سریع روز دیپلوی

کپی کنید و تیک بزنید:

- [ ] `.env` پروداکشن: `SITE_PUBLIC_URL` و NAP و مختصات و `SITE_HOURS_TEXT` درست است
- [ ] `ALLOWED_HOSTS` دامنهٔ واقعی را دارد
- [ ] HTTPS + ریدایرکت www تنظیم شد
- [ ] `/robots.txt` و `/sitemap.xml` روی دامنهٔ واقعی باز می‌شوند
- [ ] Google Search Console ثبت و Verify شد
- [ ] `GOOGLE_SITE_VERIFICATION` در env ست و دیپلوی مجدد شد (اگر از meta tag استفاده کردید)
- [ ] Sitemap در Search Console Submit شد
- [ ] Google Business Profile ساخته/به‌روز شد و وب‌سایت لینک شد
- [ ] `SITE_GOOGLE_MAPS_URL` و در صورت وجود `SITE_GBP_URL` پر شد
- [ ] `python manage.py seed_magazine` و در صورت نیاز `seed_consultations` روی پروداکشن اجرا شد
- [ ] (اختیاری) Bing Webmaster + تست OG Debugger

---

## ۹) کارهای بعدی محتوا (بعد از پایدار شدن فنی)

محتوای محلی و لینک داخلی از قبل در سایت هست. برای ادامهٔ رشد:

- بعد از دیپلوی seed مجله/مشاوره را روی پروداکشن اجرا کنید تا مقالهٔ «آرایشگاه داماد در اصفهان» و metaهای به‌روز بیاید:

```bash
python manage.py seed_magazine
python manage.py seed_consultations
```

- مقالات تازه حول: داماد اصفهان، پوست و مو اصفهان، VIP زیبایی
- لینک داخلی از مقالات جدید به `/services/` و `/appointments/new/`
- به‌روز نگه داشتن آدرس/تلفن/ساعات در `.env` و Google Business هم‌زمان

---

## مرجع سریع endpointهای SEO داخل پروژه

| مسیر | نقش |
|------|-----|
| `/robots.txt` | راهنمای خزنده + لینک sitemap |
| `/sitemap.xml` | نقشهٔ کل سایت |
| `/magazine/sitemap.xml` | فقط مجله (اختیاری؛ اصلی همان `/sitemap.xml` است) |
| `/magazine/rss.xml` | فید RSS مجله |

کد مربوطه: `apps/core/services/seo_service.py`
