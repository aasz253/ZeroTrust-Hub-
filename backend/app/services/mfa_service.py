import pyotp
import hashlib
import secrets
from typing import Optional


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "ZeroTrust Hub") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_recovery_codes(count: int = 8) -> list[str]:
    codes = []
    for _ in range(count):
        code = secrets.token_hex(4).upper()
        code = f"{code[:4]}-{code[4:]}"
        codes.append(code)
    return codes


def hash_recovery_codes(codes: list[str]) -> list[str]:
    return [hashlib.sha256(c.encode()).hexdigest() for c in codes]


def verify_recovery_code(code: str, hashed_codes: list[str]) -> bool:
    if not hashed_codes:
        return False
    hashed = hashlib.sha256(code.encode()).hexdigest()
    return hashed in hashed_codes


def remove_used_code(code: str, hashed_codes: list[str]) -> list[str]:
    hashed = hashlib.sha256(code.encode()).hexdigest()
    remaining = [c for c in hashed_codes if c != hashed]
    return remaining if remaining else []
