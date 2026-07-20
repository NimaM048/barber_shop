from django.conf import settings

from apps.core.services.footer_finale_service import FooterFinaleService


def site_settings(request):
    """Expose site-wide branding and footer finale to all templates."""
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "صالح ایوبی"),
        "SITE_TAGLINE": getattr(settings, "SITE_TAGLINE", "معماری زیبایی"),
        "SITE_SUBTITLE": getattr(settings, "SITE_SUBTITLE", ""),
        "SITE_PHONE": getattr(settings, "SITE_PHONE", ""),
        "SITE_PHONE_DISPLAY": getattr(settings, "SITE_PHONE_DISPLAY", ""),
        "SITE_ADDRESS": getattr(settings, "SITE_ADDRESS", ""),
        "SITE_INSTAGRAM": getattr(settings, "SITE_INSTAGRAM", ""),
        "SITE_WEBSITE": getattr(settings, "SITE_WEBSITE", ""),
        "footer_finale": FooterFinaleService().site_payload(),
    }
