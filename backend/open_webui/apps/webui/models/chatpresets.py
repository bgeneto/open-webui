import datetime
from typing import Optional, List
from pydantic import BaseModel
from open_webui.apps.webui.internal.db import Base, get_db
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ChatPreset(Base):
    __tablename__ = "chatpreset"

    id = Column(String, primary_key=True)
    preset_name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    system_prompt = Column(Text, nullable=False)
    advanced_params = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chatpresets")

class ChatPresetModel(BaseModel):
    id: str
    preset_name: str
    user_id: str
    system_prompt: str
    advanced_params: dict
    created_at: datetime.datetime

class ChatPresetTable:
    def insert_new_preset(self, preset_name: str, user_id: str, system_prompt: str, advanced_params: dict) -> Optional[ChatPresetModel]:
        with get_db() as db:
            id = str(uuid.uuid4())
            preset = ChatPreset(
                id=id,
                preset_name=preset_name,
                user_id=user_id,
                system_prompt=system_prompt,
                advanced_params=advanced_params,
                created_at=datetime.datetime.utcnow()
            )
            db.add(preset)
            db.commit()
            db.refresh(preset)
            return ChatPresetModel.from_orm(preset) if preset else None

    def get_presets_by_user_id(self, user_id: str) -> List[ChatPresetModel]:
        with get_db() as db:
            presets = db.query(ChatPreset).filter_by(user_id=user_id).all()
            return [ChatPresetModel.from_orm(preset) for preset in presets]

    def delete_preset_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                db.query(ChatPreset).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

ChatPresets = ChatPresetTable()
