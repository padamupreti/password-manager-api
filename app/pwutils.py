from cryptography.fernet import Fernet
from .config import settings

cipher = Fernet(settings.pw_encryption_key)


def encrypt(secret: str):
    encrypted = cipher.encrypt(secret.encode()).decode()
    return encrypted


def decrypt(secret: str):
    decrypted = cipher.decrypt(secret.encode()).decode()
    return decrypted
