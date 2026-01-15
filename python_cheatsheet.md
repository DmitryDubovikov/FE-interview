# Python Cheatsheet

## Concurrency: GIL, Async, Multiprocessing

### GIL (Global Interpreter Lock)

**Что это:** Глобальная блокировка интерпретатора — механизм в CPython, который разрешает только одному потоку выполнять Python-код в любой момент времени. Даже если у тебя 8 ядер, Python-потоки не могут работать параллельно на CPU-задачах.

**Зачем нужен:** Упрощает управление памятью (подсчёт ссылок) и делает C-расширения безопаснее.

**Когда GIL отпускается:**
- При I/O операциях (сеть, файлы) — поток ждёт ответа, GIL свободен
- При вызове некоторых C-библиотек (NumPy)
- При `time.sleep()`

**Обход GIL:** `multiprocessing` (отдельные процессы), Python 3.13+ (`--disable-gil`)

---

### Когда что использовать

| Тип задачи | Threading | Multiprocessing | Asyncio |
|------------|-----------|-----------------|---------|
| **CPU-bound** (вычисления, криптография) | Нет — GIL мешает | **Да** | Нет |
| **I/O-bound** (много запросов) | Можно | Избыточно | **Лучший выбор** |
| **I/O-bound** (мало запросов) | Да | Избыточно | Да |

**CPU-bound** — задача упирается в процессор (математика, обработка данных)
**I/O-bound** — задача ждёт внешних ресурсов (сеть, диск, БД)

---

### Threading (потоки)

**Суть:** Потоки работают в одном процессе, делят память. Из-за GIL не дают ускорения на CPU-задачах, но отлично работают для I/O.

```python
import threading

# Создаём и запускаем поток
t = threading.Thread(target=func, args=(arg,))
t.start()   # запустить
t.join()    # дождаться завершения

# Lock — защита от гонки данных (когда 2 потока меняют одну переменную)
lock = threading.Lock()
with lock:
    shared_counter += 1  # только один поток за раз
```

**Проблема race condition:** без Lock два потока могут одновременно читать/писать переменную и получить неверный результат.

---

### Multiprocessing (процессы)

**Суть:** Каждый процесс — отдельный интерпретатор со своим GIL. Настоящий параллелизм для CPU-задач. Минус: обмен данными дороже (сериализация через pickle).

```python
from multiprocessing import Pool

# Pool — пул процессов для параллельной обработки
with Pool() as pool:
    results = pool.map(func, data)  # func применится к каждому элементу data
```

**Важно:** На Windows обязательно `if __name__ == "__main__":` перед созданием процессов.

---

### Asyncio (асинхронность)

**Суть:** Один поток, но задачи "уступают" друг другу при ожидании I/O. Идеально для тысяч сетевых запросов — нет накладных расходов на потоки/процессы.

**Как работает:** Event loop крутится в цикле. Когда корутина говорит `await` (жду ответа от сервера), loop переключается на другую корутину.

```python
import asyncio

async def fetch(url):
    await asyncio.sleep(1)  # имитация запроса
    return f"data from {url}"

async def main():
    # gather — запустить параллельно и дождаться всех
    results = await asyncio.gather(
        fetch("url1"),
        fetch("url2"),
        fetch("url3")
    )

asyncio.run(main())  # точка входа

# TaskGroup (Python 3.11+) — лучше gather, автоматически отменяет задачи при ошибке
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(fetch("url1"))
    task2 = tg.create_task(fetch("url2"))
```

**Частая ошибка:** использовать `time.sleep()` или `requests.get()` — они блокируют весь event loop! Нужно `await asyncio.sleep()` и `aiohttp`.

---

## Big O Notation

### Что это

**Big O** — способ оценить, как растёт время работы алгоритма при увеличении входных данных. Не точное время, а порядок роста.

**Зачем:** Сравнивать алгоритмы независимо от железа. O(n²) всегда хуже O(n) на больших данных.

---

### Классы сложности (от лучшего к худшему)

```
O(1)       — константа: не зависит от размера данных
             Пример: dict[key], list[i]

O(log n)   — логарифм: каждый шаг отбрасывает половину данных
             Пример: бинарный поиск в отсортированном массиве

O(n)       — линейная: проходим все элементы один раз
             Пример: поиск в списке, sum(), max()

O(n log n) — линейно-логарифмическая: хорошие сортировки
             Пример: sorted(), .sort() (Timsort)

O(n²)      — квадратичная: вложенный цикл по всем элементам
             Пример: bubble sort, сравнение каждого с каждым

O(2^n)     — экспоненциальная: полный перебор
             Пример: наивный Фибоначчи, все подмножества
```

**Наглядно при n=1000:**
- O(1) = 1 операция
- O(log n) = 10 операций
- O(n) = 1,000 операций
- O(n²) = 1,000,000 операций
- O(2^n) = больше атомов во Вселенной

---

### Сложность структур Python

**list (динамический массив):**
| Операция | Сложность | Почему |
|----------|-----------|--------|
| `lst[i]`, `len()` | O(1) | Прямой доступ по индексу |
| `append()`, `pop()` | O(1)* | Амортизированно (иногда перевыделяет память) |
| `insert(i)`, `pop(i)` | O(n) | Сдвигает все элементы после i |
| `x in lst` | O(n) | Перебирает весь список |
| `sort()` | O(n log n) | Timsort |

