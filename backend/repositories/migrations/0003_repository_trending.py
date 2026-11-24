from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("repositories", "0002_repository_health")]

    operations = [
        migrations.AddField(
            model_name="repository",
            name="trending",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="repository",
            name="trending_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
