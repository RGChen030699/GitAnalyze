from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("repositories", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="repository",
            name="releases",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="repository",
            name="health",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="repository",
            name="health_fetched_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
