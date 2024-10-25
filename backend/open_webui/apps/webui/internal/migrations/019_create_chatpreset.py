import peewee as pw
from open_webui.apps.webui.internal.db import register_connection

# Define the migration
def migrate(migrator, database, fake=False, **kwargs):
    with database.atomic():
        # Create the chatpreset table
        migrator.create_model(
            "ChatPreset",
            [
                ("id", pw.AutoField(primary_key=True)),
                ("user_id", pw.CharField(max_length=255)),
                ("name", pw.CharField(max_length=255)),
                ("system_prompt", pw.TextField()),
                ("advanced_params", pw.JSONField()),
                ("created_at", pw.BigIntegerField()),
            ],
        )
        # Create a composite index on user_id and name
        migrator.add_index("ChatPreset", ("user_id", "name"), unique=True)

# Register the migration
register_connection(migrate)
