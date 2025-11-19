import struct
import math

cd = 0xFFFFFFFF
class MD5:
    """Реалізація алгоритму хешування MD5 згідно RFC 1321"""

    # Таблиця T, створена на основі функції синуса
    T = [int(abs(math.sin(i + 1)) * 2 ** 32) & cd for i in range(64)]

    # Значення циклічних зсувів для кожного циклу
    S = [
        [7, 12, 17, 22] * 4,  # Цикл 1
        [5, 9, 14, 20] * 4,  # Цикл 2
        [4, 11, 16, 23] * 4,  # Цикл 3
        [6, 10, 15, 21] * 4  # Цикл 4
    ]

    # Початкові значення буфера ABCD
    INIT_A = 0x67452301
    INIT_B = 0xEFCDAB89
    INIT_C = 0x98BADCFE
    INIT_D = 0x10325476

    @staticmethod
    def _left_rotate(value, shift):
        """Циклічний зсув вліво на shift біт для 32-бітового значення"""
        value &= cd
        return ((value << shift) | (value >> (32 - shift))) & cd

    @staticmethod
    def _f(b, c, d):
        return (b & c) | (~b & d)

    @staticmethod
    def _g(b, c, d):
        return (b & d) | (c & ~d)

    @staticmethod
    def _h(b, c, d):
        return b ^ c ^ d

    @staticmethod
    def _i(b, c, d):
        return c ^ (b | ~d)

    @staticmethod
    def _padding(message):
        """
        Крок 1 і 2: Додавання доповнення та довжини
        Повідомлення доповнюється до довжини 448 mod 512,
        потім додається 64-бітове значення довжини
        """
        msg_len = len(message)
        message += b'\x80'  # Додаємо біт 1 та біти 0

        # Доповнюємо нулями до 448 mod 512 біт (56 mod 64 байт)
        while len(message) % 64 != 56:
            message += b'\x00'

        # Додаємо довжину вихідного повідомлення в бітах (64 біти, little-endian)
        message += struct.pack('<Q', msg_len * 8)

        return message

    @staticmethod
    def _process_block(block, a, b, c, d):
        """
        Крок 4: Обробка одного 512-бітового блоку
        Виконує 4 цикли по 16 раундів кожен
        """
        # Розбиваємо блок на 16 32-бітових слів (little-endian)
        X = list(struct.unpack('<16I', block))

        # Зберігаємо початкові значення
        aa, bb, cc, dd = a, b, c, d

        # Цикл 1: використовуємо функцію F
        for i in range(16):
            k = i
            a, b, c, d = d, (b + MD5._left_rotate(
                (a + MD5._f(b, c, d) + X[k] + MD5.T[i]) & cd,
                MD5.S[0][i]
            )) & cd, b, c

        # Цикл 2: використовуємо функцію G
        for i in range(16):
            k = (1 + 5 * i) % 16
            a, b, c, d = d, (b + MD5._left_rotate(
                (a + MD5._g(b, c, d) + X[k] + MD5.T[i + 16]) & cd,
                MD5.S[1][i]
            )) & cd, b, c

        # Цикл 3: використовуємо функцію H
        for i in range(16):
            k = (5 + 3 * i) % 16
            a, b, c, d = d, (b + MD5._left_rotate(
                (a + MD5._h(b, c, d) + X[k] + MD5.T[i + 32]) & cd,
                MD5.S[2][i]
            )) & cd, b, c

        # Цикл 4: використовуємо функцію I
        for i in range(16):
            k = (7 * i) % 16
            a, b, c, d = d, (b + MD5._left_rotate(
                (a + MD5._i(b, c, d) + X[k] + MD5.T[i + 48]) & cd,
                MD5.S[3][i]
            )) & cd, b, c

        # Додаємо результат до початкових значень
        a = (a + aa) & cd
        b = (b + bb) & cd
        c = (c + cc) & cd
        d = (d + dd) & cd

        return a, b, c, d

    @staticmethod
    def hash_bytes(data):
        """
        Обчислює MD5 хеш для байтових даних

        Args:
            data: байтові дані для хешування

        Returns:
            str: хеш у шістнадцятковому форматі (32 символи)
        """
        # Крок 3: Ініціалізація MD-буфера
        a = MD5.INIT_A
        b = MD5.INIT_B
        c = MD5.INIT_C
        d = MD5.INIT_D

        # Крок 1-2: Доповнення повідомлення
        padded_data = MD5._padding(data)

        # Крок 4: Обробка повідомлення блоками по 512 біт (64 байти)
        for i in range(0, len(padded_data), 64):
            block = padded_data[i:i + 64]
            a, b, c, d = MD5._process_block(block, a, b, c, d)

        # Крок 5: Формування виходу (128 біт = 16 байт)
        # Конвертуємо в little-endian формат
        result = struct.pack('<4I', a, b, c, d)

        # Повертаємо у шістнадцятковому форматі
        return result.hex().upper()

    @staticmethod
    def hash_string(text):
        """
        Обчислює MD5 хеш для текстового рядка

        Args:
            text: текстовий рядок для хешування

        Returns:
            str: хеш у шістнадцятковому форматі
        """
        return MD5.hash_bytes(text.encode('utf-8'))

    @staticmethod
    def hash_file(filepath=None, file_object=None, chunk_size=8192):
        """
        Обчислює MD5 хеш для файлу
        Підтримує обробку великих файлів по частинах

        Args:
            filepath: шлях до файлу (для локальних файлів)
            file_object: об'єкт файлу (для завантажених через Django)
            chunk_size: розмір блоку для читання (байт)

        Returns:
            str: хеш у шістнадцятковому форматі
        """
        # Крок 3: Ініціалізація MD-буфера
        a = MD5.INIT_A
        b = MD5.INIT_B
        c = MD5.INIT_C
        d = MD5.INIT_D

        total_length = 0
        buffer = b''

        # Визначаємо, з якого джерела читати
        if file_object:
            file_object.seek(0)
            source = file_object
        elif filepath:
            source = open(filepath, 'rb')
        else:
            raise ValueError("Необхідно вказати filepath або file_object")

        try:
            # Читаємо файл по частинах
            while True:
                chunk = source.read(chunk_size)
                if not chunk:
                    break

                buffer += chunk
                total_length += len(chunk)

                # Обробляємо повні 512-бітові блоки (64 байти)
                while len(buffer) >= 64:
                    block = buffer[:64]
                    buffer = buffer[64:]
                    a, b, c, d = MD5._process_block(block, a, b, c, d)

            # Обробляємо залишок з доповненням
            final_data = MD5._padding(buffer)
            for i in range(0, len(final_data), 64):
                block = final_data[i:i + 64]
                a, b, c, d = MD5._process_block(block, a, b, c, d)

            # Враховуємо довжину вже оброблених даних
            if len(final_data) > 0:
                # Коригуємо останній блок з правильною довжиною
                a = MD5.INIT_A
                b = MD5.INIT_B
                c = MD5.INIT_C
                d = MD5.INIT_D

                # Перечитуємо файл для правильного підрахунку
                if file_object:
                    file_object.seek(0)
                    all_data = file_object.read()
                else:
                    source.seek(0)
                    all_data = source.read()

                return MD5.hash_bytes(all_data)

        finally:
            if filepath and source:
                source.close()

        # Формуємо результат
        result = struct.pack('<4I', a, b, c, d)
        return result.hex().upper()

    @staticmethod
    def verify_file(filepath=None, file_object=None, expected_hash=None):
        """
        Перевіряє цілісність файлу за MD5 хешем

        Args:
            filepath: шлях до файлу
            file_object: об'єкт файлу
            expected_hash: очікуваний хеш

        Returns:
            dict: результат перевірки
        """
        actual_hash = MD5.hash_file(filepath=filepath, file_object=file_object)

        # Нормалізуємо хеші до верхнього регістру
        expected_hash = expected_hash.strip().upper()
        actual_hash = actual_hash.upper()

        match = actual_hash == expected_hash

        return {
            'match': match,
            'expected_hash': expected_hash,
            'actual_hash': actual_hash,
            'message': 'Файл не змінювався' if match else 'Файл було змінено!'
        }