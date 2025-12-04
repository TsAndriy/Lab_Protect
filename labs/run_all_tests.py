#!/usr/bin/env python3
"""
Повний набір тестів для ЛР1, ЛР2, ЛР3, ЛР4 без Django
Використовується unittest framework
"""

import sys
import os
import unittest
import tempfile

# Додаємо шлях до проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Імпортуємо необхідні модулі
from labs.algoritm.LR1 import (
    LinearCongruentialGenerator,
    CesaroTest,
    FrequencyTest,
    RunsTest,
    gcd,
    VARIANT_17_CONFIG
)
from labs.algoritm.LR2 import MD5
from labs.algoritm.LR3 import RC5
from labs.algoritm.LR4 import RSAEngine


# ==================== ТЕСТИ ЛР2 (MD5) ====================

class TestMD5(unittest.TestCase):
    """Тести для алгоритму MD5"""

    def test_hash_empty_string(self):
        """Тест хешування порожнього рядка"""
        result = MD5.hash_string("")
        self.assertEqual(result, "D41D8CD98F00B204E9800998ECF8427E")

    def test_hash_simple_string(self):
        """Тест хешування простого рядка"""
        result = MD5.hash_string("abc")
        self.assertEqual(result, "900150983CD24FB0D6963F7D28E17F72")

    def test_hash_deterministic(self):
        """Тест детермінованості"""
        text = "test"
        hash1 = MD5.hash_string(text)
        hash2 = MD5.hash_string(text)
        self.assertEqual(hash1, hash2)

    def test_hash_format(self):
        """Тест формату"""
        result = MD5.hash_string("test")
        self.assertEqual(len(result), 32)
        self.assertTrue(all(c in '0123456789ABCDEF' for c in result))

    def test_known_vectors(self):
        """Тест з RFC 1321 векторами"""
        vectors = [
            ("", "D41D8CD98F00B204E9800998ECF8427E"),
            ("a", "0CC175B9C0F1B6A831C399E269772661"),
            ("abc", "900150983CD24FB0D6963F7D28E17F72"),
        ]
        for text, expected in vectors:
            self.assertEqual(MD5.hash_string(text), expected)


# ==================== ТЕСТИ ЛР3 (RC5) ====================

class TestRC5(unittest.TestCase):
    """Тести для алгоритму RC5"""

    def setUp(self):
        """Ініціалізація"""
        self.password = "test_password"
        self.key = RC5.derive_key_from_password(self.password, 16)
        self.rc5 = RC5(self.key, w=32, r=12, b=16)

    def test_initialization(self):
        """Тест ініціалізації"""
        self.assertEqual(self.rc5.w, 32)
        self.assertEqual(self.rc5.r, 12)
        self.assertEqual(self.rc5.b, 16)

    def test_encrypt_decrypt_block(self):
        """Тест шифрування блоку"""
        plaintext = b"12345678"
        encrypted = self.rc5._encrypt_block_ecb(plaintext)
        decrypted = self.rc5._decrypt_block_ecb(encrypted)
        self.assertEqual(plaintext, decrypted)

    def test_padding_unpadding(self):
        """Тест padding"""
        data = b"test"
        padded = RC5._pad_data(data, 8)
        unpadded = RC5._unpad_data(padded, 8)
        self.assertEqual(data, unpadded)

    def test_derive_key(self):
        """Тест генерації ключа"""
        key = RC5.derive_key_from_password("password", 16)
        self.assertEqual(len(key), 16)
        
        key2 = RC5.derive_key_from_password("password", 16)
        self.assertEqual(key, key2)

    def test_full_encryption(self):
        """Тест повного шифрування"""
        plaintext = b"Hello, World!"
        password = "test"
        rc5_config = {'w': 32, 'r': 12, 'b': 16}
        
        encrypted = RC5.encrypt_data(plaintext, password, rc5_config, VARIANT_17_CONFIG)
        decrypted = RC5.decrypt_data(encrypted, password, rc5_config, VARIANT_17_CONFIG)
        self.assertEqual(plaintext, decrypted)


# ==================== ТЕСТИ ЛР4 (RSA) ====================

