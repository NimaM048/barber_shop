from django.contrib.auth import authenticate

from apps.core.exceptions import ValidationError
from apps.core.services import BaseService

from ..repositories import UserRepository


class AuthService(BaseService[UserRepository]):
    """Authentication & registration business logic."""

    def _default_repository(self) -> UserRepository:
        return UserRepository()

    def create_customer_with_password(self, *, password: str, **data):
        """Create customer and hash password correctly."""
        if self.repository.exists(username=data["username"]):
            raise ValidationError("این نام کاربری قبلاً ثبت شده است.")

        user = self.repository.model(
            username=data["username"],
            phone=data.get("phone", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=self.repository.model.Role.CUSTOMER,
        )
        user.set_password(password)
        user.save()
        return user

    def authenticate_user(self, *, username: str, password: str):
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError("نام کاربری یا رمز عبور اشتباه است.")
        return user
