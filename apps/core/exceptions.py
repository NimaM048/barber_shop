"""
Domain exceptions raised by services (not views).
Views catch these and map them to HTTP / messages.
"""


class DomainError(Exception):
    """Base domain exception."""

    default_message = "خطایی رخ داده است."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(DomainError):
    default_message = "مورد درخواستی یافت نشد."


class ValidationError(DomainError):
    default_message = "اطلاعات وارد شده معتبر نیست."


class PermissionDeniedError(DomainError):
    default_message = "دسترسی مجاز نیست."


class ConflictError(DomainError):
    default_message = "این عملیات با وضعیت فعلی در تعارض است."
