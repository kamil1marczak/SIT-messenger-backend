
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings


def generate_password_key(password):
    # password = b"password"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=get_bytes(settings.SALT),
        iterations=100000, )

    key = base64.urlsafe_b64encode(kdf.derive(get_bytes(password)))
    return key


def get_bytes(v):

    if isinstance(v, str):
        return bytes(v.encode("utf-8"))

    if isinstance(v, bytes):
        return v

    raise TypeError(
        "SALT & PASSWORD must be specified as strings that convert nicely to "
        "bytes."
    )