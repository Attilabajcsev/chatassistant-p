# Generated by Django 5.1.7 on 2025-04-07 08:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0003_conversation_is_active"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="conversation",
            name="is_active",
        ),
        migrations.AddField(
            model_name="document",
            name="is_active",
            field=models.BooleanField(default=False),
        ),
    ]
