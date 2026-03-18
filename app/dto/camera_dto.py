from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.constants.camera_enum import AIEngineEnum


class CameraCreateDTO(BaseModel):
    name: str
    channel_id: str
    id_camera_vms: str


class CameraUpdateDTO(BaseModel):
    name: Optional[str] = None
    channel_id: Optional[str] = None
    id_camera_vms: Optional[str] = None
