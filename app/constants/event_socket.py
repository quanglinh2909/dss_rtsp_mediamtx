from enum import Enum


class EventSocket(str,Enum):
    # trạng thại online hay offline của thiết bị relay
    STATUS_RELAY_DEVICE = "status_relay_device"
    # đếm ngược thời gian cho đèn tín hiệu
    UPDATE_REMAINING_TIME = "update_remaining_time"
    # cập nhật trạng thái đèn tín hiệu
    UPDATE_LIGHTS_STATUS = "update_lights_status"
    # cập nhật trạng thái kết nối camera
    UPDATE_CAMERA_STATUS = "update_camera_status"
    STATUS_CLOUD_CONNECTION = "status_cloud_connection"
    EVENT_DETECT = "event_detect"
