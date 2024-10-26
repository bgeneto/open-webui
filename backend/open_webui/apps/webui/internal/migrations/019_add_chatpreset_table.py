import peewee as pw
from open_webui.apps.webui.internal.db import register_connection

db = register_connection()

class ChatPreset(pw.Model):
    id = pw.AutoField()
    preset_name = pw.CharField(max_length=255)
    user_id = pw.ForeignKeyField(User, backref='chatpresets')
    system_prompt = pw.TextField()
    advanced_params = pw.JSONField()
    created_at = pw.DateTimeField(constraints=[pw.SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = db

def migrate(migrator, database, fake=False, **kwargs):
    migrator.create_model(ChatPreset)
