# Generated by Django 5.1.7 on 2025-04-07 20:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0004_add_is_active_to_document"),
    ]

    operations = [
        migrations.CreateModel(
            name="Prompt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "assistant_role",
                    models.TextField(
                        default="You are a helpful AI assistant answering questions about a website's content.",
                        help_text="Defines who the assistant is and its general purpose",
                    ),
                ),
                (
                    "website_context",
                    models.TextField(
                        blank=True,
                        help_text="General information about the website/company the assistant represents",
                    ),
                ),
                (
                    "knowledge_context",
                    models.TextField(
                        blank=True,
                        help_text="Fixed knowledge the assistant should always have access to",
                    ),
                ),
                (
                    "response_guidelines",
                    models.TextField(
                        default="Provide concise, accurate information based on the context provided.",
                        help_text="Guidelines for how the assistant should format and structure responses",
                    ),
                ),
                (
                    "restrictions",
                    models.TextField(
                        blank=True,
                        help_text="Constraints or limitations on what the assistant should or shouldn't do",
                    ),
                ),
                ("is_active", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
