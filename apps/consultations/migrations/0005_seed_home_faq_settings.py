from django.db import migrations


DEFAULTS = {
    "home_faq_label": "پرسش‌های پرتکرار",
    "home_faq_title": "پیش از مراجعه، پاسخ‌ها روشن‌اند.",
    "home_faq_description": "برای جزئیات هر مسیر، راهنمای مشاوره همیشه در دسترس است.",
    "home_faq_link_label": "همهٔ راهنماهای پیش از مراجعه",
}


def seed_home_faq_settings(apps, schema_editor):
    HubPage = apps.get_model("consultations", "ConsultationHubPage")
    for page in HubPage.objects.filter(key="hub"):
        update_fields = []
        for field, value in DEFAULTS.items():
            if not getattr(page, field):
                setattr(page, field, value)
                update_fields.append(field)
        if update_fields:
            page.save(update_fields=update_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0004_home_faq_settings"),
    ]

    operations = [
        migrations.RunPython(seed_home_faq_settings, migrations.RunPython.noop),
    ]
