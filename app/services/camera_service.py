from fastapi import HTTPException

from fastapi import HTTPException

from app.constants.camera_enum import StatusCameraEnum
from app.dto.camera_dto import CameraUpdateDTO, CameraCreateDTO
from app.model.camera_model import CameraModel
from app.services.base_service import BaseService


class CameraService(BaseService[CameraModel]):

    def __init__(self):
        super().__init__(CameraModel)

    def create_camera(self, camera: CameraCreateDTO):
        result = self.create(**camera.model_dump(), status=StatusCameraEnum.UNKNOWN)
        if not result:
            return result
        from app.services.manager_public_camera import manager_public_camera
        manager_public_camera.add_camera(result.id, result.channel_id, result.id_camera_vms)

        return result

    def update_camera(self, id, camera: CameraUpdateDTO):
        camera_existing = self.get_by_id(id)
        if not camera_existing:
            raise HTTPException(status_code=404, detail=f"Camera không tồn tại")
        res = self.update(id, **camera.model_dump(exclude_unset=True))
        if not res:
            return res
        from app.services.manager_public_camera import manager_public_camera
        manager_public_camera.add_camera(res.id, res.channel_id, res.id_camera_vms)
        return res

    def delete_camera(self, id: str):
        res = self.delete(id)
        if res:
            from app.services.manager_public_camera import manager_public_camera
            manager_public_camera.delete_camera(id)
        return res

    def load_all_camera(self):
        cameras = self.get_all()
        for camera in cameras:
            from app.services.manager_public_camera import manager_public_camera
            manager_public_camera.add_camera(camera.id, camera.channel_id, camera.id_camera_vms)


camera_service = CameraService()
