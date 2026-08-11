from django.conf import settings

from apps.core.services.footer_finale_service import FooterFinaleService
from apps.core.services.seo_service import SeoService
from apps.core.services.site_settings_service import SiteSettingsService


def site_settings(request):
    """Expose site-wide branding, footer finale, and SEO defaults to all templates."""
    seo = SeoService()
    site_svc = SiteSettingsService()
    branding = site_svc.branding()
    verification = getattr(settings, "GOOGLE_SITE_VERIFICATION", "") or ""
    header = site_svc.header_payload()
    return {
        **branding,
        "SITE_ORIGIN": seo.site_origin(request),
        "DEFAULT_OG_IMAGE": seo.default_og_image(request),
        "CANONICAL_URL": seo.canonical_url(request),
        "GOOGLE_SITE_VERIFICATION": verification,
        "footer_finale": FooterFinaleService().site_payload(),
        "header_nav": header,
    }
