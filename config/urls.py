from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("services/", include("apps.catalog.urls")),
    path("appointments/", include("apps.appointments.urls")),
    path("consultations/", include("apps.consultations.urls")),
    path("magazine/", include("apps.magazine.urls")),
]

handler404 = "apps.core.views.page_not_found"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
