"""
Seed the homepage Brand Story section.

Usage:
  python manage.py seed_brand_story
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.brand_story import BrandStory, BrandTimelineStep, BrandValue


STORY = {
    "key": "home",
    "is_published": True,
    "edition_label": "Edition 01",
    "section_label": "فلسفه برند",
    "headline": "زیبایی نباید\nتصادفی باشد.",
    "subtitle": "زیبایی باید طراحی شود — مو، ریش، پوست، داماد.",
    "story_body": (
        "صالح ایوبی یک استودیوی معماری زیبایی است؛ "
        "جایی که ظاهر تصادفی نیست، طراحی می‌شود."
    ),
    "quote_text": "هر جزئیات با قصد آغاز می‌شود؛ نه با شانس.",
    "founder_name": "صالح ایوبی",
    "founder_title": "بنیان‌گذار",
    "quote_signature": "Architecture of Beauty",
    "portrait_static": "images/brand/hero-groom-2-hd.jpg",
    "portrait_webp_static": "images/brand/hero-groom-2-hd.webp",
    "portrait_lqip_static": "images/brand/hero-groom-2-lqip.jpg",
    "portrait_alt": "پرتره استودیویی — معماری زیبایی",
    "portrait_caption": "Studio Portrait — Isfahan",
    "portrait_index": "01",
    "timeline_label": "مسیر معماری زیبایی",
    "values_label": "اصول برند",
    "cta_primary_label": "رزرو مشاوره",
    "cta_primary_href": "appointments:create",
    "cta_secondary_label": "مشاهده نمونه‌کارها",
    "cta_secondary_href": "#gallery",
    "seo_title": "فلسفه برند — معماری زیبایی",
    "seo_description": "زیبایی نباید تصادفی باشد. استودیوی تخصصی داماد، پوست و مو در اصفهان.",
}

TIMELINE = [
    {
        "number_label": "۰۱",
        "title": "مشاوره",
        "description": "گفت‌وگو درباره فرم، مناسبت و استانداردی که می‌خواهید.",
        "portrait_effect": "focus",
        "sort_order": 1,
    },
    {
        "number_label": "۰۲",
        "title": "تحلیل",
        "description": "خوانش چهره، بافت پوست و تعادل بصری — پیش از هر تصمیم.",
        "portrait_effect": "light",
        "sort_order": 2,
    },
    {
        "number_label": "۰۳",
        "title": "طراحی",
        "description": "طراحی استایل به‌عنوان هویت؛ نه یک انتخاب لحظه‌ای.",
        "portrait_effect": "hair",
        "sort_order": 3,
    },
    {
        "number_label": "۰۴",
        "title": "اجرا",
        "description": "اجرای دقیق با ریتم آرام و استاندارد برند.",
        "portrait_effect": "soft",
        "sort_order": 4,
    },
    {
        "number_label": "۰۵",
        "title": "دگرگونی",
        "description": "نتیجه‌ای که دیده می‌شود و احساس می‌شود.",
        "portrait_effect": "bright",
        "sort_order": 5,
    },
    {
        "number_label": "۰۶",
        "title": "اعتماد",
        "description": "حضوری که پیش از حرف، اعتبار می‌سازد.",
        "portrait_effect": "bright",
        "sort_order": 6,
    },
]

VALUES = [
    {"title": "دقت", "subtitle": "Precision", "sort_order": 1},
    {"title": "مهارت", "subtitle": "Craft", "sort_order": 2},
    {"title": "ظرافت", "subtitle": "Elegance", "sort_order": 3},
    {"title": "اعتماد", "subtitle": "Confidence", "sort_order": 4},
    {"title": "هویت", "subtitle": "Identity", "sort_order": 5},
    {"title": "انضباط", "subtitle": "Discipline", "sort_order": 6},
]


class Command(BaseCommand):
    help = "Seed homepage Brand Story content"

    @transaction.atomic
    def handle(self, *args, **options):
        story, created = BrandStory.objects.update_or_create(
            key=STORY["key"],
            defaults={k: v for k, v in STORY.items() if k != "key"},
        )

        # all_objects uses the default manager → real DELETE
        BrandTimelineStep.all_objects.filter(story=story).delete()
        BrandValue.all_objects.filter(story=story).delete()

        BrandTimelineStep.objects.bulk_create(
            [BrandTimelineStep(story=story, **row) for row in TIMELINE]
        )
        BrandValue.objects.bulk_create(
            [BrandValue(story=story, **row) for row in VALUES]
        )

        verb = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} brand story «{story.key}» "
                f"({len(TIMELINE)} steps, {len(VALUES)} values)"
            )
        )
