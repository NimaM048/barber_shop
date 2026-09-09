"""
Django settings — Barber Shop (صالح ایوبی).

Environment: set DJANGO_ENV=production on the server; default is development.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ── Helpers ──────────────────────────────────────────────────────────────────


def _env_bool(name: str, *, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: list[str] | None = None) -> list[str]:
    raw = os.getenv(name, "")
    items = [item.strip() for item in raw.split(",") if item.strip()]
    return items if items else (default or [])


def _hosts_from_public_url(url: str) -> list[str]:
    if not url:
        return []
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = (parsed.netloc or parsed.path.split("/")[0]).strip()
    if not host:
        return []
    hosts = [host]
    if host.startswith("www."):
        bare = host[4:]
        if bare:
            hosts.append(bare)
    elif "." in host:
        hosts.append(f"www.{host}")
    return list(dict.fromkeys(hosts))


# ── Environment ──────────────────────────────────────────────────────────────

IS_PRODUCTION = os.getenv("DJANGO_ENV", "development").strip().lower() == "production"
DEBUG = _env_bool("DEBUG", default=not IS_PRODUCTION)

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-production")

SITE_PUBLIC_URL = os.getenv("SITE_PUBLIC_URL", "").strip().rstrip("/")
SITE_WEBSITE = os.getenv("SITE_WEBSITE", "salehayoubi.com").strip()

if IS_PRODUCTION:
    ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS") or _hosts_from_public_url(
        SITE_PUBLIC_URL
    ) or ["salehayoubi.com", "www.salehayoubi.com"]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

def _build_csrf_trusted_origins(
    *,
    public_url: str,
    allowed_hosts: list[str],
    is_production: bool,
) -> list[str]:
    """Origins allowed for CSRF — derived from SITE_PUBLIC_URL + ALLOWED_HOSTS."""
    origins: list[str] = []

    def _add(scheme: str, host: str, port: int | None = None) -> None:
        host = host.strip()
        if not host or host in {"*", "[::1]"}:
            return
        origin = f"{scheme}://{host}"
        if port:
            origin = f"{origin}:{port}"
        if origin not in origins:
            origins.append(origin)

    if public_url:
        parsed = urlparse(public_url)
        if parsed.scheme and parsed.netloc:
            _add(parsed.scheme, parsed.netloc)
            hostname = parsed.hostname or ""
            port = parsed.port
            if hostname.startswith("www."):
                _add(parsed.scheme, hostname[4:], port)
            elif hostname:
                _add(parsed.scheme, f"www.{hostname}", port)

    scheme = "https" if is_production else "http"
    dev_ports: tuple[int | None, ...] = (None, 8000, 8080) if not is_production else (None,)

    for host in allowed_hosts:
        if host in {"*", "[::1]"}:
            continue
        if is_production:
            _add("https", host)
            if not host.startswith("www.") and "." in host:
                _add("https", f"www.{host}")
        else:
            for port in dev_ports:
                _add(scheme, host, port)

    for extra in _env_list("CSRF_TRUSTED_ORIGINS"):
        if extra not in origins:
            origins.append(extra)

    return origins


CSRF_TRUSTED_ORIGINS = _build_csrf_trusted_origins(
    public_url=SITE_PUBLIC_URL,
    allowed_hosts=ALLOWED_HOSTS,
    is_production=IS_PRODUCTION,
)


# ── Applications ─────────────────────────────────────────────────────────────

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


# ── Middleware ─────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
]

if IS_PRODUCTION:
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

MIDDLEWARE += [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ── URLs / WSGI ────────────────────────────────────────────────────────────────

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ── Templates ──────────────────────────────────────────────────────────────────

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


# ── Database ───────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed.path.lstrip("/"),
            "USER": parsed.username or "",
            "PASSWORD": parsed.password or "",
            "HOST": parsed.hostname or "",
            "PORT": str(parsed.port or ""),
            "CONN_MAX_AGE": 600 if IS_PRODUCTION else 0,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ── Auth ───────────────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.User"


# ── i18n ───────────────────────────────────────────────────────────────────────

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


# ── Static / media ─────────────────────────────────────────────────────────────

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if IS_PRODUCTION:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }


# ── Email ──────────────────────────────────────────────────────────────────────

if IS_PRODUCTION:
    EMAIL_BACKEND = os.getenv(
        "EMAIL_BACKEND",
        "django.core.mail.backends.smtp.EmailBackend",
    )
    EMAIL_HOST = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", default=True)
    DEFAULT_FROM_EMAIL = os.getenv(
        "DEFAULT_FROM_EMAIL",
        f"noreply@{SITE_WEBSITE}",
    )
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ── Security (production) ──────────────────────────────────────────────────────

if IS_PRODUCTION:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS",
        default=True,
    )
    SECURE_HSTS_PRELOAD = _env_bool("SECURE_HSTS_PRELOAD", default=False)


# ── Logging ────────────────────────────────────────────────────────────────────

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


# ── Branding / SEO ─────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

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
SITE_LAT = float(os.getenv("SITE_LAT", "32.6412"))
SITE_LNG = float(os.getenv("SITE_LNG", "51.6902"))
SITE_MAP_ZOOM = int(os.getenv("SITE_MAP_ZOOM", "16"))
SITE_INSTAGRAM = os.getenv("SITE_INSTAGRAM", "saleh_ayoobi_academy")
DEFAULT_OG_IMAGE = os.getenv(
    "DEFAULT_OG_IMAGE",
    "images/brand/hero-cinematic-frame.jpg",
)
GOOGLE_SITE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION", "").strip()
SITE_HOURS_TEXT = os.getenv("SITE_HOURS_TEXT", "شنبه تا پنج‌شنبه · ۱۰ تا ۲۱")
SITE_GOOGLE_MAPS_URL = os.getenv("SITE_GOOGLE_MAPS_URL", "").strip()
SITE_GBP_URL = os.getenv("SITE_GBP_URL", "").strip()
