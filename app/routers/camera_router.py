# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends

from app.dto.camera_dto import CameraCreateDTO, CameraUpdateDTO
from app.services.camera_service import camera_service

router = APIRouter()
prefix = "/camera"
tags = ["Camera"]


@router.post("")
def create(req: CameraCreateDTO):
    return camera_service.create_camera(req)


@router.get("")
def get_all():
    return camera_service.get_all()


@router.get("/{id}")
def get_by_id(id: str):
    return camera_service.get_by_id(id)


@router.put("/{id}")
def update(id: str, req: CameraUpdateDTO):
    return camera_service.update_camera(id, req)


@router.delete("/{id}")
def delete(id: str):
    return camera_service.delete_camera(id)
