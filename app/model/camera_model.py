from sqlalchemy import Column, String, TEXT, INTEGER, ForeignKey
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


# Tuyến đường
class CameraModel(BaseModel):
    __tablename__ = 'camera'
    name = Column(String(250), nullable=False)
    channel_id = Column(String(100), nullable=False)
    id_camera_vms = Column(String(100), nullable=False)
    status = Column(String(100), nullable=False)
