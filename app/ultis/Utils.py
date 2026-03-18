import socket


class Utils:
    @staticmethod
    def get_value_from_key(key: str, json_obj: dict) -> str:
        return str(json_obj.get(key, ""))

    @staticmethod
    def get_ip_address() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
