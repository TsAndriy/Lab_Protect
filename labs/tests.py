from django.test import TestCase
import math
from .algoritm.LR1 import (
    LinearCongruentialGenerator,
    CesaroTest,
    FrequencyTest,
    RunsTest,
    gcd,
    VARIANT_17_CONFIG
)


class GCDTestCase(TestCase):
    """Тести для функції НСД (найбільший спільний дільник)"""

    def test_gcd_basic(self):
        """Базові тести НСД"""
        self.assertEqual(gcd(12, 8), 4)
        self.assertEqual(gcd(17, 5), 1)
        self.assertEqual(gcd(100, 50), 50)
        self.assertEqual(gcd(7, 13), 1)

    def test_gcd_same_numbers(self):
        """НСД однакових чисел"""
        self.assertEqual(gcd(5, 5), 5)
        self.assertEqual(gcd(100, 100), 100)

    def test_gcd_with_zero(self):
        """НСД з нулем"""
        self.assertEqual(gcd(0, 5), 5)
        self.assertEqual(gcd(7, 0), 7)

    def test_gcd_coprime(self):
        """НСД взаємно простих чисел"""
        self.assertEqual(gcd(13, 17), 1)
        self.assertEqual(gcd(9, 28), 1)


class LinearCongruentialGeneratorTestCase(TestCase):
    """Тести для генератора псевдовипадкових чисел"""

    def setUp(self):
        """Ініціалізація тестових даних"""
        self.generator = LinearCongruentialGenerator(
            m=VARIANT_17_CONFIG['m'],
            a=VARIANT_17_CONFIG['a'],
            c=VARIANT_17_CONFIG['c'],
            x0=VARIANT_17_CONFIG['x0']
        )

    def test_initialization(self):
        """Тест ініціалізації генератора"""
        self.assertEqual(self.generator.m, VARIANT_17_CONFIG['m'])
        self.assertEqual(self.generator.a, VARIANT_17_CONFIG['a'])
        self.assertEqual(self.generator.c, VARIANT_17_CONFIG['c'])
        self.assertEqual(self.generator.x0, VARIANT_17_CONFIG['x0'])
        self.assertEqual(self.generator.current, VARIANT_17_CONFIG['x0'])

    def test_next_generation(self):
        """Тест генерації наступного числа"""
        first = self.generator.next()
        self.assertIsInstance(first, int)
        self.assertGreaterEqual(first, 0)
        self.assertLess(first, self.generator.m)
        
        # Перевірка, що наступне число відрізняється
        second = self.generator.next()
        self.assertNotEqual(first, second)

    def test_generate_sequence(self):
        """Тест генерації послідовності"""
        n = 100
        sequence = self.generator.generate_sequence(n)
        
        self.assertEqual(len(sequence), n)
        self.assertTrue(all(isinstance(x, int) for x in sequence))
        self.assertTrue(all(0 <= x < self.generator.m for x in sequence))

    def test_reset(self):
        """Тест скидання генератора"""
        # Генеруємо кілька чисел
        self.generator.next()
        self.generator.next()
        self.generator.next()
        
        # Скидаємо
        self.generator.reset()
        
        self.assertEqual(self.generator.current, self.generator.x0)
        self.assertEqual(len(self.generator.history), 0)

    def test_deterministic_generation(self):
        """Тест детермінованості генерації"""
        # Перша послідовність
        seq1 = self.generator.generate_sequence(50)
        
        # Друга послідовність з тими ж параметрами
        seq2 = self.generator.generate_sequence(50)
        
        # Повинні бути однаковими
        self.assertEqual(seq1, seq2)

    def test_find_period(self):
        """Тест знаходження періоду"""
        # Використовуємо менший генератор для швидкого тестування
        small_gen = LinearCongruentialGenerator(m=100, a=13, c=7, x0=1)
        period, found = small_gen.find_period(max_iterations=10000)
        
        self.assertTrue(found)
        self.assertGreater(period, 0)
        self.assertLessEqual(period, 100)

    def test_statistics(self):
        """Тест статистичних функцій"""
        sequence = self.generator.generate_sequence(1000)
        stats = self.generator.get_statistics(sequence)
        
        self.assertIn('count', stats)
        self.assertIn('mean', stats)
        self.assertIn('variance', stats)
        self.assertIn('std_dev', stats)
        self.assertIn('min', stats)
        self.assertIn('max', stats)
        self.assertIn('unique_values', stats)
        
        self.assertEqual(stats['count'], 1000)
        self.assertGreater(stats['mean'], 0)
        self.assertGreater(stats['std_dev'], 0)

    def test_empty_sequence_statistics(self):
        """Тест статистики для порожньої послідовності"""
        stats = self.generator.get_statistics([])
        self.assertEqual(stats, {})

    def test_values_within_range(self):
        """Тест що всі значення в допустимому діапазоні"""
        sequence = self.generator.generate_sequence(1000)
        
        for value in sequence:
            self.assertGreaterEqual(value, 0)
            self.assertLess(value, self.generator.m)


