"""
Shared Django settings for Barber Shop.
"""

from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-change-me-in-production",
)

DEBUG = False

ALLOWED_HOSTS: list[str] = []

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.barbers",
    "apps.catalog",
    "apps.appointments",
    "apps.consultations",
    "apps.magazine",
    "apps.portfolio",
    "apps.reviews",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("fa", "Persian"),
    ("en", "English"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

# Branding
SITE_NAME = os.getenv("SITE_NAME", "صالح ایوبی")
SITE_TAGLINE = os.getenv("SITE_TAGLINE", "معماری زیبایی")
SITE_SUBTITLE = os.getenv(
    "SITE_SUBTITLE",
    "مرکز تخصصی داماد و پوست و مو",
)
SITE_PHONE = os.getenv("SITE_PHONE", "09132270519")
SITE_PHONE_DISPLAY = os.getenv("SITE_PHONE_DISPLAY", "۰۹۱۳ ۲۲۷ ۰۵۱۹")
SITE_ADDRESS = os.getenv(
    "SITE_ADDRESS",
    "اصفهان، مشتاق اول، خیابان ابوالحسن اصفهانی، بعد از کوچه ۲۶",
)
# Approximate pin for Abolhasan Esfahani St (after alley 26) — refine via env
SITE_LAT = float(os.getenv("SITE_LAT", "32.6412"))
SITE_LNG = float(os.getenv("SITE_LNG", "51.6902"))
SITE_MAP_ZOOM = int(os.getenv("SITE_MAP_ZOOM", "16"))
SITE_INSTAGRAM = os.getenv("SITE_INSTAGRAM", "saleh_ayoobi_academy")
SITE_WEBSITE = os.getenv("SITE_WEBSITE", "salehayoubi.com")
# Public origin for absolute SEO URLs (canonical / OG / sitemap). Prefer https://…
SITE_PUBLIC_URL = os.getenv("SITE_PUBLIC_URL", "").strip()
DEFAULT_OG_IMAGE = os.getenv(
    "DEFAULT_OG_IMAGE",
    "images/brand/hero-cinematic-frame.jpg",
)
GOOGLE_SITE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION", "").strip()
# Local SEO / Google Business Profile alignment
SITE_HOURS_TEXT = os.getenv("SITE_HOURS_TEXT", "شنبه تا پنج‌شنبه · ۱۰ تا ۲۱")
# Optional deep links — paste from Google Maps / Business Profile when ready
SITE_GOOGLE_MAPS_URL = os.getenv("SITE_GOOGLE_MAPS_URL", "").strip()
SITE_GBP_URL = os.getenv("SITE_GBP_URL", "").strip()
