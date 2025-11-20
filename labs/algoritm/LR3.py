import struct
from .LR1 import LinearCongruentialGenerator
from .LR2 import MD5

#Реалізація алгоритму RC5
class RC5:

    # Константи для w=16
    # P16 = 0xB7E1
    # Q16 = 0x9E37
    # MASK_16 = 0xFFFF

    # Константи для w=32
    P32 = 0xB7E15163 #Ox позначення в шістнадцятковому виді для Python
    Q32 = 0x9E3779B9
    MASK_32 = 0xFFFFFFFF

    # Константи для w=64
    # P64 = 0xB7E151628AED2A6B
    # Q64 = 0x9E3779B97F4A7C15
    # MASK_64 = 0xFFFFFFFFFFFFFFFF

    def __init__(self, key_bytes, w, r, b):
        """
        Ініціалізація RC5.
        :param key_bytes: байти ключа
        :param w: розмір слова в бітах
        :param r: кількість раундів
        :param b: довжина ключа в байтах
        """
        self.w = w
        self.r = r
        self.b = b

        if self.w != 32:
            raise ValueError("Ця реалізація підтримує лише w=32")

        self.mask = self.MASK_32

        # Обрізаємо або беремо ключ відповідно до довжини b
        self.key = key_bytes[:self.b]
        self.S = self.key_expansion()

    def rotate_left(self, val, n):
        n %= self.w
        return ((val << n) | (val >> (self.w - n))) & self.mask

    def rotate_right(self, val, n):
        n %= self.w
        return ((val >> n) | (val << (self.w - n))) & self.mask

    def key_expansion(self):
        """Генерація підключів (Key Expansion)"""
        # c - кількість слів у ключі (b / u, де u = w/8)
        u = self.w // 8
        c = max(1, len(self.key) // u)

        # Конвертуємо байти ключа в масив слів L
        L = [0] * c
        for i in range(c):
            L[i] = int.from_bytes(self.key[i * u: (i + 1) * u], byteorder='little')

        # Ініціалізація масиву S
        t = 2 * (self.r + 1)
        S = [0] * t
        S[0] = self.P32
        for i in range(1, t):
            S[i] = (S[i - 1] + self.Q32) & self.mask

        # Змішування S і L
        i = j = 0
        A = B = 0
        loops = 3 * max(t, c)

        for _ in range(loops):
            A = S[i] = self.rotate_left((S[i] + A + B) & self.mask, 3)
            B = L[j] = self.rotate_left((L[j] + A + B) & self.mask, (A + B))
            i = (i + 1) % t
            j = (j + 1) % c

        return S

    def _encrypt_block_ecb(self, data_bytes):
        """Шифрування одного блоку (64 біти для w=32)"""
        # Розпаковуємо 2 слова по 4 байти (для w=32)
        A, B = struct.unpack('<II', data_bytes)

        A = (A + self.S[0]) & self.mask
        B = (B + self.S[1]) & self.mask

        for i in range(1, self.r + 1):
            A = (self.rotate_left(A ^ B, B) + self.S[2 * i]) & self.mask
            B = (self.rotate_left(B ^ A, A) + self.S[2 * i + 1]) & self.mask

        return struct.pack('<II', A, B)

    def _decrypt_block_ecb(self, data_bytes):
        """Дешифрування одного блоку"""
        A, B = struct.unpack('<II', data_bytes)

        for i in range(self.r, 0, -1):
            B = self.rotate_right((B - self.S[2 * i + 1]) & self.mask, A) ^ A
            A = self.rotate_right((A - self.S[2 * i]) & self.mask, B) ^ B

        B = (B - self.S[1]) & self.mask
        A = (A - self.S[0]) & self.mask

        return struct.pack('<II', A, B)

    @staticmethod
    def _pad_data(data, block_size_bytes=8):
        """PKCS7 Padding"""
        padding_len = block_size_bytes - (len(data) % block_size_bytes)
        padding = bytes([padding_len] * padding_len)
        return data + padding

    @staticmethod
    def _unpad_data(data, block_size_bytes=8):
        """Видалення PKCS7 Padding"""
        if not data:
            return b''
        padding_len = data[-1]
        if padding_len > block_size_bytes or padding_len == 0:
            raise ValueError("Invalid padding")
        return data[:-padding_len]

    @staticmethod
    def derive_key_from_password(password, key_length_bytes):
        """
        Генерація ключа з паролю через MD5.
        :param key_length_bytes: необхідна довжина ключа (b)
        """
        md5_hash_hex = MD5.hash_string(password)
        full_hash = bytes.fromhex(md5_hash_hex)
        # Беремо потрібну кількість байт
        return full_hash[:key_length_bytes]

    @staticmethod
    def generate_iv(lr1_config):
        """
        Генерація вектора ініціалізації (IV) за допомогою ГПВЧ з ЛР1.
        :param lr1_config: словник з параметрами m, a, c, x0
        """
        lcg = LinearCongruentialGenerator(
            m=lr1_config['m'],
            a=lr1_config['a'],
            c=lr1_config['c'],
            x0=lr1_config['x0']
        )

        # Генеруємо 2 слова по 32 біти для IV (всього 8 байт)
        iv_part1 = lcg.next()
        iv_part2 = lcg.next()

        return struct.pack('<II', iv_part1, iv_part2)

    @staticmethod
    def encrypt_data(data, password, rc5_config, lr1_config):
        """Головна функція шифрування (RC5-CBC-Pad)."""
        w = rc5_config['w']
        r = rc5_config['r']
        b = rc5_config['b']

        block_size = (w // 8) * 2  # 8 байт для w=32

        # 1. Підготовка ключа
        key = RC5.derive_key_from_password(password, b)
        rc5 = RC5(key, w, r, b)

        # 2. Підготовка IV
        iv = RC5.generate_iv(lr1_config)

        # 3. Шифруємо IV в режимі ECB
        encrypted_iv = rc5._encrypt_block_ecb(iv)

        # 4. Доповнення даних
        padded_data = RC5._pad_data(data, block_size)

        # 5. Шифрування CBC
        ciphertext = bytearray()
        previous_block = iv

        for i in range(0, len(padded_data), block_size):
            block = padded_data[i: i + block_size]

            blk_int = int.from_bytes(block, 'little')
            prev_int = int.from_bytes(previous_block, 'little')

            xored = (blk_int ^ prev_int).to_bytes(block_size, 'little')

            encrypted_block = rc5._encrypt_block_ecb(xored)

            ciphertext.extend(encrypted_block)
            previous_block = encrypted_block

        return encrypted_iv + ciphertext

    @staticmethod
    def decrypt_data(encrypted_data, password, rc5_config):
        """Головна функція дешифрування."""
        w = rc5_config['w']
        r = rc5_config['r']
        b = rc5_config['b']

        block_size = (w // 8) * 2  # 8 байт

        if len(encrypted_data) < block_size * 2:  # Мін: Enc_IV + 1 блок
            raise ValueError("Data too short")

        # 1. Підготовка ключа
        key = RC5.derive_key_from_password(password, b)
        rc5 = RC5(key, w, r, b)

        # 2. Витягуємо та розшифровуємо IV
        encrypted_iv = encrypted_data[:block_size]
        iv = rc5._decrypt_block_ecb(encrypted_iv)

        ciphertext = encrypted_data[block_size:]
        plaintext = bytearray()
        previous_block = iv

        # 3. Дешифрування CBC
        for i in range(0, len(ciphertext), block_size):
            encrypted_block = ciphertext[i: i + block_size]

            decrypted_block = rc5._decrypt_block_ecb(encrypted_block)

            dec_int = int.from_bytes(decrypted_block, 'little')
            prev_int = int.from_bytes(previous_block, 'little')

            original_block = (dec_int ^ prev_int).to_bytes(block_size, 'little')

            plaintext.extend(original_block)
            previous_block = encrypted_block

        # 4. Зняття Padding
        try:
            return RC5._unpad_data(plaintext, block_size)
        except ValueError:
            raise ValueError("Помилка дешифрування: невірний пароль або пошкоджені дані")