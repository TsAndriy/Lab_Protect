"""
Модуль для генерації псевдовипадкових чисел
Лабораторна робота №1 - Варіант 17
"""
import math
import random
from typing import List, Tuple, Dict, Any

class LinearCongruentialGenerator:
    #Генератор псевдовипадкових чисел за методом лінійного порівняння

    def __init__(self, m: int, a: int, c: int, x0: int):
        # m: модуль порівняння (m > 0)
        # a: множник (0 <= a < m)
        # c: приріст (0 <= c < m)
        # x0: початкове значення (0 <= x0 < m)
        self.m = m
        self.a = a
        self.c = c
        self.x0 = x0
        self.current = x0
        self.history = []

    def reset(self):
        #Скидання генератора до початкового стану
        self.current = self.x0
        self.history = []

    def next(self) -> int:
        #енерація наступного псевдовипадкового числа
        self.current = (self.a * self.current + self.c) % self.m
        self.history.append(self.current)
        return self.current

    def generate_sequence(self, n: int) -> List[int]:
        #Генерація послідовності псевдовипадкових чисел

        self.reset()
        sequence = []
        for _ in range(n):
            sequence.append(self.next())
        return sequence

    def find_period(self, max_iterations: int = 1000000000) -> Tuple[int, bool]: # change
        #Знаходження періоду функції генерації
        #max_iterations: максимальна кількість ітерацій для пошуку
        #Tuple (період, чи знайдено повний період)

        self.reset()
        seen = {self.x0: 0}

        for i in range(1, max_iterations + 1):
            value = self.next()
            if value in seen:
                period = i - seen[value]
                return period, True
            seen[value] = i

        return max_iterations, False

    def get_statistics(self, sequence: List[int]) -> Dict[str, Any]:

        #Отримання статистики послідовності

        if not sequence:
            return {}

        n = len(sequence)
        mean = sum(sequence) / n
        variance = sum((x - mean) ** 2 for x in sequence) / n
        std_dev = math.sqrt(variance)

        # Частотний аналіз
        frequency = {}
        for num in sequence:
            frequency[num] = frequency.get(num, 0) + 1

        return {
            'count': n,
            'mean': mean,
            'variance': variance,
            'std_dev': std_dev,
            'min': min(sequence),
            'max': max(sequence),
            'unique_values': len(set(sequence)),
            'frequency_top10': dict(sorted(frequency.items(), #Топ 10 за кількістю одинакових значеньА
                                         key=lambda x: x[1],
                                         reverse=True)[:10])
        }


def gcd(a: int, b: int) -> int:
    #Алгоритм Евкліда для знаходження Найбільшого спільного дільника

    while b:
        a, b = b, a % b
    return a


class CesaroTest:
    # Тестування генератора на основі теореми Чезаро
    @staticmethod
    def estimate_pi(generator: LinearCongruentialGenerator,
                   num_pairs: int = 10000000) -> Tuple[float, float, List[float]]:

        # generator: генератор псевдовипадкових чисел
        # num_pairs: кількість пар для тестування
        # Tuple (оцінка Pi, відхилення від початкового Pi, історія оцінок)

        coprime_count = 0
        pi_estimates = []

        for i in range(num_pairs):
            x = generator.next()
            y = generator.next()

            if gcd(x, y) == 1:
                coprime_count += 1

            # Проміжні оцінки кожні 100 пар
            if (i + 1) % 100 == 0 and coprime_count > 0:
                probability = coprime_count / (i + 1)
                if probability > 0:
                    pi_estimate = math.sqrt(6.0 / probability)
                    pi_estimates.append(pi_estimate)

        # Фінальна оцінка
        if coprime_count > 0:
            probability = coprime_count / num_pairs
            pi_estimate = math.sqrt(6.0 / probability)
            error = abs(pi_estimate - math.pi)
            return pi_estimate, error, pi_estimates

        return 0, float('inf'), pi_estimates

    @staticmethod
    def compare_with_system_random(num_pairs: int = 10000000) -> Dict[str, Any]:
        #Порівняння з системним генератором випадкових чисел (random)
        #num_pairs: кількість пар для тестування
        coprime_count = 0
        max_val = 2 ** 31 - 1

        for _ in range(num_pairs):
            x = random.randint(1, max_val)
            y = random.randint(1, max_val)

            if gcd(x, y) == 1:
                coprime_count += 1

        probability = coprime_count / num_pairs
        pi_estimate = math.sqrt(6.0 / probability) if probability > 0 else 0
        error = abs(pi_estimate - math.pi)

        return {
            'pi_estimate': pi_estimate,
            'error': error,
            'coprime_probability': probability
        }


class FrequencyTest:
    #Частотний тест для перевірки випадковості

    @staticmethod
    def test_bits(sequence: List[int], bit_length: int = 32) -> Dict[str, Any]:
        #sequence: послідовність чисел
        #bit_length: довжина представлення числа в бітах
        ones_count = 0
        zeros_count = 0

        for num in sequence:
            binary = bin(num)[2:].zfill(bit_length)
            ones_count += binary.count('1')
            zeros_count += binary.count('0')

        total_bits = ones_count + zeros_count
        if total_bits == 0:
            return {'error': 'Порожня послідовність'}

        ones_ratio = ones_count / total_bits
        zeros_ratio = zeros_count / total_bits

        # Cпіввідношення - 0.5 на 0.5
        chi_square = ((ones_count - total_bits / 2) ** 2 +
                      (zeros_count - total_bits / 2) ** 2) / (total_bits / 2)

        return {
            'ones_count': ones_count,
            'zeros_count': zeros_count,
            'ones_ratio': ones_ratio,
            'zeros_ratio': zeros_ratio,
            'chi_square': chi_square,
            'is_random': chi_square < 3.841  # критичне значення для p=0.05
        }


class RunsTest:
    # Тест на послідовності однакових бітів
    @staticmethod
    def test(sequence: List[int]) -> Dict[str, Any]:

        # Перетворення на бітову послідовність
        bits = []
        for num in sequence:
            binary = bin(num)[2:]
            bits.extend([int(b) for b in binary])

        if len(bits) < 2:
            return {'error': 'Послідовність коротка'}

        runs = 1  # кількість послідовностей
        for i in range(1, len(bits)):
            if bits[i] != bits[i - 1]:
                runs += 1

        n = len(bits)
        ones = sum(bits)
        zeros = n - ones

        if ones == 0 or zeros == 0:
            return {'error': 'Біто однакові'}

        # Очікувана кількість послідовностей
        expected_runs = (2 * ones * zeros) / n + 1

        # Дисперсія
        variance = (2 * ones * zeros * (2 * ones * zeros - n)) / (n ** 2 * (n - 1))

        if variance <= 0:
            return {'error': 'Невірна дисперсія'}

        # Z-статистика
        z = (runs - expected_runs) / math.sqrt(variance)

        return {
            'runs': runs,
            'expected_runs': expected_runs,
            'variance': variance,
            'z_statistic': z,
            'is_random': abs(z) < 1.96  # критичне значення для p=0.05
        }

VARIANT_17_CONFIG = {
    'm': 2**26 - 1,  # 67108863
    'a': 13**3,      # 2197
    'c': 1597,
    'x0': 13
}


def create_variant_17_generator() -> LinearCongruentialGenerator:
    """Створення генератора для варіанту 17"""
    config = VARIANT_17_CONFIG
    return LinearCongruentialGenerator(
        m=config['m'],
        a=config['a'],
        c=config['c'],
        x0=config['x0']
    )