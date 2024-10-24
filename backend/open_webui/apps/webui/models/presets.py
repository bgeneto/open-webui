from sqlalchemy import Column, Integer, String, Text
from open_webui.apps.webui.internal.db import Base, JSONField

class Preset(Base):
    __tablename__ = "preset"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    system_prompt = Column(Text, nullable=False)
    advanced_params = Column(JSONField, nullable=False)
