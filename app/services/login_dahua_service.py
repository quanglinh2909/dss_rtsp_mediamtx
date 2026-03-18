import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.config.settings import settings
from app.dto.LoginResponse import LoginResponse
from app.ultis.APIDahuaBase import APIDahuaBase
from app.ultis.Utils import Utils


class LoginDahuaService:
    def __init__(self):
        self.api_dahua_base = APIDahuaBase()

    def get_rsa_keys(self) -> Tuple[str, str]:
        """Sinh ra cặp khóa RSA (2048 bit). Trả về (public_key_b64, private_key_b64)"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Generate base64 string for Public Key (X.509 format tương tự như java getEncoded)
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Generate base64 string for Private Key (PKCS#8 format tương tự như java getEncoded)
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_b64 = base64.b64encode(public_bytes).decode('utf-8')
        private_b64 = base64.b64encode(private_bytes).decode('utf-8')

        return public_b64, private_b64

    def md5_hex(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def login(self) -> Optional[LoginResponse]:
        user_name = settings.DAHUA_USERNAME
        password = settings.DAHUA_PASSWORD
        url_base = settings.DAHUA_URL_BASE
        # Lần authorize thứ nhất
        params_1 = {
            "userName": user_name,
            "ipAddress": password,  # Tuân theo logic ở Java (Lưu ý: map.put("ipAddress", password))
            "clientType": "WINPC_V2"
        }

        try:
            first_response_str = self.api_dahua_base.post(
                f"{url_base}/brms/api/v1.0/accounts/authorize",
                params_1,
                "POST"
            )

            if not first_response_str:
                return None

            first_login_response = json.loads(first_response_str)
            realm = Utils.get_value_from_key("realm", first_login_response)

            if not first_response_str or not realm:
                return None

            random_key = str(first_login_response.get("randomKey", ""))

            # Tính MD5 theo hướng dẫn của API
            temp1 = self.md5_hex(password)
            temp2 = self.md5_hex(user_name + temp1)
            temp3 = self.md5_hex(temp2)
            temp4 = self.md5_hex(f"{user_name}:{realm}:{temp3}")

            # Retain the temp4 to calculate signature later
            signature_md5_temp4 = temp4
            signature = self.md5_hex(f"{temp4}:{random_key}")

            # Sinh khóa RSA
            public_key_b64, private_key_b64 = self.get_rsa_keys()

            # Lần authorize thứ hai
            second_login_params = {
                "signature": signature,
                "userName": user_name,
                "randomKey": random_key,
                "publicKey": public_key_b64,
                "encrytType": "MD5",
                "ipAddress": Utils.get_ip_address(),
                "clientType": "WINPC_V2",
                "userType": "0"
            }

            second_response_str = self.api_dahua_base.post(
                f"{url_base}/brms/api/v1.0/accounts/authorize",
                second_login_params,
                "POST"
            )

            if not second_response_str:
                return None

            second_response = json.loads(second_response_str)

            if "code" in second_response:
                return None

            # Lấy token value. (Java dùng key bằng APIConstants.TOKEN, assume nó là 'token')
            token_value = second_response.get("token", "")
            secret_key_with_sa = str(second_response.get("secretKey", ""))
            duration = str(second_response.get("duration", ""))
            secret_vector = str(second_response.get("secretVector", ""))
            user_id = str(second_response.get("userId", ""))

            return LoginResponse(
                duration=duration,
                private_key=private_key_b64,
                public_key=public_key_b64,
                secret_key_with_sa=secret_key_with_sa,
                secret_vector=secret_vector,
                user_id=user_id,
                token_value=token_value,
                signature_md5_temp4=signature_md5_temp4
            )

        except Exception as e:
            print(f"Exception khi đăng nhập: {e}")
            return None

    def get_rtsp(self,channel_id,streamType):
        response = self.login()
        if response:
            token_value = response.token_value
            data_send = {
                "clientType": "WINPC_V1",
                "clientMac": "1C-61-B4-97-7C-0F",
                "clientPushId": "",
                "project": "PSDK",
                "method": "MTS.Video.StartVideo",
                "token": token_value,
                "data": {
                    "streamType": streamType,
                    "trackId": "",
                    "extend": "",
                    "channelId":channel_id,
                    "keyCode": "",
                    "planId": "",
                    "dataType": "3",
                    "enableRtsps": "0"
                }
            }
            try:
                rtsp_response = self.api_dahua_base.post(
                    f"{settings.DAHUA_URL_BASE}/brms/api/v1.0/MTS/Video/StartVideo",
                    data_send,
                )
                if not rtsp_response:
                    return None
                # convert string to json
                rtsp_response = json.loads(rtsp_response)
                data_res = rtsp_response.get("data", {})
                rtsp = data_res.get("url", None)
                token = data_res.get("token", None)
                if not rtsp or not token:
                    return None
                return f"{rtsp}?token={token}"
            except Exception as e:
                print(f"Exception khi rtsp: {e}")
                return None
        return None


login_dahua_service = LoginDahuaService()

if __name__ == '__main__':
    response = login_dahua_service.get_rtsp("1", "1")
    print(response)
