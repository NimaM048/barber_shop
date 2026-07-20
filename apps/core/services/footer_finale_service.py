"""Footer Finale service — site-wide payload + graceful fallbacks."""

from __future__ import annotations

from django.conf import settings
from django.templatetags.static import static
from django.utils import timezone

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
        "cta_prompt": "سفر خود را آغاز کنید.",
        "cta_primary_label": "دریافت مشاوره تخصصی",
        "cta_primary_href": FooterFinale.resolve_href("consultations:hub"),
        "cta_secondary_label": "رزرو نوبت",
        "cta_secondary_href": FooterFinale.resolve_href("appointments:create"),
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
                "href": "/#services",
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
        ],
        "website": website,
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
            "nav_links": nav_links or fallback["nav_links"],
            "website": finale.website or _site("SITE_WEBSITE"),
            "seo_title": finale.seo_title,
            "seo_description": finale.seo_description,
        }

        if not payload["philosophy_lines"]:
            payload["philosophy"] = fallback["philosophy"]
            payload["philosophy_lines"] = fallback["philosophy_lines"]
        if not payload["cta_statement"]:
            payload["cta_statement"] = fallback["cta_statement"]
        if not payload["cta_prompt"]:
            payload["cta_prompt"] = fallback["cta_prompt"]
        if not payload["cta_primary_href"]:
            payload["cta_primary_href"] = fallback["cta_primary_href"]
            payload["cta_primary_label"] = (
                payload["cta_primary_label"] or fallback["cta_primary_label"]
            )
        if not payload["cta_secondary_href"]:
            payload["cta_secondary_href"] = fallback["cta_secondary_href"]
            payload["cta_secondary_label"] = (
                payload["cta_secondary_label"] or fallback["cta_secondary_label"]
            )
        if not payload["philosophy_caption"]:
            payload["philosophy_caption"] = fallback["philosophy_caption"]

        return payload
