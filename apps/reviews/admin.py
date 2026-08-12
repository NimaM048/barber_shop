from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone

from .models import Review, ReviewCategory


@admin.register(ReviewCategory)
class ReviewCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "key", "slug", "is_published", "sort_order", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "key", "slug", "lede")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("sort_order", "is_published")
    ordering = ("sort_order", "title")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "key",
                    "slug",
                    "lede",
                    "sort_order",
                    "is_published",
                )
            },
        ),
        (
            "لینک‌های تبدیل",
            {
                "fields": ("booking_service_key", "consultation_category_key"),
            },
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("seo_title", "seo_description"),
            },
        ),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author_display_name",
        "category",
        "rating",
        "status",
        "is_featured",
        "sort_order",
        "published_at",
        "view_on_site_link",
    )
    list_filter = ("status", "is_featured", "category", "rating")
    search_fields = (
        "title",
        "body",
        "author_display_name",
        "author_role",
        "service_name",
        "slug",
        "city",
    )
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    list_editable = ("is_featured", "sort_order")
    autocomplete_fields = ()
    raw_id_fields = ()
    actions = ["action_publish", "action_unpublish", "action_feature"]
    readonly_fields = ("created_at", "updated_at", "view_on_site_link")
    fieldsets = (
        (
            "محتوا",
            {
                "fields": (
                    "title",
                    "slug",
                    "body",
                    "category",
                    "service_name",
                )
            },
        ),
        (
            "نویسنده",
            {
                "fields": (
                    "author_display_name",
                    "author_role",
                    "city",
                    "visited_on",
                    "source_note",
                )
            },
        ),
        (
            "امتیاز و انتشار",
            {
                "fields": (
                    "rating",
                    "status",
                    "is_featured",
                    "published_at",
                    "sort_order",
                )
            },
        ),
        (
            "رسانه",
            {
                "classes": ("collapse",),
                "fields": ("portrait", "portrait_static"),
            },
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("seo_title", "seo_description"),
            },
        ),
        (
            "سیستم",
            {
                "classes": ("collapse",),
                "fields": ("view_on_site_link", "created_at", "updated_at"),
            },
        ),
    )

    @admin.display(description="مشاهده در سایت")
    def view_on_site_link(self, obj: Review):
        if not obj.pk or obj.status != Review.Status.PUBLISHED:
            return "—"
        try:
            url = obj.get_absolute_url()
        except Exception:
            return "—"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">مشاهده</a>',
            url,
        )

    @admin.action(description="انتشار نظرات انتخاب‌شده")
    def action_publish(self, request, queryset):
        now = timezone.now()
        updated = 0
        for review in queryset:
            review.status = Review.Status.PUBLISHED
            if review.published_at is None:
                review.published_at = now
            review.save(update_fields=["status", "published_at", "updated_at"])
            updated += 1
        self.message_user(request, f"{updated} نظر منتشر شد.", messages.SUCCESS)

    @admin.action(description="بازگشت به پیش‌نویس")
    def action_unpublish(self, request, queryset):
        updated = queryset.update(status=Review.Status.DRAFT)
        self.message_user(request, f"{updated} نظر به پیش‌نویس برگشت.", messages.WARNING)

    @admin.action(description="نمایش در صفحه اصلی")
    def action_feature(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} نظر ویژه شد.", messages.SUCCESS)
