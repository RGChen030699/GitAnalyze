from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("repositories", "0004_trending_period_keys")]

    operations = [
        migrations.AddField(
            model_name="repository",
            name="ai",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="repository",
            name="ai_fetched_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
