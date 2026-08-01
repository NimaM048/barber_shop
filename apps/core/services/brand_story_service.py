"""Brand Story service — homepage payload + graceful fallbacks."""

from __future__ import annotations

from django.conf import settings
from django.templatetags.static import static

from apps.core.brand_story import BrandStory, BrandTimelineStep, BrandValue


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


def _fallback_payload() -> dict:
    site = getattr(settings, "SITE_NAME", "صالح ایوبی")
    return {
        "key": "home",
        "edition_label": "",
        "section_label": "",
        "headline": "زیبایی نباید\nتصادفی باشد.",
        "headline_lines": ["زیبایی نباید", "تصادفی باشد."],
        "subtitle": "",
        "story_body": (
            f"{site} یک استودیوی معماری زیبایی است؛ "
            "جایی که ظاهر تصادفی نیست، طراحی می‌شود."
        ),
        "quote_text": "هر جزئیات با قصد آغاز می‌شود؛ نه با شانس.",
        "founder_name": "صالح ایوبی",
        "founder_title": "بنیان‌گذار",
        "quote_signature": "",
        "bg_words": [],
        "portrait": {
            "src": static("images/brand/hero-groom-2-hd.jpg"),
            "webp": static("images/brand/hero-groom-2-hd.webp"),
            "lqip": static("images/brand/hero-groom-2-lqip.jpg"),
            "alt": site,
            "caption": "Isfahan",
            "index": "",
        },
        "timeline_label": "",
        "values_label": "",
        "timeline": [],
        "values": [
            {"title": "دقت", "subtitle": ""},
            {"title": "مهارت", "subtitle": ""},
            {"title": "ظرافت", "subtitle": ""},
        ],
        "cta_primary_label": "رزرو نوبت",
        "cta_primary_href": BrandStory.resolve_href("appointments:create"),
        "cta_secondary_label": "",
        "cta_secondary_href": "",
        "seo_title": "",
        "seo_description": "",
    }


class BrandStoryService:
    """Serialize published brand story content for the homepage."""

    def homepage_payload(self, key: str = "home") -> dict:
        try:
            story = BrandStory.objects.filter(key=key, is_published=True).first()
        except Exception:
            return _fallback_payload()

        if not story:
            return _fallback_payload()

        return self.serialize(story)

    def serialize(self, story: BrandStory) -> dict:
        fallback = _fallback_payload()

        if story.portrait:
            src = story.portrait.url
        else:
            src = _static_or_empty(story.portrait_static)

        bg_words = [
            w
            for w in (
                story.bg_word_1,
                story.bg_word_2,
                story.bg_word_3,
                story.bg_word_4,
            )
            if w
        ]

        timeline = [
            {
                "number": step.number_label,
                "title": step.title,
                "description": step.description,
                "effect": step.portrait_effect or "none",
            }
            for step in BrandTimelineStep.objects.filter(
                story=story, is_active=True
            ).order_by("sort_order", "id")
        ]

        values = [
            {"title": value.title, "subtitle": value.subtitle or ""}
            for value in BrandValue.objects.filter(
                story=story, is_active=True
            ).order_by("sort_order", "id")
        ]

        payload = {
            "key": story.key,
            "edition_label": story.edition_label,
            "section_label": story.section_label,
            "headline": story.headline,
            "headline_lines": _split_lines(story.headline),
            "subtitle": story.subtitle,
            "story_body": story.story_body,
            "quote_text": story.quote_text,
            "founder_name": story.founder_name,
            "founder_title": story.founder_title,
            "quote_signature": story.quote_signature,
            "bg_words": bg_words,
            "portrait": {
                "src": src,
                "webp": _static_or_empty(story.portrait_webp_static),
                "lqip": _static_or_empty(story.portrait_lqip_static),
                "alt": story.portrait_alt
                or getattr(settings, "SITE_NAME", "صالح ایوبی"),
                "caption": story.portrait_caption,
                "index": story.portrait_index or "",
            },
            "timeline_label": story.timeline_label,
            "values_label": story.values_label,
            "timeline": timeline,
            "values": values,
            "cta_primary_label": story.cta_primary_label,
            "cta_primary_href": BrandStory.resolve_href(story.cta_primary_href),
            "cta_secondary_label": story.cta_secondary_label,
            "cta_secondary_href": BrandStory.resolve_href(story.cta_secondary_href),
            "seo_title": story.seo_title or "",
            "seo_description": story.seo_description or "",
        }

        if not payload["headline_lines"]:
            payload["headline"] = fallback["headline"]
            payload["headline_lines"] = fallback["headline_lines"]
        if not payload["portrait"]["src"]:
            payload["portrait"] = fallback["portrait"]
        if not payload["story_body"] and not payload["subtitle"]:
            payload["story_body"] = fallback["story_body"]
        if not payload["values"]:
            payload["values"] = fallback["values"]
        if not payload["cta_primary_href"]:
            payload["cta_primary_href"] = fallback["cta_primary_href"]
            payload["cta_primary_label"] = (
                payload["cta_primary_label"] or fallback["cta_primary_label"]
            )

        return payload
