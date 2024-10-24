from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from open_webui.apps.webui.internal.db import get_db
from open_webui.apps.webui.models.presets import Preset
from open_webui.apps.webui.models.users import get_current_user

router = APIRouter()

@router.post("/save", response_model=Preset)
def save_preset(preset: Preset, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_preset = db.query(Preset).filter(Preset.name == preset.name).first()
    if db_preset:
        raise HTTPException(status_code=400, detail="Preset name already exists")
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset

@router.get("/", response_model=List[Preset])
def get_presets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Preset).all()

@router.get("/{preset_name}", response_model=Preset)
def get_preset(preset_name: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    preset = db.query(Preset).filter(Preset.name == preset_name).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset
