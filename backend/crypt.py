from cryptography.fernet import Fernet
from passlib.hash import bcrypt
import base64

class CryptoHelper:
    def __init__(self, key: str = None):
        if key is None:
            self.key = Fernet.generate_key()
        elif not key.startswith("gAAAA"):
            key = base64.urlsafe_b64decode(key)

        self.fernet = Fernet(key)
        self.secret_key = key;

    def encrypt(self, plaintext: str) -> str:
        return self.fernet.encrypt(plaintext.encode().decode("utf8"))

    def decrypt(self, ciphertext: str) -> str:
        return self.fernet.decrypt(ciphertext.encode().decode("utf8"))

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf8"), self.secret_key)

    def verify_password(self, plaintext: str, password: str) -> bool:
        return bcrypt.verify(password, self.hash_password(plaintext))

    def get_key(self) -> str:
        return self.secret_key.decode()