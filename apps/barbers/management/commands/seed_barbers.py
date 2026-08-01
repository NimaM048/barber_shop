"""
Seed sample barbers for the public barbers list/detail pages.

Usage:
  python manage.py seed_barbers
"""

from datetime import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.barbers.models import Barber, WorkingHour

User = get_user_model()

BARBERS = [
    {
        "username": "barber_saleh",
        "display_name": "صالح ایوبی",
        "bio": (
            "بنیان‌گذار استودیو؛ تخصص در معماری ظاهر داماد، طراحی مو و استانداردهای VIP."
        ),
        "experience_years": 14,
        "avatar_static": "images/brand/hero-groom-1-hd.jpg",
        "avatar_webp_static": "images/brand/hero-groom-1-hd.webp",
        "days": (0, 1, 2, 3, 4),
        "start": time(10, 0),
        "end": time(20, 0),
    },
    {
        "username": "barber_arian",
        "display_name": "آرین محمدی",
        "bio": (
            "تمرکز روی فرم‌دهی مو و اصلاح دقیق؛ اجرا با ریتم آرام و جزئیات کامل."
        ),
        "experience_years": 8,
        "avatar_static": "images/brand/hero-groom-2-hd.jpg",
        "avatar_webp_static": "images/brand/hero-groom-2-hd.webp",
        "days": (0, 1, 2, 3, 5),
        "start": time(11, 0),
        "end": time(21, 0),
    },
    {
        "username": "barber_nima",
        "display_name": "نیما رضایی",
        "bio": (
            "مراقبت پوست و آماده‌سازی چهره برای مراسم؛ پروتکل‌های اختصاصی استودیو."
        ),
        "experience_years": 6,
        "avatar_static": "images/brand/hero-groom-3-hd.jpg",
        "avatar_webp_static": "images/brand/hero-groom-3-hd.webp",
        "days": (1, 2, 3, 4, 5),
        "start": time(10, 0),
        "end": time(19, 0),
    },
]


class Command(BaseCommand):
    help = "Seed sample active barbers with working hours"

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        updated = 0

        for item in BARBERS:
            user, user_created = User.objects.get_or_create(
                username=item["username"],
                defaults={
                    "first_name": item["display_name"].split()[0],
                    "is_staff": False,
                    "is_active": True,
                },
            )
            if user_created:
                user.set_unusable_password()
                user.save(update_fields=["password"])

            barber, barber_created = Barber.objects.update_or_create(
                user=user,
                defaults={
                    "display_name": item["display_name"],
                    "bio": item["bio"],
                    "experience_years": item["experience_years"],
                    "avatar_static": item["avatar_static"],
                    "avatar_webp_static": item["avatar_webp_static"],
                    "is_active": True,
                },
            )
            if barber_created:
                created += 1
            else:
                updated += 1

            WorkingHour.objects.filter(barber=barber).delete()
            WorkingHour.objects.bulk_create(
                [
                    WorkingHour(
                        barber=barber,
                        weekday=day,
                        start_time=item["start"],
                        end_time=item["end"],
                        is_active=True,
                    )
                    for day in item["days"]
                ]
            )

            self.stdout.write(
                f"  - barber id={barber.pk} years={barber.experience_years} "
                f"days={len(item['days'])}"
            )

        self.stdout.write(
            self.style.SUCCESS(f"Barbers seeded. created={created}, updated={updated}")
        )
