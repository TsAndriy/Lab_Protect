import math
import time  # Імпортуємо модуль time
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import io
from .algoritm.Config.config import VARIANT_17_CONFIG
from .algoritm.LR1 import (
    LinearCongruentialGenerator,
    CesaroTest,
    FrequencyTest,
    RunsTest)


def index(request):
    labs = [
        {
            'number': 1,
            'title': 'Генератор псевдовипадкових чисел',
            'description': 'Створення та тестування ГПВЧ за методом лінійного порівняння',
            'url': 'lab1/',
        },
        {
            'number': 2,
            'title': 'Створенння програмного засобу для забезбечення цілісності інформації',
            'description': '',
            'url': 'lab2/',
        }
    ]

    context = {
        'labs': labs,
        'title': 'Лабораторні роботи з захисту інформації'
    }
    return render(request, 'index.html', context)


def lab1_prng(request):
    context = {
        'title': 'Лабораторна робота 1',
        'config': VARIANT_17_CONFIG
    }
    return render(request, 'labs/lab1/index.html', context)


@csrf_exempt
def generate_prng(request):
    # Генерація псевдовипадкових чисел
    if request.method == 'POST':
        try:
            start_time = time.time()  # Початок вимірювання часу
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m', VARIANT_17_CONFIG['m']))
            a = int(data.get('a', VARIANT_17_CONFIG['a']))
            c = int(data.get('c', VARIANT_17_CONFIG['c']))
            x0 = int(data.get('x0', VARIANT_17_CONFIG['x0']))
            count = int(data.get('count', 200))

            # Валідація
            if m <= 0:
                return JsonResponse({'error': 'Модуль m повинен бути > 0'})
            if not (0 <= a < m):
                return JsonResponse({'error': f'Множник a повинен бути в діапазоні [0, {m})'})
            if not (0 <= c < m):
                return JsonResponse({'error': f'Приріст c повинен бути в діапазоні [0, {m})'})
            if not (0 <= x0 < m):
                return JsonResponse({'error': f'Початкове значення x0 повинен бути в діапазоні [0, {m})'})
            if count <= 0 or count > 10000000:
                return JsonResponse({'error': 'Кількість чисел повинна бути від 1 до 10000000'})

            # Генерація
            generator = LinearCongruentialGenerator(m, a, c, x0)
            sequence = generator.generate_sequence(count)

            # Статистика
            stats = generator.get_statistics(sequence)

            end_time = time.time()  # Кінець вимірювання часу
            duration_ms = (end_time - start_time) * 1000  # Розрахунок часу в мілісекундах

            response = {
                'success': True,
                'sequence': sequence,
                'count': len(sequence),
                'statistics': stats,
                'generation_time_ms': duration_ms,  # Додаємо час генерації у відповідь
                'parameters': {
                    'm': m,
                    'a': a,
                    'c': c,
                    'x0': x0
                }
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Помилка'})


@csrf_exempt
def test_period(request):
    # Тестування періоду генератора
    if request.method == 'POST':
        try:
            start_time = time.time()
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m', VARIANT_17_CONFIG['m']))
            a = int(data.get('a', VARIANT_17_CONFIG['a']))
            c = int(data.get('c', VARIANT_17_CONFIG['c']))
            x0 = int(data.get('x0', VARIANT_17_CONFIG['x0']))
            max_iterations = int(data.get('max_iterations'))

            # Генератор
            generator = LinearCongruentialGenerator(m, a, c, x0)

            # Знаходження періоду
            period, found = generator.find_period(max_iterations)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Оцінка якості
            max_period = m if c != 0 else m - 1
            quality = 'Відмінно' if period == max_period \
                else 'Добре' if period > m / 2 \
                else 'Задовільно' if period > m / 4 \
                else 'Погано'

            response = {
                'success': True,
                'period': period,
                'found': found,
                'max_possible_period': max_period,
                'quality': quality,
                'percentage': (period / max_period) * 100,
                'execution_time_ms': duration_ms,
                'parameters': {
                    'm': m,
                    'a': a,
                    'c': c,
                    'x0': x0
                }
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Помилка'})


@csrf_exempt
def test_cesaro(request):
    # Тестування генератора за теоремою Чезаро
    if request.method == 'POST':
        try:
            start_time = time.time()
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m', VARIANT_17_CONFIG['m']))
            a = int(data.get('a', VARIANT_17_CONFIG['a']))
            c = int(data.get('c', VARIANT_17_CONFIG['c']))
            x0 = int(data.get('x0', VARIANT_17_CONFIG['x0']))
            num_pairs = min(int(data.get('num_pairs', 10000)), 5000000)

            # Тестування лінійного генератора
            generator = LinearCongruentialGenerator(m, a, c, x0)
            pi_estimate, error, pi_history = CesaroTest.estimate_pi(generator, num_pairs)

            # Тестування системного генератора (random)
            system_results = CesaroTest.compare_with_system_random(num_pairs)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            response = {
                'success': True,
                'our_generator': {
                    'pi_estimate': pi_estimate,
                    'error': error,
                    'error_percentage': (error / math.pi) * 100,
                },
                'system_generator': {
                    'pi_estimate': system_results['pi_estimate'],
                    'error': system_results['error'],
                    'error_percentage': (system_results['error'] / math.pi) * 100
                },
                'actual_pi': math.pi,
                'num_pairs': num_pairs,
                'execution_time_ms': duration_ms
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Помилка'})


@csrf_exempt
def test_randomness(request):
    # Комплексне тестування випадковості
    if request.method == 'POST':
        try:
            start_time = time.time()
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m', VARIANT_17_CONFIG['m']))
            a = int(data.get('a', VARIANT_17_CONFIG['a']))
            c = int(data.get('c', VARIANT_17_CONFIG['c']))
            x0 = int(data.get('x0', VARIANT_17_CONFIG['x0']))
            count = min(int(data.get('count', 1000)), 5000000)

            # Генерація послідовності
            generator = LinearCongruentialGenerator(m, a, c, x0)
            sequence = generator.generate_sequence(count)

            # Частотний тест
            frequency_results = FrequencyTest.test_bits(sequence)

            # Тест послідовностей
            runs_results = RunsTest.test(sequence)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            response = {
                'success': True,
                'tests': {
                    'frequency': frequency_results,
                    'runs': runs_results
                },
                'execution_time_ms': duration_ms,
                'parameters': {
                    'm': m,
                    'a': a,
                    'c': c,
                    'x0': x0,
                    'count': count
                }
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Помилка'})


@csrf_exempt
def export_results(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Дозволено тільки POST запити'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Невірний JSON'}, status=400)

    m = int(data.get('m', VARIANT_17_CONFIG['m']))
    a = int(data.get('a', VARIANT_17_CONFIG['a']))
    c = int(data.get('c', VARIANT_17_CONFIG['c']))
    x0 = int(data.get('x0', VARIANT_17_CONFIG['x0']))
    count = int(data.get('count', 100))

    # Генерація послідовності
    generator = LinearCongruentialGenerator(m, a, c, x0)
    sequence = generator.generate_sequence(count)

    # Формуємо txt файл в пам'яті
    output = io.StringIO()
    output.write(f"Модуль порівняння m = {m}\n")
    output.write(f"Множник a = {a}\n")
    output.write(f"Приріст c = {c}\n")
    output.write(f"Початкове число x0 = {x0}\n")
    output.write("-" * 20 + "\n")
    output.write(f"Кількість змінних = {len(sequence)}\n")
    output.write("-" * 20 + "\n")
    output.write("Індекс\tЗначення змінної\n")

    for i, val in enumerate(sequence, 1):
        output.write(f"{i}\t{val}\n")

    file_content = output.getvalue()
    output.close()

    # Створюємо HTTP-відповідь із правильними заголовками
    response = HttpResponse(file_content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="lr1_lin.txt"'
    return response
