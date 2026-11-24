from typing import Any

from django.db import migrations

from repositories.trending import with_period_keys


def forwards(apps: Any, schema_editor: Any) -> None:
    """Ranks stored before Trending periods existed were all weekly (F8 G4)."""
    repository = apps.get_model("repositories", "Repository")
    for repo in repository.objects.filter(trending__isnull=False):
        repo.trending = with_period_keys(repo.trending)
        repo.save(update_fields=["trending"])


class Migration(migrations.Migration):
    dependencies = [("repositories", "0003_repository_trending")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
