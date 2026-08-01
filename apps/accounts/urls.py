from django.urls import path

app_name = "accounts"

# Customer auth routes removed — guest booking only.
# Keep app_name for reverse lookups / admin domain; User model stays.
urlpatterns: list = []
