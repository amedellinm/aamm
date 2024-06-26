import os
from base64 import urlsafe_b64encode

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(hashes.SHA256(), 32, salt, 100_000)
    return urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(data: bytes, password: str, salt_size: int = 16) -> bytes:
    salt = os.urandom(salt_size)
    keys = key_from_password(password, salt)
    return salt_size.to_bytes(1) + salt + Fernet(keys).encrypt(data)


def decrypt(encrypted_data: bytes, password: str) -> bytes | None:
    size = encrypted_data[0]
    salt = encrypted_data[1 : size + 1]
    data = encrypted_data[size + 1 :]
    keys = key_from_password(password, salt)
    try:
        return Fernet(keys).decrypt(data)
    except InvalidToken:
        return None


# if __name__ == "__main__":
#     import json

#     password = "my_secure_password"
#     data = {"name": "John", "age": 30}

#     encrypted_data = encrypt(json.dumps(data).encode(), password)
#     print(f"Encrypted data:\n\t{encrypted_data.hex()}")

#     decrypted_data = decrypt(encrypted_data, password)
#     if decrypted_data is None:
#         print("Unable to decrypt")
#     else:
#         print("Decrypted data:")
#         for k, v in json.loads(decrypted_data.decode()).items():
#             print(f"\t{k!r}: {v!r}")
