"""
Base service — business logic layer.

Rules:
- Orchestrate repositories
- Enforce domain rules and validation
- Raise DomainError subclasses (never HttpResponse)
- Views stay thin: call service → render / redirect
"""

from __future__ import annotations

from typing import Generic, TypeVar

from apps.core.repositories.base import BaseRepository

RepoT = TypeVar("RepoT", bound=BaseRepository)


class BaseService(Generic[RepoT]):
    """Service that owns a primary repository."""

    def __init__(self, repository: RepoT | None = None):
        if repository is not None:
            self.repository = repository
        else:
            self.repository = self._default_repository()

    def _default_repository(self) -> RepoT:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _default_repository() "
            "or receive a repository in __init__."
        )
