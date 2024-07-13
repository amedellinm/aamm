import os
import secrets
import string
from base64 import urlsafe_b64encode

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def decrypt(encrypted_data: bytes, password: str) -> bytes | None:
    size = encrypted_data[0]
    salt = encrypted_data[1 : size + 1]
    data = encrypted_data[size + 1 :]
    keys = key_from_password(password, salt)
    try:
        return Fernet(keys).decrypt(data)
    except InvalidToken:
        return None


def encrypt(data: bytes, password: str, salt_size: int = 16) -> bytes:
    salt = os.urandom(salt_size)
    keys = key_from_password(password, salt)
    return salt_size.to_bytes(1) + salt + Fernet(keys).encrypt(data)


def generate_password(
    length: int = 32,
    lowers: bool = True,
    uppers: bool = True,
    digits: bool = True,
    others: bool = True,
) -> str:

    chars = (
        uppers * string.ascii_uppercase
        + lowers * string.ascii_lowercase
        + digits * string.digits
        + others * string.punctuation
    )

    return "".join(secrets.choice(chars) for _ in range(length))


def key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(hashes.SHA256(), 32, salt, 100_000)
    return urlsafe_b64encode(kdf.derive(password.encode()))
