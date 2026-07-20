"""
Load settings by environment.

Default: development
Set DJANGO_ENV=production for production settings.
"""

import os

_env = os.getenv("DJANGO_ENV", "development").lower()

if _env == "production":
    from .production import *  # noqa: F401,F403
else:
    from .development import *  # noqa: F401,F403
