from django.urls import path

from .views import ReviewCategoryView, ReviewDetailView, ReviewHubView

app_name = "reviews"

urlpatterns = [
    path("", ReviewHubView.as_view(), name="hub"),
    path("<slug:category>/", ReviewCategoryView.as_view(), name="category"),
    path("<slug:category>/<slug:slug>/", ReviewDetailView.as_view(), name="detail"),
]
