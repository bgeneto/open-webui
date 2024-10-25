from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from open_webui.apps.webui.internal.db import get_db
from open_webui.apps.webui.models.presets import Preset, PresetCreate, PresetUpdate
from open_webui.apps.webui.utils import get_current_user

router = APIRouter()

@router.post("/save", response_model=Preset)
def save_preset(preset: PresetCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_preset = db.query(Preset).filter(Preset.user_id == user.id, Preset.name == preset.name).first()
    if db_preset:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Preset name already exists")
    new_preset = Preset(user_id=user.id, **preset.dict())
    db.add(new_preset)
    db.commit()
    db.refresh(new_preset)
    return new_preset

@router.get("/", response_model=List[Preset])
def get_presets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Preset).filter(Preset.user_id == user.id).all()

@router.get("/{preset_name}", response_model=Preset)
def get_preset(preset_name: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_preset = db.query(Preset).filter(Preset.user_id == user.id, Preset.name == preset_name).first()
    if not db_preset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return db_preset

@router.delete("/{preset_name}", response_model=bool)
def delete_preset(preset_name: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_preset = db.query(Preset).filter(Preset.user_id == user.id, Preset.name == preset_name).first()
    if not db_preset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    db.delete(db_preset)
    db.commit()
    return True
