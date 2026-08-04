"""
Site-wide SEO helpers: absolute URLs, LocalBusiness schema, sitemaps, page meta.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urljoin

from django.conf import settings
from django.urls import NoReverseMatch, reverse


DEFAULT_OG_STATIC = "images/brand/hero-cinematic-frame.jpg"


def _setting(name: str, default: Any = "") -> Any:
    return getattr(settings, name, default)


class SeoService:
    """Stateless SEO builders used by views and context processors."""

    def site_origin(self, request=None) -> str:
        public = (_setting("SITE_PUBLIC_URL") or "").strip().rstrip("/")
        if public:
            return public

        website = (_setting("SITE_WEBSITE") or "").strip()
        if website:
            if website.startswith("http://") or website.startswith("https://"):
                return website.rstrip("/")
            return f"https://{website}".rstrip("/")

        if request is not None:
            return request.build_absolute_uri("/").rstrip("/")
        return ""

    def absolute_url(self, path: str, request=None) -> str:
        path = path or "/"
        if path.startswith("http://") or path.startswith("https://"):
            return path
        origin = self.site_origin(request)
        if not origin and request is not None:
            return request.build_absolute_uri(path)
        return urljoin(origin + "/", path.lstrip("/"))

    def absolute_static(self, static_path: str, request=None) -> str:
        from django.templatetags.static import static

        url = static(static_path)
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return self.absolute_url(url, request)

    def canonical_url(self, request) -> str:
        """Path-only canonical (strips query strings)."""
        return request.build_absolute_uri(request.path)

    def default_og_image(self, request=None) -> str:
        path = _setting("DEFAULT_OG_IMAGE", DEFAULT_OG_STATIC) or DEFAULT_OG_STATIC
        return self.absolute_static(path, request)

    def dumps(self, data: Any) -> str:
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    # ── Page meta copy ─────────────────────────────────────────────

    def home_meta(self) -> dict[str, str]:
        site = _setting("SITE_NAME", "صالح ایوبی")
        title = f"{site} | آرایشگاه داماد و پوست و مو در اصفهان"
        description = (
            f"{site} — مرکز تخصصی داماد، پوست و مو در اصفهان. "
            "رزرو آنلاین نوبت، مشاوره قبل از مراجعه و تجربه اختصاصی زیبایی."
        )
        return {
            "title": title,
            "description": description,
            "og_title": title,
            "og_description": description,
        }

    def catalog_meta(self) -> dict[str, str]:
        site = _setting("SITE_NAME", "صالح ایوبی")
        title = f"خدمات داماد، پوست و مو | {site}"
        description = (
            f"کاتالوگ خدمات {site} در اصفهان — داماد، مراقبت پوست، طراحی مو و VIP. "
            "جزئیات، زمان و رزرو آنلاین."
        )
        return {
            "title": title,
            "description": description,
            "og_title": title,
            "og_description": description,
        }

    def booking_meta(self) -> dict[str, str]:
        site = _setting("SITE_NAME", "صالح ایوبی")
        title = f"رزرو آنلاین نوبت | {site}"
        description = (
            f"رزرو آنلاین نوبت {site} در اصفهان — VIP، داماد، پوست و مو. "
            "زمان دلخواه را انتخاب کنید و نوبت خود را ثبت کنید."
        )
        return {
            "title": title,
            "description": description,
            "og_title": title,
            "og_description": description,
        }

    def consultation_hub_meta(self, hub: dict[str, Any] | None = None) -> dict[str, str]:
        site = _setting("SITE_NAME", "صالح ایوبی")
        hub = hub or {}
        raw_title = (hub.get("document_title") or hub.get("title") or "").strip()
        title = f"{raw_title} | {site}" if raw_title else f"مشاوره قبل از مراجعه | {site}"
        description = (
            (hub.get("meta_description") or "").strip()
            or (
                f"مشاوره تخصصی قبل از مراجعه در {site} — راهنمای VIP، داماد و پوست و مو "
                "برای آمادگی بهتر در اصفهان."
            )
        )
        return {
            "title": title,
            "description": description,
            "og_title": title,
            "og_description": description,
        }

    def consultation_detail_meta(self, category: Any) -> dict[str, str]:
        site = _setting("SITE_NAME", "صالح ایوبی")
        if isinstance(category, dict):
            cat_title = category.get("title") or "راهنمای مشاوره"
            short = category.get("short_description") or ""
        else:
            cat_title = getattr(category, "title", "") or "راهنمای مشاوره"
            short = getattr(category, "short_description", "") or ""
        title = f"{cat_title} | {site}"
        description = (
            f"{short} — راهنمای تخصصی قبل از مراجعه در {site}، اصفهان."
            if short
            else f"{cat_title} — نکات مراقبت و آمادگی قبل از مراجعه در {site}."
        )
        return {
            "title": title,
            "description": description[:300],
            "og_title": title,
            "og_description": description[:300],
        }

    def magazine_hub_meta(self) -> dict[str, str]:
        site = _setting("SITE_NAME", "صالح ایوبی")
        title = f"مجله زیبایی | {site}"
        description = (
            f"دانشنامه تخصصی داماد، پوست، مو و استایل — مقالات آموزشی {site} در اصفهان."
        )
        return {
            "title": title,
            "description": description,
            "og_title": title,
            "og_description": description,
        }

    # ── JSON-LD ────────────────────────────────────────────────────

    def local_business_schema(self, request=None) -> dict[str, Any]:
        origin = self.site_origin(request)
        site = _setting("SITE_NAME", "صالح ایوبی")
        phone = _setting("SITE_PHONE", "")
        address = _setting("SITE_ADDRESS", "")
        hours_text = _setting("SITE_HOURS_TEXT", "شنبه تا پنج‌شنبه · ۱۰ تا ۲۱")
        instagram = (_setting("SITE_INSTAGRAM") or "").lstrip("@")
        maps_url = (_setting("SITE_GOOGLE_MAPS_URL") or "").strip()
        gbp_url = (_setting("SITE_GBP_URL") or "").strip()

        same_as: list[str] = []
        if instagram:
            same_as.append(f"https://www.instagram.com/{instagram}/")
        if gbp_url:
            same_as.append(gbp_url)
        if maps_url and maps_url not in same_as:
            same_as.append(maps_url)

        # Default: Sat–Thu 10:00–21:00 (Iran business week; matches SITE_HOURS_TEXT)
        opening_hours = [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Saturday",
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                ],
                "opens": "10:00",
                "closes": "21:00",
            }
        ]

        if not maps_url:
            lat = float(_setting("SITE_LAT", 32.6412))
            lng = float(_setting("SITE_LNG", 51.6902))
            maps_url = (
                f"https://www.google.com/maps/search/?api=1&query={lat}%2C{lng}"
            )

        schema: dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "BeautySalon",
            "@id": f"{origin}/#business" if origin else "#business",
            "name": site,
            "alternateName": "Saleh Ayoubi",
            "description": (
                f"{site} — {_setting('SITE_SUBTITLE', 'مرکز تخصصی داماد و پوست و مو')} "
                f"در اصفهان. آرایشگاه تخصصی داماد، مراقبت پوست و طراحی مو با رزرو آنلاین."
            ),
            "url": f"{origin}/" if origin else "/",
            "image": self.default_og_image(request),
            "telephone": phone,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": address,
                "addressLocality": "اصفهان",
                "addressRegion": "اصفهان",
                "addressCountry": "IR",
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": float(_setting("SITE_LAT", 32.6412)),
                "longitude": float(_setting("SITE_LNG", 51.6902)),
            },
            "hasMap": maps_url,
            "openingHoursSpecification": opening_hours,
            "areaServed": [
                {"@type": "City", "name": "اصفهان"},
                {"@type": "AdministrativeArea", "name": "استان اصفهان"},
            ],
            "knowsAbout": [
                "آرایش داماد اصفهان",
                "مراقبت پوست مردانه",
                "طراحی مو",
                "اصلاح تخصصی",
                "خدمات VIP زیبایی",
            ],
            "priceRange": "$$",
            "currenciesAccepted": "IRR",
            "paymentAccepted": "Cash, Card",
            "inLanguage": "fa",
            "slogan": _setting("SITE_TAGLINE", "معماری زیبایی"),
        }
        if hours_text:
            schema["openingHours"] = hours_text
        if same_as:
            schema["sameAs"] = same_as
        return schema

    def breadcrumb_schema(
        self,
        items: list[dict[str, str]],
        request=None,
    ) -> dict[str, Any]:
        """items: [{"name": "...", "path": "/..."}, ...]"""
        elements = []
        for i, item in enumerate(items, start=1):
            loc = item.get("url") or self.absolute_url(item.get("path", "/"), request)
            elements.append(
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": item["name"],
                    "item": loc,
                }
            )
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": elements,
        }

    def faq_schema(self, faqs: list[dict[str, Any]]) -> dict[str, Any] | None:
        entities = []
        for faq in faqs:
            q = (faq.get("question") or "").strip()
            a = (faq.get("answer") or "").strip()
            if not q or not a:
                continue
            entities.append(
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a,
                    },
                }
            )
        if not entities:
            return None
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": entities,
        }

    def service_catalog_schema(
        self,
        services: list[dict[str, Any]],
        request=None,
    ) -> dict[str, Any]:
        origin = self.site_origin(request)
        site = _setting("SITE_NAME", "صالح ایوبی")
        elements = []
        for i, svc in enumerate(services, start=1):
            name = svc.get("name") or "خدمت"
            elements.append(
                {
                    "@type": "ListItem",
                    "position": i,
                    "item": {
                        "@type": "Service",
                        "name": name,
                        "description": svc.get("description") or "",
                        "provider": {
                            "@type": "BeautySalon",
                            "name": site,
                        },
                        "areaServed": "اصفهان",
                        "url": self.absolute_url(
                            reverse("appointments:create")
                            + (f"?service={svc['slug']}" if svc.get("slug") else ""),
                            request,
                        ),
                    },
                }
            )
        return {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"خدمات {site}",
            "url": self.absolute_url(reverse("catalog:list"), request),
            "numberOfItems": len(elements),
            "itemListElement": elements,
            "provider": {"@id": f"{origin}/#business"} if origin else {"name": site},
        }

    # ── robots / sitemap ───────────────────────────────────────────

    def robots_txt(self, request=None) -> str:
        sitemap = self.absolute_url("/sitemap.xml", request)
        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /appointments/api/",
            "Disallow: /consultations/api/",
            "Disallow: /magazine/api/",
            "",
            f"Sitemap: {sitemap}",
            "",
        ]
        return "\n".join(lines)

    def static_sitemap_entries(self, request=None) -> list[dict[str, Any]]:
        """Core public pages for the site-wide sitemap."""
        pages: list[tuple[str, str, str]] = [
            ("core:home", "daily", "1.0"),
            ("catalog:list", "weekly", "0.9"),
            ("appointments:create", "weekly", "0.9"),
            ("consultations:hub", "weekly", "0.8"),
            ("magazine:hub", "daily", "0.8"),
        ]
        entries: list[dict[str, Any]] = []
        for name, changefreq, priority in pages:
            try:
                path = reverse(name)
            except NoReverseMatch:
                continue
            entries.append(
                {
                    "loc": self.absolute_url(path, request),
                    "changefreq": changefreq,
                    "priority": priority,
                }
            )
        return entries

    def consultation_sitemap_entries(self, request=None) -> list[dict[str, Any]]:
        from apps.consultations.repositories import ConsultationCategoryRepository

        entries: list[dict[str, Any]] = []
        for cat in ConsultationCategoryRepository().list_enabled():
            try:
                path = reverse("consultations:detail", kwargs={"key": cat.key})
            except NoReverseMatch:
                continue
            entries.append(
                {
                    "loc": self.absolute_url(path, request),
                    "changefreq": "weekly",
                    "priority": "0.7",
                    "lastmod": cat.updated_at.date().isoformat()
                    if getattr(cat, "updated_at", None)
                    else None,
                }
            )
        return entries

    def magazine_sitemap_entries(self, request=None) -> list[dict[str, Any]]:
        from apps.magazine.services.magazine_service import MagazineService

        entries: list[dict[str, Any]] = []
        for e in MagazineService().sitemap_entries():
            try:
                path = reverse("magazine:article", kwargs={"slug": e["slug"]})
            except NoReverseMatch:
                continue
            lastmod = None
            if e.get("updated_at"):
                lastmod = e["updated_at"].date().isoformat()
            entries.append(
                {
                    "loc": self.absolute_url(path, request),
                    "changefreq": "weekly",
                    "priority": "0.7",
                    "lastmod": lastmod,
                }
            )
        return entries

    def build_sitemap_xml(self, request=None) -> str:
        all_entries = (
            self.static_sitemap_entries(request)
            + self.consultation_sitemap_entries(request)
            + self.magazine_sitemap_entries(request)
        )
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        for e in all_entries:
            parts = [f"<loc>{e['loc']}</loc>"]
            if e.get("lastmod"):
                parts.append(f"<lastmod>{e['lastmod']}</lastmod>")
            if e.get("changefreq"):
                parts.append(f"<changefreq>{e['changefreq']}</changefreq>")
            if e.get("priority"):
                parts.append(f"<priority>{e['priority']}</priority>")
            lines.append(f"<url>{''.join(parts)}</url>")
        lines.append("</urlset>")
        return "\n".join(lines)
