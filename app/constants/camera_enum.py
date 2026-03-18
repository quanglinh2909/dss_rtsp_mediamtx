from enum import Enum


class AIEngineEnum(str, Enum):
    CUSTOM = "custom"
    CAMERA = "camera"


class StatusCameraEnum(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    LOIN_ERROR = "login_error"
    AUTHORITY_ERROR = "authority_error"
    BAD_REQUEST = "bad_request"
    REQUEST_ERROR = "request_error"
    UNEXPECTED_ERROR = "unexpected_error"
    UNKNOWN = "unknown"
    RESTARTING = "restarting"
