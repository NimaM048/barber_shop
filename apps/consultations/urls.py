from django.urls import path

from .views import (
    ConsultationBookingSummaryAPIView,
    ConsultationCategoriesAPIView,
    ConsultationDetailAPIView,
    ConsultationDetailView,
    ConsultationHubView,
    ConsultationTicketCreateAPIView,
)

app_name = "consultations"

urlpatterns = [
    path("", ConsultationHubView.as_view(), name="hub"),
    path("api/categories/", ConsultationCategoriesAPIView.as_view(), name="api-categories"),
    path(
        "api/categories/<slug:key>/",
        ConsultationDetailAPIView.as_view(),
        name="api-detail",
    ),
    path(
        "api/booking-summary/<slug:service_key>/",
        ConsultationBookingSummaryAPIView.as_view(),
        name="api-booking-summary",
    ),
    path("api/tickets/", ConsultationTicketCreateAPIView.as_view(), name="api-tickets"),
    path("<slug:key>/", ConsultationDetailView.as_view(), name="detail"),
]
