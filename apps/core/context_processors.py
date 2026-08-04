from django.conf import settings

from apps.core.services.footer_finale_service import FooterFinaleService
from apps.core.services.seo_service import SeoService


def site_settings(request):
    """Expose site-wide branding, footer finale, and SEO defaults to all templates."""
    seo = SeoService()
    verification = getattr(settings, "GOOGLE_SITE_VERIFICATION", "") or ""
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "صالح ایوبی"),
        "SITE_TAGLINE": getattr(settings, "SITE_TAGLINE", "معماری زیبایی"),
        "SITE_SUBTITLE": getattr(settings, "SITE_SUBTITLE", ""),
        "SITE_PHONE": getattr(settings, "SITE_PHONE", ""),
        "SITE_PHONE_DISPLAY": getattr(settings, "SITE_PHONE_DISPLAY", ""),
        "SITE_ADDRESS": getattr(settings, "SITE_ADDRESS", ""),
        "SITE_LAT": getattr(settings, "SITE_LAT", 32.6412),
        "SITE_LNG": getattr(settings, "SITE_LNG", 51.6902),
        "SITE_INSTAGRAM": getattr(settings, "SITE_INSTAGRAM", ""),
        "SITE_WEBSITE": getattr(settings, "SITE_WEBSITE", ""),
        "SITE_HOURS_TEXT": getattr(settings, "SITE_HOURS_TEXT", ""),
        "SITE_GOOGLE_MAPS_URL": getattr(settings, "SITE_GOOGLE_MAPS_URL", ""),
        "SITE_GBP_URL": getattr(settings, "SITE_GBP_URL", ""),
        "SITE_ORIGIN": seo.site_origin(request),
        "DEFAULT_OG_IMAGE": seo.default_og_image(request),
        "CANONICAL_URL": seo.canonical_url(request),
        "GOOGLE_SITE_VERIFICATION": verification,
        "footer_finale": FooterFinaleService().site_payload(),
    }
