"""Seed CMS defaults for admin-managed site content."""

from django.core.management.base import BaseCommand

from apps.appointments.models import BookingSettings
from apps.core.home_page import HomeAssuranceStep, HomePage, HomeProofBullet
from apps.core.page_content import PageContent
from apps.core.services.home_page_service import DEFAULT_ASSURANCE, DEFAULT_PROOF, DEFAULTS
from apps.core.services.page_content_service import (
    BOOKING_DEFAULTS,
    CATALOG_DEFAULTS,
    CONSULTATIONS_DEFAULTS,
    MAGAZINE_DEFAULTS,
    BARBERS_DEFAULTS,
    PageContentService,
)
from apps.core.site_settings import HeaderNavLink, SiteSettings


class Command(BaseCommand):
    help = "Seed SiteSettings, HomePage, PageContent, and BookingSettings with production defaults."

    def handle(self, *args, **options):
        site, created = SiteSettings.objects.get_or_create(key="site")
        if created or not site.site_name:
            site.site_name = "صالح ایوبی"
            site.site_tagline = "معماری زیبایی"
            site.phone_display = "۰۹۱۳ ۲۲۷ ۰۵۱۹"
            site.address = "اصفهان، مشتاق اول، خیابان ابوالحسن اصفهانی، بعد از کوچه ۲۶"
            site.city = "اصفهان"
            site.hours_text = "شنبه تا پنج‌شنبه · ۱۰ تا ۲۱"
            site.logo_path = "images/brand/logo-signature-800.webp"
            site.is_published = True
            site.save()
            self.stdout.write("SiteSettings seeded.")

        if not site.nav_links.exists():
            defaults = [
                ("خدمات", "core:home#services", 0),
                ("گالری", "core:home#gallery", 1),
                ("نظرات", "reviews:hub", 2),
                ("مجله", "magazine:hub", 3),
                ("مشاوره", "consultations:hub", 4),
            ]
            for label, href, order in defaults:
                HeaderNavLink.objects.create(
                    settings=site,
                    label=label,
                    href=href,
                    sort_order=order,
                )
            self.stdout.write("Header nav links seeded.")
        elif not site.nav_links.filter(href__in=["reviews:hub", "/reviews/"]).exists():
            HeaderNavLink.objects.create(
                settings=site,
                label="نظرات",
                href="reviews:hub",
                sort_order=2,
                is_active=True,
                show_on_mobile=True,
            )
            self.stdout.write("Header nav link for reviews added.")

        home, created = HomePage.objects.get_or_create(key="home")
        if created or not home.hero_title:
            for field, value in DEFAULTS.items():
                setattr(home, field, value)
            home.hero_cta_primary_href = "appointments:create"
            home.hero_cta_secondary_href = "consultations:hub"
            home.services_cta_href = "catalog:list"
            home.is_published = True
            home.save()
            if not home.proof_bullets.exists():
                for i, text in enumerate(DEFAULT_PROOF):
                    HomeProofBullet.objects.create(home_page=home, text=text, sort_order=i)
            if not home.assurance_steps.exists():
                for i, step in enumerate(DEFAULT_ASSURANCE):
                    HomeAssuranceStep.objects.create(
                        home_page=home,
                        number_label=step["number_label"],
                        title=step["title"],
                        description=step["description"],
                        sort_order=i,
                    )
            self.stdout.write("HomePage seeded.")
        else:
            reviews_fields = (
                "reviews_label",
                "reviews_title",
                "reviews_lede",
                "reviews_cta_label",
            )
            changed = [
                field for field in reviews_fields if not getattr(home, field, "")
            ]
            if changed:
                for field in changed:
                    setattr(home, field, DEFAULTS[field])
                home.save(update_fields=[*changed, "updated_at"])
                self.stdout.write("HomePage reviews chrome seeded.")

        for page_key, defaults in PageContentService.DEFAULTS.items():
            content, created = PageContent.objects.get_or_create(page=page_key)
            if created or not content.title:
                for key, val in defaults.items():
                    if key != "content_json":
                        setattr(content, key, val)
                content.content_json = defaults.get("content_json", {})
                content.is_published = True
                content.save()
                self.stdout.write(f"PageContent '{page_key}' seeded.")
            elif not content.content_json:
                content.content_json = defaults.get("content_json", {})
                content.save(update_fields=["content_json", "updated_at"])
                self.stdout.write(f"PageContent '{page_key}' content_json updated.")

        booking_settings, created = BookingSettings.objects.get_or_create(key="site")
        if created:
            booking_settings.confirmation_message = "نوبت شما با موفقیت ثبت شد."
            booking_settings.pending_message = "نوبت شما ثبت شد و در انتظار تأیید است."
            booking_settings.is_active = True
            booking_settings.save()
            self.stdout.write("BookingSettings seeded.")

        self.stdout.write(self.style.SUCCESS("CMS seed complete."))
