from dataclasses import dataclass


@dataclass
class LoginResponse:
    duration: str
    private_key: str
    public_key: str
    secret_key_with_sa: str
    secret_vector: str
    user_id: str
    token_value: str
    signature_md5_temp4: str