class CesaroTestCase(TestCase):
    """Тести для тесту Чезаро"""

    def setUp(self):
        """Ініціалізація генератора"""
        self.generator = LinearCongruentialGenerator(
            m=VARIANT_17_CONFIG['m'],
            a=VARIANT_17_CONFIG['a'],
            c=VARIANT_17_CONFIG['c'],
            x0=VARIANT_17_CONFIG['x0']
        )

    def test_estimate_pi_basic(self):
        """Базовий тест оцінки Pi"""
        self.generator.reset()
        pi_estimate, error, history = CesaroTest.estimate_pi(
            self.generator, 
            num_pairs=1000
        )
        
        self.assertIsInstance(pi_estimate, float)
        self.assertIsInstance(error, float)
        self.assertIsInstance(history, list)
        
        # Pi має бути близько до 3.14159
        self.assertGreater(pi_estimate, 2.0)
        self.assertLess(pi_estimate, 4.0)

    def test_compare_with_system_random(self):
        """Тест порівняння з системним генератором"""
        result = CesaroTest.compare_with_system_random(num_pairs=1000)
        
        self.assertIn('pi_estimate', result)
        self.assertIn('error', result)
        self.assertIn('coprime_probability', result)
        
        self.assertGreater(result['pi_estimate'], 2.0)
        self.assertLess(result['pi_estimate'], 4.0)
        self.assertGreaterEqual(result['coprime_probability'], 0)
        self.assertLessEqual(result['coprime_probability'], 1)


class FrequencyTestCase(TestCase):
    """Тести для частотного тесту"""

    def test_frequency_test_basic(self):
        """Базовий тест частот"""
        generator = LinearCongruentialGenerator(
            m=VARIANT_17_CONFIG['m'],
            a=VARIANT_17_CONFIG['a'],
            c=VARIANT_17_CONFIG['c'],
            x0=VARIANT_17_CONFIG['x0']
        )
        sequence = generator.generate_sequence(100)
        result = FrequencyTest.test_bits(sequence, bit_length=32)
        
        self.assertIn('ones_count', result)
        self.assertIn('zeros_count', result)
        self.assertIn('ones_ratio', result)
        self.assertIn('zeros_ratio', result)
        self.assertIn('chi_square', result)
        self.assertIn('is_random', result)
        
        # Перевірка раціо
        self.assertGreaterEqual(result['ones_ratio'], 0)
        self.assertLessEqual(result['ones_ratio'], 1)
        self.assertGreaterEqual(result['zeros_ratio'], 0)
        self.assertLessEqual(result['zeros_ratio'], 1)
        
        # Сума раціо має бути 1
        self.assertAlmostEqual(
            result['ones_ratio'] + result['zeros_ratio'], 
            1.0, 
            places=5
        )

    def test_empty_sequence(self):
        """Тест з порожньою послідовністю"""
        result = FrequencyTest.test_bits([], bit_length=32)
        self.assertIn('error', result)

    def test_different_bit_lengths(self):
        """Тест з різною довжиною бітів"""
        generator = LinearCongruentialGenerator(m=100, a=13, c=7, x0=1)
        sequence = generator.generate_sequence(50)
        
        for bit_length in [8, 16, 32]:
            result = FrequencyTest.test_bits(sequence, bit_length=bit_length)
            self.assertIn('ones_count', result)
            self.assertIn('zeros_count', result)


