# Generated by Django 3.2.19 on 2023-10-06 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rolodex', '0045_project_extra_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='extra_fields',
            field=models.JSONField(default=dict),
        ),
    ]
