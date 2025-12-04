#!/usr/bin/env python3
"""
Простий скрипт для запуску тестів ЛР1 без Django
Використовується unittest framework
"""

import sys
import os
import unittest

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


class TestGCD(unittest.TestCase):
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


class TestLinearCongruentialGenerator(unittest.TestCase):
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

    def test_find_period_small(self):
        """Тест знаходження періоду на малому генераторі"""
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


class TestCesaro(unittest.TestCase):
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
        self.assertLess(pi_estimate, 4.5)

    def test_compare_with_system_random(self):
        """Тест порівняння з системним генератором"""
        result = CesaroTest.compare_with_system_random(num_pairs=1000)
        
        self.assertIn('pi_estimate', result)
        self.assertIn('error', result)
        self.assertIn('coprime_probability', result)
        
        self.assertGreater(result['pi_estimate'], 2.0)
        self.assertLess(result['pi_estimate'], 4.5)
        self.assertGreaterEqual(result['coprime_probability'], 0)
        self.assertLessEqual(result['coprime_probability'], 1)


class TestFrequency(unittest.TestCase):
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


class TestRuns(unittest.TestCase):
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


class TestIntegration(unittest.TestCase):
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


def run_tests():
    """Запуск всіх тестів"""
    # Створюємо test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Додаємо всі тести
    suite.addTests(loader.loadTestsFromTestCase(TestGCD))
    suite.addTests(loader.loadTestsFromTestCase(TestLinearCongruentialGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestCesaro))
    suite.addTests(loader.loadTestsFromTestCase(TestFrequency))
    suite.addTests(loader.loadTestsFromTestCase(TestRuns))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Запускаємо тести
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Виводимо підсумок
    print("\n" + "="*70)
    print("ПІДСУМОК ТЕСТУВАННЯ")
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
