from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from open_webui.apps.webui.models.chatpresets import ChatPresetModel, ChatPresets
from open_webui.constants import ERROR_MESSAGES
from open_webui.utils.utils import get_verified_user

router = APIRouter()

############################
# SaveChatPreset
############################

@router.post("/save", response_model=Optional[ChatPresetModel])
async def save_chat_preset(preset_name: str, system_prompt: str, advanced_params: dict, user=Depends(get_verified_user)):
    preset = ChatPresets.insert_new_preset(preset_name, user.id, system_prompt, advanced_params)
    if preset:
        return preset
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )

############################
# GetChatPresets
############################

@router.get("/", response_model=List[ChatPresetModel])
async def get_chat_presets(user=Depends(get_verified_user)):
    return ChatPresets.get_presets_by_user_id(user.id)

############################
# DeleteChatPreset
############################

@router.delete("/delete/{preset_id}", response_model=bool)
async def delete_chat_preset(preset_id: str, user=Depends(get_verified_user)):
    result = ChatPresets.delete_preset_by_id(preset_id)
    return result
