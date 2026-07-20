"""
Magazine / beauty encyclopedia — premium editorial content CMS.
All article copy and media live here; frontend never hardcodes articles.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import SoftDeleteModel, TimeStampedModel


class MagazineAuthor(TimeStampedModel, SoftDeleteModel):
    """Editorial author profile shown on articles."""

    name = models.CharField("نام", max_length=120)
    slug = models.SlugField("اسلاگ", max_length=140, unique=True, allow_unicode=True)
    role = models.CharField("سمت", max_length=120, blank=True)
    bio = models.TextField("بیوگرافی", blank=True)
    avatar = models.ImageField(
        "تصویر نویسنده",
        upload_to="magazine/authors/",
        blank=True,
        null=True,
    )
    avatar_static = models.CharField(
        "مسیر تصویر استاتیک",
        max_length=255,
        blank=True,
        help_text="اگر ImageField خالی باشد از این مسیر static استفاده می‌شود",
    )
    is_active = models.BooleanField("فعال", default=True, db_index=True)

    class Meta:
        verbose_name = "نویسنده"
        verbose_name_plural = "نویسندگان"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name, allow_unicode=True) or f"author-{timezone.now().timestamp():.0f}"
        super().save(*args, **kwargs)


class MagazineCategory(TimeStampedModel, SoftDeleteModel):
    """Unlimited editorial categories (groom, skin, trends, …)."""

    title = models.CharField("عنوان", max_length=120)
    slug = models.SlugField("اسلاگ", max_length=140, unique=True, allow_unicode=True)
    description = models.TextField("توضیحات", blank=True)
    icon = models.CharField("آیکون", max_length=80, blank=True)
    accent_color = models.CharField("رنگ اختصاصی", max_length=20, blank=True, default="#f7f4ef")
    image_webp = models.CharField("تصویر WebP", max_length=255, blank=True)
    image_jpg = models.CharField("تصویر JPG", max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True, db_index=True)
    booking_service_keys = models.JSONField(
        "کلیدهای سرویس رزرو مرتبط",
        default=list,
        blank=True,
        help_text='مثلاً ["groom"] یا ["skin", "vip"]',
    )
    cta_title = models.CharField(
        "عنوان CTA تبدیل",
        max_length=180,
        blank=True,
        default="آماده دریافت مشاوره هستید؟",
    )
    cta_consultation_label = models.CharField(
        "برچسب مشاوره",
        max_length=120,
        blank=True,
        default="دریافت مشاوره تخصصی",
    )
    cta_booking_label = models.CharField(
        "برچسب رزرو",
        max_length=120,
        blank=True,
        default="رزرو نوبت",
    )
    consultation_category_key = models.SlugField(
        "کلید دسته مشاوره",
        max_length=40,
        blank=True,
        help_text="برای لینک به /consultations/<key>/",
    )

    class Meta:
        verbose_name = "دسته‌بندی مجله"
        verbose_name_plural = "دسته‌بندی‌های مجله"
        ordering = ["sort_order", "title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title, allow_unicode=True) or f"cat-{timezone.now().timestamp():.0f}"
        super().save(*args, **kwargs)


class MagazineTag(TimeStampedModel):
    title = models.CharField("عنوان", max_length=80)
    slug = models.SlugField("اسلاگ", max_length=100, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title, allow_unicode=True) or f"tag-{timezone.now().timestamp():.0f}"
        super().save(*args, **kwargs)


class Article(TimeStampedModel, SoftDeleteModel):
    """Core magazine article with full SEO and editorial flags."""

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        SCHEDULED = "scheduled", "زمان‌بندی‌شده"
        PUBLISHED = "published", "منتشر شده"
        ARCHIVED = "archived", "بایگانی"

    title = models.CharField("عنوان", max_length=220)
    subtitle = models.CharField("زیرعنوان", max_length=255, blank=True)
    slug = models.SlugField("اسلاگ", max_length=240, unique=True, allow_unicode=True)
    excerpt = models.TextField("خلاصه", blank=True)
    body = models.TextField(
        "محتوای کامل",
        help_text="HTML غنی: تیتر، پاراگراف، نقل‌قول، جدول، ویدئو، callout",
    )
    cover_image = models.ImageField(
        "تصویر شاخص",
        upload_to="magazine/covers/",
        blank=True,
        null=True,
    )
    cover_image_static = models.CharField(
        "مسیر تصویر شاخص استاتیک",
        max_length=255,
        blank=True,
    )
    cover_image_alt = models.CharField("متن جایگزین تصویر", max_length=200, blank=True)
    video_url = models.URLField("لینک ویدئو", blank=True)
    audio_file = models.FileField(
        "فایل صوتی",
        upload_to="magazine/audio/",
        blank=True,
        null=True,
    )
    pdf_file = models.FileField(
        "فایل PDF",
        upload_to="magazine/pdfs/",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        MagazineCategory,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="دسته‌بندی",
    )
    tags = models.ManyToManyField(
        MagazineTag,
        related_name="articles",
        blank=True,
        verbose_name="برچسب‌ها",
    )
    author = models.ForeignKey(
        MagazineAuthor,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="نویسنده",
    )
    related_articles = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="related_from",
        verbose_name="مقالات مرتبط",
    )
    reading_minutes = models.PositiveSmallIntegerField("زمان مطالعه (دقیقه)", default=5)
    published_at = models.DateTimeField("تاریخ انتشار", null=True, blank=True, db_index=True)
    scheduled_at = models.DateTimeField("زمان‌بندی انتشار", null=True, blank=True, db_index=True)
    status = models.CharField(
        "وضعیت انتشار",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    is_active = models.BooleanField("فعال", default=True, db_index=True)
    is_featured = models.BooleanField("مقاله ویژه", default=False, db_index=True)
    is_editors_pick = models.BooleanField("منتخب سردبیر", default=False, db_index=True)
    is_hero = models.BooleanField("مقاله Hero هفته", default=False, db_index=True)
    display_priority = models.PositiveIntegerField("اولویت نمایش", default=0, db_index=True)
    allow_comments = models.BooleanField("فعال بودن نظرات", default=False)

    # Engagement counters (denormalized for performance)
    view_count = models.PositiveIntegerField("بازدید", default=0)
    complete_read_count = models.PositiveIntegerField("مطالعه کامل", default=0)
    like_count = models.PositiveIntegerField("لایک", default=0)
    bookmark_count = models.PositiveIntegerField("ذخیره", default=0)
    share_count = models.PositiveIntegerField("اشتراک‌گذاری", default=0)
    rating_sum = models.PositiveIntegerField("جمع امتیاز", default=0)
    rating_count = models.PositiveIntegerField("تعداد امتیاز", default=0)

    # SEO
    meta_title = models.CharField("Meta Title", max_length=70, blank=True)
    meta_description = models.CharField("Meta Description", max_length=170, blank=True)
    meta_keywords = models.CharField("Meta Keywords", max_length=255, blank=True)
    og_title = models.CharField("OpenGraph Title", max_length=100, blank=True)
    og_description = models.CharField("OpenGraph Description", max_length=200, blank=True)
    og_image = models.ImageField(
        "OpenGraph Image",
        upload_to="magazine/og/",
        blank=True,
        null=True,
    )
    twitter_title = models.CharField("Twitter Title", max_length=100, blank=True)
    twitter_description = models.CharField("Twitter Description", max_length=200, blank=True)
    canonical_url = models.URLField("Canonical URL", blank=True)
    schema_json = models.JSONField(
        "Structured Data (Schema.org)",
        default=dict,
        blank=True,
        help_text="JSON-LD Article schema — در صورت خالی بودن به‌صورت خودکار ساخته می‌شود",
    )
    robots_noindex = models.BooleanField("NoIndex", default=False)

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-display_priority", "-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "is_active", "published_at"]),
            models.Index(fields=["is_featured", "status"]),
            models.Index(fields=["is_hero", "status"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base = slugify(self.title, allow_unicode=True) or "article"
            candidate = base
            n = 1
            while Article.all_objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                n += 1
                candidate = f"{base}-{n}"
            self.slug = candidate
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:170]
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def average_rating(self) -> float:
        if self.rating_count == 0:
            return 0.0
        return round(self.rating_sum / self.rating_count, 1)

    @property
    def is_publicly_visible(self) -> bool:
        if not self.is_active or self.is_deleted:
            return False
        if self.status != self.Status.PUBLISHED:
            return False
        if self.published_at and self.published_at > timezone.now():
            return False
        return True


class ArticleImage(TimeStampedModel):
    """Inline gallery / body images for an article."""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="مقاله",
    )
    image = models.ImageField("تصویر", upload_to="magazine/inline/")
    caption = models.CharField("کپشن", max_length=255, blank=True)
    alt_text = models.CharField("متن جایگزین", max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "تصویر مقاله"
        verbose_name_plural = "تصاویر مقاله"
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.article_id} / {self.caption or self.pk}"


class ArticleVersion(TimeStampedModel):
    """Content versioning — restore previous revisions from admin."""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name="مقاله",
    )
    version_number = models.PositiveIntegerField("شماره نسخه")
    title = models.CharField("عنوان", max_length=220)
    subtitle = models.CharField("زیرعنوان", max_length=255, blank=True)
    excerpt = models.TextField("خلاصه", blank=True)
    body = models.TextField("محتوا")
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=170, blank=True)
    changed_by = models.CharField("ویرایش‌کننده", max_length=120, blank=True)
    change_note = models.CharField("یادداشت تغییر", max_length=255, blank=True)
    snapshot = models.JSONField("اسنپ‌شات کامل", default=dict, blank=True)

    class Meta:
        verbose_name = "نسخه مقاله"
        verbose_name_plural = "نسخه‌های مقاله"
        ordering = ["-version_number"]
        unique_together = ("article", "version_number")

    def __str__(self) -> str:
        return f"{self.article_id} v{self.version_number}"


class ArticleInteraction(TimeStampedModel):
    """Guest/session engagement: like, bookmark, share, rating, complete-read."""

    class Kind(models.TextChoices):
        LIKE = "like", "لایک"
        BOOKMARK = "bookmark", "ذخیره"
        SHARE = "share", "اشتراک"
        RATING = "rating", "امتیاز"
        COMPLETE_READ = "complete_read", "مطالعه کامل"
        VIEW = "view", "بازدید"

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="interactions",
        verbose_name="مقاله",
    )
    kind = models.CharField("نوع", max_length=20, choices=Kind.choices, db_index=True)
    session_key = models.CharField("کلید نشست", max_length=64, db_index=True)
    rating_value = models.PositiveSmallIntegerField(
        "امتیاز",
        null=True,
        blank=True,
        help_text="۱ تا ۵",
    )
    share_channel = models.CharField("کانال اشتراک", max_length=40, blank=True)
    ip_hash = models.CharField("هش IP", max_length=64, blank=True)

    class Meta:
        verbose_name = "تعامل مقاله"
        verbose_name_plural = "تعاملات مقاله"
        indexes = [
            models.Index(fields=["article", "kind", "session_key"]),
        ]

    def __str__(self) -> str:
        return f"{self.article_id} / {self.kind}"


class ArticleComment(TimeStampedModel, SoftDeleteModel):
    """Optional moderated comments."""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="مقاله",
    )
    author_name = models.CharField("نام", max_length=80)
    author_phone = models.CharField("تلفن", max_length=20, blank=True)
    body = models.TextField("متن نظر")
    is_approved = models.BooleanField("تأیید شده", default=False, db_index=True)

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.author_name}: {self.body[:40]}"
