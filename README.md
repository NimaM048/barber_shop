# Barber Shop — نوبت‌دهی آرایشگاه مردانه

پروژه Django با معماری **Service / Repository**، UI مبتنی بر **HTML + Tailwind CSS + JS**.

## ساختار پروژه

```
barber_shop/
├── config/                 # تنظیمات پروژه (settings, urls, wsgi)
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
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

```powershell
python manage.py runserver
```

سایت: http://127.0.0.1:8000/

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