class RunsTestCase(TestCase):
    """Тести для тесту послідовностей"""

    def test_runs_basic(self):
        """Базовий тест послідовностей"""
        generator = LinearCongruentialGenerator(
            m=VARIANT_17_CONFIG['m'],
            a=VARIANT_17_CONFIG['a'],
            c=VARIANT_17_CONFIG['c'],
            x0=VARIANT_17_CONFIG['x0']
        )
        sequence = generator.generate_sequence(100)
        result = RunsTest.test(sequence)
        
        self.assertIn('runs', result)
        self.assertIn('expected_runs', result)
        self.assertIn('variance', result)
        self.assertIn('z_statistic', result)
        self.assertIn('is_random', result)
        
        self.assertGreater(result['runs'], 0)
        self.assertGreater(result['expected_runs'], 0)

    def test_runs_short_sequence(self):
        """Тест з короткою послідовністю"""
        result = RunsTest.test([1])
        self.assertIn('error', result)

    def test_runs_pattern_detection(self):
        """Тест виявлення патернів"""
        generator = LinearCongruentialGenerator(m=100, a=13, c=7, x0=1)
        sequence = generator.generate_sequence(50)
        result = RunsTest.test(sequence)
        
        # Має повернути валідний результат
        if 'error' not in result:
            self.assertIsInstance(result['z_statistic'], float)
            self.assertIsInstance(result['is_random'], bool)


class IntegrationTestCase(TestCase):
    """Інтеграційні тести для перевірки взаємодії компонентів"""

    def test_full_workflow(self):
        """Тест повного робочого процесу"""
        # Створення генератора
        generator = LinearCongruentialGenerator(
            m=VARIANT_17_CONFIG['m'],
            a=VARIANT_17_CONFIG['a'],
            c=VARIANT_17_CONFIG['c'],
            x0=VARIANT_17_CONFIG['x0']
        )
        
        # Генерація послідовності
        sequence = generator.generate_sequence(1000)
        self.assertEqual(len(sequence), 1000)
        
        # Статистика
        stats = generator.get_statistics(sequence)
        self.assertGreater(stats['unique_values'], 500)
        
        # Частотний тест
        freq_result = FrequencyTest.test_bits(sequence[:100])
        if 'error' not in freq_result:
            self.assertIn('is_random', freq_result)
        
        # Тест послідовностей
        runs_result = RunsTest.test(sequence[:100])
        if 'error' not in runs_result:
            self.assertIn('is_random', runs_result)

    def test_variant_17_config(self):
        """Тест конфігурації варіанту 17"""
        self.assertEqual(VARIANT_17_CONFIG['m'], 2**26 - 1)
        self.assertEqual(VARIANT_17_CONFIG['a'], 13**3)
        self.assertEqual(VARIANT_17_CONFIG['c'], 1597)
        self.assertEqual(VARIANT_17_CONFIG['x0'], 13)
        
        # Перевірка що параметри коректні для LCG
        self.assertGreater(VARIANT_17_CONFIG['m'], 0)
        self.assertGreaterEqual(VARIANT_17_CONFIG['a'], 0)
        self.assertLess(VARIANT_17_CONFIG['a'], VARIANT_17_CONFIG['m'])
        self.assertGreaterEqual(VARIANT_17_CONFIG['c'], 0)
        self.assertLess(VARIANT_17_CONFIG['c'], VARIANT_17_CONFIG['m'])
        self.assertGreaterEqual(VARIANT_17_CONFIG['x0'], 0)
        self.assertLess(VARIANT_17_CONFIG['x0'], VARIANT_17_CONFIG['m'])


# ==================== ТЕСТИ ДЛЯ ЛР2 (MD5) ====================

from .algoritm.LR2 import MD5


