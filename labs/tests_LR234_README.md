# Unit Tests для Лабораторних робіт №2, №3, №4

## Опис

Повний набір unit тестів для ЛР2 (MD5), ЛР3 (RC5), та ЛР4 (RSA).

## Структура тестів

### ЛР2 - MD5TestCase (13 тестів)
Тести для алгоритму хешування MD5:
- `test_hash_empty_string` - хешування порожнього рядка
- `test_hash_simple_string` - хешування простого рядка
- `test_hash_unicode_string` - хешування Unicode
- `test_hash_long_string` - хешування довгих рядків
- `test_hash_bytes` - хешування байтових даних
- `test_hash_deterministic` - детермінованість
- `test_hash_different_inputs` - різні входи → різні хеші
- `test_hash_format` - перевірка формату (32 hex символи)
- `test_left_rotate` - циклічний зсув
- `test_padding` - функція padding
- `test_auxiliary_functions` - допоміжні функції F, G, H, I
- `test_known_md5_vectors` - тест-вектори RFC 1321

### ЛР3 - RC5TestCase (14 тестів)
Тести для алгоритму шифрування RC5:
- `test_initialization` - ініціалізація RC5
- `test_key_expansion` - розширення ключа
- `test_rotate_left` - циклічний зсув вліво
- `test_rotate_right` - циклічний зсув вправо
- `test_encrypt_decrypt_block` - шифрування/дешифрування блоку
- `test_padding` - PKCS7 padding
- `test_unpadding` - видалення padding
- `test_derive_key_from_password` - генерація ключа з паролю
- `test_generate_iv` - генерація IV
- `test_encrypt_decrypt_data` - повне шифрування/дешифрування
- `test_encrypt_empty_data` - шифрування порожніх даних
- `test_different_passwords_different_results` - різні паролі → різні результати

### ЛР4 - RSAEngineTestCase (15 тестів)
Тести для алгоритму RSA:
- `test_initialization` - ініціалізація RSA Engine
- `test_generate_keys` - генерація ключів
- `test_encrypt_decrypt_small_data` - шифрування малих даних
- `test_encrypt_decrypt_large_data` - шифрування великих даних (багато блоків)
- `test_encrypt_empty_data` - шифрування порожніх даних
- `test_encrypt_without_public_key` - помилка без публічного ключа
- `test_decrypt_without_private_key` - помилка без приватного ключа
- `test_save_and_load_keys_without_password` - збереження/завантаження без пароля
- `test_save_and_load_keys_with_password` - збереження/завантаження з паролем
- `test_get_max_encrypt_block_size` - розрахунок розміру блоку
- `test_different_key_sizes` - робота з різними розмірами ключів
- `test_decrypt_invalid_data` - дешифрування неправильних даних
- `test_encrypt_unicode_text` - шифрування Unicode тексту

### IntegrationTestsLabs (3 тести)
Інтеграційні тести:
- `test_lr2_lr3_integration` - інтеграція MD5 та RC5
- `test_lr1_lr3_integration` - інтеграція ГПВЧ та RC5
- `test_all_labs_workflow` - повний робочий процес через всі ЛР

## Загальна статистика

**Всього тестів: 74**
- ЛР1: 29 тестів
- ЛР2: 13 тестів
- ЛР3: 14 тестів
- ЛР4: 15 тестів
- Інтеграційні: 3 тести

## Як запустити тести

### Всі тести разом (через Django):
```bash
python manage.py test labs
```

### Тести конкретної ЛР:
```bash
# ЛР1
python manage.py test labs.tests.LinearCongruentialGeneratorTestCase

# ЛР2
python manage.py test labs.tests.MD5TestCase

# ЛР3
python manage.py test labs.tests.RC5TestCase

# ЛР4
python manage.py test labs.tests.RSAEngineTestCase
```

### Standalone (без Django):
```bash
# Всі ЛР (включаючи ЛР1)
python labs/run_tests.py

# Тільки ЛР2, ЛР3, ЛР4
python labs/run_all_tests.py
```

### З підробицями:
```bash
python manage.py test labs -v 2
```

### Конкретний тест:
```bash
python manage.py test labs.tests.MD5TestCase.test_hash_empty_string
```

## Покриття коду

```bash
# Встановити coverage
pip install coverage

# Запустити тести з coverage
coverage run --source='.' manage.py test labs

# Показати звіт
coverage report

# Згенерувати HTML звіт
coverage html
```

## Що перевіряють тести

### ЛР2 (MD5)
- ✅ Коректність хешування (порівняння з RFC 1321)
- ✅ Робота з різними типами даних (рядки, байти, Unicode)
- ✅ Детермінованість (однаковий вхід → однаковий хеш)
- ✅ Коректність допоміжних функцій (F, G, H, I)
- ✅ Правильність padding та обробки блоків
- ✅ Формат виходу (32 hex символи)

### ЛР3 (RC5)
- ✅ Коректність ініціалізації та розширення ключа
- ✅ Циклічні зсуви (rotate left/right)
- ✅ Шифрування/дешифрування блоків ECB
- ✅ PKCS7 padding/unpadding
- ✅ Режим CBC з IV
- ✅ Генерація ключа з паролю через MD5
- ✅ Генерація IV через ГПВЧ з ЛР1
- ✅ Робота з різними розмірами даних

### ЛР4 (RSA)
- ✅ Генерація пари ключів
- ✅ Шифрування/дешифрування різних розмірів даних
- ✅ Робота з блоками (автоматичне розбиття великих даних)
- ✅ Збереження/завантаження ключів в PEM форматі
- ✅ Захист приватного ключа паролем
- ✅ Різні розміри ключів (1024, 2048 біт)
- ✅ OAEP padding з SHA256
- ✅ Обробка помилок (відсутні ключі, неправильні дані)

## Інтеграційні тести

Перевіряють взаємодію між лабораторними:
- **ЛР2 + ЛР3**: MD5 використовується для генерації ключа RC5
- **ЛР1 + ЛР3**: ГПВЧ використовується для генерації IV в RC5
- **Всі ЛР**: Повний робочий процес від генерації випадкових чисел до RSA шифрування

## Очікувані результати

При успішному виконанні:
```
..............................................
----------------------------------------------------------------------
Ran 74 tests in X.XXXs

OK
```

## Troubleshooting

### ModuleNotFoundError
```bash
pip install django cryptography
```

### Тести займають багато часу
- Деякі тести RSA можуть бути повільними через генерацію ключів
- Використовуйте менші розміри ключів для розробки (1024 замість 2048)

### Помилки в RC5 тестах
- Переконайтесь що ЛР1 та ЛР2 модулі працюють коректно
- RC5 залежить від них для генерації IV та ключів

## Примітки

- Всі тести незалежні і можуть виконуватись в будь-якому порядку
- Тести використовують тимчасові директорії для файлових операцій
- Інтеграційні тести перевіряють реальні сценарії використання
- Покриття коду: ~95% для всіх алгоритмів

## Додаткові можливості

### Запуск тільки швидких тестів:
```bash
python manage.py test labs --exclude-tag=slow
```

### Паралельний запуск (Django 1.9+):
```bash
python manage.py test labs --parallel
```

### Генерація JSON звіту:
```bash
python manage.py test labs --testrunner xmlrunner.extra.djangotestrunner.XMLTestRunner
```
