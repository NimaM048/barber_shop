"""Page + JSON API for the magazine / beauty encyclopedia."""

from __future__ import annotations

import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import feedgenerator

from apps.core.exceptions import DomainError, NotFoundError, ValidationError
from apps.core.services import SeoService

from apps.magazine.services import MagazineService


def _json_error(exc: Exception, status: int = 400) -> JsonResponse:
    message = getattr(exc, "message", None) or str(exc) or "خطایی رخ داد."
    return JsonResponse({"ok": False, "error": message}, status=status)


def _status_for(exc: Exception) -> int:
    if isinstance(exc, NotFoundError):
        return 404
    if isinstance(exc, ValidationError):
        return 400
    if isinstance(exc, DomainError):
        return 400
    return 500


def _ensure_session(request) -> str:
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key or ""


def _parse_json(request) -> dict:
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise ValidationError("درخواست نامعتبر است.") from exc


# ── Pages ──────────────────────────────────────────────────────────


class MagazineHubView(View):
    template_name = "magazine/hub.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        service = MagazineService()
        hub = service.get_hub_payload()

        sort = request.GET.get("sort", "newest") or "newest"
        category = request.GET.get("category", "") or ""
        tag = request.GET.get("tag", "") or ""
        q = request.GET.get("q", "") or ""
        try:
            page = max(1, int(request.GET.get("page", "1") or "1"))
        except ValueError:
            page = 1

        listing = service.list_articles(
            category=category,
            tag=tag,
            q=q,
            sort=sort,
            page=page,
            page_size=9,
        )

        return render(
            request,
            self.template_name,
            {
                "api_base": "/magazine/api",
                "hub": hub,
                "listing": listing,
                "filters": {
                    "category": category,
                    "tag": tag,
                    "q": q,
                    "sort": sort,
                    "page": page,
                },
            },
        )


class MagazineArticleView(View):
    template_name = "magazine/article.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, slug):
        service = MagazineService()
        try:
            payload = service.get_article_detail(slug, session_key=_ensure_session(request))
        except NotFoundError:
            return render(request, "magazine/not_found.html", status=404)

        article = payload["article"]
        seo = dict(article.get("seo", {}))
        seo_helper = SeoService()
        if seo.get("og_image"):
            seo["og_image"] = seo_helper.absolute_url(seo["og_image"], request)
        if seo.get("canonical_url"):
            seo["canonical_url"] = seo_helper.absolute_url(seo["canonical_url"], request)
        else:
            seo["canonical_url"] = seo_helper.canonical_url(request)
        schema = seo.get("schema") or {}
        if isinstance(schema, dict):
            # Ensure absolute image/url in Article schema when present
            if schema.get("image"):
                schema = {**schema, "image": seo_helper.absolute_url(schema["image"], request)}
            if schema.get("mainEntityOfPage"):
                schema = {
                    **schema,
                    "mainEntityOfPage": seo_helper.absolute_url(
                        schema["mainEntityOfPage"], request
                    ),
                }
            schema_json = json.dumps(schema, ensure_ascii=False)
        else:
            schema_json = str(schema)
        return render(
            request,
            self.template_name,
            {
                "api_base": "/magazine/api",
                "slug": slug,
                "initial": payload,
                "article": article,
                "seo": seo,
                "schema_json": schema_json,
                "related": payload.get("related", []),
                "conversion": payload.get("conversion", {}),
                "share": payload.get("share", {}),
                "engagement": payload.get("engagement", {}),
            },
        )


class MagazineSitemapView(View):
    def get(self, request):
        entries = MagazineService().sitemap_entries()
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        base = request.build_absolute_uri("/magazine/").rstrip("/")
        lines.append(f"<url><loc>{base}/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>")
        for e in entries:
            loc = f"{base}/{e['slug']}/"
            lastmod = ""
            if e.get("updated_at"):
                lastmod = f"<lastmod>{e['updated_at'].date().isoformat()}</lastmod>"
            lines.append(
                f"<url><loc>{loc}</loc>{lastmod}<changefreq>weekly</changefreq><priority>0.8</priority></url>"
            )
        lines.append("</urlset>")
        return HttpResponse("\n".join(lines), content_type="application/xml; charset=utf-8")


