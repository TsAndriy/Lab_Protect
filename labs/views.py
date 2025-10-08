import math
from urllib.parse import parse_qs
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import io
from typing import Dict, Any

from .algoritm.LR1 import (
    LinearCongruentialGenerator,
    CesaroTest,
    FrequencyTest,
    RunsTest)
# Create your views here.
def index(request):
    """Головна сторінка зі списком лабораторних робіт"""
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
    """Сторінка лабораторної роботи №1 - ГПВЧ"""
    context = {
        'title': 'Лабораторна робота 1',
    }
    return render(request, 'labs/lab1/index.html', context)


@csrf_exempt
def generate_prng(request):
    """API для генерації псевдовипадкових чисел"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m'))
            a = int(data.get('a'))
            c = int(data.get('c'))
            x0 = int(data.get('x0'))
            count = int(data.get('count', 200))

            # Валідація
            if m <= 0:
                return JsonResponse({'error': 'Модуль m повинен бути > 0'}, status=400)
            if not (0 <= a < m):
                return JsonResponse({'error': f'Множник a повинен бути в діапазоні [0, {m})'}, status=400)
            if not (0 <= c < m):
                return JsonResponse({'error': f'Приріст c повинен бути в діапазоні [0, {m})'}, status=400)
            if not (0 <= x0 < m):
                return JsonResponse({'error': f'Початкове значення x0 повинен бути в діапазоні [0, {m})'}, status=400)
            if count <= 0 or count > 10000:
                return JsonResponse({'error': 'Кількість чисел повинна бути від 1 до 10000'}, status=400)

            # Генерація
            generator = LinearCongruentialGenerator(m, a, c, x0)
            sequence = generator.generate_sequence(count)

            # Статистика
            stats = generator.get_statistics(sequence)

            response = {
                'success': True,
                'sequence': sequence[:1000],  # Обмеження для відображення
                'count': len(sequence),
                'statistics': stats,
                'parameters': {
                    'm': m,
                    'a': a,
                    'c': c,
                    'x0': x0
                }
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Помилка'}, status=405)


@csrf_exempt
def test_period(request):
    """API для тестування періоду генератора"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m'))
            a = int(data.get('a'))
            c = int(data.get('c'))
            x0 = int(data.get('x0'))
            max_iterations = min(int(data.get('max_iterations', 100000)), 1000000000)#change

            # Генератор
            generator = LinearCongruentialGenerator(m, a, c, x0)

            # Знаходження періоду
            period, found = generator.find_period(max_iterations)

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
                'parameters': {
                    'm': m,
                    'a': a,
                    'c': c,
                    'x0': x0
                }
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Помилка'}, status=405)


@csrf_exempt
def test_cesaro(request):
    """API для тестування генератора за теоремою Чезаро"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m'))
            a = int(data.get('a'))
            c = int(data.get('c'))
            x0 = int(data.get('x0'))
            num_pairs = min(int(data.get('num_pairs', 10000)), 50000)

            # Тестування нашого генератора
            generator = LinearCongruentialGenerator(m, a, c, x0)
            pi_estimate, error, pi_history = CesaroTest.estimate_pi(generator, num_pairs)

            # Тестування системного генератора
            system_results = CesaroTest.compare_with_system_random(num_pairs)

            response = {
                'success': True,
                'our_generator': {
                    'pi_estimate': pi_estimate,
                    'error': error,
                    'error_percentage': (error / math.pi) * 100,
                    'pi_history': pi_history[-20:] if pi_history else []  # Останні 20 оцінок
                },
                'system_generator': {
                    'pi_estimate': system_results['pi_estimate'],
                    'error': system_results['error'],
                    'error_percentage': (system_results['error'] / math.pi) * 100
                },
                'actual_pi': math.pi,
                'num_pairs': num_pairs
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Помилка'}, status=405)


@csrf_exempt
def test_randomness(request):
    """API для комплексного тестування випадковості"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m'))
            a = int(data.get('a'))
            c = int(data.get('c'))
            x0 = int(data.get('x0'))
            count = min(int(data.get('count', 1000)), 10000)

            # Генерація послідовності
            generator = LinearCongruentialGenerator(m, a, c, x0)
            sequence = generator.generate_sequence(count)

            # Частотний тест
            frequency_results = FrequencyTest.test_bits(sequence)

            # Тест послідовностей
            runs_results = RunsTest.test(sequence)

            response = {
                'success': True,
                'tests': {
                    'frequency': frequency_results,
                    'runs': runs_results
                },
                'overall_result': 'Пройдено' if (
                        frequency_results.get('is_random', False) and
                        runs_results.get('is_random', False)
                ) else 'Не пройдено',
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
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Помилка'}, status=405)

@csrf_exempt
def export_results(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Помилка'}, status=405)

    # Беремо параметри з POST
    import json
    data = {}
    if 'data' in request.POST:
        try:
            data = json.loads(request.POST['data'])
        except:
            return JsonResponse({'error': 'Невірний JSON файл'})

    m = int(data.get('m'))
    a = int(data.get('a'))
    c = int(data.get('c'))
    x0 = int(data.get('x0'))
    count = int(data.get('count', 100))

    # генерація послідовності
    generator = LinearCongruentialGenerator(m, a, c, x0)
    sequence = generator.generate_sequence(count)

    # формуємо CSV
    output = io.StringIO()

    output.write(f"Модуль порівняння m = {m}\n")
    output.write(f"Множник a = {a}\n")
    output.write(f"Приріст c = {c}\n")
    output.write(f"Початкове число x0 = {x0}\n")
    output.write("-" * 20 + "\n")
    output.write(f"Кількість змінних = {len(sequence)}\n")
    output.write("-" * 20 + "\n")
    # Записуємо заголовок таблиці
    output.write("Індекс\tЗначення змінної\n")

    # Записуємо згенеровані дані
    for i, val in enumerate(sequence, 1):
        output.write(f"{i}\t{val}\n")

    file_content = output.getvalue()
    output.close()

    # Створюємо відповідь сервера
    resp = HttpResponse(file_content, content_type='text/plain')
    resp['Content-Disposition'] = 'attachment; filename="result_lr1.txt"'
    return resp
