from django.urls import path

from .views import (
    MagazineArticleAPIView,
    MagazineArticleView,
    MagazineArticlesAPIView,
    MagazineBookmarkAPIView,
    MagazineCommentAPIView,
    MagazineCompleteReadAPIView,
    MagazineHubAPIView,
    MagazineHubView,
    MagazineLikeAPIView,
    MagazineMetaAPIView,
    MagazineRateAPIView,
    MagazineRSSView,
    MagazineSearchAPIView,
    MagazineShareAPIView,
    MagazineSitemapView,
    MagazineViewAPIView,
)

app_name = "magazine"

urlpatterns = [
    path("", MagazineHubView.as_view(), name="hub"),
    path("sitemap.xml", MagazineSitemapView.as_view(), name="sitemap"),
    path("rss.xml", MagazineRSSView.as_view(), name="rss"),
    path("api/hub/", MagazineHubAPIView.as_view(), name="api-hub"),
    path("api/articles/", MagazineArticlesAPIView.as_view(), name="api-articles"),
    path("api/search/", MagazineSearchAPIView.as_view(), name="api-search"),
    path("api/meta/", MagazineMetaAPIView.as_view(), name="api-meta"),
    path("api/articles/<slug:slug>/", MagazineArticleAPIView.as_view(), name="api-article"),
    path("api/articles/<slug:slug>/view/", MagazineViewAPIView.as_view(), name="api-view"),
    path("api/articles/<slug:slug>/like/", MagazineLikeAPIView.as_view(), name="api-like"),
    path(
        "api/articles/<slug:slug>/bookmark/",
        MagazineBookmarkAPIView.as_view(),
        name="api-bookmark",
    ),
    path("api/articles/<slug:slug>/share/", MagazineShareAPIView.as_view(), name="api-share"),
    path(
        "api/articles/<slug:slug>/complete-read/",
        MagazineCompleteReadAPIView.as_view(),
        name="api-complete-read",
    ),
    path("api/articles/<slug:slug>/rate/", MagazineRateAPIView.as_view(), name="api-rate"),
    path(
        "api/articles/<slug:slug>/comments/",
        MagazineCommentAPIView.as_view(),
        name="api-comments",
    ),
    path("<slug:slug>/", MagazineArticleView.as_view(), name="article"),
]
