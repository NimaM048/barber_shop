"""SSR pages for the reviews hub, category collections, and detail narratives."""

from __future__ import annotations

from django.shortcuts import render
from django.views import View

from apps.core.exceptions import NotFoundError
from apps.core.services import SeoService
from apps.core.services.page_content_service import PageContentService

from apps.reviews.services import ReviewService


class ReviewHubView(View):
    template_name = "reviews/hub.html"

    def get(self, request):
        seo = SeoService()
        service = ReviewService()
        payload = service.get_hub_payload()
        page_content = PageContentService().get("reviews")
        page_seo = seo.reviews_hub_meta()
        schemas = [
            seo.breadcrumb_schema(
                [
                    {"name": "خانه", "path": "/"},
                    {"name": "نظرات", "path": "/reviews/"},
                ],
                request,
            ),
            seo.local_business_schema(request, include_reviews=True),
        ]
        item_list = seo.review_item_list_schema(payload["reviews"], request)
        if item_list:
            schemas.append(item_list)
        return render(
            request,
            self.template_name,
            {
                "page_content": page_content,
                "page_seo": page_seo,
                "hub": payload,
                "schema_json": seo.dumps(schemas),
            },
        )


class ReviewCategoryView(View):
    template_name = "reviews/category.html"

    def get(self, request, category):
        seo = SeoService()
        service = ReviewService()
        try:
            payload = service.get_category_payload(category)
        except NotFoundError:
            return render(request, "reviews/not_found.html", status=404)

        cat = payload["category"]
        page_content = PageContentService().get("reviews")
        page_seo = seo.reviews_category_meta(cat)
        schemas = [
            seo.breadcrumb_schema(
                [
                    {"name": "خانه", "path": "/"},
                    {"name": "نظرات", "path": "/reviews/"},
                    {"name": cat["title"], "path": cat["url"]},
                ],
                request,
            ),
            seo.review_collection_schema(cat, payload["reviews"], request),
        ]
        return render(
            request,
            self.template_name,
            {
                "page_content": page_content,
                "page_seo": page_seo,
                "hub": payload,
                "category": cat,
                "schema_json": seo.dumps(schemas),
            },
        )


class ReviewDetailView(View):
    template_name = "reviews/detail.html"

    def get(self, request, category, slug):
        seo = SeoService()
        service = ReviewService()
        try:
            payload = service.get_detail_payload(category, slug)
        except NotFoundError:
            return render(request, "reviews/not_found.html", status=404)

        review = payload["review"]
        page_seo = seo.reviews_detail_meta(review)
        schemas = [
            seo.breadcrumb_schema(
                [
                    {"name": "خانه", "path": "/"},
                    {"name": "نظرات", "path": "/reviews/"},
                    {
                        "name": review["category"]["title"],
                        "path": review["category"]["url"],
                    },
                    {"name": review["title"], "path": review["url"]},
                ],
                request,
            ),
            seo.review_detail_schema(review, request),
        ]
        return render(
            request,
            self.template_name,
            {
                "page_seo": page_seo,
                "review": review,
                "related": payload["related"],
                "booking_href": payload["booking_href"],
                "consultation_href": payload["consultation_href"],
                "schema_json": seo.dumps(schemas),
            },
        )