**dict / set (хэш-таблица):**
| Операция | Сложность | Почему |
|----------|-----------|--------|
| `d[key]`, `key in d` | O(1) | Хэш сразу даёт позицию |
| `d[key] = val`, `del d[key]` | O(1) | |
| `set.add()`, `x in set` | O(1) | |

**Вывод:** Если нужен быстрый поиск — используй `set` или `dict`, не `list`.

---

### Правила упрощения

```python
# Константы отбрасываем
O(2n) → O(n)
O(n/2) → O(n)

# Младшие члены отбрасываем (при больших n они незначительны)
O(n² + n) → O(n²)
O(n + log n) → O(n)

# Вложенные операции умножаются
for i in range(n):       # O(n)
    for j in range(n):   # O(n)
        ...              # Итого O(n²)
```

---

## Recursion & Functional Programming

### Рекурсия

**Что это:** Функция вызывает сама себя. Нужны два компонента:
1. **Базовый случай** — когда остановиться
2. **Рекурсивный случай** — вызов с меньшей задачей

```python
def factorial(n):
    if n <= 1:              # база: когда n=1, возвращаем 1
        return 1
    return n * factorial(n-1)  # рекурсия: n! = n * (n-1)!
```

**Лимит глубины:** Python ограничивает до ~1000 вызовов (защита от бесконечной рекурсии)
```python
import sys
sys.getrecursionlimit()     # узнать лимит
sys.setrecursionlimit(2000) # изменить (осторожно!)
```

**Хвостовая рекурсия:** когда рекурсивный вызов — последняя операция. Некоторые языки оптимизируют это в цикл, но **Python не оптимизирует** (Гвидо считает стектрейсы важнее).

**Когда использовать:** деревья, графы, задачи "разделяй и властвуй". Для простых случаев цикл понятнее.

---

### Мемоизация

**Что это:** Кэширование результатов функции. Если вызвали с теми же аргументами — возвращаем из кэша.

```python
from functools import cache, lru_cache

@cache  # безлимитный кэш (Python 3.9+)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

# Без кэша: O(2^n) — каждый вызов порождает 2 новых
# С кэшем: O(n) — каждое значение считается один раз

@lru_cache(maxsize=128)  # ограниченный кэш (LRU = Least Recently Used)
def expensive(x, y):
    return x ** y

expensive.cache_info()   # статистика: hits, misses
expensive.cache_clear()  # очистить кэш
```

**Ограничение:** аргументы должны быть хэшируемы (нельзя list, можно tuple).

---

### map / filter / reduce

**map** — применить функцию к каждому элементу:
```python
names = ["alice", "bob"]
list(map(str.upper, names))      # ['ALICE', 'BOB']
[x.upper() for x in names]       # то же, но читабельнее
```

**filter** — оставить элементы, для которых функция вернула True:
```python
nums = [-1, 0, 1, 2]
list(filter(lambda x: x > 0, nums))  # [1, 2]
[x for x in nums if x > 0]           # то же, но читабельнее
```

**reduce** — свернуть список в одно значение, применяя функцию попарно:
```python
from functools import reduce
reduce(lambda acc, x: acc + x, [1,2,3,4])  # ((1+2)+3)+4 = 10
# Лучше использовать sum(), max(), "".join() где возможно
```

**Рекомендация:** В Python предпочитай list comprehension — они понятнее.

---

### Lambda

**Что это:** Анонимная функция из одного выражения.

```python
square = lambda x: x ** 2
add = lambda x, y: x + y

# Типичное использование — короткие функции для sort/map/filter
users = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
sorted(users, key=lambda u: u["age"])  # сортировка по возрасту
```

**Ограничения:** только одно выражение, нет аннотаций типов, нет docstring. Для сложной логики — обычная функция.

---

### Замыкания (Closures)

**Что это:** Функция "запоминает" переменные из внешней области видимости, даже когда та уже завершилась.

```python
def make_multiplier(n):
    def multiplier(x):
        return x * n  # n "захвачена" из внешней функции
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15
```

**nonlocal** — чтобы изменить (а не просто прочитать) внешнюю переменную:
```python
def counter():
    count = 0
    def increment():
        nonlocal count  # без этого будет ошибка
        count += 1
        return count
    return increment

c = counter()
print(c(), c(), c())  # 1, 2, 3
```

**Ловушка late binding:**
```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])  # [2, 2, 2] — все ссылаются на одну i!

# Решение: зафиксировать через default argument
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])  # [0, 1, 2]
```

---

### functools

```python
from functools import partial, wraps

# partial — создать новую функцию с предустановленными аргументами
import json
pretty_json = partial(json.dumps, indent=2, ensure_ascii=False)
print(pretty_json({"name": "Алиса"}))

# wraps — сохранить имя и docstring оригинальной функции в декораторе
def my_decorator(func):
    @wraps(func)  # без этого func.__name__ станет "wrapper"
    def wrapper(*args, **kwargs):
        print("Before")
        return func(*args, **kwargs)
    return wrapper
```
