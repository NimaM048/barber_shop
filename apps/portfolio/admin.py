from django.contrib import admin

from .models import GalleryCategory, GalleryImage, GalleryItem, GalleryTag


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 0
    fields = (
        "image",
        "image_static",
        "webp_static",
        "avif_static",
        "lqip_static",
        "caption",
        "alt_text",
        "sort_order",
    )


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(GalleryTag)
class GalleryTagAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_published",
        "is_featured",
        "has_before_after",
        "sort_order",
    )
    list_filter = ("is_published", "is_featured", "has_before_after", "category")
    search_fields = ("title", "subtitle", "description", "slug")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    inlines = [GalleryImageInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "subtitle",
                    "slug",
                    "description",
                    "category",
                    "tags",
                    "sort_order",
                    "is_published",
                    "is_featured",
                )
            },
        ),
        (
            "کاور و رسانه",
            {
                "fields": (
                    "cover_image",
                    "cover_image_static",
                    "cover_webp_static",
                    "cover_avif_static",
                    "cover_lqip_static",
                    "alt_text",
                    "video",
                    "video_url",
                    "video_poster_static",
                )
            },
        ),
        (
            "قبل و بعد",
            {
                "fields": (
                    "has_before_after",
                    "before_image",
                    "after_image",
                    "before_image_static",
                    "after_image_static",
                    "before_alt",
                    "after_alt",
                )
            },
        ),
        (
            "داستان پروژه",
            {
                "fields": (
                    "problem",
                    "solution",
                    "services_text",
                    "duration_text",
                    "result",
                    "customer_review",
                    "location",
                    "completed_at",
                )
            },
        ),
        (
            "تبدیل",
            {
                "fields": (
                    "related_service",
                    "cta_title",
                    "cta_consultation_label",
                    "cta_booking_label",
                )
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description", "meta_keywords"),
                "classes": ("collapse",),
            },
        ),
    )