class MD5TestCase(TestCase):
    """Тести для алгоритму хешування MD5"""

    def test_hash_empty_string(self):
        """Тест хешування порожнього рядка"""
        result = MD5.hash_string("")
        # MD5 порожнього рядка: D41D8CD98F00B204E9800998ECF8427E
        self.assertEqual(result, "D41D8CD98F00B204E9800998ECF8427E")

    def test_hash_simple_string(self):
        """Тест хешування простого рядка"""
        result = MD5.hash_string("abc")
        # MD5 "abc": 900150983CD24FB0D6963F7D28E17F72
        self.assertEqual(result, "900150983CD24FB0D6963F7D28E17F72")

    def test_hash_unicode_string(self):
        """Тест хешування Unicode рядка"""
        result = MD5.hash_string("Привіт")
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 32)  # MD5 завжди 32 hex символи
        # Перевіряємо що всі символи hex
        self.assertTrue(all(c in '0123456789ABCDEF' for c in result))

    def test_hash_long_string(self):
        """Тест хешування довгого рядка"""
        long_string = "a" * 1000
        result = MD5.hash_string(long_string)
        self.assertEqual(len(result), 32)
        self.assertIsInstance(result, str)

    def test_hash_bytes(self):
        """Тест хешування байтових даних"""
        data = b"test data"
        result = MD5.hash_bytes(data)
        self.assertEqual(len(result), 32)
        self.assertIsInstance(result, str)

    def test_hash_deterministic(self):
        """Тест детермінованості хешування"""
        text = "test string"
        hash1 = MD5.hash_string(text)
        hash2 = MD5.hash_string(text)
        self.assertEqual(hash1, hash2)

    def test_hash_different_inputs(self):
        """Тест що різні входи дають різні хеші"""
        hash1 = MD5.hash_string("test1")
        hash2 = MD5.hash_string("test2")
        self.assertNotEqual(hash1, hash2)

    def test_hash_format(self):
        """Тест формату хешу"""
        result = MD5.hash_string("test")
        # MD5 має бути рівно 32 символи (128 біт у hex)
        self.assertEqual(len(result), 32)
        # Всі символи мають бути hex
        self.assertTrue(all(c in '0123456789ABCDEF' for c in result))

    def test_left_rotate(self):
        """Тест циклічного зсуву вліво"""
        # Тест для 0x80000000 (найстарший біт встановлений)
        result = MD5._left_rotate(0x80000000, 1)
        self.assertEqual(result, 0x00000001)
        
        # Тест для 0x00000001
        result = MD5._left_rotate(0x00000001, 1)
        self.assertEqual(result, 0x00000002)

    def test_padding(self):
        """Тест функції padding"""
        # Порожнє повідомлення
        padded = MD5._padding(b"")
        # Має бути кратно 64 байтам
        self.assertEqual(len(padded) % 64, 0)
        
        # Коротке повідомлення
        padded = MD5._padding(b"abc")
        self.assertEqual(len(padded) % 64, 0)

    def test_auxiliary_functions(self):
        """Тест допоміжних функцій F, G, H, I"""
        b, c, d = 0x01234567, 0x89ABCDEF, 0xFEDCBA98
        
        # Тестуємо що функції повертають числа
        f_result = MD5._f(b, c, d)
        g_result = MD5._g(b, c, d)
        h_result = MD5._h(b, c, d)
        i_result = MD5._i(b, c, d)
        
        self.assertIsInstance(f_result, int)
        self.assertIsInstance(g_result, int)
        self.assertIsInstance(h_result, int)
        self.assertIsInstance(i_result, int)

    def test_known_md5_vectors(self):
        """Тест з відомими MD5 тест-векторами (RFC 1321)"""
        # Офіційні тест-вектори з RFC 1321
        test_vectors = [
            ("", "D41D8CD98F00B204E9800998ECF8427E"),
            ("a", "0CC175B9C0F1B6A831C399E269772661"),
            ("abc", "900150983CD24FB0D6963F7D28E17F72"),
            ("message digest", "F96B697D7CB7938D525A2F31AAF161D0"),
            ("abcdefghijklmnopqrstuvwxyz", "C3FCD3D76192E4007DFB496CCA67E13B"),
        ]
        
        for text, expected_hash in test_vectors:
            with self.subTest(text=text):
                result = MD5.hash_string(text)
                self.assertEqual(result, expected_hash)


# ==================== ТЕСТИ ДЛЯ ЛР3 (RC5) ====================

from .algoritm.LR3 import RC5


