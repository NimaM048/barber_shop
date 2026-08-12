"""Footer Finale service — site-wide payload + graceful fallbacks."""

from __future__ import annotations

from django.conf import settings
from django.templatetags.static import static
from django.utils import timezone
from urllib.parse import quote_plus

from apps.core.footer_finale import FooterFinale, FooterNavLink

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _to_persian(value: str | int) -> str:
    return str(value).translate(PERSIAN_DIGITS)


def _static_or_empty(path: str) -> str:
    if not path:
        return ""
    if path.startswith(("http://", "https://", "/media/", "/static/")):
        return path
    return static(path)


def _split_lines(text: str) -> list[str]:
    if not text:
        return []
    return [line.strip() for line in text.replace("\r\n", "\n").split("\n") if line.strip()]


def _site(attr: str, default: str = "") -> str:
    return getattr(settings, attr, default) or default


def _wa_digits(phone: str) -> str:
    """Build WhatsApp path digits from a local Iranian mobile if needed."""
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    if not digits:
        return ""
    if digits.startswith("98"):
        return digits
    if digits.startswith("0"):
        return f"98{digits[1:]}"
    return digits


def _location_payload(address: str, hours: str = "") -> dict:
    """Premium location block — Leaflet map + Google Maps deep links."""
    from apps.core.services.site_settings_service import SiteSettingsService

    chrome = SiteSettingsService().location_chrome()
    branding = SiteSettingsService().branding()
    lat = branding["SITE_LAT"]
    lng = branding["SITE_LNG"]
    zoom = int(branding.get("SITE_MAP_ZOOM", 16) or 16)
    query = f"{lat},{lng}"
    maps_query = quote_plus(address) if address else query
    hours_value = hours or branding["SITE_HOURS_TEXT"] or "شنبه تا پنج‌شنبه · ۱۰ تا ۲۱"
    site = branding["SITE_NAME"]
    maps_place = (branding["SITE_GOOGLE_MAPS_URL"] or "").strip()
    gbp_url = (branding["SITE_GBP_URL"] or "").strip()
    maps_url = maps_place or (
        f"https://www.google.com/maps/search/?api=1&query={maps_query}"
    )

    return {
        "show": bool(address),
        "eyebrow": chrome["eyebrow"],
        "title_find": "Find",
        "title_us": "Us",
        "title_fa": chrome["title_fa"],
        "badge": chrome["badge"],
        "lede": chrome["lede"],
        "city": branding["SITE_CITY"],
        "address": address,
        "address_parts": [
            {"role": "district", "text": chrome["district"]},
            {"role": "street", "text": chrome["street"]},
            {"role": "cue", "text": chrome["cue"]},
        ],
        "address_lines": [
            chrome["district"],
            chrome["street"],
            chrome["cue"],
        ],
        "hours_label": "ساعات",
        "hours": hours_value,
        "availability_label": "نوبت",
        "availability": chrome["availability"],
        "cta_directions": chrome["cta_directions"],
        "cta_maps": chrome["cta_maps"],
        "cta_copy": chrome["cta_copy"],
        "cta_gbp": chrome["cta_gbp"],
        "gbp_url": gbp_url,
        "lat": lat,
        "lng": lng,
        "zoom": zoom,
        "marker_label": site,
        "maps_url": maps_url,
        "directions_url": (
            f"https://www.google.com/maps/dir/?api=1&destination={query}"
            f"&travelmode=driving"
        ),
        "embed_url": (
            f"https://www.google.com/maps?q={query}&z={zoom}&hl=fa&output=embed"
        ),
    }


