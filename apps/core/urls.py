from django.urls import path

from .views import HomeView, RobotsTxtView, SitemapXmlView

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("robots.txt", RobotsTxtView.as_view(), name="robots"),
    path("sitemap.xml", SitemapXmlView.as_view(), name="sitemap"),
]
