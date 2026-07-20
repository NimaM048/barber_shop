from django.contrib import admin, messages
from django.utils.html import format_html

from apps.magazine.services import MagazineService

from .models import (
    Article,
    ArticleComment,
    ArticleImage,
    ArticleInteraction,
    ArticleVersion,
    MagazineAuthor,
    MagazineCategory,
    MagazineTag,
)


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 0


class ArticleVersionInline(admin.TabularInline):
    model = ArticleVersion
    extra = 0
    readonly_fields = (
        "version_number",
        "title",
        "changed_by",
        "change_note",
        "created_at",
    )
    can_delete = False
    max_num = 0
    show_change_link = True


@admin.register(MagazineAuthor)
class MagazineAuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "is_active", "slug")
    list_filter = ("is_active",)
    search_fields = ("name", "role", "bio")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MagazineCategory)
class MagazineCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "sort_order", "consultation_category_key")
    list_filter = ("is_active",)
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "description",
                    "icon",
                    "accent_color",
                    "sort_order",
                    "is_active",
                )
            },
        ),
        ("تصاویر", {"fields": ("image_webp", "image_jpg")}),
        (
            "تبدیل به رزرو / مشاوره",
            {
                "fields": (
                    "booking_service_keys",
                    "consultation_category_key",
                    "cta_title",
                    "cta_consultation_label",
                    "cta_booking_label",
                )
            },
        ),
    )


@admin.register(MagazineTag)
class MagazineTagAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "status",
        "is_featured",
        "is_editors_pick",
        "is_hero",
        "view_count",
        "published_at",
        "is_active",
    )
    list_filter = (
        "status",
        "is_active",
        "is_featured",
        "is_editors_pick",
        "is_hero",
        "category",
        "author",
    )
    search_fields = ("title", "subtitle", "excerpt", "slug", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags", "related_articles")
    date_hierarchy = "published_at"
    inlines = [ArticleImageInline, ArticleVersionInline]
    actions = ["action_publish", "action_feature", "action_snapshot_version"]
    readonly_fields = (
        "view_count",
        "complete_read_count",
        "like_count",
        "bookmark_count",
        "share_count",
        "rating_sum",
        "rating_count",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "محتوا",
            {
                "fields": (
                    "title",
                    "subtitle",
                    "slug",
                    "excerpt",
                    "body",
                    "category",
                    "tags",
                    "author",
                    "related_articles",
                )
            },
        ),
        (
            "رسانه",
            {
                "fields": (
                    "cover_image",
                    "cover_image_static",
                    "cover_image_alt",
                    "video_url",
                    "audio_file",
                    "pdf_file",
                )
            },
        ),
        (
            "انتشار",
            {
                "fields": (
                    "status",
                    "is_active",
                    "published_at",
                    "scheduled_at",
                    "reading_minutes",
                    "display_priority",
                    "is_featured",
                    "is_editors_pick",
                    "is_hero",
                    "allow_comments",
                )
            },
        ),
        (
            "سئو",
            {
                "classes": ("collapse",),
                "fields": (
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                    "og_title",
                    "og_description",
                    "og_image",
                    "twitter_title",
                    "twitter_description",
                    "canonical_url",
                    "schema_json",
                    "robots_noindex",
                ),
            },
        ),
        (
            "آمار",
            {
                "classes": ("collapse",),
                "fields": (
                    "view_count",
                    "complete_read_count",
                    "like_count",
                    "bookmark_count",
                    "share_count",
                    "rating_sum",
                    "rating_count",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        creating_version = change and form.changed_data
        if creating_version and obj.pk:
            try:
                old = Article.objects.get(pk=obj.pk)
                content_fields = {"title", "subtitle", "excerpt", "body", "meta_title", "meta_description"}
                if content_fields.intersection(form.changed_data):
                    MagazineService().snapshot_version(
                        old,
                        changed_by=getattr(request.user, "username", "") or str(request.user),
                        change_note="خودکار قبل از ذخیره",
                    )
            except Article.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

    @admin.action(description="انتشار مقالات انتخاب‌شده")
    def action_publish(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
            is_active=True,
        )
        self.message_user(request, f"{updated} مقاله منتشر شد.", messages.SUCCESS)

    @admin.action(description="علامت‌گذاری به‌عنوان ویژه")
    def action_feature(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} مقاله ویژه شد.", messages.SUCCESS)

    @admin.action(description="ثبت نسخه فعلی")
    def action_snapshot_version(self, request, queryset):
        service = MagazineService()
        count = 0
        for article in queryset:
            service.snapshot_version(
                article,
                changed_by=getattr(request.user, "username", "") or str(request.user),
                change_note="ثبت دستی از ادمین",
            )
            count += 1
        self.message_user(request, f"{count} نسخه ذخیره شد.", messages.SUCCESS)


@admin.register(ArticleVersion)
class ArticleVersionAdmin(admin.ModelAdmin):
    list_display = ("article", "version_number", "title", "changed_by", "created_at", "restore_link")
    list_filter = ("article",)
    search_fields = ("title", "change_note", "changed_by")
    readonly_fields = (
        "article",
        "version_number",
        "title",
        "subtitle",
        "excerpt",
        "body",
        "meta_title",
        "meta_description",
        "changed_by",
        "change_note",
        "snapshot",
        "created_at",
    )
    actions = ["action_restore"]

    def restore_link(self, obj):
        return format_html(
            '<span style="color:#0d2d28">از Actions → بازگردانی استفاده کنید</span>'
        )

    restore_link.short_description = "بازگردانی"

    @admin.action(description="بازگردانی این نسخه روی مقاله")
    def action_restore(self, request, queryset):
        service = MagazineService()
        for version in queryset:
            service.restore_version(version.article_id, version.version_number)
        self.message_user(request, "نسخه(ها) بازگردانی شد.", messages.SUCCESS)


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ("author_name", "article", "is_approved", "created_at")
    list_filter = ("is_approved",)
    search_fields = ("author_name", "body", "article__title")
    actions = ["approve_comments"]

    @admin.action(description="تأیید نظرات")
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} نظر تأیید شد.", messages.SUCCESS)


@admin.register(ArticleInteraction)
class ArticleInteractionAdmin(admin.ModelAdmin):
    list_display = ("article", "kind", "session_key", "rating_value", "share_channel", "created_at")
    list_filter = ("kind",)
    search_fields = ("article__title", "session_key")
    readonly_fields = ("article", "kind", "session_key", "rating_value", "share_channel", "ip_hash")
