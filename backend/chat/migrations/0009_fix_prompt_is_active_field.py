from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0008_migrate_existing_data_to_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]