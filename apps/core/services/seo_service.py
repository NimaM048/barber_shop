"""
Site-wide SEO helpers: absolute URLs, LocalBusiness schema, sitemaps, page meta.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urljoin

from django.conf import settings
from django.urls import NoReverseMatch, reverse

from apps.core.page_content import PageContent
from apps.core.services.home_page_service import HomePageService
from apps.core.services.page_content_service import PageContentService
from apps.core.services.site_settings_service import SiteSettingsService

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

    def _site_name(self) -> str:
        return SiteSettingsService().branding()["SITE_NAME"]

    def _meta_from_cms(
        self,
        *,
        seo_title: str = "",
        seo_description: str = "",
        fallback_title: str,
        fallback_description: str,
    ) -> dict[str, str]:
        site = self._site_name()
        title = (seo_title or "").strip() or fallback_title
        if title and site and site not in title:
            title = f"{title} | {site}"
        description = (seo_description or "").strip() or fallback_description
        return {
            "title": title,
            "description": description,
            "og_title": title,
            "og_description": description,
        }

    def home_meta(self) -> dict[str, str]:
        site = self._site_name()
        home_rec = HomePageService().get_record()
        site_rec = SiteSettingsService().get_record()
        seo_title = ""
        seo_desc = ""
        if home_rec and home_rec.seo_title:
            seo_title = home_rec.seo_title
        elif site_rec and site_rec.seo_title_default:
            seo_title = site_rec.seo_title_default
        if home_rec and home_rec.seo_description:
            seo_desc = home_rec.seo_description
        elif site_rec and site_rec.seo_description_default:
            seo_desc = site_rec.seo_description_default

        fallback_title = f"{site} | آرایشگاه داماد و پوست و مو در اصفهان"
        fallback_desc = (
            f"{site} — مرکز تخصصی داماد، پوست و مو در اصفهان. "
            "رزرو آنلاین نوبت، مشاوره قبل از مراجعه و تجربه اختصاصی زیبایی."
        )
        return self._meta_from_cms(
            seo_title=seo_title,
            seo_description=seo_desc,
            fallback_title=fallback_title,
            fallback_description=fallback_desc,
        )

    def catalog_meta(self) -> dict[str, str]:
        site = self._site_name()
        pc = PageContentService().get(PageContent.PageKey.CATALOG)
        fallback_title = f"خدمات داماد، پوست و مو | {site}"
        fallback_desc = (
            f"کاتالوگ خدمات {site} در اصفهان — داماد، مراقبت پوست، طراحی مو و VIP. "
            "جزئیات، زمان و رزرو آنلاین."
        )
        return self._meta_from_cms(
            seo_title=pc.get("seo_title", ""),
            seo_description=pc.get("seo_description", ""),
            fallback_title=fallback_title,
            fallback_description=fallback_desc,
        )

    def booking_meta(self) -> dict[str, str]:
        site = self._site_name()
        pc = PageContentService().get(PageContent.PageKey.BOOKING)
        fallback_title = f"رزرو آنلاین نوبت | {site}"
        fallback_desc = (
            f"رزرو آنلاین نوبت {site} در اصفهان — VIP، داماد، پوست و مو. "
            "زمان دلخواه را انتخاب کنید و نوبت خود را ثبت کنید."
        )
        return self._meta_from_cms(
            seo_title=pc.get("seo_title", ""),
            seo_description=pc.get("seo_description", ""),
            fallback_title=fallback_title,
            fallback_description=fallback_desc,
        )

    def consultation_hub_meta(self, hub: dict[str, Any] | None = None) -> dict[str, str]:
        site = self._site_name()
        hub = hub or {}
        pc = PageContentService().get(PageContent.PageKey.CONSULTATIONS)
        raw_title = (
            (hub.get("document_title") or hub.get("title") or "").strip()
            or pc.get("seo_title", "")
            or pc.get("title", "")
        )
        fallback_title = f"{raw_title} | {site}" if raw_title else f"مشاوره قبل از مراجعه | {site}"
        description = (
            (hub.get("meta_description") or "").strip()
            or pc.get("seo_description", "")
            or pc.get("lede", "")
            or (
                f"مشاوره تخصصی قبل از مراجعه در {site} — راهنمای VIP، داماد و پوست و مو "
                "برای آمادگی بهتر در اصفهان."
            )
        )
        title = pc.get("seo_title") or fallback_title
        if pc.get("seo_title"):
            title = f"{pc['seo_title']} | {site}" if site not in pc["seo_title"] else pc["seo_title"]
        return {
            "title": title,
            "description": description[:300],
            "og_title": title,
            "og_description": description[:300],
        }

    def consultation_detail_meta(self, category: Any) -> dict[str, str]:
        site = self._site_name()
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
        site = self._site_name()
        pc = PageContentService().get(PageContent.PageKey.MAGAZINE)
        fallback_title = f"مجله زیبایی | {site}"
        fallback_desc = (
            f"دانشنامه تخصصی داماد، پوست، مو و استایل — مقالات آموزشی {site} در اصفهان."
        )
        return self._meta_from_cms(
            seo_title=pc.get("seo_title", ""),
            seo_description=pc.get("seo_description", ""),
            fallback_title=fallback_title,
            fallback_description=fallback_desc,
        )

    def barbers_meta(self) -> dict[str, str]:
        site = self._site_name()
        pc = PageContentService().get(PageContent.PageKey.BARBERS)
        fallback_title = f"آرایشگران | {site}"
        fallback_desc = f"تیم و آرایشگران {site} در اصفهان."
        return self._meta_from_cms(
            seo_title=pc.get("seo_title", ""),
            seo_description=pc.get("seo_description", ""),
            fallback_title=fallback_title,
            fallback_description=fallback_desc,
        )

    def reviews_hub_meta(self) -> dict[str, str]:
        site = self._site_name()
        pc = PageContentService().get(PageContent.PageKey.REVIEWS)
        fallback_title = f"نظرات مشتریان | آرایشگاه {site} اصفهان"
        fallback_desc = (
            f"روایت داماد، اصلاح VIP و مراقبت پوست در {site} اصفهان — "
            "تجربه واقعی مشتریان با امتیاز مشخص."
        )
        return self._meta_from_cms(
            seo_title=pc.get("seo_title", ""),
            seo_description=pc.get("seo_description", ""),
            fallback_title=fallback_title,
            fallback_description=fallback_desc,
        )

    def reviews_category_meta(self, category: dict[str, Any]) -> dict[str, str]:
        site = self._site_name()
        title = (category.get("seo_title") or "").strip()
        desc = (category.get("seo_description") or "").strip()
        cat_title = category.get("title") or "نظرات"
        fallback_title = f"نظرات {cat_title} | {site} اصفهان"
        fallback_desc = (
            desc
            or (category.get("lede") or "").strip()
            or f"تجربه مشتریان {cat_title} در {site} اصفهان."
        )
        return self._meta_from_cms(
            seo_title=title,
            seo_description=desc,
            fallback_title=fallback_title,
            fallback_description=fallback_desc,
        )

    def reviews_detail_meta(self, review: dict[str, Any]) -> dict[str, str]:
        site = self._site_name()
        title = (review.get("seo_title") or "").strip() or review.get("title") or "نظر مشتری"
        desc = (review.get("seo_description") or "").strip() or review.get("excerpt") or ""
        if desc and site not in desc:
            desc = f"{desc} — {site}، اصفهان."
        fallback_title = f"{title} | {site}"
        return self._meta_from_cms(
            seo_title=title if title != review.get("title") else "",
            seo_description=(review.get("seo_description") or "").strip(),
            fallback_title=fallback_title,
            fallback_description=desc[:300] or f"نظر مشتری درباره خدمات {site} در اصفهان.",
        )

    # ── JSON-LD ────────────────────────────────────────────────────

    def local_business_schema(self, request=None, *, include_reviews: bool = False) -> dict[str, Any]:
        branding = SiteSettingsService().branding()
        origin = self.site_origin(request)
        site = branding["SITE_NAME"]
        phone = branding["SITE_PHONE"]
        address = branding["SITE_ADDRESS"]
        hours_text = branding["SITE_HOURS_TEXT"] or "شنبه تا پنج‌شنبه · ۱۰ تا ۲۱"
        instagram = (branding["SITE_INSTAGRAM"] or "").lstrip("@")
        maps_url = (branding["SITE_GOOGLE_MAPS_URL"] or "").strip()
        gbp_url = (branding["SITE_GBP_URL"] or "").strip()
        tagline = branding.get("SITE_TAGLINE") or _setting("SITE_TAGLINE", "معماری زیبایی")

        same_as: list[str] = []
        if instagram:
            same_as.append(f"https://www.instagram.com/{instagram}/")
        if gbp_url:
            same_as.append(gbp_url)
        if maps_url and maps_url not in same_as:
            same_as.append(maps_url)

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

        lat = branding["SITE_LAT"]
        lng = branding["SITE_LNG"]
        if not maps_url:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={lat}%2C{lng}"

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
                "addressLocality": branding.get("SITE_CITY", "اصفهان"),
                "addressRegion": "اصفهان",
                "addressCountry": "IR",
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": lat,
                "longitude": lng,
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
            "slogan": tagline,
        }
        if hours_text:
            schema["openingHours"] = hours_text
        if same_as:
            schema["sameAs"] = same_as
        if include_reviews:
            self._attach_review_schema(schema, request)
        return schema

    def _iso_date(self, value: Any) -> str:
        if value is None:
            return ""
        if hasattr(value, "date") and callable(getattr(value, "date")):
            try:
                return value.date().isoformat()
            except Exception:
                pass
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    def review_node(self, card: dict[str, Any], request=None) -> dict[str, Any]:
        origin = self.site_origin(request)
        site = self._site_name()
        item_reviewed: dict[str, Any] = (
            {"@id": f"{origin}/#business"} if origin else {"@type": "BeautySalon", "name": site}
        )
        node: dict[str, Any] = {
            "@type": "Review",
            "name": card.get("title") or "نظر مشتری",
            "reviewBody": (card.get("body") or card.get("excerpt") or "").strip(),
            "author": {
                "@type": "Person",
                "name": card.get("author_display_name") or "مشتری",
            },
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": card.get("rating") or 5,
                "bestRating": 5,
                "worstRating": 1,
            },
            "itemReviewed": item_reviewed,
        }
        published = self._iso_date(card.get("published_at"))
        if published:
            node["datePublished"] = published
        url = card.get("url")
        if url:
            node["url"] = self.absolute_url(url, request)
        return node

    def _attach_review_schema(self, schema: dict[str, Any], request=None) -> None:
        from apps.reviews.services import ReviewService

        payload = ReviewService().homepage_payload(limit=6)
        aggregate = payload.get("aggregate") or {}
        if not aggregate.get("has_reviews"):
            return
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": aggregate["rating_value"],
            "reviewCount": aggregate["review_count"],
            "bestRating": 5,
            "worstRating": 1,
        }
        reviews = payload.get("items") or []
        if reviews:
            schema["review"] = [self.review_node(card, request) for card in reviews]

    def review_item_list_schema(
        self,
        reviews: list[dict[str, Any]],
        request=None,
    ) -> dict[str, Any] | None:
        if not reviews:
            return None
        site = self._site_name()
        elements = []
        for i, card in enumerate(reviews, start=1):
            elements.append(
                {
                    "@type": "ListItem",
                    "position": i,
                    "url": self.absolute_url(card.get("url") or "/reviews/", request),
                    "item": self.review_node(card, request),
                }
            )
        return {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"نظرات مشتریان {site}",
            "url": self.absolute_url("/reviews/", request),
            "numberOfItems": len(elements),
            "itemListElement": elements,
        }

    def review_collection_schema(
        self,
        category: dict[str, Any],
        reviews: list[dict[str, Any]],
        request=None,
    ) -> dict[str, Any]:
        site = self._site_name()
        title = category.get("title") or "نظرات"
        item_list = self.review_item_list_schema(reviews, request) or {
            "@type": "ItemList",
            "numberOfItems": 0,
            "itemListElement": [],
        }
        item_list.pop("@context", None)
        return {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f"نظرات {title} | {site}",
            "url": self.absolute_url(category.get("url") or "/reviews/", request),
            "description": (category.get("lede") or category.get("seo_description") or "").strip(),
            "mainEntity": item_list,
        }

    def review_detail_schema(self, review: dict[str, Any], request=None) -> dict[str, Any]:
        node = self.review_node(review, request)
        node["@context"] = "https://schema.org"
        return node

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
        site = self._site_name()
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
            ("reviews:hub", "weekly", "0.8"),
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

    def review_sitemap_entries(self, request=None) -> list[dict[str, Any]]:
        from apps.reviews.services import ReviewService

        entries: list[dict[str, Any]] = []
        for e in ReviewService().sitemap_entries():
            lastmod = None
            if e.get("updated_at"):
                lastmod = e["updated_at"].date().isoformat()
            entries.append(
                {
                    "loc": self.absolute_url(e["path"], request),
                    "changefreq": "weekly",
                    "priority": "0.6" if e.get("kind") == "detail" else "0.7",
                    "lastmod": lastmod,
                }
            )
        return entries

    def build_sitemap_xml(self, request=None) -> str:
        all_entries = (
            self.static_sitemap_entries(request)
            + self.consultation_sitemap_entries(request)
            + self.magazine_sitemap_entries(request)
            + self.review_sitemap_entries(request)
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
