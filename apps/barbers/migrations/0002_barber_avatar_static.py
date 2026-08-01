# Generated manually for avatar_static fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("barbers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="barber",
            name="avatar_static",
            field=models.CharField(
                blank=True,
                help_text="اگر ImageField خالی باشد از این مسیر static استفاده می‌شود",
                max_length=255,
                verbose_name="مسیر تصویر استاتیک",
            ),
        ),
        migrations.AddField(
            model_name="barber",
            name="avatar_webp_static",
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name="مسیر WebP استاتیک",
            ),
        ),
    ]
