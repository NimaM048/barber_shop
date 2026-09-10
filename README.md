# Barber Shop — نوبت‌دهی آرایشگاه مردانه

پروژه Django با معماری **Service / Repository**، UI مبتنی بر **HTML + Tailwind CSS + JS**.

## ساختار پروژه

```
barber_shop/
├── config/                 # تنظیمات پروژه (settings.py, urls, wsgi)
├── apps/
│   ├── core/               # مدل‌های پایه، Repository/Service پایه، صفحه خانه
│   ├── accounts/           # کاربران و احراز هویت
│   ├── barbers/            # آرایشگران و ساعات کاری
│   ├── catalog/            # خدمات و قیمت‌ها
│   ├── appointments/       # نوبت‌دهی
│   ├── consultations/      # مشاوره آنلاین / VIP
│   ├── magazine/           # مجله و مقالات
│   └── portfolio/          # گالری نمونه‌کارها
├── templates/              # قالب‌های HTML
├── static/                 # CSS, JS, تصاویر
└── media/                  # آپلود کاربران
```

## معماری (Service / Repository)

| لایه | مسئولیت |
|------|---------|
| **View** | دریافت request، فراخوانی Service، render/redirect |
| **Service** | منطق کسب‌وکار، اعتبارسنجی، هماهنگی Repositoryها |
| **Repository** | دسترسی به دیتابیس (ORM) |
| **Model** | ساختار داده |

قوانین:
- Viewها نباید مستقیم query بزنند
- Service نباید HttpResponse برگرداند
- Repository نباید business rule داشته باشد

## راه‌اندازی

### 1. محیط Python

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. متغیرهای محیطی

```powershell
copy .env.example .env
```

### 3. دیتابیس

```powershell
python manage.py migrate
python manage.py createsuperuser
```

### 4. Tailwind CSS

```powershell
npm install
npm run build:css
```

برای توسعه (watch):

```powershell
npm run dev:css
```

### 5. اجرای سرور

**توسعه:**

```powershell
$env:DJANGO_ENV="development"
python manage.py runserver
```

**پروداکشن:**

```powershell
npm run build:css
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

روی سرور `.env` را با `DJANGO_ENV=production` و `SITE_PUBLIC_URL=https://salehayoubi.com` تنظیم کنید.
Nginx/Cloudflare باید `X-Forwarded-Proto: https` را به Django پاس دهد.

سایت: http://127.0.0.1:8000/ (توسعه) · https://salehayoubi.com (پروداکشن)

## SEO هنگام دیپلوی

چک‌لیست اقدامات دستی (Search Console، Sitemap، Google Business، env پروداکشن):

→ [`docs/seo-deploy-checklist.md`](docs/seo-deploy-checklist.md)

## اپ‌ها

| اپ | URL | توضیح |
|----|-----|-------|
| core | `/` | صفحه اصلی |
| accounts | `/accounts/` | ورود / ثبت‌نام |
| catalog | `/services/` | لیست خدمات |
| barbers | `/barbers/` | لیست آرایشگران |
| appointments | `/appointments/` | نوبت‌های من / رزرو |
| consultations | `/consultations/` | مشاوره و راهنمایی |
| magazine | `/magazine/` | مجله و مقالات |
| portfolio | `/portfolio/` | گالری نمونه‌کارها |

## مراحل بعدی

- [ ] فرم کامل رزرو نوبت با انتخاب زمان
- [ ] پنل مدیریت آرایشگر
- [ ] اعلان SMS / ایمیل
- [ ] تست‌های واحد برای Serviceها