def _fallback_payload() -> dict:
    site = _site("SITE_NAME", "صالح ایوبی")
    phone = _site("SITE_PHONE", "09132270519")
    phone_display = _site("SITE_PHONE_DISPLAY", "۰۹۱۳ ۲۲۷ ۰۵۱۹")
    instagram = _site("SITE_INSTAGRAM", "saleh_ayoobi_academy")
    website = _site("SITE_WEBSITE", "salehayoubi.com")
    address = _site(
        "SITE_ADDRESS",
        "اصفهان، مشتاق اول، خیابان ابوالحسن اصفهانی، بعد از کوچه ۲۶",
    )
    year = _to_persian(timezone.now().year)

    return {
        "key": "site",
        "edition_label": "Finale 01",
        "section_label": "پایان",
        "aria_label": "پایان تجربه برند",
        "philosophy": "زیبایی،\nاگر معماری نشود،\nتصادفی می‌ماند.",
        "philosophy_lines": ["زیبایی،", "اگر معماری نشود،", "تصادفی می‌ماند."],
        "philosophy_caption": "Architecture of Beauty",
        "bg_word": "ARCHITECTURE",
        "cta_statement": "هر دگرگونی با یک تصمیم آغاز می‌شود.",
        "cta_prompt": "",
        "cta_primary_label": "رزرو نوبت",
        "cta_primary_href": FooterFinale.resolve_href("appointments:create"),
        "cta_secondary_label": "",
        "cta_secondary_href": "",
        "contacts": [
            {
                "key": "phone",
                "label": "تلفن",
                "value": phone_display,
                "href": f"tel:{phone}" if phone else "",
                "external": False,
                "ltr": True,
            },
            {
                "key": "instagram",
                "label": "اینستاگرام",
                "value": f"@{instagram}" if instagram else "",
                "href": f"https://instagram.com/{instagram}" if instagram else "",
                "external": True,
                "ltr": True,
            },
            {
                "key": "whatsapp",
                "label": "واتساپ",
                "value": phone_display,
                "href": f"https://wa.me/{_wa_digits(phone)}" if phone else "",
                "external": True,
                "ltr": True,
            },
            {
                "key": "website",
                "label": "وب‌سایت",
                "value": website,
                "href": f"https://{website}" if website else "",
                "external": True,
                "ltr": True,
            },
            {
                "key": "address",
                "label": "آدرس",
                "value": address,
                "href": "",
                "external": False,
                "ltr": False,
            },
            {
                "key": "hours",
                "label": "ساعات کاری",
                "value": "شنبه تا پنج‌شنبه · ۱۰ تا ۲۱",
                "href": "",
                "external": False,
                "ltr": False,
            },
        ],
        "contact_caption": "ارتباط",
        "logo_src": static("images/brand/logo-signature.webp"),
        "logo_alt": site,
        "signature": "Architecture of Beauty",
        "show_founder": True,
        "founder_name": site,
        "founder_title": "بنیان‌گذار",
        "founded_year": year,
        "copyright": f"© {year} {site}",
        "show_navigation": True,
        "nav_links": [
            {
                "label": "خدمات",
                "href": FooterFinale.resolve_href("catalog:list"),
                "external": False,
            },
            {
                "label": "نمونه‌کارها",
                "href": "/#gallery",
                "external": False,
            },
            {
                "label": "مجله",
                "href": FooterFinale.resolve_href("magazine:hub"),
                "external": False,
            },
            {
                "label": "نظرات",
                "href": FooterFinale.resolve_href("reviews:hub"),
                "external": False,
            },
            {
                "label": "مشاوره",
                "href": FooterFinale.resolve_href("consultations:hub"),
                "external": False,
            },
        ],
        "website": website,
        "location": _location_payload(address),
        "seo_title": "",
        "seo_description": "",
    }


def _build_contacts(finale: FooterFinale, fallback: dict) -> list[dict]:
    phone = finale.phone or _site("SITE_PHONE")
    phone_display = finale.phone_display or _site("SITE_PHONE_DISPLAY") or phone
    instagram = finale.instagram or _site("SITE_INSTAGRAM")
    website = finale.website or _site("SITE_WEBSITE")
    address = finale.address or _site("SITE_ADDRESS")
    whatsapp = finale.whatsapp or _wa_digits(phone)

    items: list[dict] = []

    if finale.show_phone and (phone or phone_display):
        items.append(
            {
                "key": "phone",
                "label": finale.phone_label or "تلفن",
                "value": phone_display or phone,
                "href": f"tel:{phone}" if phone else "",
                "external": False,
                "ltr": True,
            }
        )

    if finale.show_instagram and instagram:
        items.append(
            {
                "key": "instagram",
                "label": finale.instagram_label or "اینستاگرام",
                "value": f"@{instagram.lstrip('@')}",
                "href": f"https://instagram.com/{instagram.lstrip('@')}",
                "external": True,
                "ltr": True,
            }
        )

    if finale.show_whatsapp and whatsapp:
        items.append(
            {
                "key": "whatsapp",
                "label": finale.whatsapp_label or "واتساپ",
                "value": phone_display or whatsapp,
                "href": f"https://wa.me/{_wa_digits(whatsapp)}",
                "external": True,
                "ltr": True,
            }
        )

    if finale.show_telegram and finale.telegram:
        handle = finale.telegram.lstrip("@")
        items.append(
            {
                "key": "telegram",
                "label": finale.telegram_label or "تلگرام",
                "value": f"@{handle}",
                "href": f"https://t.me/{handle}",
                "external": True,
                "ltr": True,
            }
        )

    if finale.show_email and finale.email:
        items.append(
            {
                "key": "email",
                "label": finale.email_label or "ایمیل",
                "value": finale.email,
                "href": f"mailto:{finale.email}",
                "external": False,
                "ltr": True,
            }
        )

    if finale.show_website and website:
        href = website if website.startswith("http") else f"https://{website}"
        display = website.replace("https://", "").replace("http://", "")
        items.append(
            {
                "key": "website",
                "label": finale.website_label or "وب‌سایت",
                "value": display,
                "href": href,
                "external": True,
                "ltr": True,
            }
        )

    if finale.show_address and address:
        items.append(
            {
                "key": "address",
                "label": finale.address_label or "آدرس",
                "value": address,
                "href": "",
                "external": False,
                "ltr": False,
            }
        )

    if finale.show_hours and finale.working_hours:
        items.append(
            {
                "key": "hours",
                "label": finale.hours_label or "ساعات کاری",
                "value": finale.working_hours,
                "href": "",
                "external": False,
                "ltr": False,
            }
        )

    return items or fallback["contacts"]


