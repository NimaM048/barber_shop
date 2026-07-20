from apps.core.repositories import BaseRepository

from ..models import GalleryCategory, GalleryItem, GalleryTag


class GalleryCategoryRepository(BaseRepository[GalleryCategory]):
    model = GalleryCategory

    def list_active(self):
        return self.get_queryset().filter(is_active=True)


class GalleryTagRepository(BaseRepository[GalleryTag]):
    model = GalleryTag


class GalleryItemRepository(BaseRepository[GalleryItem]):
    model = GalleryItem

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "related_service")
            .prefetch_related("tags", "images")
        )

    def list_published(self):
        return self.get_queryset().filter(is_published=True)
