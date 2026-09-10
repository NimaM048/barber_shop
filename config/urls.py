from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("services/", include("apps.catalog.urls")),
    path("appointments/", include("apps.appointments.urls")),
    path("consultations/", include("apps.consultations.urls")),
    path("magazine/", include("apps.magazine.urls")),
    path("reviews/", include("apps.reviews.urls")),
]

handler404 = "apps.core.views.page_not_found"

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