class TestRSA(unittest.TestCase):
    """Тести для алгоритму RSA"""

    def setUp(self):
        """Ініціалізація"""
        self.rsa = RSAEngine(key_size=1024)  # Менший для швидкості

    def test_generate_keys(self):
        """Тест генерації ключів"""
        private, public = self.rsa.generate_keys()
        self.assertIsNotNone(private)
        self.assertIsNotNone(public)

    def test_encrypt_decrypt(self):
        """Тест шифрування/дешифрування"""
        self.rsa.generate_keys()
        plaintext = b"Test message"
        encrypted = self.rsa.encrypt_data(plaintext)
        decrypted = self.rsa.decrypt_data(encrypted)
        self.assertEqual(plaintext, decrypted)

    def test_large_data(self):
        """Тест з великими даними"""
        self.rsa.generate_keys()
        plaintext = b"A" * 200
        encrypted = self.rsa.encrypt_data(plaintext)
        decrypted = self.rsa.decrypt_data(encrypted)
        self.assertEqual(plaintext, decrypted)

    def test_save_load_keys(self):
        """Тест збереження/завантаження ключів"""
        self.rsa.generate_keys()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            priv_path = os.path.join(tmpdir, 'priv.pem')
            pub_path = os.path.join(tmpdir, 'pub.pem')
            
            self.rsa.save_keys(priv_path, pub_path)
            
            new_rsa = RSAEngine()
            new_rsa.load_keys(priv_path, pub_path)
            
            plaintext = b"Test"
            encrypted = new_rsa.encrypt_data(plaintext)
            decrypted = new_rsa.decrypt_data(encrypted)
            self.assertEqual(plaintext, decrypted)


# ==================== ІНТЕГРАЦІЙНІ ТЕСТИ ====================

class TestIntegration(unittest.TestCase):
    """Інтеграційні тести"""

    def test_md5_rc5_integration(self):
        """MD5 для генерації ключа RC5"""
        password = "test"
        key = RC5.derive_key_from_password(password, 16)
        self.assertEqual(len(key), 16)
        
        rc5 = RC5(key, w=32, r=12, b=16)
        plaintext = b"12345678"
        encrypted = rc5._encrypt_block_ecb(plaintext)
        decrypted = rc5._decrypt_block_ecb(encrypted)
        self.assertEqual(plaintext, decrypted)

    def test_lcg_rc5_integration(self):
        """ЛР1 для генерації IV в RC5"""
        iv = RC5.generate_iv(VARIANT_17_CONFIG)
        self.assertEqual(len(iv), 8)

    def test_full_workflow(self):
        """Повний workflow через всі ЛР"""
        # ЛР1
        lcg = LinearCongruentialGenerator(
            m=VARIANT_17_CONFIG['m'],
            a=VARIANT_17_CONFIG['a'],
            c=VARIANT_17_CONFIG['c'],
            x0=VARIANT_17_CONFIG['x0']
        )
        nums = lcg.generate_sequence(10)
        self.assertEqual(len(nums), 10)
        
        # ЛР2
        hash_result = MD5.hash_string("test")
        self.assertEqual(len(hash_result), 32)
        
        # ЛР3
        plaintext = b"Secret"
        password = "pass"
        rc5_config = {'w': 32, 'r': 12, 'b': 16}
        encrypted = RC5.encrypt_data(plaintext, password, rc5_config, VARIANT_17_CONFIG)
        decrypted = RC5.decrypt_data(encrypted, password, rc5_config, VARIANT_17_CONFIG)
        self.assertEqual(plaintext, decrypted)
        
        # ЛР4
        rsa = RSAEngine(key_size=1024)
        rsa.generate_keys()
        rsa_plain = b"RSA test"
        rsa_enc = rsa.encrypt_data(rsa_plain)
        rsa_dec = rsa.decrypt_data(rsa_enc)
        self.assertEqual(rsa_plain, rsa_dec)


def run_tests():
    """Запуск всіх тестів"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Додаємо тести
    suite.addTests(loader.loadTestsFromTestCase(TestMD5))
    suite.addTests(loader.loadTestsFromTestCase(TestRC5))
    suite.addTests(loader.loadTestsFromTestCase(TestRSA))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Запускаємо
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Підсумок
    print("\n" + "="*70)
    print("ПІДСУМОК ТЕСТУВАННЯ ЛР2, ЛР3, ЛР4")
    print("="*70)
    print(f"Всього тестів: {result.testsRun}")
    print(f"Успішних: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Помилок: {len(result.failures)}")
    print(f"Критичних помилок: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