class MagazineRSSView(View):
    def get(self, request):
        from django.conf import settings

        feed = feedgenerator.Rss201rev2Feed(
            title=f"مجله {getattr(settings, 'SITE_NAME', 'صالح ایوبی')}",
            link=request.build_absolute_uri("/magazine/"),
            description="دانشنامه زیبایی — مقالات تخصصی داماد، پوست و مو",
            language="fa",
        )
        for item in MagazineService().rss_entries(20):
            feed.add_item(
                title=item["title"],
                link=request.build_absolute_uri(item["url"]),
                description=item["excerpt"],
                unique_id=item["slug"],
                pubdate=None,
            )
        return HttpResponse(feed.writeString("utf-8"), content_type="application/rss+xml; charset=utf-8")


# ── API ────────────────────────────────────────────────────────────


class MagazineHubAPIView(View):
    def get(self, request):
        try:
            data = MagazineService().get_hub_payload()
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineArticlesAPIView(View):
    def get(self, request):
        try:
            reading_min = request.GET.get("reading_min")
            reading_max = request.GET.get("reading_max")
            data = MagazineService().list_articles(
                category=request.GET.get("category", ""),
                tag=request.GET.get("tag", ""),
                author=request.GET.get("author", ""),
                q=request.GET.get("q", ""),
                sort=request.GET.get("sort", "newest"),
                reading_min=int(reading_min) if reading_min and reading_min.isdigit() else None,
                reading_max=int(reading_max) if reading_max and reading_max.isdigit() else None,
                page=int(request.GET.get("page", "1") or "1"),
                page_size=int(request.GET.get("page_size", "12") or "12"),
            )
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))
        except ValueError:
            return _json_error(ValidationError("پارامترهای فیلتر نامعتبر است."))


class MagazineSearchAPIView(View):
    def get(self, request):
        try:
            data = MagazineService().search_autocomplete(request.GET.get("q", ""))
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineMetaAPIView(View):
    def get(self, request):
        try:
            data = MagazineService().list_filter_meta()
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineArticleAPIView(View):
    def get(self, request, slug):
        try:
            data = MagazineService().get_article_detail(
                slug, session_key=_ensure_session(request)
            )
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineViewAPIView(View):
    def post(self, request, slug):
        try:
            data = MagazineService().record_view(
                slug,
                session_key=_ensure_session(request),
                ip=request.META.get("REMOTE_ADDR", ""),
            )
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineLikeAPIView(View):
    def post(self, request, slug):
        try:
            data = MagazineService().toggle_like(slug, session_key=_ensure_session(request))
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineBookmarkAPIView(View):
    def post(self, request, slug):
        try:
            data = MagazineService().toggle_bookmark(slug, session_key=_ensure_session(request))
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineShareAPIView(View):
    def post(self, request, slug):
        try:
            body = _parse_json(request)
            data = MagazineService().record_share(
                slug,
                session_key=_ensure_session(request),
                channel=body.get("channel", ""),
            )
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineCompleteReadAPIView(View):
    def post(self, request, slug):
        try:
            data = MagazineService().record_complete_read(
                slug, session_key=_ensure_session(request)
            )
            return JsonResponse({"ok": True, **data})
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))


class MagazineRateAPIView(View):
    def post(self, request, slug):
        try:
            body = _parse_json(request)
            # Accept editorial feedback keys or numeric value
            feedback = (body.get("feedback") or "").strip().lower()
            if feedback in ("helpful", "useful", "yes"):
                value = 5
            elif feedback in ("needs_improvement", "improve", "no"):
                value = 1
            else:
                value = int(body.get("value", 0))
            data = MagazineService().rate_article(
                slug, session_key=_ensure_session(request), value=value
            )
            return JsonResponse({"ok": True, **data})
        except (DomainError, TypeError, ValueError) as exc:
            if isinstance(exc, DomainError):
                return _json_error(exc, _status_for(exc))
            return _json_error(ValidationError("بازخورد نامعتبر است."))


class MagazineCommentAPIView(View):
    def post(self, request, slug):
        try:
            body = _parse_json(request)
            data = MagazineService().create_comment(
                slug,
                author_name=body.get("author_name", ""),
                body=body.get("body", ""),
                author_phone=body.get("author_phone", ""),
            )
            return JsonResponse({"ok": True, "comment": data}, status=201)
        except DomainError as exc:
            return _json_error(exc, _status_for(exc))
