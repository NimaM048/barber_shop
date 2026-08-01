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
    "edition_label": "",
    "section_label": "",
    "headline": "زیبایی نباید\nتصادفی باشد.",
    "subtitle": "",
    "story_body": (
        "صالح ایوبی یک استودیوی معماری زیبایی است؛ "
        "جایی که ظاهر تصادفی نیست، طراحی می‌شود."
    ),
    "quote_text": "هر جزئیات با قصد آغاز می‌شود؛ نه با شانس.",
    "founder_name": "صالح ایوبی",
    "founder_title": "بنیان‌گذار",
    "quote_signature": "",
    "bg_word_1": "",
    "bg_word_2": "",
    "bg_word_3": "",
    "bg_word_4": "",
    "portrait_static": "images/brand/hero-groom-2-hd.jpg",
    "portrait_webp_static": "images/brand/hero-groom-2-hd.webp",
    "portrait_lqip_static": "images/brand/hero-groom-2-lqip.jpg",
    "portrait_alt": "پرتره استودیویی — معماری زیبایی",
    "portrait_caption": "Isfahan",
    "portrait_index": "",
    "timeline_label": "",
    "values_label": "",
    "cta_primary_label": "رزرو نوبت",
    "cta_primary_href": "appointments:create",
    "cta_secondary_label": "",
    "cta_secondary_href": "",
    "seo_title": "فلسفه برند — معماری زیبایی",
    "seo_description": "زیبایی نباید تصادفی باشد. استودیوی تخصصی داماد، پوست و مو در اصفهان.",
}

VALUES = [
    {"title": "دقت", "subtitle": "", "sort_order": 1},
    {"title": "مهارت", "subtitle": "", "sort_order": 2},
    {"title": "ظرافت", "subtitle": "", "sort_order": 3},
]


class Command(BaseCommand):
    help = "Seed homepage Brand Story content"

    @transaction.atomic
    def handle(self, *args, **options):
        story, created = BrandStory.objects.update_or_create(
            key=STORY["key"],
            defaults={k: v for k, v in STORY.items() if k != "key"},
        )

        BrandTimelineStep.all_objects.filter(story=story).delete()
        BrandValue.all_objects.filter(story=story).delete()

        BrandValue.objects.bulk_create(
            [BrandValue(story=story, **row) for row in VALUES]
        )

        verb = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} brand story «{story.key}» "
                f"(0 steps, {len(VALUES)} values)"
            )
        )
