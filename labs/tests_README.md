# Unit Tests для Лабораторної роботи №1

## Опис

Цей файл містить повний набір unit тестів для ЛР1 - Генератор псевдовипадкових чисел (ГПВЧ).

## Структура тестів

### 1. GCDTestCase
Тести для функції найбільшого спільного дільника (НСД):
- `test_gcd_basic` - базові тести НСД
- `test_gcd_same_numbers` - НСД однакових чисел
- `test_gcd_with_zero` - НСД з нулем
- `test_gcd_coprime` - НСД взаємно простих чисел

### 2. LinearCongruentialGeneratorTestCase
Тести для генератора псевдовипадкових чисел:
- `test_initialization` - перевірка ініціалізації
- `test_next_generation` - генерація наступного числа
- `test_generate_sequence` - генерація послідовності
- `test_reset` - скидання генератора
- `test_deterministic_generation` - детермінованість генерації
- `test_find_period` - знаходження періоду
- `test_statistics` - статистичні функції
- `test_empty_sequence_statistics` - статистика для порожньої послідовності
- `test_values_within_range` - перевірка діапазону значень

### 3. CesaroTestCase
Тести для тесту Чезаро:
- `test_estimate_pi_basic` - базова оцінка Pi
- `test_compare_with_system_random` - порівняння з системним генератором

### 4. FrequencyTestCase
Тести для частотного тесту:
- `test_frequency_test_basic` - базовий тест частот
- `test_empty_sequence` - тест з порожньою послідовністю
- `test_different_bit_lengths` - тест з різною довжиною бітів

### 5. RunsTestCase
Тести для тесту послідовностей:
- `test_runs_basic` - базовий тест послідовностей
- `test_runs_short_sequence` - тест з короткою послідовністю
- `test_runs_pattern_detection` - виявлення патернів

### 6. IntegrationTestCase
Інтеграційні тести:
- `test_full_workflow` - повний робочий процес
- `test_variant_17_config` - конфігурація варіанту 17

## Як запустити тести

### Всі тести для labs app:
```bash
python manage.py test labs
```

### Конкретний тестовий клас:
```bash
python manage.py test labs.tests.LinearCongruentialGeneratorTestCase
```

### Конкретний тест:
```bash
python manage.py test labs.tests.LinearCongruentialGeneratorTestCase.test_generate_sequence
```

### З підробицями (verbose):
```bash
python manage.py test labs -v 2
```

### Тільки швидкі тести (без інтеграційних):
```bash
python manage.py test labs --exclude-tag=slow
```

## Покриття коду

Для перевірки покриття коду тестами:

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

## Очікувані результати

При успішному виконанні всіх тестів ви побачите:
```
.............................
----------------------------------------------------------------------
Ran 29 tests in X.XXXs

OK
```

## Примітки

- Деякі тести (наприклад, тест Чезаро) можуть тривати довше через велику кількість обчислень
- Тести використовують конфігурацію варіанту 17: m=2^26-1, a=13^3, c=1597, x0=13
- Всі тести незалежні один від одного і можуть виконуватись в будь-якому порядку
- Тести перевіряють як коректність алгоритмів, так і граничні випадки

## Troubleshooting

Якщо тести не проходять:

1. **ModuleNotFoundError: No module named 'django'**
   - Встановіть Django: `pip install django`

2. **Тести займають багато часу**
   - Зменшіть кількість ітерацій в тестах Чезаро (параметр `num_pairs`)

3. **Помилки імпорту**
   - Переконайтесь що ви в правильній директорії проекту
   - Перевірте PYTHONPATH

## Покращення

Можливі напрямки для покращення тестів:
- Додати performance тести
- Додати параметризовані тести для різних конфігурацій
- Додати тести для граничних випадків (дуже великі числа)
- Додати mock тести для перевірки взаємодії з Django views
