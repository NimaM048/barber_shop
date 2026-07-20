"""
Seed catalog services + dynamic booking configs.

Usage:
  python manage.py seed_booking
"""

from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.appointments.models import BookingServiceConfig, default_working_days
from apps.catalog.models import ServiceCategory, ServiceItem

DEFAULTS = [
    {
        "key": "vip",
        "category_name": "اصلاح VIP",
        "category_slug": "vip",
        "name": "اصلاح VIP",
        "slug": "vip",
        "description": "تجربه اختصاصی اصلاح با استاندارد لوکس برند — تمرکز کامل روی شما.",
        "card_label": "👑 اصلاح VIP",
        "short_description": "نوبت اختصاصی با دقت و حوصله کامل",
        "duration_minutes": 90,
        "price": 2_500_000,
        "slot_duration": 90,
        "capacity": 1,
        "start_time": time(10, 0),
        "end_time": time(21, 0),
        "working_days": default_working_days(),
        "image_webp": "images/brand/hero-groom-3-hd.webp",
        "image_jpg": "images/brand/hero-groom-3-hd.jpg",
        "sort_order": 1,
    },
    {
        "key": "skin",
        "category_name": "پوست و مو",
        "category_slug": "skin-hair",
        "name": "پوست و مو",
        "slug": "skin",
        "description": "مراقبت تخصصی پوست و طراحی مو با پروتکل اختصاصی استودیو.",
        "card_label": "✨ پوست و مو",
        "short_description": "مراقبت پوست و استایل مو در یک نوبت",
        "duration_minutes": 60,
        "price": 1_800_000,
        "slot_duration": 60,
        "capacity": 2,
        "start_time": time(10, 0),
        "end_time": time(20, 0),
        "working_days": default_working_days(),
        "image_webp": "images/brand/hero-groom-2-hd.webp",
        "image_jpg": "images/brand/hero-groom-2-hd.jpg",
        "sort_order": 2,
    },
    {
        "key": "groom",
        "category_name": "داماد",
        "category_slug": "groom",
        "name": "آرایش داماد",
        "slug": "groom",
        "description": "آماده‌سازی کامل داماد برای روز مهم — استایل، پوست و جزئیات نهایی.",
        "card_label": "💈 داماد",
        "short_description": "آماده‌سازی کامل برای روز عروسی",
        "duration_minutes": 120,
        "price": 4_500_000,
        "slot_duration": 120,
        "capacity": 1,
        "start_time": time(9, 0),
        "end_time": time(20, 0),
        "working_days": [
            "saturday",
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
        ],
        "image_webp": "images/brand/hero-groom-1-hd.webp",
        "image_jpg": "images/brand/hero-groom-1-hd.jpg",
        "sort_order": 3,
    },
]


class Command(BaseCommand):
    help = "Seed three bookable services with dynamic schedule configs"

    @transaction.atomic
    def handle(self, *args, **options):
        created_services = 0
        created_configs = 0
        updated = 0

        for item in DEFAULTS:
            category, _ = ServiceCategory.objects.get_or_create(
                slug=item["category_slug"],
                defaults={
                    "name": item["category_name"],
                    "description": item["description"],
                    "sort_order": item["sort_order"],
                },
            )

            service, svc_created = ServiceItem.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "category": category,
                    "name": item["name"],
                    "description": item["description"],
                    "duration_minutes": item["duration_minutes"],
                    "price": item["price"],
                    "is_active": True,
                    "sort_order": item["sort_order"],
                },
            )
            if svc_created:
                created_services += 1

            config, cfg_created = BookingServiceConfig.objects.update_or_create(
                key=item["key"],
                defaults={
                    "service": service,
                    "enabled": True,
                    "working_days": item["working_days"],
                    "start_time": item["start_time"],
                    "end_time": item["end_time"],
                    "slot_duration": item["slot_duration"],
                    "capacity": item["capacity"],
                    "short_description": item["short_description"],
                    "card_label": item["card_label"],
                    "image_webp": item["image_webp"],
                    "image_jpg": item["image_jpg"],
                    "sort_order": item["sort_order"],
                    "booking_lead_hours": 2,
                    "booking_window_days": 45,
                },
            )
            if cfg_created:
                created_configs += 1
            else:
                updated += 1

            self.stdout.write(
                f"  - {config.key}: duration={config.slot_duration}min capacity={config.capacity}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. services+={created_services}, configs+={created_configs}, "
                f"updated={updated}"
            )
        )
