"""
Seed the site-wide Footer Finale (closing brand chapter).

Usage:
  python manage.py seed_footer_finale
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.footer_finale import FooterFinale, FooterNavLink


FINALE = {
    "key": "site",
    "is_published": True,
    "edition_label": "Finale 01",
    "section_label": "پایان",
    "aria_label": "پایان تجربه برند",
    "philosophy": "زیبایی،\nاگر معماری نشود،\nتصادفی می‌ماند.",
    "philosophy_caption": "Architecture of Beauty",
    "bg_word": "ARCHITECTURE",
    "cta_statement": "هر دگرگونی با یک تصمیم آغاز می‌شود.",
    "cta_prompt": "",
    "cta_primary_label": "رزرو نوبت",
    "cta_primary_href": "appointments:create",
    "cta_secondary_label": "",
    "cta_secondary_href": "",
    "show_phone": True,
    "phone": "",
    "phone_display": "",
    "phone_label": "تلفن",
    "show_whatsapp": True,
    "whatsapp": "",
    "whatsapp_label": "واتساپ",
    "show_instagram": True,
    "instagram": "",
    "instagram_label": "اینستاگرام",
    "show_telegram": False,
    "telegram": "",
    "telegram_label": "تلگرام",
    "show_email": False,
    "email": "",
    "email_label": "ایمیل",
    "show_website": True,
    "website": "",
    "website_label": "وب‌سایت",
    "show_address": True,
    "address": "",
    "address_label": "آدرس",
    "show_hours": True,
    "working_hours": "شنبه تا پنج‌شنبه · ۱۰ تا ۲۱",
    "hours_label": "ساعات کاری",
    "contact_caption": "ارتباط",
    "logo_static": "images/brand/logo-signature.webp",
    "logo_alt": "",
    "signature": "Architecture of Beauty",
    "show_founder": True,
    "founder_name": "صالح ایوبی",
    "founder_title": "بنیان‌گذار",
    "founded_year": "۲۰۱۸",
    "copyright_text": "",
    "show_navigation": True,
    "seo_title": "پایان — معماری زیبایی",
    "seo_description": "زیبایی اگر معماری نشود، تصادفی می‌ماند.",
}

NAV_LINKS = [
    {"label": "خدمات", "href": "/#services", "sort_order": 1},
    {"label": "نمونه‌کارها", "href": "/#gallery", "sort_order": 2},
    {"label": "مجله", "href": "magazine:hub", "sort_order": 3},
    {"label": "نظرات", "href": "reviews:hub", "sort_order": 4},
    {"label": "مشاوره", "href": "consultations:hub", "sort_order": 5},
]


class Command(BaseCommand):
    help = "Seed the Footer Finale CMS content"

    @transaction.atomic
    def handle(self, *args, **options):
        finale, created = FooterFinale.objects.update_or_create(
            key=FINALE["key"],
            defaults={k: v for k, v in FINALE.items() if k != "key"},
        )

        FooterNavLink.all_objects.filter(footer=finale).delete()
        FooterNavLink.objects.bulk_create(
            [
                FooterNavLink(footer=finale, is_active=True, **item)
                for item in NAV_LINKS
            ]
        )

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} Footer Finale · {finale.key}"))