def _ensure_nav_links(nav_links: list[dict]) -> list[dict]:
    """Keep footer nav complete without requiring a re-seed."""
    extras = (
        ("نظرات", "reviews:hub"),
        ("مشاوره", "consultations:hub"),
    )
    hrefs = {item.get("href") for item in nav_links}
    labels = {item.get("label") for item in nav_links}
    for label, name in extras:
        href = FooterFinale.resolve_href(name)
        if not href or href == name or href in hrefs or label in labels:
            continue
        nav_links.append({"label": label, "href": href, "external": False})
        hrefs.add(href)
        labels.add(label)
    return nav_links


class FooterFinaleService:
    """Serialize published footer finale content for all pages."""

    def site_payload(self, key: str = "site") -> dict:
        try:
            finale = FooterFinale.objects.filter(key=key, is_published=True).first()
        except Exception:
            return _fallback_payload()

        if not finale:
            return _fallback_payload()

        return self.serialize(finale)

    def serialize(self, finale: FooterFinale) -> dict:
        fallback = _fallback_payload()
        site = _site("SITE_NAME", "صالح ایوبی")
        founded_year = finale.founded_year or ""
        current_year = str(timezone.now().year)

        if finale.logo:
            logo_src = finale.logo.url
        else:
            logo_src = _static_or_empty(finale.logo_static) or fallback["logo_src"]

        nav_links = [
            {
                "label": link.label,
                "href": link.resolved_href,
                "external": link.open_in_new_tab,
            }
            for link in FooterNavLink.objects.filter(footer=finale, is_active=True)
        ]
        if nav_links:
            nav_links = _ensure_nav_links(nav_links)
        else:
            nav_links = fallback["nav_links"]

        copyright_text = finale.copyright_text.strip() if finale.copyright_text else ""
        if not copyright_text:
            copyright_text = f"© {_to_persian(current_year)} {site}"

        payload = {
            "key": finale.key,
            "edition_label": finale.edition_label or fallback["edition_label"],
            "section_label": finale.section_label or fallback["section_label"],
            "aria_label": finale.aria_label or fallback["aria_label"],
            "philosophy": finale.philosophy,
            "philosophy_lines": _split_lines(finale.philosophy),
            "philosophy_caption": finale.philosophy_caption,
            "bg_word": finale.bg_word or fallback["bg_word"],
            "cta_statement": finale.cta_statement,
            "cta_prompt": finale.cta_prompt,
            "cta_primary_label": finale.cta_primary_label,
            "cta_primary_href": FooterFinale.resolve_href(finale.cta_primary_href),
            "cta_secondary_label": finale.cta_secondary_label,
            "cta_secondary_href": FooterFinale.resolve_href(finale.cta_secondary_href),
            "contacts": _build_contacts(finale, fallback),
            "contact_caption": finale.contact_caption or fallback["contact_caption"],
            "logo_src": logo_src,
            "logo_alt": finale.logo_alt or site,
            "signature": finale.signature or fallback["signature"],
            "show_founder": finale.show_founder,
            "founder_name": finale.founder_name or site,
            "founder_title": finale.founder_title,
            "founded_year": founded_year or _to_persian(current_year),
            "copyright": copyright_text,
            "show_navigation": finale.show_navigation,
            "nav_links": nav_links,
            "website": finale.website or _site("SITE_WEBSITE"),
            "location": _location_payload(
                finale.address or _site("SITE_ADDRESS"),
                finale.working_hours or "",
            ),
            "seo_title": finale.seo_title,
            "seo_description": finale.seo_description,
        }

        if not payload["philosophy_lines"]:
            payload["philosophy"] = fallback["philosophy"]
            payload["philosophy_lines"] = fallback["philosophy_lines"]
        if not payload["cta_statement"]:
            payload["cta_statement"] = fallback["cta_statement"]
        if not payload["cta_primary_href"]:
            payload["cta_primary_href"] = fallback["cta_primary_href"]
            payload["cta_primary_label"] = (
                payload["cta_primary_label"] or fallback["cta_primary_label"]
            )

        return payload
