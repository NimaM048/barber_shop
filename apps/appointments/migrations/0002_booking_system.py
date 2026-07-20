# Generated manually for booking system overhaul

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.appointments.models


class Migration(migrations.Migration):

    dependencies = [
        ("appointments", "0001_initial"),
        ("catalog", "0001_initial"),
        ("barbers", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BookingServiceConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد شده")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="به‌روزرسانی")),
                ("is_deleted", models.BooleanField(db_index=True, default=False, verbose_name="حذف شده")),
                ("key", models.SlugField(help_text="مثلاً vip، skin، groom — برای API و فرانت", max_length=40, unique=True, verbose_name="کلید سرویس")),
                ("enabled", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("working_days", models.JSONField(default=apps.appointments.models.default_working_days, help_text="لیست کلیدها: saturday … friday", verbose_name="روزهای کاری")),
                ("start_time", models.TimeField(verbose_name="ساعت شروع")),
                ("end_time", models.TimeField(verbose_name="ساعت پایان")),
                ("slot_duration", models.PositiveSmallIntegerField(help_text="مدت هر Slot — فرانت فقط نمایش می‌دهد", verbose_name="فاصله نوبت (دقیقه)")),
                ("capacity", models.PositiveSmallIntegerField(default=1, help_text="تعداد مراجعه‌کننده همزمان در هر Slot", verbose_name="ظرفیت هر بازه")),
                ("short_description", models.CharField(blank=True, max_length=255, verbose_name="توضیح کوتاه کارت")),
                ("card_label", models.CharField(blank=True, max_length=80, verbose_name="برچسب کارت")),
                ("image_webp", models.CharField(blank=True, max_length=255, verbose_name="مسیر تصویر WebP")),
                ("image_jpg", models.CharField(blank=True, max_length=255, verbose_name="مسیر تصویر JPG")),
                ("sort_order", models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")),
                ("booking_lead_hours", models.PositiveSmallIntegerField(default=2, verbose_name="حداقل فاصله تا نوبت (ساعت)")),
                ("booking_window_days", models.PositiveSmallIntegerField(default=45, verbose_name="بازه رزرو آینده (روز)")),
                ("service", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="booking_config", to="catalog.serviceitem", verbose_name="خدمت کاتالوگ")),
            ],
            options={
                "verbose_name": "تنظیمات رزرو سرویس",
                "verbose_name_plural": "تنظیمات رزرو سرویس‌ها",
                "ordering": ["sort_order", "key"],
            },
        ),
        migrations.CreateModel(
            name="BookingBreak",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد شده")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="به‌روزرسانی")),
                ("start_time", models.TimeField(verbose_name="شروع استراحت")),
                ("end_time", models.TimeField(verbose_name="پایان استراحت")),
                ("label", models.CharField(blank=True, max_length=100, verbose_name="عنوان")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("config", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="breaks", to="appointments.bookingserviceconfig", verbose_name="سرویس")),
            ],
            options={
                "verbose_name": "استراحت کاری",
                "verbose_name_plural": "استراحت‌های کاری",
                "ordering": ["start_time"],
            },
        ),
        migrations.CreateModel(
            name="BookingHoliday",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد شده")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="به‌روزرسانی")),
                ("date", models.DateField(db_index=True, verbose_name="تاریخ")),
                ("title", models.CharField(blank=True, max_length=150, verbose_name="عنوان")),
                ("is_closed", models.BooleanField(default=True, verbose_name="تعطیل")),
                ("config", models.ForeignKey(blank=True, help_text="خالی = تعطیلی عمومی برای همه سرویس‌ها", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="holidays", to="appointments.bookingserviceconfig", verbose_name="سرویس")),
            ],
            options={
                "verbose_name": "تعطیلی",
                "verbose_name_plural": "تعطیلات",
                "ordering": ["date"],
                "unique_together": {("config", "date")},
            },
        ),
        migrations.CreateModel(
            name="BookingSpecialDate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد شده")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="به‌روزرسانی")),
                ("date", models.DateField(db_index=True, verbose_name="تاریخ")),
                ("is_closed", models.BooleanField(default=False, verbose_name="تعطیل در این روز")),
                ("start_time", models.TimeField(blank=True, null=True, verbose_name="ساعت شروع جایگزین")),
                ("end_time", models.TimeField(blank=True, null=True, verbose_name="ساعت پایان جایگزین")),
                ("slot_duration", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="فاصله نوبت جایگزین")),
                ("capacity", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="ظرفیت جایگزین")),
                ("note", models.CharField(blank=True, max_length=200, verbose_name="یادداشت")),
                ("config", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="special_dates", to="appointments.bookingserviceconfig", verbose_name="سرویس")),
            ],
            options={
                "verbose_name": "تاریخ خاص",
                "verbose_name_plural": "تاریخ‌های خاص",
                "ordering": ["date"],
                "unique_together": {("config", "date")},
            },
        ),
        migrations.CreateModel(
            name="DisabledTimeSlot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد شده")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="به‌روزرسانی")),
                ("date", models.DateField(db_index=True, verbose_name="تاریخ")),
                ("start_time", models.TimeField(verbose_name="شروع بازه")),
                ("end_time", models.TimeField(verbose_name="پایان بازه")),
                ("reason", models.CharField(blank=True, max_length=200, verbose_name="دلیل")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("config", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="disabled_slots", to="appointments.bookingserviceconfig", verbose_name="سرویس")),
            ],
            options={
                "verbose_name": "بازه غیرفعال",
                "verbose_name_plural": "بازه‌های غیرفعال",
                "ordering": ["date", "start_time"],
            },
        ),
        migrations.AddField(
            model_name="appointment",
            name="booking_code",
            field=models.CharField(blank=True, db_index=True, default="", editable=False, max_length=20, verbose_name="کد رزرو"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="booking_config",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="appointments.bookingserviceconfig", verbose_name="تنظیمات رزرو"),
        ),
        migrations.AddField(
            model_name="appointment",
            name="first_name",
            field=models.CharField(default="", max_length=80, verbose_name="نام"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="last_name",
            field=models.CharField(default="", max_length=80, verbose_name="نام خانوادگی"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="phone",
            field=models.CharField(db_index=True, default="", max_length=15, verbose_name="شماره تماس"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="appointment",
            name="barber",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="appointments", to="barbers.barber", verbose_name="آرایشگر"),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="customer",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="appointments", to=settings.AUTH_USER_MODEL, verbose_name="مشتری"),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="price_at_booking",
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name="قیمت در زمان رزرو"),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="status",
            field=models.CharField(choices=[("pending", "در انتظار تأیید"), ("confirmed", "تأیید شده"), ("cancelled", "لغو شده"), ("completed", "انجام شده"), ("no_show", "حاضر نشد")], db_index=True, default="confirmed", max_length=20, verbose_name="وضعیت"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["service", "starts_at"], name="appointment_service_6c1e2a_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["phone", "starts_at"], name="appointment_phone_8f3a1c_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["booking_config", "starts_at"], name="appointment_booking_2d4b9e_idx"),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="booking_code",
            field=models.CharField(blank=True, db_index=True, editable=False, max_length=20, unique=True, verbose_name="کد رزرو"),
        ),
    ]