class RC5TestCase(TestCase):
    """Тести для алгоритму шифрування RC5"""

    def setUp(self):
        """Ініціалізація тестових даних"""
        self.password = "test_password"
        self.key = RC5.derive_key_from_password(self.password, 16)
        self.rc5 = RC5(self.key, w=32, r=12, b=16)

    def test_initialization(self):
        """Тест ініціалізації RC5"""
        self.assertEqual(self.rc5.w, 32)
        self.assertEqual(self.rc5.r, 12)
        self.assertEqual(self.rc5.b, 16)
        self.assertIsNotNone(self.rc5.S)

    def test_key_expansion(self):
        """Тест розширення ключа"""
        S = self.rc5.key_expansion()
        # Кількість підключів має бути 2*(r+1)
        expected_len = 2 * (self.rc5.r + 1)
        self.assertEqual(len(S), expected_len)

    def test_rotate_left(self):
        """Тест циклічного зсуву вліво"""
        value = 0x12345678
        rotated = self.rc5.rotate_left(value, 4)
        self.assertIsInstance(rotated, int)
        # Перевірка що значення змінилось
        self.assertNotEqual(rotated, value)

    def test_rotate_right(self):
        """Тест циклічного зсуву вправо"""
        value = 0x12345678
        rotated = self.rc5.rotate_right(value, 4)
        self.assertIsInstance(rotated, int)
        # Перевірка симетричності
        back = self.rc5.rotate_left(rotated, 4)
        self.assertEqual(back, value)

    def test_encrypt_decrypt_block(self):
        """Тест шифрування та дешифрування блоку"""
        plaintext = b"12345678"  # 8 байт
        encrypted = self.rc5._encrypt_block_ecb(plaintext)
        decrypted = self.rc5._decrypt_block_ecb(encrypted)
        
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, encrypted)

    def test_padding(self):
        """Тест PKCS7 padding"""
        data = b"test"
        padded = RC5._pad_data(data, 8)
        
        # Має бути кратно 8 байтам
        self.assertEqual(len(padded) % 8, 0)
        # Має бути більше оригінальних даних
        self.assertGreater(len(padded), len(data))

    def test_unpadding(self):
        """Тест видалення padding"""
        data = b"test"
        padded = RC5._pad_data(data, 8)
        unpadded = RC5._unpad_data(padded, 8)
        
        self.assertEqual(data, unpadded)

    def test_derive_key_from_password(self):
        """Тест генерації ключа з паролю"""
        key = RC5.derive_key_from_password("password", 16)
        
        self.assertEqual(len(key), 16)
        self.assertIsInstance(key, bytes)
        
        # Однаковий пароль має давати однаковий ключ
        key2 = RC5.derive_key_from_password("password", 16)
        self.assertEqual(key, key2)
        
        # Різні паролі дають різні ключі
        key3 = RC5.derive_key_from_password("different", 16)
        self.assertNotEqual(key, key3)

    def test_generate_iv(self):
        """Тест генерації IV"""
        from .algoritm.LR1 import VARIANT_17_CONFIG
        
        iv = RC5.generate_iv(VARIANT_17_CONFIG)
        
        self.assertEqual(len(iv), 8)  # IV має бути 8 байт для w=32
        self.assertIsInstance(iv, bytes)
        
        # IV має бути детермінованим з тією ж конфігурацією
        iv2 = RC5.generate_iv(VARIANT_17_CONFIG)
        self.assertEqual(iv, iv2)

    def test_encrypt_decrypt_data(self):
        """Тест повного шифрування та дешифрування"""
        from .algoritm.LR1 import VARIANT_17_CONFIG
        
        plaintext = b"Hello, World! This is a test message."
        password = "test_password"
        
        rc5_config = {'w': 32, 'r': 12, 'b': 16}
        
        # Шифрування
        encrypted = RC5.encrypt_data(plaintext, password, rc5_config, VARIANT_17_CONFIG)
        
        # Перевірки зашифрованих даних
        self.assertIsInstance(encrypted, bytes)
        self.assertNotEqual(encrypted, plaintext)
        
        # Дешифрування
        decrypted = RC5.decrypt_data(encrypted, password, rc5_config, VARIANT_17_CONFIG)
        
        self.assertEqual(plaintext, decrypted)

    def test_encrypt_empty_data(self):
        """Тест шифрування порожніх даних"""
        from .algoritm.LR1 import VARIANT_17_CONFIG
        
        plaintext = b""
        password = "test_password"
        rc5_config = {'w': 32, 'r': 12, 'b': 16}
        
        encrypted = RC5.encrypt_data(plaintext, password, rc5_config, VARIANT_17_CONFIG)
        decrypted = RC5.decrypt_data(encrypted, password, rc5_config, VARIANT_17_CONFIG)
        
        self.assertEqual(plaintext, decrypted)

    def test_different_passwords_different_results(self):
        """Тест що різні паролі дають різні результати"""
        from .algoritm.LR1 import VARIANT_17_CONFIG
        
        plaintext = b"Secret message"
        rc5_config = {'w': 32, 'r': 12, 'b': 16}
        
        encrypted1 = RC5.encrypt_data(plaintext, "password1", rc5_config, VARIANT_17_CONFIG)
        encrypted2 = RC5.encrypt_data(plaintext, "password2", rc5_config, VARIANT_17_CONFIG)
        
        self.assertNotEqual(encrypted1, encrypted2)


