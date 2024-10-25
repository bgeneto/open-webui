"""Peewee migrations -- 019_add_preset_table.py."""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""

    @migrator.create_model
    class Preset(pw.Model):
        id = pw.AutoField()
        user_id = pw.CharField(max_length=255)
        name = pw.CharField(max_length=255)
        system_prompt = pw.TextField()
        advanced_params = pw_pext.JSONField()
        created_at = pw.BigIntegerField()

        class Meta:
            table_name = "preset"
            indexes = (
                (("user_id", "name"), True),
            )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    migrator.remove_model("preset")
