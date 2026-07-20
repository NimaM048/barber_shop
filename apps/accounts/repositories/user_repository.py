from apps.core.repositories import BaseRepository

from ..models import User


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_username(self, username: str) -> User | None:
        try:
            return self.get_queryset().get(username=username)
        except User.DoesNotExist:
            return None

    def get_by_phone(self, phone: str) -> User | None:
        try:
            return self.get_queryset().get(phone=phone)
        except User.DoesNotExist:
            return None
