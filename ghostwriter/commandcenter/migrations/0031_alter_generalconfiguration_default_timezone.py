# Generated by Django 4.2 on 2024-09-10 20:27

from django.db import migrations
import timezone_field.fields


class Migration(migrations.Migration):
    dependencies = [
        ("commandcenter", "0030_alter_extrafieldspec_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generalconfiguration",
            name="default_timezone",
            field=timezone_field.fields.TimeZoneField(
                default="America/Los_Angeles",
                help_text="Select a default timezone for clients and projects",
                use_pytz=False,
                verbose_name="Default Timezone",
            ),
        ),
    ]
