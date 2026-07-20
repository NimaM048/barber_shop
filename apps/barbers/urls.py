from django.urls import path

from .views import BarberDetailView, BarberListView

app_name = "barbers"

urlpatterns = [
    path("", BarberListView.as_view(), name="list"),
    path("<int:pk>/", BarberDetailView.as_view(), name="detail"),
]
