from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import math


class RSAEngine:
    """
    Клас для реалізації алгоритму RSA з використанням бібліотеки cryptography.
    Забезпечує генерацію ключів, збереження/завантаження та шифрування/дешифрування даних довільного розміру.
    """

    def __init__(self, key_size=2048):
        self.key_size = key_size
        self.private_key = None
        self.public_key = None
        self.backend = default_backend()

    def generate_keys(self):
        """Генерація пари ключів (публічний та приватний)"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=self.backend
        )
        self.public_key = self.private_key.public_key()
        return self.private_key, self.public_key

    def save_keys(self, private_path: str, public_path: str, password: str = None):
        """
        Збереження ключів у файли (формат PEM).
        Приватний ключ може бути зашифрований паролем.
        """
        if not self.private_key or not self.public_key:
            raise ValueError("Ключі не згенеровані або не завантажені")

        # Визначаємо алгоритм шифрування приватного ключа
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password.encode('utf-8'))
        else:
            encryption_algorithm = serialization.NoEncryption()

        # Серіалізація приватного ключа
        pem_private = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )

        # Серіалізація публічного ключа
        pem_public = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Запис у файли
        with open(private_path, 'wb') as f:
            f.write(pem_private)

        with open(public_path, 'wb') as f:
            f.write(pem_public)

    def load_keys(self, private_path: str, public_path: str, password: str = None):
        """Завантаження ключів з файлів PEM"""

        # Завантаження приватного ключа
        with open(private_path, 'rb') as f:
            private_bytes = f.read()
            self.private_key = serialization.load_pem_private_key(
                private_bytes,
                password=password.encode('utf-8') if password else None,
                backend=self.backend
            )

        # Завантаження публічного ключа
        with open(public_path, 'rb') as f:
            public_bytes = f.read()
            self.public_key = serialization.load_pem_public_key(
                public_bytes,
                backend=self.backend
            )

        # Оновлюємо розмір ключа на основі завантаженого
        self.key_size = self.private_key.key_size

    def _get_max_encrypt_block_size(self):
        """
        Розрахунок максимального розміру блоку даних для шифрування.
        RSA з OAEP padding (SHA256) має накладні витрати.
        Max data size = KeySizeBytes - 2 * HashLen - 2
        """
        key_size_bytes = self.key_size // 8
        hash_len = 32  # SHA256 digest size in bytes
        return key_size_bytes - 2 * hash_len - 2

    def encrypt_data(self, data: bytes) -> bytes:
        """
        Шифрування даних довільного розміру.
        Дані розбиваються на блоки, кожен блок шифрується окремо.
        """
        if not self.public_key:
            raise ValueError("Публічний ключ не встановлено")

        max_block_size = self._get_max_encrypt_block_size()
        encrypted_data = bytearray()

        # Розбиваємо дані на блоки та шифруємо кожен
        for i in range(0, len(data), max_block_size):
            chunk = data[i: i + max_block_size]

            encrypted_chunk = self.public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_data.extend(encrypted_chunk)

        return bytes(encrypted_data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        Дешифрування даних.
        Вхідні дані розбиваються на блоки розміром з ключ (в байтах),
        кожен блок дешифрується окремо.
        """
        if not self.private_key:
            raise ValueError("Приватний ключ не встановлено")

        # Розмір зашифрованого блоку завжди дорівнює розміру ключа в байтах
        block_size = self.key_size // 8
        decrypted_data = bytearray()

        if len(encrypted_data) % block_size != 0:
            raise ValueError("Некоректна довжина зашифрованих даних (не кратна розміру блоку)")

        for i in range(0, len(encrypted_data), block_size):
            chunk = encrypted_data[i: i + block_size]

            decrypted_chunk = self.private_key.decrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_data.extend(decrypted_chunk)

        return bytes(decrypted_data)