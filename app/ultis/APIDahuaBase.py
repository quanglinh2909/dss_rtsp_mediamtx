from typing import Optional

import requests


class APIDahuaBase:
    def get(self, url: str, token_value: Optional[str] = None) -> Optional[str]:
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        if token_value:
            headers["X-Subject-Token"] = token_value

        try:
            response = requests.get(url, headers=headers)
            return response.text
        except Exception as e:
            print(f"GET Lỗi: {e}")
            return None

    def post(self, url: str, params: dict, request_mode: str = "POST") -> Optional[str]:
        if request_mode not in ("POST", "PUT"):
            print("requestMode phải là POST hoặc PUT")
            return None

        headers = {"Content-Type": "application/json;charset=UTF-8"}
        if "token" in params:
            headers["X-Subject-Token"] = str(params["token"])

        try:
            if request_mode == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif request_mode == "PUT":
                response = requests.put(url, json=params, headers=headers)

            return response.text
        except Exception as e:
            print(f"{request_mode} Lỗi: {e}")
            return None