# ==================== ТЕСТИ ДЛЯ ЛР4 (RSA) ====================

from .algoritm.LR4 import RSAEngine
import tempfile
import os


class RSAEngineTestCase(TestCase):
    """Тести для алгоритму шифрування RSA"""

    def setUp(self):
        """Ініціалізація тестових даних"""
        self.rsa_engine = RSAEngine(key_size=2048)

    def test_initialization(self):
        """Тест ініціалізації RSA Engine"""
        self.assertEqual(self.rsa_engine.key_size, 2048)
        self.assertIsNone(self.rsa_engine.private_key)
        self.assertIsNone(self.rsa_engine.public_key)

    def test_generate_keys(self):
        """Тест генерації ключів"""
        private_key, public_key = self.rsa_engine.generate_keys()
        
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertEqual(self.rsa_engine.key_size, private_key.key_size)
        self.assertEqual(self.rsa_engine.private_key, private_key)
        self.assertEqual(self.rsa_engine.public_key, public_key)

    def test_encrypt_decrypt_small_data(self):
        """Тест шифрування та дешифрування малих даних"""
        self.rsa_engine.generate_keys()
        
        plaintext = b"Hello, RSA!"
        encrypted = self.rsa_engine.encrypt_data(plaintext)
        decrypted = self.rsa_engine.decrypt_data(encrypted)
        
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, encrypted)

    def test_encrypt_decrypt_large_data(self):
        """Тест шифрування та дешифрування великих даних (багато блоків)"""
        self.rsa_engine.generate_keys()
        
        # Дані більші за один блок
        plaintext = b"A" * 500
        encrypted = self.rsa_engine.encrypt_data(plaintext)
        decrypted = self.rsa_engine.decrypt_data(encrypted)
        
        self.assertEqual(plaintext, decrypted)

    def test_encrypt_empty_data(self):
        """Тест шифрування порожніх даних"""
        self.rsa_engine.generate_keys()
        
        plaintext = b""
        encrypted = self.rsa_engine.encrypt_data(plaintext)
        decrypted = self.rsa_engine.decrypt_data(encrypted)
        
        self.assertEqual(plaintext, decrypted)

    def test_encrypt_without_public_key(self):
        """Тест шифрування без публічного ключа"""
        with self.assertRaises(ValueError):
            self.rsa_engine.encrypt_data(b"test")

    def test_decrypt_without_private_key(self):
        """Тест дешифрування без приватного ключа"""
        with self.assertRaises(ValueError):
            self.rsa_engine.decrypt_data(b"test")

    def test_save_and_load_keys_without_password(self):
        """Тест збереження та завантаження ключів без пароля"""
        self.rsa_engine.generate_keys()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            private_path = os.path.join(tmpdir, 'private.pem')
            public_path = os.path.join(tmpdir, 'public.pem')
            
            # Збереження
            self.rsa_engine.save_keys(private_path, public_path)
            
            # Перевірка що файли створені
            self.assertTrue(os.path.exists(private_path))
            self.assertTrue(os.path.exists(public_path))
            
            # Створення нового engine та завантаження
            new_engine = RSAEngine()
            new_engine.load_keys(private_path, public_path)
            
            # Перевірка що ключі працюють
            plaintext = b"Test message"
            encrypted = new_engine.encrypt_data(plaintext)
            decrypted = new_engine.decrypt_data(encrypted)
            
            self.assertEqual(plaintext, decrypted)

    def test_save_and_load_keys_with_password(self):
        """Тест збереження та завантаження ключів з паролем"""
        self.rsa_engine.generate_keys()
        password = "secure_password"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            private_path = os.path.join(tmpdir, 'private.pem')
            public_path = os.path.join(tmpdir, 'public.pem')
            
            # Збереження з паролем
            self.rsa_engine.save_keys(private_path, public_path, password)
            
            # Завантаження з паролем
            new_engine = RSAEngine()
            new_engine.load_keys(private_path, public_path, password)
            
            # Перевірка функціональності
            plaintext = b"Secret message"
            encrypted = new_engine.encrypt_data(plaintext)
            decrypted = new_engine.decrypt_data(encrypted)
            
            self.assertEqual(plaintext, decrypted)

    def test_get_max_encrypt_block_size(self):
        """Тест розрахунку максимального розміру блоку"""
        self.rsa_engine.generate_keys()
        
        max_size = self.rsa_engine._get_max_encrypt_block_size()
        
        # Має бути додатнім числом
        self.assertGreater(max_size, 0)
        # Має бути менше розміру ключа
        self.assertLess(max_size, self.rsa_engine.key_size // 8)

    def test_different_key_sizes(self):
        """Тест роботи з різними розмірами ключів"""
        for key_size in [1024, 2048]:
            with self.subTest(key_size=key_size):
                engine = RSAEngine(key_size=key_size)
                engine.generate_keys()
                
                plaintext = b"Test"
                encrypted = engine.encrypt_data(plaintext)
                decrypted = engine.decrypt_data(encrypted)
                
                self.assertEqual(plaintext, decrypted)

    def test_decrypt_invalid_data(self):
        """Тест дешифрування неправильних даних"""
        self.rsa_engine.generate_keys()
        
        # Неправильна довжина
        with self.assertRaises(ValueError):
            self.rsa_engine.decrypt_data(b"invalid data")

    def test_encrypt_unicode_text(self):
        """Тест шифрування Unicode тексту"""
        self.rsa_engine.generate_keys()
        
        plaintext = "Привіт, світ! 🌍".encode('utf-8')
        encrypted = self.rsa_engine.encrypt_data(plaintext)
        decrypted = self.rsa_engine.decrypt_data(encrypted)
        
        self.assertEqual(plaintext, decrypted)
        self.assertEqual(plaintext.decode('utf-8'), decrypted.decode('utf-8'))


# ==================== ІНТЕГРАЦІЙНІ ТЕСТИ ====================

class IntegrationTestsLabs(TestCase):
    """Інтеграційні тести для всіх лабораторних"""

    def test_lr2_lr3_integration(self):
        """Тест інтеграції ЛР2 (MD5) та ЛР3 (RC5)"""
        # MD5 використовується для генерації ключа в RC5
        password = "test_password"
        key = RC5.derive_key_from_password(password, 16)
        
        # Перевірка що ключ коректний
        self.assertEqual(len(key), 16)
        
        # Використання ключа для RC5
        rc5 = RC5(key, w=32, r=12, b=16)
        plaintext = b"12345678"
        encrypted = rc5._encrypt_block_ecb(plaintext)
        decrypted = rc5._decrypt_block_ecb(encrypted)
        
        self.assertEqual(plaintext, decrypted)

    def test_lr1_lr3_integration(self):
        """Тест інтеграції ЛР1 (ГПВЧ) та ЛР3 (RC5)"""
        from .algoritm.LR1 import VARIANT_17_CONFIG
        
        # ЛР1 використовується для генерації IV в RC5
        iv = RC5.generate_iv(VARIANT_17_CONFIG)
        
        self.assertEqual(len(iv), 8)
        self.assertIsInstance(iv, bytes)

    def test_all_labs_workflow(self):
        """Тест повного робочого процесу через всі лабораторні"""
        from .algoritm.LR1 import VARIANT_17_CONFIG
        
        # ЛР1: Генерація псевдовипадкових чисел
        lcg = LinearCongruentialGenerator(
            m=VARIANT_17_CONFIG['m'],
            a=VARIANT_17_CONFIG['a'],
            c=VARIANT_17_CONFIG['c'],
            x0=VARIANT_17_CONFIG['x0']
        )
        random_numbers = lcg.generate_sequence(10)
        self.assertEqual(len(random_numbers), 10)
        
        # ЛР2: Хешування даних
        test_data = "Test data for hashing"
        hash_result = MD5.hash_string(test_data)
        self.assertEqual(len(hash_result), 32)
        
        # ЛР3: Шифрування даних
        plaintext = b"Secret message"
        password = "secure_password"
        rc5_config = {'w': 32, 'r': 12, 'b': 16}
        
        encrypted = RC5.encrypt_data(plaintext, password, rc5_config, VARIANT_17_CONFIG)
        decrypted = RC5.decrypt_data(encrypted, password, rc5_config, VARIANT_17_CONFIG)
        self.assertEqual(plaintext, decrypted)
        
        # ЛР4: RSA шифрування
        rsa_engine = RSAEngine(key_size=1024)  # Менший ключ для швидкості тесту
        rsa_engine.generate_keys()
        
        rsa_plaintext = b"RSA message"
        rsa_encrypted = rsa_engine.encrypt_data(rsa_plaintext)
        rsa_decrypted = rsa_engine.decrypt_data(rsa_encrypted)
        self.assertEqual(rsa_plaintext, rsa_decrypted)


