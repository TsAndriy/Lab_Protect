import math
import time
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import io
from .algoritm.Config.config import (
    CONFIG_LR1, CONFIG_LR3
)
from .algoritm.LR1 import (
    LinearCongruentialGenerator,
    CesaroTest,
    FrequencyTest,
    RunsTest)
from .algoritm.LR2 import MD5
from .algoritm.LR3 import RC5


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
            'title': 'Створення програмного засобу для забезбечення цілісності інформації',
            'description': 'Реалізація алгоритму хешування MD5',
            'url': 'lab2/',
        },
        {
            'number': 3,
            'title': 'Створення програмного засобу для забезбечення конфідеційності інформації',
            'description': 'Реалізація алгоритму шифрування інформацій RC5',
            'url': 'lab3/',
        }
    ]

    context = {
        'labs': labs,
        'title': 'Лабораторні роботи з захисту інформації'
    }
    return render(request, 'index.html', context)


# ==================== Лабораторна робота 1 ====================

def lab1_prng(request):
    context = {
        'title': 'Лабораторна робота 1',
        'config': CONFIG_LR1
    }
    return render(request, 'labs/lab1/index.html', context)


@csrf_exempt
def generate_prng(request):
    # Генерація псевдовипадкових чисел
    if request.method == 'POST':
        try:
            start_time = time.time()
            data = json.loads(request.body)

            # Отримання параметрів
            m = int(data.get('m', CONFIG_LR1['m']))
            a = int(data.get('a', CONFIG_LR1['a']))
            c = int(data.get('c', CONFIG_LR1['c']))
            x0 = int(data.get('x0', CONFIG_LR1['x0']))
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

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            response = {
                'success': True,
                'sequence': sequence,
                'count': len(sequence),
                'statistics': stats,
                'generation_time_ms': duration_ms,
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
            m = int(data.get('m', CONFIG_LR1['m']))
            a = int(data.get('a', CONFIG_LR1['a']))
            c = int(data.get('c', CONFIG_LR1['c']))
            x0 = int(data.get('x0', CONFIG_LR1['x0']))
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
            m = int(data.get('m', CONFIG_LR1['m']))
            a = int(data.get('a', CONFIG_LR1['a']))
            c = int(data.get('c', CONFIG_LR1['c']))
            x0 = int(data.get('x0', CONFIG_LR1['x0']))
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
            m = int(data.get('m', CONFIG_LR1['m']))
            a = int(data.get('a', CONFIG_LR1['a']))
            c = int(data.get('c', CONFIG_LR1['c']))
            x0 = int(data.get('x0', CONFIG_LR1['x0']))
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

    m = int(data.get('m', CONFIG_LR1['m']))
    a = int(data.get('a', CONFIG_LR1['a']))
    c = int(data.get('c', CONFIG_LR1['c']))
    x0 = int(data.get('x0', CONFIG_LR1['x0']))
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


# ==================== Лабораторна робота 2 ====================

def lab2_md5(request):
    """Головна сторінка ЛР2"""
    context = {'title': 'Лабораторна робота 2'}
    return render(request, 'labs/lab2/index.html', context)


@csrf_exempt
def hash_text(request):
    """Хешування текстового рядка"""
    if request.method == 'POST':
        try:
            start_time = time.time()
            data = json.loads(request.body)

            text = data.get('text', '')

            # Обчислюємо хеш
            hash_result = MD5.hash_string(text)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            response = {
                'success': True,
                'hash': hash_result,
                'text_length': len(text),
                'execution_time_ms': duration_ms
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Дозволено тільки POST запити'}, status=405)


@csrf_exempt
def hash_file(request):
    """Хешування файлу"""
    if request.method == 'POST':
        try:
            start_time = time.time()

            # Перевіряємо наявність файлу
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'Файл не знайдено'}, status=400)

            uploaded_file = request.FILES['file']

            # Обчислюємо хеш
            hash_result = MD5.hash_file(file_object=uploaded_file)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            response = {
                'success': True,
                'hash': hash_result,
                'filename': uploaded_file.name,
                'file_size': uploaded_file.size,
                'execution_time_ms': duration_ms
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Дозволено тільки POST запити'}, status=405)


@csrf_exempt
def verify_file(request):
    """Перевірка цілісності файлу за хешем"""
    if request.method == 'POST':
        try:
            start_time = time.time()

            # Перевіряємо наявність файлу
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'Файл не знайдено'}, status=400)

            uploaded_file = request.FILES['file']
            expected_hash = request.POST.get('expected_hash', '').strip()

            # Валідація хешу
            if not expected_hash:
                return JsonResponse({'error': 'Не вказано очікуваний хеш'}, status=400)

            if len(expected_hash) != 32:
                return JsonResponse({'error': 'Невірний формат хешу (повинен бути 32 символи)'}, status=400)

            # Перевіряємо файл
            verification_result = MD5.verify_file(
                file_object=uploaded_file,
                expected_hash=expected_hash
            )

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            response = {
                'success': True,
                'match': verification_result['match'],
                'expected_hash': verification_result['expected_hash'],
                'actual_hash': verification_result['actual_hash'],
                'message': verification_result['message'],
                'filename': uploaded_file.name,
                'file_size': uploaded_file.size,
                'execution_time_ms': duration_ms
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Дозволено тільки POST запити'}, status=405)


@csrf_exempt
def export_hash(request):
    """Експорт хешу у файл"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            hash_value = data.get('hash', '')
            filename = data.get('filename', 'file')

            if not hash_value:
                return JsonResponse({'error': 'Не вказано хеш'}, status=400)

            # Формуємо вміст файлу
            output = io.StringIO()
            output.write(hash_value)

            file_content = output.getvalue()
            output.close()

            # Створюємо HTTP-відповідь
            response = HttpResponse(file_content, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}.md5.txt"'

            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Дозволено тільки POST запити'}, status=405)

# ==================== Лабораторна робота 3 (RC5) ====================

def lab3_rc5(request):
    """Головна сторінка ЛР3"""
    context = {'title': 'Лабораторна робота 3: Шифрування RC5'}
    return render(request, 'labs/lab3/index.html', context)


@csrf_exempt
def rc5_encrypt(request):
    """Шифрування файлу/даних алгоритмом RC5"""
    if request.method == 'POST':
        try:
            start_time = time.time()

            # Отримуємо пароль
            password = request.POST.get('password', '')
            if not password:
                return JsonResponse({'error': 'Пароль не може бути порожнім'}, status=400)

            # Отримуємо дані для шифрування
            if 'file' in request.FILES:
                file_obj = request.FILES['file']
                input_data = file_obj.read()
                filename = file_obj.name
            else:
                # Якщо не файл, пробуємо взяти текст
                text = request.POST.get('text', '')
                if not text:
                    return JsonResponse({'error': 'Не надано даних для шифрування'}, status=400)
                input_data = text.encode('utf-8')
                filename = 'text.txt'

            # Шифруємо (передаємо конфігурації з views)
            encrypted_data = RC5.encrypt_data(input_data, password, CONFIG_LR3, CONFIG_LR1)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            response = {
                'success': True,
                'filename': filename + '.bin',
                'original_size': len(input_data),
                'encrypted_size': len(encrypted_data),
                'encrypted_hex': encrypted_data.hex(),
                'encrypted_data_full_hex': encrypted_data.hex(),
                'execution_time_ms': duration_ms
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': f"Помилка шифрування: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Дозволено тільки POST запити'}, status=405)


@csrf_exempt
def rc5_decrypt(request):
    """Дешифрування файлу/даних алгоритмом RC5"""
    if request.method == 'POST':
        try:
            start_time = time.time()

            # Отримуємо пароль
            password = request.POST.get('password', '')
            if not password:
                return JsonResponse({'error': 'Пароль не може бути порожнім'}, status=400)

            # Отримуємо зашифровані дані
            input_data = b''
            filename = 'decrypted_file'

            if 'file' in request.FILES:
                file_obj = request.FILES['file']
                input_data = file_obj.read()
                filename = file_obj.name.replace('.bin', '')
            elif 'encrypted_hex' in request.POST:
                # Якщо передаємо HEX рядок напряму
                hex_data = request.POST.get('encrypted_hex', '').strip()
                try:
                    input_data = bytes.fromhex(hex_data)
                except ValueError:
                    return JsonResponse({'error': 'Некоректний HEX формат'}, status=400)
            else:
                return JsonResponse({'error': 'Не надано даних для дешифрування'}, status=400)

            # Дешифруємо (передаємо конфігурацію з views)
            try:
                decrypted_data = RC5.decrypt_data(input_data, password, CONFIG_LR3)
            except ValueError as ve:
                return JsonResponse({'error': str(ve)}, status=400)

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Пробуємо декодувати як текст для прев'ю
            try:
                text_preview = decrypted_data.decode('utf-8')
                is_text = True
            except UnicodeDecodeError:
                text_preview = "Бінарні дані (неможливо відобразити як текст)"
                is_text = False

            response = {
                'success': True,
                'filename': filename,
                'decrypted_size': len(decrypted_data),
                'text_preview': text_preview,
                'is_text': is_text,
                'decrypted_hex': decrypted_data.hex(),
                'decrypted_text_full': text_preview if is_text else None,
                'execution_time_ms': duration_ms
            }

            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': f"Помилка дешифрування: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Дозволено тільки POST запити'}, status=405)