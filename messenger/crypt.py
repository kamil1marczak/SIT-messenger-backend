import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings


class Cryptographer:
    def __init__(self, password, key=None):

        self.password = self.get_bytes(password)
        self.key = key if key else self.generate_key()
        # self.fernet()
        self.fernet = Fernet(self.key)

    # @property
    # def fernet(self):
    #     if self.fernet == None:
    #         self.fernet = Fernet(self.key)
        # return Fernet(self.key)


    def generate_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.get_bytes(settings.SALT),
            iterations=100000, )

        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key

    def encrypt(self, message):
        b_message = self.get_bytes(message)
        encrypted_message = self.fernet.encrypt(b_message)
        return encrypted_message

    def decrypt(self, encrypted_message):
        b_message = self.get_bytes(encrypted_message)
        decrypted_message = self.fernet.decrypt(b_message)
        return decrypted_message

    @staticmethod
    def get_bytes(v):

        if isinstance(v, str):
            return bytes(v.encode("utf-8"))

        if isinstance(v, bytes):
            return v

        raise TypeError(
            "SALT & PASSWORD must be specified as strings that convert nicely to "
            "bytes."
        )
