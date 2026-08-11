from django.urls import path

from .views import (
    BookingCalendarAPIView,
    BookingCancelAPIView,
    BookingCreateAPIView,
    BookingLookupAPIView,
    BookingPageView,
    BookingServiceDetailAPIView,
    BookingServicesAPIView,
    BookingSettingsAPIView,
    BookingSlotsAPIView,
)

app_name = "appointments"

urlpatterns = [
    path("new/", BookingPageView.as_view(), name="create"),
    path("api/services/", BookingServicesAPIView.as_view(), name="api-services"),
    path(
        "api/services/<slug:key>/",
        BookingServiceDetailAPIView.as_view(),
        name="api-service-detail",
    ),
    path(
        "api/services/<slug:key>/calendar/",
        BookingCalendarAPIView.as_view(),
        name="api-calendar",
    ),
    path(
        "api/services/<slug:key>/slots/",
        BookingSlotsAPIView.as_view(),
        name="api-slots",
    ),
    path("api/book/", BookingCreateAPIView.as_view(), name="api-book"),
    path("api/settings/", BookingSettingsAPIView.as_view(), name="api-settings"),
    path("api/lookup/", BookingLookupAPIView.as_view(), name="api-lookup"),
    path("api/cancel/", BookingCancelAPIView.as_view(), name="api-cancel"),
]
