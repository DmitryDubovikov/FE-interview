# Вопросы для Python собеседования (Middle/Senior)

Этот список составлен для подготовки к собеседованиям на позицию Python Developer. Вопросы охватывают core Python, concurrency, алгоритмы и функциональное программирование. Фокус на современном Python 3.10+.

## 🟢 Pure Python — Стандартная библиотека

_Фундаментальные знания языка без использования внешних фреймворков._

1. **Как устроены встроенные типы данных: list, dict, set, tuple?**

   **list** — динамический массив (не связный список). Под капотом это массив указателей на объекты. При добавлении элементов массив перевыделяется с запасом (over-allocation), чтобы `append` работал за амортизированное O(1).

   ```python
   import sys
   lst = []
   for i in range(10):
       print(f"len={len(lst)}, size={sys.getsizeof(lst)} bytes")
       lst.append(i)
   # Размер растёт скачками: 56 → 88 → 88 → 88 → 88 → 120 → ...
   ```

   **dict** — хэш-таблица с открытой адресацией. С Python 3.7 гарантирует сохранение порядка вставки. Использует две структуры: компактный массив для хранения пар (hash, key, value) и разреженный массив индексов.

   **set** — тоже хэш-таблица, но хранит только ключи. Операции `in`, `add`, `remove` работают за O(1) в среднем.

   **tuple** — неизменяемый массив фиксированного размера. Занимает меньше памяти, чем list, и может быть хэширован (если все элементы хэшируемы).

   | Тип | Изменяемый | Упорядоченный | Хэшируемый | Дубликаты |
   |-----|------------|---------------|------------|-----------|
   | list | Да | Да | Нет | Да |
   | tuple | Нет | Да | Да* | Да |
   | dict | Да | Да (3.7+) | Нет | Ключи — нет |
   | set | Да | Нет | Нет | Нет |

   *tuple хэшируем только если все его элементы хэшируемы

---

2. **В чём разница между mutable и immutable типами? Как это влияет на хэширование?**

   **Immutable** (неизменяемые): `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`
   **Mutable** (изменяемые): `list`, `dict`, `set`, `bytearray`

   **Почему это важно:**

   ```python
   # Проблема с mutable default argument
   def add_item(item, lst=[]):  # lst создаётся ОДИН раз
       lst.append(item)
       return lst

   print(add_item(1))  # [1]
   print(add_item(2))  # [1, 2] — неожиданно!

   # Правильно:
   def add_item(item, lst=None):
       if lst is None:
           lst = []
       lst.append(item)
       return lst
   ```

   **Хэширование:** Только immutable объекты могут быть ключами dict или элементами set. Хэш объекта должен быть постоянным на протяжении его жизни.

   ```python
   # Это работает
   d = {(1, 2): "tuple as key"}
   s = {frozenset([1, 2, 3])}

   # Это вызовет TypeError
   d = {[1, 2]: "list as key"}  # TypeError: unhashable type: 'list'
   ```

   **Важно:** `id()` объекта не равен его `hash()`. Для пользовательских классов можно определить `__hash__`, но если объект изменяемый — это опасно.

---

3. **Comprehensions и generator expressions: синтаксис и различия**

   **List comprehension** — создаёт список сразу целиком в памяти:
   ```python
   squares = [x**2 for x in range(1000)]  # Список из 1000 элементов в памяти
   ```

   **Generator expression** — ленивый итератор, вычисляет элементы по требованию:
   ```python
   squares_gen = (x**2 for x in range(1000))  # Генератор, почти не занимает память
   ```

   **Dict и set comprehensions:**
   ```python
   # Dict comprehension
   word_lengths = {word: len(word) for word in ["hello", "world"]}
   # {'hello': 5, 'world': 5}

   # Set comprehension
   unique_lengths = {len(word) for word in ["hello", "world", "hi"]}
   # {2, 5}
   ```

   **Вложенные comprehensions:**
   ```python
   # Эквивалент вложенных циклов
   matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
   flat = [num for row in matrix for num in row]
   # [1, 2, 3, 4, 5, 6, 7, 8, 9]

   # С условием
   even_flat = [num for row in matrix for num in row if num % 2 == 0]
   # [2, 4, 6, 8]
   ```

   **Когда использовать generator expression:**
   - Обработка больших данных (файлы, API responses)
   - Когда нужен только один проход по данным
   - Для передачи в функции типа `sum()`, `max()`, `any()`

   ```python
   # Эффективно — генератор не создаёт список
   total = sum(x**2 for x in range(1_000_000))

   # Неэффективно — создаётся промежуточный список
   total = sum([x**2 for x in range(1_000_000)])
   ```

---

4. **Как работают декораторы? Напишите декоратор с аргументами.**

   Декоратор — это функция, которая принимает функцию и возвращает новую функцию (обычно с расширенной функциональностью).

   **Простой декоратор:**
   ```python
   def timer(func):
       from time import perf_counter
       from functools import wraps

       @wraps(func)  # Сохраняет __name__, __doc__ оригинальной функции
       def wrapper(*args, **kwargs):
           start = perf_counter()
           result = func(*args, **kwargs)
           elapsed = perf_counter() - start
           print(f"{func.__name__} took {elapsed:.4f}s")
           return result
       return wrapper

   @timer
   def slow_function():
       import time
       time.sleep(1)

   slow_function()  # slow_function took 1.0012s
   ```

   **Декоратор с аргументами** — это фабрика декораторов (функция, возвращающая декоратор):
   ```python
   def retry(max_attempts: int = 3, exceptions: tuple = (Exception,)):
       def decorator(func):
           from functools import wraps

           @wraps(func)
           def wrapper(*args, **kwargs):
               for attempt in range(1, max_attempts + 1):
                   try:
                       return func(*args, **kwargs)
                   except exceptions as e:
                       if attempt == max_attempts:
                           raise
                       print(f"Attempt {attempt} failed: {e}")
           return wrapper
       return decorator

   @retry(max_attempts=5, exceptions=(ConnectionError, TimeoutError))
   def fetch_data(url):
       ...
   ```

   **Декоратор как класс:**
   ```python
   class CountCalls:
       def __init__(self, func):
           self.func = func
           self.count = 0

       def __call__(self, *args, **kwargs):
           self.count += 1
           print(f"Call #{self.count}")
           return self.func(*args, **kwargs)

   @CountCalls
   def say_hello():
       print("Hello!")
   ```

---

5. **Контекстные менеджеры: протокол и contextlib**

   Контекстный менеджер управляет ресурсами через `with` statement. Гарантирует освобождение ресурсов даже при исключениях.

   **Протокол контекстного менеджера:**
   ```python
   class FileManager:
       def __init__(self, filename, mode):
           self.filename = filename
           self.mode = mode
           self.file = None

       def __enter__(self):
           self.file = open(self.filename, self.mode)
           return self.file  # Это значение присваивается переменной после as

       def __exit__(self, exc_type, exc_val, exc_tb):
           if self.file:
               self.file.close()
           # Вернуть True = подавить исключение
           # Вернуть False/None = пробросить исключение дальше
           return False

   with FileManager("test.txt", "w") as f:
       f.write("Hello")
   # Файл закрыт автоматически, даже если было исключение
   ```

   **contextlib.contextmanager** — создание контекстного менеджера через генератор:
   ```python
   from contextlib import contextmanager

   @contextmanager
   def timer(label):
       from time import perf_counter
       start = perf_counter()
       try:
           yield  # Здесь выполняется код внутри with
       finally:
           elapsed = perf_counter() - start
           print(f"{label}: {elapsed:.4f}s")

   with timer("Processing"):
       heavy_computation()
   ```

   **Полезные инструменты из contextlib:**
   ```python
   from contextlib import suppress, redirect_stdout, ExitStack

   # suppress — игнорировать определённые исключения
   with suppress(FileNotFoundError):
       os.remove("temp.txt")

   # redirect_stdout — перенаправить вывод
   from io import StringIO
   f = StringIO()
   with redirect_stdout(f):
       print("Hello")
   output = f.getvalue()  # "Hello\n"

   # ExitStack — динамическое управление несколькими контекстами
   with ExitStack() as stack:
       files = [stack.enter_context(open(f)) for f in filenames]
   ```

---

6. **Dataclasses: когда и как использовать?**

   `dataclass` — декоратор для автоматической генерации `__init__`, `__repr__`, `__eq__` и других методов.

   ```python
   from dataclasses import dataclass, field

   @dataclass
   class User:
       name: str
       email: str
       age: int = 0
       tags: list[str] = field(default_factory=list)  # Для mutable defaults

   user = User("Alice", "alice@example.com", 30)
   print(user)  # User(name='Alice', email='alice@example.com', age=30, tags=[])
   ```

   **Полезные параметры:**
   ```python
   @dataclass(frozen=True)  # Immutable (можно использовать как ключ dict)
   class Point:
       x: float
       y: float

   @dataclass(order=True)  # Генерирует __lt__, __le__, __gt__, __ge__
   class Version:
       major: int
       minor: int
       patch: int

   @dataclass(slots=True)  # Python 3.10+ — использует __slots__ для экономии памяти
   class OptimizedUser:
       name: str
       email: str
   ```

   **field() для тонкой настройки:**
   ```python
   from dataclasses import dataclass, field

   @dataclass
   class Request:
       url: str
       headers: dict = field(default_factory=dict)
       _internal: str = field(default="", repr=False)  # Не показывать в repr
       id: str = field(init=False)  # Не включать в __init__

       def __post_init__(self):
           import uuid
           self.id = str(uuid.uuid4())
   ```

   **Когда использовать dataclass:**
   - Простые контейнеры данных (DTO, конфиги)
   - Когда нужны автоматические `__eq__` и `__hash__`
   - Замена namedtuple с большей гибкостью

   **Когда НЕ использовать:**
   - Сложная логика инициализации
   - Наследование с переопределением полей
   - Когда нужна полная совместимость с ORM (лучше Pydantic/attrs)

---

7. **Type hints в Python 3.10+: новый синтаксис и возможности**

   Python 3.10+ значительно упростил синтаксис аннотаций типов.

   **Новый синтаксис Union (Python 3.10+):**
   ```python
   # Старый способ (до 3.10)
   from typing import Union, Optional
   def process(value: Union[int, str]) -> Optional[str]:
       ...

   # Новый способ (3.10+)
   def process(value: int | str) -> str | None:
       ...
   ```

   **Встроенные generic типы (Python 3.9+):**
   ```python
   # Старый способ
   from typing import List, Dict, Set, Tuple
   def func(items: List[int]) -> Dict[str, int]:
       ...

   # Новый способ — используем встроенные типы напрямую
   def func(items: list[int]) -> dict[str, int]:
       ...
   ```

   **TypeAlias и type statement (Python 3.12+):**
   ```python
   # Python 3.10-3.11
   from typing import TypeAlias
   Vector: TypeAlias = list[float]

   # Python 3.12+
   type Vector = list[float]
   type Point = tuple[float, float]
   type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
   ```

   **Полезные типы из typing:**
   ```python
   from typing import Callable, TypeVar, Generic, Self, ParamSpec

   # Callable — тип функции
   Handler = Callable[[int, str], bool]  # (int, str) -> bool

   # TypeVar — generic параметр
   T = TypeVar("T")
   def first(items: list[T]) -> T | None:
       return items[0] if items else None

   # Self — ссылка на текущий класс (Python 3.11+)
   class Builder:
       def set_name(self, name: str) -> Self:
           self.name = name
           return self
   ```

   **Проверка типов в runtime:**
   ```python
   from typing import get_type_hints

   def greet(name: str, age: int) -> str:
       return f"Hello {name}, you are {age}"

   hints = get_type_hints(greet)
   # {'name': <class 'str'>, 'age': <class 'int'>, 'return': <class 'str'>}
   ```

---

8. **Pattern Matching (match-case) в Python 3.10+**

   Structural pattern matching — мощный инструмент для деструктуризации и сопоставления данных.

   **Базовый синтаксис:**
   ```python
   def http_status(status: int) -> str:
       match status:
           case 200:
               return "OK"
           case 404:
               return "Not Found"
           case 500 | 502 | 503:  # OR паттерн
               return "Server Error"
           case _:  # Wildcard — ловит всё остальное
               return "Unknown"
   ```

   **Деструктуризация последовательностей:**
   ```python
   def process_command(command: list[str]) -> str:
       match command:
           case ["quit"]:
               return "Exiting..."
           case ["load", filename]:
               return f"Loading {filename}"
           case ["save", filename, *options]:  # *rest захватывает остаток
               return f"Saving {filename} with options: {options}"
           case _:
               return "Unknown command"

   process_command(["save", "data.txt", "--force", "--backup"])
   # "Saving data.txt with options: ['--force', '--backup']"
   ```

   **Сопоставление словарей:**
   ```python
   def handle_event(event: dict) -> str:
       match event:
           case {"type": "click", "x": x, "y": y}:
               return f"Click at ({x}, {y})"
           case {"type": "keypress", "key": key}:
               return f"Key pressed: {key}"
           case {"type": t}:  # Захватываем значение type
               return f"Unknown event type: {t}"
   ```

   **Сопоставление объектов (классов):**
   ```python
   from dataclasses import dataclass

   @dataclass
   class Point:
       x: float
       y: float

   @dataclass
   class Circle:
       center: Point
       radius: float

   def describe(shape) -> str:
       match shape:
           case Point(x=0, y=0):
               return "Origin"
           case Point(x=x, y=y) if x == y:  # Guard condition
               return f"Point on diagonal at {x}"
           case Circle(center=Point(x=0, y=0), radius=r):
               return f"Circle at origin with radius {r}"
           case _:
               return "Some shape"
   ```

   **Захват значений с as:**
   ```python
   match data:
       case {"user": {"name": name, "email": email} as user_data}:
           print(f"User: {name}, full data: {user_data}")
   ```

---

9. **Walrus operator (:=) — оператор присваивания в выражениях**

   Walrus operator (`:=`) позволяет присваивать значение переменной внутри выражения. Появился в Python 3.8.

   **Основное применение — избежать повторных вычислений:**
   ```python
   # Без walrus — вызываем функцию дважды
   if len(data) > 10:
       print(f"Too long: {len(data)}")

   # С walrus — вычисляем один раз
   if (n := len(data)) > 10:
       print(f"Too long: {n}")
   ```

   **В циклах while:**
   ```python
   # Классический паттерн чтения
   while True:
       line = file.readline()
       if not line:
           break
       process(line)

   # С walrus — компактнее
   while (line := file.readline()):
       process(line)
   ```

   **В list comprehensions:**
   ```python
   # Фильтрация с сохранением вычисленного значения
   results = [y for x in data if (y := expensive_func(x)) is not None]

   # Без walrus пришлось бы вызывать expensive_func дважды или использовать генератор
   ```

   **В условных выражениях:**
   ```python
   # Поиск в regex с проверкой
   import re
   if (match := re.search(r'\d+', text)):
       print(f"Found number: {match.group()}")

   # Проверка и использование результата
   if (user := get_user(user_id)) and user.is_active:
       send_notification(user)
   ```

   **Когда НЕ использовать:**
   - Когда усложняет читаемость
   - В простых случаях, где обычное присваивание понятнее
   - Избегайте вложенных walrus операторов

   ```python
   # Плохо — слишком сложно читать
   if (x := (y := func()).attr) > 10:
       ...

   # Лучше — разбить на шаги
   y = func()
   x = y.attr
   if x > 10:
       ...
   ```

---

10. **F-strings: возможности форматирования**

    F-strings (formatted string literals) — самый быстрый и удобный способ форматирования строк в Python.

    **Базовое использование:**
    ```python
    name = "Alice"
    age = 30
    print(f"Name: {name}, Age: {age}")
    ```

    **Debug mode (Python 3.8+):**
    ```python
    x = 10
    y = 20
    print(f"{x=}, {y=}")  # x=10, y=20
    print(f"{x + y=}")     # x + y=30

    # С форматированием
    value = 3.14159
    print(f"{value=:.2f}")  # value=3.14
    ```

    **Форматирование чисел:**
    ```python
    n = 1234567.89

    # Разделители тысяч
    print(f"{n:,}")      # 1,234,567.89
    print(f"{n:_}")      # 1_234_567.89

    # Точность и ширина
    print(f"{n:.2f}")    # 1234567.89
    print(f"{n:15.2f}")  #     1234567.89 (выравнивание по правому краю)
    print(f"{n:<15.2f}") # 1234567.89     (по левому)
    print(f"{n:^15.2f}") #   1234567.89   (по центру)

    # Проценты
    ratio = 0.857
    print(f"{ratio:.1%}")  # 85.7%

    # Экспоненциальная запись
    big = 1234567890
    print(f"{big:.2e}")  # 1.23e+09
    ```

    **Выравнивание и заполнение:**
    ```python
    text = "hi"
    print(f"{text:>10}")   # "        hi"
    print(f"{text:<10}")   # "hi        "
    print(f"{text:^10}")   # "    hi    "
    print(f"{text:*^10}")  # "****hi****"
    print(f"{text:0>10}")  # "00000000hi"
    ```

    **Вызов методов и выражения:**
    ```python
    name = "alice"
    print(f"{name.upper()}")  # ALICE
    print(f"{2 ** 10}")       # 1024
    print(f"{', '.join(['a', 'b', 'c'])}")  # a, b, c
    ```

    **Вложенные выражения для формата:**
    ```python
    width = 10
    precision = 2
    value = 3.14159
    print(f"{value:{width}.{precision}f}")  # "      3.14"
    ```

    **Дата и время:**
    ```python
    from datetime import datetime
    now = datetime.now()
    print(f"{now:%Y-%m-%d %H:%M:%S}")  # 2024-01-15 14:30:00
    print(f"{now:%A, %B %d}")          # Monday, January 15
    ```

---

11. **__slots__ — оптимизация памяти классов**

    По умолчанию Python хранит атрибуты экземпляра в `__dict__` — словаре. `__slots__` заменяет dict на фиксированный массив, экономя память.

    ```python
    class RegularUser:
        def __init__(self, name, email):
            self.name = name
            self.email = email

    class SlottedUser:
        __slots__ = ("name", "email")

        def __init__(self, name, email):
            self.name = name
            self.email = email

    # Сравнение памяти
    import sys
    regular = RegularUser("Alice", "alice@example.com")
    slotted = SlottedUser("Alice", "alice@example.com")

    print(sys.getsizeof(regular.__dict__))  # ~104 bytes
    # У slotted нет __dict__!
    ```

    **Экономия на большом количестве объектов:**
    ```python
    # При создании 1 миллиона объектов разница может составить сотни МБ
    ```

    **Ограничения __slots__:**
    ```python
    class SlottedUser:
        __slots__ = ("name", "email")

    user = SlottedUser("Alice", "alice@example.com")
    user.age = 30  # AttributeError: 'SlottedUser' object has no attribute 'age'

    # Нельзя динамически добавлять атрибуты
    ```

    **__slots__ с наследованием:**
    ```python
    class Base:
        __slots__ = ("x",)

    class Child(Base):
        __slots__ = ("y",)  # Добавляем только новые слоты

        def __init__(self):
            self.x = 1
            self.y = 2

    # Если Child не определит __slots__, у него появится __dict__
    ```

    **Когда использовать:**
    - Создаётся очень много экземпляров класса
    - Набор атрибутов фиксирован и известен заранее
    - Важна производительность и экономия памяти

    **Когда НЕ использовать:**
    - Нужны динамические атрибуты
    - Используется множественное наследование
    - Класс используется редко (преждевременная оптимизация)

    **Совмещение с dataclass (Python 3.10+):**
    ```python
    from dataclasses import dataclass

    @dataclass(slots=True)
    class Point:
        x: float
        y: float
    ```

---

12. **Protocol и structural subtyping (typing.Protocol)**

    `Protocol` позволяет описывать интерфейсы без наследования — достаточно, чтобы объект имел нужные методы/атрибуты (duck typing с проверкой типов).

    **Проблема без Protocol:**
    ```python
    # Как указать, что функция принимает "что-то с методом read()"?
    from typing import IO

    def process(f: IO[str]) -> str:  # Слишком строго — только файловые объекты
        return f.read()

    # StringIO работает, но mypy может ругаться
    from io import StringIO
    process(StringIO("hello"))
    ```

    **Решение с Protocol:**
    ```python
    from typing import Protocol

    class Readable(Protocol):
        def read(self) -> str: ...

    def process(f: Readable) -> str:
        return f.read()

    # Любой объект с методом read() -> str подходит
    class MyReader:
        def read(self) -> str:
            return "data"

    process(MyReader())  # OK — MyReader "реализует" Readable
    ```

    **Protocol с атрибутами:**
    ```python
    from typing import Protocol

    class Named(Protocol):
        name: str  # Атрибут должен присутствовать

    class HasLength(Protocol):
        def __len__(self) -> int: ...

    def greet(obj: Named) -> str:
        return f"Hello, {obj.name}"

    def show_length(obj: HasLength) -> None:
        print(f"Length: {len(obj)}")
    ```

    **runtime_checkable — проверка в runtime:**
    ```python
    from typing import Protocol, runtime_checkable

    @runtime_checkable
    class Closeable(Protocol):
        def close(self) -> None: ...

    file = open("test.txt")
    print(isinstance(file, Closeable))  # True

    class MyClass:
        pass

    print(isinstance(MyClass(), Closeable))  # False
    ```

    **Сравнение с ABC (Abstract Base Class):**

    | Аспект | Protocol | ABC |
    |--------|----------|-----|
    | Наследование | Не требуется | Требуется |
    | Проверка | Структурная (duck typing) | Номинальная |
    | Runtime isinstance | Только с @runtime_checkable | Всегда |
    | Подходит для | Внешних классов, которые нельзя изменить | Своей иерархии классов |

    ```python
    # ABC — класс ДОЛЖЕН явно наследоваться
    from abc import ABC, abstractmethod

    class Serializable(ABC):
        @abstractmethod
        def serialize(self) -> str: ...

    class User(Serializable):  # Обязательное наследование
        def serialize(self) -> str:
            return f"User(...)"

    # Protocol — наследование не нужно
    class SerializableProto(Protocol):
        def serialize(self) -> str: ...

    class Product:  # Не наследуется от Protocol
        def serialize(self) -> str:
            return f"Product(...)"

    def save(obj: SerializableProto) -> None:
        print(obj.serialize())

    save(Product())  # OK — Product имеет нужный метод
    ```

## 🟡 Concurrency — GIL, Async, Multiprocessing

_Параллелизм и конкурентность в Python._

13. **Что такое GIL и почему он есть в CPython?**

    **GIL (Global Interpreter Lock)** — это мьютекс, который позволяет только одному потоку выполнять Python байткод в любой момент времени.

    **Почему GIL существует:**
    - Упрощает реализацию CPython
    - Защищает внутренние структуры данных (reference counting)
    - Делает C-расширения проще и безопаснее

    **Как работает:**
    ```
    Thread 1: [выполняется]----[ждёт GIL]----[выполняется]----
    Thread 2: ----[ждёт GIL]----[выполняется]----[ждёт GIL]----
    Thread 3: ----[ждёт GIL]----[ждёт GIL]----[выполняется]----
    ```

    **GIL освобождается при:**
    - I/O операциях (чтение файла, сетевой запрос)
    - Вызове некоторых C-расширений (NumPy операции)
    - Явном вызове `time.sleep()`

    **Демонстрация проблемы:**
    ```python
    import threading
    import time

    def cpu_bound():
        count = 0
        for _ in range(10_000_000):
            count += 1

    # Однопоточно
    start = time.perf_counter()
    cpu_bound()
    cpu_bound()
    print(f"Sequential: {time.perf_counter() - start:.2f}s")

    # Многопоточно — НЕ быстрее из-за GIL!
    start = time.perf_counter()
    t1 = threading.Thread(target=cpu_bound)
    t2 = threading.Thread(target=cpu_bound)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"Threaded: {time.perf_counter() - start:.2f}s")

    # Результат: оба варианта примерно одинаковы!
    ```

    **Альтернативы GIL:**
    - PyPy — имеет STM (Software Transactional Memory)
    - Jython, IronPython — нет GIL
    - Python 3.13+ — экспериментальный режим без GIL (`--disable-gil`)

---

14. **I/O-bound vs CPU-bound задачи: когда GIL не мешает?**

    **CPU-bound** — задачи, ограниченные вычислительной мощностью:
    - Математические расчёты
    - Обработка изображений
    - Шифрование
    - Парсинг больших данных

    **I/O-bound** — задачи, ограниченные операциями ввода-вывода:
    - Сетевые запросы (HTTP, DB)
    - Чтение/запись файлов
    - Ожидание пользовательского ввода

    **Почему GIL не мешает I/O-bound:**
    ```python
    # При I/O операции GIL освобождается
    import threading
    import requests
    import time

    urls = ["https://api.github.com"] * 10

    def fetch(url):
        requests.get(url)

    # Последовательно — медленно
    start = time.perf_counter()
    for url in urls:
        fetch(url)
    print(f"Sequential: {time.perf_counter() - start:.2f}s")  # ~5s

    # Параллельно — быстрее!
    start = time.perf_counter()
    threads = [threading.Thread(target=fetch, args=(url,)) for url in urls]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"Threaded: {time.perf_counter() - start:.2f}s")  # ~0.5s
    ```

    **Выбор инструмента:**

    | Тип задачи | Threading | Multiprocessing | Asyncio |
    |------------|-----------|-----------------|---------|
    | CPU-bound | Нет | Да | Нет |
    | I/O-bound (много соединений) | Да | Избыточно | Да (лучший выбор) |
    | I/O-bound (мало соединений) | Да | Избыточно | Да |
    | Смешанный | Нет | Да | С осторожностью |

---

15. **Threading: когда использовать и ограничения**

    `threading` — модуль для создания потоков. Потоки разделяют память процесса.

    **Базовое использование:**
    ```python
    import threading

    def worker(name: str, count: int) -> None:
        for i in range(count):
            print(f"{name}: {i}")

    # Создание и запуск потоков
    t1 = threading.Thread(target=worker, args=("Thread-1", 5))
    t2 = threading.Thread(target=worker, args=("Thread-2", 5))

    t1.start()
    t2.start()

    t1.join()  # Ждём завершения
    t2.join()
    ```

    **Thread как класс:**
    ```python
    class DownloadThread(threading.Thread):
        def __init__(self, url: str):
            super().__init__()
            self.url = url
            self.result = None

        def run(self):
            import requests
            response = requests.get(self.url)
            self.result = response.text

    thread = DownloadThread("https://example.com")
    thread.start()
    thread.join()
    print(thread.result)
    ```

    **Daemon threads:**
    ```python
    # Daemon-поток завершается вместе с основной программой
    t = threading.Thread(target=background_task, daemon=True)
    t.start()
    # Если main завершится, daemon-поток будет убит
    ```

    **Проблемы threading:**
    ```python
    # Race condition — гонка данных
    counter = 0

    def increment():
        global counter
        for _ in range(100_000):
            counter += 1  # Не атомарная операция!

    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(counter)  # Ожидаем 1_000_000, получаем меньше!
    ```

    **Когда использовать threading:**
    - I/O-bound задачи с небольшим количеством потоков
    - Когда нужна общая память между задачами
    - Простые фоновые задачи

    **Когда НЕ использовать:**
    - CPU-bound задачи (из-за GIL)
    - Большое количество конкурентных задач (лучше asyncio)

---

16. **Multiprocessing: обход GIL для CPU-bound задач**

    `multiprocessing` создаёт отдельные процессы, каждый со своим GIL и памятью.

    **Базовое использование:**
    ```python
    from multiprocessing import Process, cpu_count

    def cpu_intensive(n: int) -> int:
        return sum(i * i for i in range(n))

    if __name__ == "__main__":  # Обязательно на Windows!
        processes = []
        for i in range(cpu_count()):
            p = Process(target=cpu_intensive, args=(10_000_000,))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
    ```

    **Pool — пул процессов:**
    ```python
    from multiprocessing import Pool

    def square(x: int) -> int:
        return x * x

    if __name__ == "__main__":
        with Pool(processes=4) as pool:
            # map — применить функцию к каждому элементу
            results = pool.map(square, range(10))
            print(results)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

            # starmap — для функций с несколькими аргументами
            def add(a, b):
                return a + b
            results = pool.starmap(add, [(1, 2), (3, 4), (5, 6)])
    ```

    **Обмен данными между процессами:**
    ```python
    from multiprocessing import Process, Queue, Value, Array

    # Queue — очередь для передачи данных
    def producer(q: Queue):
        for i in range(5):
            q.put(i)
        q.put(None)  # Сигнал завершения

    def consumer(q: Queue):
        while True:
            item = q.get()
            if item is None:
                break
            print(f"Got: {item}")

    # Value и Array — разделяемая память
    def increment_shared(counter: Value):
        for _ in range(1000):
            with counter.get_lock():
                counter.value += 1

    if __name__ == "__main__":
        counter = Value('i', 0)  # 'i' = integer
        processes = [Process(target=increment_shared, args=(counter,)) for _ in range(4)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        print(counter.value)  # 4000
    ```

    **Сравнение с threading:**

    | Аспект | Threading | Multiprocessing |
    |--------|-----------|-----------------|
    | GIL | Ограничивает | Обходит |
    | Память | Общая | Изолированная |
    | Накладные расходы | Низкие | Высокие |
    | Обмен данными | Простой | Сложный (сериализация) |
    | Подходит для | I/O-bound | CPU-bound |

---

17. **Asyncio: event loop, корутины, tasks**

    `asyncio` — библиотека для асинхронного программирования на основе event loop.

    **Корутина (coroutine):**
    ```python
    import asyncio

    async def fetch_data(url: str) -> str:
        print(f"Start fetching {url}")
        await asyncio.sleep(1)  # Имитация I/O
        print(f"Done fetching {url}")
        return f"Data from {url}"

    # Запуск корутины
    async def main():
        result = await fetch_data("https://example.com")
        print(result)

    asyncio.run(main())
    ```

    **Task — обёртка для конкурентного выполнения:**
    ```python
    async def main():
        # Создаём tasks для параллельного выполнения
        task1 = asyncio.create_task(fetch_data("url1"))
        task2 = asyncio.create_task(fetch_data("url2"))

        # Ждём завершения обоих
        result1 = await task1
        result2 = await task2

        # Или используем gather
        results = await asyncio.gather(
            fetch_data("url1"),
            fetch_data("url2"),
            fetch_data("url3"),
        )
    ```

    **Event Loop — сердце asyncio:**
    ```
    Event Loop работает в одном потоке:
    1. Проверяет очередь готовых задач
    2. Выполняет задачу до первого await
    3. При await регистрирует callback и переключается на другую задачу
    4. Когда I/O готов — задача возвращается в очередь
    ```

    **Низкоуровневый доступ к event loop:**
    ```python
    async def main():
        loop = asyncio.get_running_loop()

        # Запуск блокирующего кода в thread pool
        result = await loop.run_in_executor(
            None,  # default executor
            blocking_function,
            arg1, arg2
        )
    ```

    **Частые ошибки:**
    ```python
    # НЕПРАВИЛЬНО — блокирует event loop
    async def bad():
        time.sleep(1)  # Блокирующий вызов!
        requests.get(url)  # Блокирующий вызов!

    # ПРАВИЛЬНО
    async def good():
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
            await session.get(url)
    ```

---

18. **async/await и асинхронные контекстные менеджеры**

    **Асинхронные контекстные менеджеры:**
    ```python
    class AsyncResource:
        async def __aenter__(self):
            print("Acquiring resource...")
            await asyncio.sleep(0.1)
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print("Releasing resource...")
            await asyncio.sleep(0.1)

    async def main():
        async with AsyncResource() as resource:
            print("Using resource")
    ```

    **contextlib для async:**
    ```python
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def async_timer(label: str):
        import time
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            print(f"{label}: {elapsed:.4f}s")

    async def main():
        async with async_timer("Operation"):
            await asyncio.sleep(1)
    ```

    **Асинхронные итераторы:**
    ```python
    class AsyncCounter:
        def __init__(self, stop: int):
            self.stop = stop
            self.current = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.current >= self.stop:
                raise StopAsyncIteration
            await asyncio.sleep(0.1)
            self.current += 1
            return self.current

    async def main():
        async for num in AsyncCounter(5):
            print(num)
    ```

    **Async comprehensions:**
    ```python
    # Async list comprehension
    results = [x async for x in async_generator()]

    # Async generator expression
    gen = (x async for x in async_generator())

    # С условием
    filtered = [x async for x in async_generator() if x > 0]
    ```

---

19. **asyncio.gather vs asyncio.TaskGroup (Python 3.11+)**

    **asyncio.gather:**
    ```python
    async def main():
        results = await asyncio.gather(
            fetch("url1"),
            fetch("url2"),
            fetch("url3"),
            return_exceptions=True  # Не прерывать при ошибке
        )
        # results = [result1, result2, result3] или Exception объект
    ```

    **Проблема gather — отмена задач:**
    ```python
    async def main():
        try:
            results = await asyncio.gather(
                task_that_succeeds(),
                task_that_fails(),  # Выбросит исключение
                task_that_succeeds(),
            )
        except Exception:
            # Другие задачи НЕ отменяются автоматически!
            pass
    ```

    **TaskGroup (Python 3.11+) — лучшая альтернатива:**
    ```python
    async def main():
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(fetch("url1"))
            task2 = tg.create_task(fetch("url2"))
            task3 = tg.create_task(fetch("url3"))

        # После выхода из with все задачи гарантированно завершены
        print(task1.result(), task2.result(), task3.result())
    ```

    **Преимущества TaskGroup:**
    ```python
    async def main():
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(task_that_succeeds())
                tg.create_task(task_that_fails())
                tg.create_task(task_that_succeeds())
        except* ValueError as eg:  # except* для ExceptionGroup (Python 3.11+)
            # Все задачи автоматически отменяются при ошибке
            for exc in eg.exceptions:
                print(f"Error: {exc}")
    ```

    **Сравнение:**

    | Аспект | gather | TaskGroup |
    |--------|--------|-----------|
    | Отмена при ошибке | Нет | Да |
    | Структурированный вывод | Нет | Да |
    | Обработка ошибок | return_exceptions | except* |
    | Python версия | 3.4+ | 3.11+ |

---

20. **concurrent.futures: ThreadPoolExecutor и ProcessPoolExecutor**

    `concurrent.futures` — высокоуровневый API для параллельного выполнения.

    **ThreadPoolExecutor:**
    ```python
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import requests

    urls = ["https://example.com", "https://python.org", "https://github.com"]

    def fetch(url: str) -> str:
        return requests.get(url).text[:100]

    # Как контекстный менеджер
    with ThreadPoolExecutor(max_workers=5) as executor:
        # submit — запустить одну задачу
        future = executor.submit(fetch, urls[0])
        result = future.result()  # Блокирующее ожидание

        # map — применить к коллекции
        results = list(executor.map(fetch, urls))

        # as_completed — обрабатывать по мере готовности
        futures = [executor.submit(fetch, url) for url in urls]
        for future in as_completed(futures):
            print(future.result())
    ```

    **ProcessPoolExecutor:**
    ```python
    from concurrent.futures import ProcessPoolExecutor

    def cpu_heavy(n: int) -> int:
        return sum(i * i for i in range(n))

    if __name__ == "__main__":
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(cpu_heavy, [10**6] * 4))
    ```

    **Future объект:**
    ```python
    from concurrent.futures import ThreadPoolExecutor, Future

    def task() -> str:
        return "result"

    with ThreadPoolExecutor() as executor:
        future: Future = executor.submit(task)

        future.done()      # Завершена ли задача
        future.running()   # Выполняется ли сейчас
        future.cancelled() # Была ли отменена
        future.result(timeout=5)  # Получить результат
        future.exception()  # Получить исключение (если было)
        future.cancel()     # Попытаться отменить

        # Callback при завершении
        future.add_done_callback(lambda f: print(f.result()))
    ```

    **Интеграция с asyncio:**
    ```python
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    def blocking_io():
        import time
        time.sleep(1)
        return "done"

    async def main():
        loop = asyncio.get_running_loop()

        # Запуск блокирующей функции в thread pool
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, blocking_io)
            print(result)

    asyncio.run(main())
    ```

---

21. **Синхронизация: Lock, Semaphore, Event, Condition**

    **Lock — взаимное исключение:**
    ```python
    import threading

    counter = 0
    lock = threading.Lock()

    def safe_increment():
        global counter
        for _ in range(100_000):
            with lock:  # Только один поток может войти
                counter += 1

    # RLock — реентерабельный lock (можно захватить несколько раз из одного потока)
    rlock = threading.RLock()
    ```

    **Semaphore — ограничение количества потоков:**
    ```python
    # Максимум 3 потока одновременно
    semaphore = threading.Semaphore(3)

    def limited_resource():
        with semaphore:
            print(f"{threading.current_thread().name} acquired")
            time.sleep(1)
        print(f"{threading.current_thread().name} released")

    # BoundedSemaphore — не позволяет release() больше раз, чем acquire()
    bounded = threading.BoundedSemaphore(3)
    ```

    **Event — сигнализация между потоками:**
    ```python
    event = threading.Event()

    def waiter():
        print("Waiting for event...")
        event.wait()  # Блокируется пока event не установлен
        print("Event received!")

    def setter():
        time.sleep(2)
        print("Setting event")
        event.set()  # Пробуждает всех ждущих

    # event.clear() — сбросить флаг
    # event.is_set() — проверить состояние
    ```

    **Condition — ожидание с условием:**
    ```python
    condition = threading.Condition()
    items = []

    def producer():
        for i in range(5):
            with condition:
                items.append(i)
                condition.notify()  # Пробудить одного consumer
            time.sleep(0.1)

    def consumer():
        while True:
            with condition:
                while not items:  # Проверяем условие в цикле!
                    condition.wait()  # Освобождает lock и ждёт
                item = items.pop(0)
                print(f"Consumed: {item}")
    ```

    **Asyncio версии:**
    ```python
    import asyncio

    lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(3)
    event = asyncio.Event()
    condition = asyncio.Condition()

    async def with_lock():
        async with lock:
            await do_something()
    ```

---

22. **Race conditions и deadlocks: примеры и решения**

    **Race condition — гонка данных:**
    ```python
    # Проблема: неатомарная операция
    balance = 100

    def withdraw(amount):
        global balance
        if balance >= amount:  # Проверка
            time.sleep(0.001)  # Между проверкой и изменением может вклиниться другой поток
            balance -= amount  # Изменение
        return balance

    # Два потока одновременно снимают по 100
    # Оба проходят проверку (balance >= 100)
    # balance становится -100 вместо ошибки
    ```

    **Решение — Lock:**
    ```python
    lock = threading.Lock()

    def safe_withdraw(amount):
        global balance
        with lock:
            if balance >= amount:
                balance -= amount
                return True
        return False
    ```

    **Deadlock — взаимная блокировка:**
    ```python
    lock_a = threading.Lock()
    lock_b = threading.Lock()

    def thread_1():
        with lock_a:
            time.sleep(0.1)
            with lock_b:  # Ждёт lock_b
                print("Thread 1")

    def thread_2():
        with lock_b:
            time.sleep(0.1)
            with lock_a:  # Ждёт lock_a
                print("Thread 2")

    # Deadlock! Thread 1 держит lock_a и ждёт lock_b
    #           Thread 2 держит lock_b и ждёт lock_a
    ```

    **Решения deadlock:**
    ```python
    # 1. Всегда захватывать locks в одном порядке
    def thread_safe():
        with lock_a:
            with lock_b:
                do_work()

    # 2. Использовать timeout
    if lock_a.acquire(timeout=1):
        try:
            if lock_b.acquire(timeout=1):
                try:
                    do_work()
                finally:
                    lock_b.release()
        finally:
            lock_a.release()

    # 3. Использовать RLock для рекурсивных вызовов
    rlock = threading.RLock()
    ```

---

23. **Async generators и async comprehensions**

    **Async generator:**
    ```python
    async def async_range(start: int, stop: int):
        for i in range(start, stop):
            await asyncio.sleep(0.1)
            yield i

    async def main():
        async for num in async_range(0, 5):
            print(num)
    ```

    **Практический пример — streaming данных:**
    ```python
    async def fetch_pages(urls: list[str]):
        async with aiohttp.ClientSession() as session:
            for url in urls:
                async with session.get(url) as response:
                    yield await response.text()

    async def main():
        urls = ["https://example.com/1", "https://example.com/2"]
        async for page in fetch_pages(urls):
            process(page)
    ```

    **Async comprehensions:**
    ```python
    async def main():
        # Async list comprehension
        results = [x async for x in async_range(0, 10)]

        # С await внутри обычного comprehension
        tasks = [fetch(url) for url in urls]
        results = [await task for task in tasks]  # Последовательно!

        # Параллельно нужно через gather
        results = await asyncio.gather(*[fetch(url) for url in urls])
    ```

    **asend и athrow:**
    ```python
    async def async_accumulator():
        total = 0
        while True:
            value = yield total
            if value is not None:
                total += value

    async def main():
        acc = async_accumulator()
        await acc.asend(None)  # Инициализация
        print(await acc.asend(10))  # 10
        print(await acc.asend(20))  # 30
    ```

---

24. **Сравнение подходов: когда что выбрать?**

    **Таблица выбора:**

    | Сценарий | Threading | Multiprocessing | Asyncio |
    |----------|-----------|-----------------|---------|
    | HTTP запросы (много) | - | - | Лучший выбор |
    | HTTP запросы (мало) | OK | - | OK |
    | CPU-intensive | Нет | Лучший выбор | Нет |
    | Работа с файлами | OK | - | OK |
    | GUI приложения | Для фоновых задач | - | - |
    | WebSocket | - | - | Лучший выбор |
    | Простой параллелизм | OK | OK | Сложнее |

    **Asyncio — когда использовать:**
    ```python
    # Тысячи одновременных соединений
    async def handle_many_clients():
        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, url) for url in urls]  # 10000 urls
            await asyncio.gather(*tasks)
    ```

    **Threading — когда использовать:**
    ```python
    # Простые фоновые задачи, интеграция с sync кодом
    def background_logger():
        while True:
            log_queue.get()
            write_to_file()

    thread = threading.Thread(target=background_logger, daemon=True)
    thread.start()
    ```

    **Multiprocessing — когда использовать:**
    ```python
    # Параллельная обработка данных
    def process_chunk(data):
        return heavy_computation(data)

    with Pool(cpu_count()) as pool:
        results = pool.map(process_chunk, data_chunks)
    ```

    **Комбинирование подходов:**
    ```python
    # Asyncio + ThreadPoolExecutor для блокирующих вызовов
    async def main():
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            # Блокирующая библиотека в отдельном потоке
            result = await loop.run_in_executor(pool, blocking_library_call)

    # Asyncio + ProcessPoolExecutor для CPU-bound в async контексте
    async def main():
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, cpu_intensive_task)
    ```

## 🟡 Алгоритмическая сложность — Big O

_Оценка производительности алгоритмов._

25. **Что такое Big O notation и зачем она нужна?**

    **Big O** описывает верхнюю границу роста времени выполнения или памяти алгоритма относительно размера входных данных.

    **Зачем нужна:**
    - Сравнение алгоритмов независимо от железа
    - Предсказание поведения на больших данных
    - Выбор правильной структуры данных

    **Основные классы сложности:**
    ```
    O(1)       — константная (доступ к элементу массива)
    O(log n)   — логарифмическая (бинарный поиск)
    O(n)       — линейная (проход по списку)
    O(n log n) — линейно-логарифмическая (хорошие сортировки)
    O(n²)      — квадратичная (вложенные циклы)
    O(2^n)     — экспоненциальная (полный перебор)
    O(n!)      — факториальная (перестановки)
    ```

    **Визуализация роста:**
    ```
    n = 10:
    O(1)       = 1
    O(log n)   = 3
    O(n)       = 10
    O(n log n) = 30
    O(n²)      = 100
    O(2^n)     = 1024

    n = 1000:
    O(1)       = 1
    O(log n)   = 10
    O(n)       = 1,000
    O(n log n) = 10,000
    O(n²)      = 1,000,000
    O(2^n)     = больше атомов во Вселенной
    ```

    **Правила упрощения:**
    ```python
    # Отбрасываем константы
    O(2n) → O(n)
    O(n/2) → O(n)

    # Отбрасываем младшие члены
    O(n² + n) → O(n²)
    O(n + log n) → O(n)

    # Умножение для вложенных операций
    O(n) * O(n) = O(n²)
    ```

---

26. **Примеры разных классов сложности**

    **O(1) — константное время:**
    ```python
    def get_first(lst: list) -> any:
        return lst[0]  # Доступ по индексу

    def dict_lookup(d: dict, key: str) -> any:
        return d[key]  # Хэш-таблица

    def check_even(n: int) -> bool:
        return n % 2 == 0  # Арифметическая операция
    ```

    **O(log n) — логарифмическое:**
    ```python
    def binary_search(arr: list, target: int) -> int:
        left, right = 0, len(arr) - 1
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return -1
    # На каждом шаге отбрасываем половину данных
    ```

    **O(n) — линейное:**
    ```python
    def find_max(arr: list) -> int:
        max_val = arr[0]
        for num in arr:  # Один проход
            if num > max_val:
                max_val = num
        return max_val

    def sum_list(arr: list) -> int:
        return sum(arr)  # sum() — O(n)
    ```

    **O(n log n) — линейно-логарифмическое:**
    ```python
    def merge_sort(arr: list) -> list:
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = merge_sort(arr[:mid])   # log n уровней
        right = merge_sort(arr[mid:])  # рекурсии
        return merge(left, right)      # O(n) на каждом уровне

    # sorted() в Python использует Timsort — O(n log n)
    ```

    **O(n²) — квадратичное:**
    ```python
    def bubble_sort(arr: list) -> list:
        n = len(arr)
        for i in range(n):          # n итераций
            for j in range(n - 1):  # n итераций
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

    def find_pairs(arr: list) -> list:
        pairs = []
        for i in range(len(arr)):
            for j in range(len(arr)):
                pairs.append((arr[i], arr[j]))
        return pairs
    ```

    **O(2^n) — экспоненциальное:**
    ```python
    def fibonacci_naive(n: int) -> int:
        if n <= 1:
            return n
        return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)
    # Дерево вызовов растёт экспоненциально

    def all_subsets(arr: list) -> list:
        if not arr:
            return [[]]
        rest = all_subsets(arr[1:])
        return rest + [[arr[0]] + s for s in rest]
    # 2^n подмножеств
    ```

---

27. **Временная vs пространственная сложность**

    **Временная сложность** — как растёт время выполнения.
    **Пространственная сложность** — как растёт потребление памяти.

    **Пример — разные компромиссы:**
    ```python
    # O(1) память, O(n²) время
    def has_duplicate_v1(arr: list) -> bool:
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if arr[i] == arr[j]:
                    return True
        return False

    # O(n) память, O(n) время
    def has_duplicate_v2(arr: list) -> bool:
        seen = set()  # Дополнительная память
        for item in arr:
            if item in seen:
                return True
            seen.add(item)
        return False
    ```

    **Анализ рекурсии:**
    ```python
    def factorial(n: int) -> int:
        if n <= 1:
            return 1
        return n * factorial(n - 1)

    # Время: O(n) — n вызовов
    # Память: O(n) — глубина стека вызовов
    ```

    **In-place алгоритмы:**
    ```python
    # O(n) дополнительной памяти
    def reverse_v1(arr: list) -> list:
        return arr[::-1]  # Создаёт новый список

    # O(1) дополнительной памяти (in-place)
    def reverse_v2(arr: list) -> None:
        left, right = 0, len(arr) - 1
        while left < right:
            arr[left], arr[right] = arr[right], arr[left]
            left += 1
            right -= 1
    ```

    **Таблица компромиссов:**

    | Структура | Доступ | Поиск | Вставка | Память |
    |-----------|--------|-------|---------|--------|
    | list | O(1) | O(n) | O(n)* | O(n) |
    | dict | O(1) | O(1) | O(1) | O(n) |
    | set | — | O(1) | O(1) | O(n) |
    | sorted list + binary search | O(1) | O(log n) | O(n) | O(n) |

---

28. **Сложность операций list**

    ```python
    lst = [1, 2, 3, 4, 5]
    ```

    | Операция | Сложность | Пояснение |
    |----------|-----------|-----------|
    | `lst[i]` | O(1) | Прямой доступ по индексу |
    | `lst[i] = x` | O(1) | Прямая запись |
    | `lst.append(x)` | O(1)* | Амортизированная |
    | `lst.pop()` | O(1) | Удаление с конца |
    | `lst.pop(i)` | O(n) | Сдвиг элементов |
    | `lst.insert(i, x)` | O(n) | Сдвиг элементов |
    | `lst.remove(x)` | O(n) | Поиск + сдвиг |
    | `x in lst` | O(n) | Линейный поиск |
    | `lst.index(x)` | O(n) | Линейный поиск |
    | `len(lst)` | O(1) | Хранится как атрибут |
    | `lst.sort()` | O(n log n) | Timsort |
    | `lst + other` | O(n + m) | Создание нового списка |
    | `lst * k` | O(n * k) | Копирование |
    | `lst[a:b]` | O(b - a) | Копирование среза |

    **Почему append O(1) амортизированно:**
    ```python
    # Python выделяет память с запасом
    # Когда список заполнен — перевыделение в ~1.125 раза больше
    # Большинство append — O(1), редкие — O(n)
    # В среднем (амортизированно) — O(1)
    ```

    **Подводные камни:**
    ```python
    # Это O(n²)!
    result = []
    for item in items:
        result = result + [item]  # Каждый раз новый список

    # Это O(n)
    result = []
    for item in items:
        result.append(item)  # In-place добавление
    ```

---

29. **Сложность операций dict и set**

    **dict:**
    ```python
    d = {"a": 1, "b": 2}
    ```

    | Операция | Average | Worst | Пояснение |
    |----------|---------|-------|-----------|
    | `d[key]` | O(1) | O(n) | Хэш-коллизии |
    | `d[key] = value` | O(1) | O(n) | |
    | `del d[key]` | O(1) | O(n) | |
    | `key in d` | O(1) | O(n) | |
    | `len(d)` | O(1) | O(1) | |
    | `d.keys()` | O(1) | O(1) | View object |
    | `list(d.keys())` | O(n) | O(n) | Копирование |
    | `d.get(key)` | O(1) | O(n) | |
    | `d.pop(key)` | O(1) | O(n) | |

    **set:**
    ```python
    s = {1, 2, 3}
    ```

    | Операция | Average | Worst |
    |----------|---------|-------|
    | `x in s` | O(1) | O(n) |
    | `s.add(x)` | O(1) | O(n) |
    | `s.remove(x)` | O(1) | O(n) |
    | `s \| other` (union) | O(n + m) | |
    | `s & other` (intersection) | O(min(n, m)) | |
    | `s - other` (difference) | O(n) | |

    **Практический пример:**
    ```python
    # Поиск дубликатов

    # O(n²) — плохо
    def has_dup_slow(lst):
        for i, x in enumerate(lst):
            if x in lst[i+1:]:  # O(n) на каждой итерации
                return True
        return False

    # O(n) — хорошо
    def has_dup_fast(lst):
        return len(lst) != len(set(lst))  # set создаётся за O(n)
    ```

---

30. **Timsort: как работает сортировка в Python**

    **Timsort** — гибридный алгоритм, комбинирующий merge sort и insertion sort. Создан Тимом Петерсом для Python.

    **Характеристики:**
    - Время: O(n log n) worst/average, O(n) best
    - Память: O(n)
    - Стабильный (сохраняет порядок равных элементов)

    **Как работает:**
    1. Разбивает массив на "runs" — уже отсортированные подпоследовательности
    2. Короткие runs расширяются insertion sort (эффективен на малых данных)
    3. Runs сливаются merge sort

    **Почему быстр на реальных данных:**
    ```python
    # Частично отсортированные данные — O(n)
    almost_sorted = list(range(1000))
    almost_sorted[500], almost_sorted[501] = almost_sorted[501], almost_sorted[500]
    sorted(almost_sorted)  # Очень быстро

    # Конкатенация отсортированных списков — O(n)
    a = list(range(0, 500))
    b = list(range(500, 1000))
    sorted(a + b)  # Два "run" — одно слияние
    ```

    **Стабильность:**
    ```python
    data = [("Alice", 30), ("Bob", 25), ("Charlie", 30)]

    # Сортировка по возрасту — порядок Alice и Charlie сохранится
    sorted(data, key=lambda x: x[1])
    # [('Bob', 25), ('Alice', 30), ('Charlie', 30)]
    ```

    **Сравнение с другими алгоритмами:**

    | Алгоритм | Best | Average | Worst | Стабильный |
    |----------|------|---------|-------|------------|
    | Timsort | O(n) | O(n log n) | O(n log n) | Да |
    | Quicksort | O(n log n) | O(n log n) | O(n²) | Нет |
    | Mergesort | O(n log n) | O(n log n) | O(n log n) | Да |
    | Heapsort | O(n log n) | O(n log n) | O(n log n) | Нет |

---

31. **Амортизированная сложность**

    **Амортизированный анализ** рассматривает среднюю стоимость операции за длинную последовательность операций.

    **Пример: list.append()**
    ```python
    # Большинство append — O(1)
    # Изредка — O(n) при перевыделении памяти
    # Амортизированно — O(1)

    # Последовательность из n операций append:
    # Всего операций копирования: n + n/2 + n/4 + ... ≈ 2n
    # На одну операцию: 2n / n = O(1)
    ```

    **Динамический массив:**
    ```
    Capacity: 1 → 2 → 4 → 8 → 16 → ...

    append() при capacity=4, size=4:
    1. Выделить память на 8 элементов — O(1)
    2. Скопировать 4 элемента — O(4)
    3. Добавить новый элемент — O(1)

    Но такие "дорогие" операции редки!
    ```

    **Пример: dict**
    ```python
    # Средняя сложность операций — O(1)
    # Но при rehashing (когда таблица заполнена) — O(n)
    # Амортизированно — O(1)
    ```

    **Когда важно различать:**
    ```python
    # Для real-time систем амортизированная O(1) может быть проблемой
    # Иногда операция занимает O(n) — latency spike

    # Для большинства приложений амортизированная сложность — OK
    ```

---

32. **Как анализировать сложность своего кода**

    **Правила анализа:**

    1. **Последовательные операции — складываем:**
    ```python
    def process(arr):
        total = sum(arr)      # O(n)
        sorted_arr = sorted(arr)  # O(n log n)
        return total, sorted_arr
    # O(n) + O(n log n) = O(n log n)
    ```

    2. **Вложенные циклы — умножаем:**
    ```python
    def nested(arr):
        for i in arr:           # O(n)
            for j in arr:       # O(n)
                print(i, j)
    # O(n) * O(n) = O(n²)
    ```

    3. **Условия — берём худший случай:**
    ```python
    def conditional(arr, flag):
        if flag:
            return sum(arr)     # O(n)
        else:
            return sorted(arr)  # O(n log n)
    # O(n log n)
    ```

    4. **Рекурсия — считаем вызовы × работу на вызов:**
    ```python
    def binary_search(arr, target, left, right):
        if left > right:
            return -1
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            return binary_search(arr, target, mid + 1, right)
        else:
            return binary_search(arr, target, left, mid - 1)

    # log n вызовов, O(1) работы на вызов → O(log n)
    ```

    **Частые паттерны:**
    ```python
    # Один цикл по данным — O(n)
    for x in data: ...

    # Цикл с делением пополам — O(log n)
    while n > 0:
        n //= 2

    # Вложенный цикл — O(n²)
    for i in range(n):
        for j in range(n): ...

    # Сортировка + линейный проход — O(n log n)
    sorted_data = sorted(data)
    for x in sorted_data: ...
    ```

---

33. **Best/Average/Worst case**

    **Quicksort — классический пример:**
    ```python
    # Best case: O(n log n) — pivot всегда делит пополам
    # Average case: O(n log n)
    # Worst case: O(n²) — уже отсортированный массив, плохой pivot
    ```

    **Hash table:**
    ```python
    # Best/Average: O(1) — хорошая хэш-функция
    # Worst: O(n) — все ключи коллизируют
    ```

    **Бинарное дерево поиска:**
    ```python
    # Best/Average: O(log n) — сбалансированное дерево
    # Worst: O(n) — вырожденное в список
    ```

    **Когда важен worst case:**
    - Безопасность (DoS через hash collision)
    - Real-time системы
    - Критичные операции

    ```python
    # Python dict защищён от hash collision attacks
    # Использует рандомизацию хэша (PYTHONHASHSEED)
    ```

---

34. **Trade-offs: время vs память**

    **Пример 1: Кэширование vs пересчёт:**
    ```python
    # Больше памяти, меньше времени
    @functools.cache
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    # Время: O(n), Память: O(n)

    # Меньше памяти, больше времени (без кэша)
    def fibonacci_slow(n):
        if n < 2:
            return n
        return fibonacci_slow(n - 1) + fibonacci_slow(n - 2)
    # Время: O(2^n), Память: O(n) стек
    ```

    **Пример 2: Предвычисление:**
    ```python
    # Быстрый lookup, много памяти
    squares = {i: i**2 for i in range(10000)}
    result = squares[42]  # O(1)

    # Медленный расчёт, мало памяти
    result = 42 ** 2  # O(1), но может быть медленнее
    ```

    **Пример 3: Индексы:**
    ```python
    # Без индекса
    users = [{"id": 1, "name": "Alice"}, ...]
    def find_user(user_id):
        for u in users:  # O(n)
            if u["id"] == user_id:
                return u

    # С индексом (дополнительная память)
    users_by_id = {u["id"]: u for u in users}  # O(n) память
    def find_user(user_id):
        return users_by_id.get(user_id)  # O(1)
    ```

---

35. **Collections: сложность операций**

    **deque (двусторонняя очередь):**
    ```python
    from collections import deque

    d = deque([1, 2, 3])
    ```

    | Операция | Сложность |
    |----------|-----------|
    | `d.append(x)` | O(1) |
    | `d.appendleft(x)` | O(1) |
    | `d.pop()` | O(1) |
    | `d.popleft()` | O(1) |
    | `d[i]` | O(n) |
    | `len(d)` | O(1) |

    ```python
    # list.insert(0, x) — O(n)
    # deque.appendleft(x) — O(1)
    ```

    **Counter:**
    ```python
    from collections import Counter

    c = Counter([1, 1, 2, 3, 3, 3])
    ```

    | Операция | Сложность |
    |----------|-----------|
    | Создание | O(n) |
    | `c[key]` | O(1) |
    | `c.most_common(k)` | O(n log k) |
    | `c.update(iterable)` | O(m) |

    **defaultdict:**
    ```python
    from collections import defaultdict

    d = defaultdict(list)
    d["key"].append(1)  # Не нужно проверять существование
    ```

    Все операции как у обычного dict — O(1) average.

---

36. **Когда O(n²) допустимо?**

    **Допустимо когда:**
    ```python
    # 1. Малый размер данных (n < 100)
    def sort_small_list(lst):
        # Простой bubble sort быстрее на маленьких данных
        # из-за меньшего overhead
        for i in range(len(lst)):
            for j in range(len(lst) - 1):
                if lst[j] > lst[j + 1]:
                    lst[j], lst[j + 1] = lst[j + 1], lst[j]

    # 2. Код выполняется редко
    def daily_report(users):  # Запускается раз в день
        # O(n²) на 1000 пользователей — не проблема
        pass

    # 3. n гарантированно мало по бизнес-логике
    def process_user_roles(roles):  # У пользователя < 10 ролей
        for r1 in roles:
            for r2 in roles:
                check_conflict(r1, r2)
    ```

    **НЕ допустимо когда:**
    ```python
    # 1. n может расти неограниченно
    def process_all_orders(orders):  # Миллионы заказов
        for o1 in orders:
            for o2 in orders:  # ПЛОХО!
                ...

    # 2. Код в hot path (вызывается часто)
    def validate_request(data):  # Каждый HTTP запрос
        # O(n²) недопустимо
        pass

    # 3. Real-time требования
    def handle_game_frame():  # 60 FPS = 16ms на кадр
        # O(n²) может сломать timing
        pass
    ```

    **Порог:**
    ```
    n = 100:    O(n²) = 10,000 операций — ОК
    n = 1,000:  O(n²) = 1,000,000 операций — начинает тормозить
    n = 10,000: O(n²) = 100,000,000 операций — неприемлемо
    ```

## 🟠 Рекурсия и Функциональное программирование

_Альтернативные подходы к решению задач._

37. **Рекурсия: базовый случай, рекурсивный случай, стек вызовов**

    **Структура рекурсивной функции:**
    ```python
    def factorial(n: int) -> int:
        # Базовый случай — условие остановки
        if n <= 1:
            return 1
        # Рекурсивный случай — вызов самой себя
        return n * factorial(n - 1)
    ```

    **Стек вызовов:**
    ```python
    factorial(4)
    → 4 * factorial(3)
    → 4 * (3 * factorial(2))
    → 4 * (3 * (2 * factorial(1)))
    → 4 * (3 * (2 * 1))
    → 4 * (3 * 2)
    → 4 * 6
    → 24
    ```

    **Важные принципы:**
    1. Базовый случай обязателен (иначе бесконечная рекурсия)
    2. Каждый рекурсивный вызов должен приближать к базовому случаю
    3. Глубина стека ограничена (в Python ~1000 по умолчанию)

    **Примеры:**
    ```python
    # Сумма списка
    def sum_list(lst: list[int]) -> int:
        if not lst:  # Базовый случай
            return 0
        return lst[0] + sum_list(lst[1:])  # Рекурсивный случай

    # Обход дерева
    def tree_sum(node) -> int:
        if node is None:  # Базовый случай
            return 0
        return node.value + tree_sum(node.left) + tree_sum(node.right)

    # Fibonacci (неэффективная версия)
    def fib(n: int) -> int:
        if n < 2:  # Базовый случай
            return n
        return fib(n - 1) + fib(n - 2)
    ```

---

38. **Лимит рекурсии в Python**

    Python ограничивает глубину рекурсии для защиты от переполнения стека.

    ```python
    import sys

    print(sys.getrecursionlimit())  # 1000 по умолчанию

    # Изменить лимит (осторожно!)
    sys.setrecursionlimit(2000)
    ```

    **Почему есть лимит:**
    ```python
    def infinite():
        return infinite()  # RecursionError без лимита → segfault

    infinite()  # RecursionError: maximum recursion depth exceeded
    ```

    **Альтернатива глубокой рекурсии — итерация:**
    ```python
    # Рекурсивный factorial — ограничен глубиной стека
    def factorial_recursive(n):
        if n <= 1:
            return 1
        return n * factorial_recursive(n - 1)

    # Итеративный — без ограничений
    def factorial_iterative(n):
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    # Или с reduce
    from functools import reduce
    def factorial_reduce(n):
        return reduce(lambda a, b: a * b, range(1, n + 1), 1)
    ```

    **Преобразование рекурсии в итерацию (стек):**
    ```python
    # Рекурсивный обход дерева
    def traverse_recursive(node):
        if node is None:
            return
        print(node.value)
        traverse_recursive(node.left)
        traverse_recursive(node.right)

    # Итеративный с явным стеком
    def traverse_iterative(root):
        stack = [root]
        while stack:
            node = stack.pop()
            if node is None:
                continue
            print(node.value)
            stack.append(node.right)
            stack.append(node.left)
    ```

---

39. **Мемоизация: @lru_cache и @cache**

    Мемоизация — кэширование результатов функции для избежания повторных вычислений.

    **@functools.cache (Python 3.9+):**
    ```python
    from functools import cache

    @cache
    def fibonacci(n: int) -> int:
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    # Без кэша: O(2^n)
    # С кэшем: O(n)

    fibonacci(100)  # Мгновенно
    ```

    **@functools.lru_cache:**
    ```python
    from functools import lru_cache

    @lru_cache(maxsize=128)  # Ограничение размера кэша
    def expensive_computation(x: int, y: int) -> int:
        print(f"Computing {x}, {y}")
        return x ** y

    expensive_computation(2, 10)  # Computing 2, 10 → 1024
    expensive_computation(2, 10)  # Из кэша → 1024 (без print)

    # Статистика кэша
    print(expensive_computation.cache_info())
    # CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)

    # Очистка кэша
    expensive_computation.cache_clear()
    ```

    **Ограничения:**
    ```python
    # Аргументы должны быть хэшируемы
    @cache
    def process(items: list):  # TypeError: unhashable type: 'list'
        ...

    # Решение — использовать tuple
    @cache
    def process(items: tuple):
        ...

    # Или конвертировать при вызове
    process(tuple(my_list))
    ```

    **Практический пример:**
    ```python
    @lru_cache(maxsize=1000)
    def get_user_permissions(user_id: int) -> set[str]:
        # Дорогой запрос к БД
        return db.query_permissions(user_id)

    # Первый вызов — запрос к БД
    # Последующие — из кэша
    ```

---

40. **Хвостовая рекурсия: почему Python её не оптимизирует?**

    **Хвостовая рекурсия** — когда рекурсивный вызов является последней операцией функции.

    ```python
    # Обычная рекурсия — результат используется после возврата
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)  # Умножение ПОСЛЕ рекурсивного вызова

    # Хвостовая рекурсия — ничего не делается после возврата
    def factorial_tail(n, accumulator=1):
        if n <= 1:
            return accumulator
        return factorial_tail(n - 1, n * accumulator)  # Просто возврат результата
    ```

    **Оптимизация хвостовой рекурсии (TCO):**
    - В языках с TCO компилятор превращает хвостовую рекурсию в цикл
    - Не создаётся новый stack frame
    - Нет ограничения глубины

    **Почему Python НЕ оптимизирует:**
    1. **Guido van Rossum считает стектрейсы важными** для отладки
    2. **Философия Python**: явное лучше неявного
    3. **Читаемость**: итеративный код часто понятнее

    **Альтернативы в Python:**
    ```python
    # 1. Использовать цикл
    def factorial_loop(n):
        result = 1
        while n > 1:
            result *= n
            n -= 1
        return result

    # 2. Trampolining (ручная оптимизация)
    def trampoline(fn):
        def wrapper(*args):
            result = fn(*args)
            while callable(result):
                result = result()
            return result
        return wrapper

    def factorial_trampoline(n, acc=1):
        if n <= 1:
            return acc
        return lambda: factorial_trampoline(n - 1, n * acc)

    result = trampoline(factorial_trampoline)(10000)  # Работает!
    ```

---

41. **map, filter и их современные альтернативы**

    **map — применение функции к каждому элементу:**
    ```python
    numbers = [1, 2, 3, 4, 5]

    # map возвращает итератор (ленивый)
    squared = map(lambda x: x ** 2, numbers)
    print(list(squared))  # [1, 4, 9, 16, 25]

    # Эквивалентный list comprehension (предпочтительнее)
    squared = [x ** 2 for x in numbers]

    # Generator expression (ленивый, как map)
    squared = (x ** 2 for x in numbers)
    ```

    **filter — фильтрация элементов:**
    ```python
    numbers = [1, 2, 3, 4, 5, 6]

    # filter возвращает итератор
    evens = filter(lambda x: x % 2 == 0, numbers)
    print(list(evens))  # [2, 4, 6]

    # Эквивалентный list comprehension
    evens = [x for x in numbers if x % 2 == 0]

    # Generator expression
    evens = (x for x in numbers if x % 2 == 0)
    ```

    **Когда map/filter лучше:**
    ```python
    # 1. Когда функция уже существует
    names = ["alice", "bob", "charlie"]
    upper_names = list(map(str.upper, names))  # Чище чем [n.upper() for n in names]

    # 2. Множественные итерируемые
    a = [1, 2, 3]
    b = [4, 5, 6]
    sums = list(map(lambda x, y: x + y, a, b))  # [5, 7, 9]
    # Comprehension требует zip: [x + y for x, y in zip(a, b)]
    ```

    **Когда comprehension лучше:**
    ```python
    # 1. Нужна и трансформация, и фильтрация
    result = [x ** 2 for x in numbers if x % 2 == 0]
    # vs
    result = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))

    # 2. Читаемость
    result = [user.name for user in users if user.is_active]
    ```

    **Рекомендация:** В Python предпочитайте comprehensions для большинства случаев.

---

42. **functools.reduce: когда оправдано использование?**

    `reduce` применяет функцию к элементам последовательно, накапливая результат.

    ```python
    from functools import reduce

    # reduce(f, [a, b, c, d]) = f(f(f(a, b), c), d)

    numbers = [1, 2, 3, 4, 5]

    # Сумма
    total = reduce(lambda acc, x: acc + x, numbers)  # 15
    # Лучше: sum(numbers)

    # Произведение
    product = reduce(lambda acc, x: acc * x, numbers)  # 120
    # Лучше: math.prod(numbers) в Python 3.8+

    # С начальным значением
    total = reduce(lambda acc, x: acc + x, numbers, 100)  # 115
    ```

    **Когда reduce оправдан:**
    ```python
    # 1. Нет встроенной альтернативы
    # Объединение словарей
    dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
    merged = reduce(lambda acc, d: {**acc, **d}, dicts)
    # {'a': 1, 'b': 2, 'c': 3}

    # 2. Композиция функций
    def compose(*funcs):
        return reduce(lambda f, g: lambda x: f(g(x)), funcs)

    add_one = lambda x: x + 1
    double = lambda x: x * 2
    pipeline = compose(str, add_one, double)  # str(add_one(double(x)))
    print(pipeline(5))  # "11"

    # 3. Вложенная структура
    data = {"a": {"b": {"c": 42}}}
    keys = ["a", "b", "c"]
    value = reduce(lambda d, key: d[key], keys, data)  # 42
    ```

    **Когда НЕ использовать reduce:**
    ```python
    # Есть встроенная альтернатива
    sum(numbers)           # вместо reduce(lambda a, b: a + b, numbers)
    max(numbers)           # вместо reduce(lambda a, b: a if a > b else b, numbers)
    "".join(strings)       # вместо reduce(lambda a, b: a + b, strings)
    all(bools)             # вместо reduce(lambda a, b: a and b, bools)
    any(bools)             # вместо reduce(lambda a, b: a or b, bools)
    ```

---

43. **Lambda функции: возможности и ограничения**

    Lambda — анонимная функция, состоящая из одного выражения.

    ```python
    # Синтаксис: lambda arguments: expression

    square = lambda x: x ** 2
    add = lambda x, y: x + y
    greet = lambda name="World": f"Hello, {name}!"

    print(square(5))      # 25
    print(add(2, 3))      # 5
    print(greet("Alice")) # Hello, Alice!
    ```

    **Ограничения lambda:**
    ```python
    # 1. Только одно выражение (нет statements)
    # НЕЛЬЗЯ:
    # lambda x: if x > 0: return x  # SyntaxError
    # lambda x: x = 1               # SyntaxError

    # 2. Нет аннотаций типов
    # НЕЛЬЗЯ:
    # lambda x: int -> int: x * 2  # SyntaxError

    # 3. Нет документации
    ```

    **Типичные применения:**
    ```python
    # Сортировка
    users = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
    sorted(users, key=lambda u: u["age"])

    # map/filter
    list(map(lambda x: x * 2, [1, 2, 3]))
    list(filter(lambda x: x > 0, [-1, 0, 1, 2]))

    # Callbacks
    button.on_click(lambda event: print("Clicked!"))

    # defaultdict
    from collections import defaultdict
    d = defaultdict(lambda: "N/A")
    ```

    **Когда использовать обычную функцию:**
    ```python
    # 1. Нужна документация или сложная логика
    def process_user(user):
        """Process user data and return formatted string."""
        name = user.get("name", "Unknown")
        age = user.get("age", 0)
        return f"{name} ({age})"

    # 2. Функция используется несколько раз
    # 3. Нужна отладка (lambda не имеет имени в traceback)
    ```

---

44. **Замыкания (closures) и nonlocal**

    **Замыкание** — функция, которая "запоминает" переменные из внешней области видимости.

    ```python
    def make_multiplier(n):
        def multiplier(x):
            return x * n  # n "захвачена" из внешней функции
        return multiplier

    double = make_multiplier(2)
    triple = make_multiplier(3)

    print(double(5))  # 10
    print(triple(5))  # 15

    # double и triple — замыкания, они "помнят" значение n
    ```

    **nonlocal — изменение переменной из внешней области:**
    ```python
    def counter():
        count = 0

        def increment():
            nonlocal count  # Без nonlocal будет ошибка
            count += 1
            return count

        return increment

    c = counter()
    print(c())  # 1
    print(c())  # 2
    print(c())  # 3
    ```

    **Распространённая ошибка — late binding:**
    ```python
    # ПРОБЛЕМА
    funcs = []
    for i in range(3):
        funcs.append(lambda: i)  # Все lambda ссылаются на одну переменную i

    print([f() for f in funcs])  # [2, 2, 2] — не [0, 1, 2]!

    # РЕШЕНИЕ 1: default argument (создаёт копию)
    funcs = []
    for i in range(3):
        funcs.append(lambda i=i: i)

    print([f() for f in funcs])  # [0, 1, 2]

    # РЕШЕНИЕ 2: functools.partial
    from functools import partial
    funcs = [partial(lambda x: x, i) for i in range(3)]
    ```

    **Практические применения:**
    ```python
    # Фабрика логгеров
    def make_logger(prefix):
        def log(message):
            print(f"[{prefix}] {message}")
        return log

    error_log = make_logger("ERROR")
    info_log = make_logger("INFO")

    # Декоратор с параметрами
    def repeat(times):
        def decorator(func):
            def wrapper(*args, **kwargs):
                for _ in range(times):
                    result = func(*args, **kwargs)
                return result
            return wrapper
        return decorator
    ```

---

45. **functools: partial, wraps, singledispatch**

    **functools.partial — частичное применение:**
    ```python
    from functools import partial

    def power(base, exponent):
        return base ** exponent

    square = partial(power, exponent=2)
    cube = partial(power, exponent=3)

    print(square(5))  # 25
    print(cube(5))    # 125

    # Практический пример
    import json
    pretty_json = partial(json.dumps, indent=2, ensure_ascii=False)
    print(pretty_json({"name": "Алиса"}))
    ```

    **functools.wraps — сохранение метаданных:**
    ```python
    from functools import wraps

    def my_decorator(func):
        @wraps(func)  # Копирует __name__, __doc__, etc.
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @my_decorator
    def greet(name):
        """Greet the user."""
        return f"Hello, {name}"

    print(greet.__name__)  # "greet" (без @wraps было бы "wrapper")
    print(greet.__doc__)   # "Greet the user."
    ```

    **functools.singledispatch — перегрузка по типу:**
    ```python
    from functools import singledispatch

    @singledispatch
    def process(value):
        raise NotImplementedError(f"Cannot process {type(value)}")

    @process.register(int)
    def _(value):
        return f"Integer: {value * 2}"

    @process.register(str)
    def _(value):
        return f"String: {value.upper()}"

    @process.register(list)
    def _(value):
        return f"List with {len(value)} items"

    print(process(10))       # Integer: 20
    print(process("hello"))  # String: HELLO
    print(process([1, 2]))   # List with 2 items
    ```

    **singledispatchmethod для методов:**
    ```python
    from functools import singledispatchmethod

    class Processor:
        @singledispatchmethod
        def process(self, value):
            raise NotImplementedError

        @process.register(int)
        def _(self, value):
            return value * 2

        @process.register(str)
        def _(self, value):
            return value.upper()
    ```

---

46. **itertools: инструменты для итераторов**

    **Бесконечные итераторы:**
    ```python
    from itertools import count, cycle, repeat

    # count(start, step) — бесконечный счётчик
    for i in count(10, 2):
        if i > 20:
            break
        print(i)  # 10, 12, 14, 16, 18, 20

    # cycle — бесконечное повторение
    colors = cycle(["red", "green", "blue"])
    for _ in range(5):
        print(next(colors))  # red, green, blue, red, green

    # repeat — повторение значения
    list(repeat("x", 3))  # ["x", "x", "x"]
    ```

    **Комбинаторика:**
    ```python
    from itertools import permutations, combinations, product

    # permutations — перестановки
    list(permutations("ABC", 2))
    # [('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]

    # combinations — сочетания (без повторений)
    list(combinations("ABC", 2))
    # [('A', 'B'), ('A', 'C'), ('B', 'C')]

    # combinations_with_replacement — сочетания с повторениями
    list(combinations_with_replacement("AB", 2))
    # [('A', 'A'), ('A', 'B'), ('B', 'B')]

    # product — декартово произведение
    list(product("AB", "12"))
    # [('A', '1'), ('A', '2'), ('B', '1'), ('B', '2')]

    list(product([0, 1], repeat=3))  # Все 3-битные числа
    # [(0,0,0), (0,0,1), (0,1,0), (0,1,1), (1,0,0), (1,0,1), (1,1,0), (1,1,1)]
    ```

    **Группировка и слияние:**
    ```python
    from itertools import groupby, chain

    # groupby — группировка (данные должны быть отсортированы!)
    data = [("A", 1), ("A", 2), ("B", 3), ("B", 4)]
    for key, group in groupby(data, key=lambda x: x[0]):
        print(key, list(group))
    # A [('A', 1), ('A', 2)]
    # B [('B', 3), ('B', 4)]

    # chain — объединение итераторов
    list(chain([1, 2], [3, 4], [5]))  # [1, 2, 3, 4, 5]

    # chain.from_iterable — для вложенных
    list(chain.from_iterable([[1, 2], [3, 4]]))  # [1, 2, 3, 4]
    ```

    **Фильтрация и срезы:**
    ```python
    from itertools import takewhile, dropwhile, islice, filterfalse

    numbers = [1, 3, 5, 2, 4, 6]

    # takewhile — брать пока условие True
    list(takewhile(lambda x: x < 4, numbers))  # [1, 3]

    # dropwhile — пропускать пока условие True
    list(dropwhile(lambda x: x < 4, numbers))  # [5, 2, 4, 6]

    # islice — срез итератора
    list(islice(count(), 5, 10))  # [5, 6, 7, 8, 9]

    # filterfalse — обратный filter
    list(filterfalse(lambda x: x % 2, numbers))  # [2, 4, 6]
    ```

---

47. **Генераторы и yield: ленивые вычисления**

    **Генератор** — функция, которая возвращает итератор. Вычисляет значения по требованию.

    ```python
    def countdown(n):
        while n > 0:
            yield n  # "Возвращает" значение и приостанавливается
            n -= 1

    gen = countdown(3)
    print(next(gen))  # 3
    print(next(gen))  # 2
    print(next(gen))  # 1
    print(next(gen))  # StopIteration

    # Или в цикле
    for num in countdown(3):
        print(num)
    ```

    **Преимущества генераторов:**
    ```python
    # 1. Экономия памяти
    # Плохо — загружает весь файл в память
    def read_all(filename):
        with open(filename) as f:
            return f.readlines()  # Миллионы строк в RAM

    # Хорошо — по одной строке
    def read_lazy(filename):
        with open(filename) as f:
            for line in f:
                yield line.strip()

    # 2. Бесконечные последовательности
    def fibonacci():
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b

    fib = fibonacci()
    print([next(fib) for _ in range(10)])  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    ```

    **yield from — делегирование:**
    ```python
    def flatten(nested):
        for item in nested:
            if isinstance(item, list):
                yield from flatten(item)  # Делегируем вложенному генератору
            else:
                yield item

    list(flatten([1, [2, [3, 4], 5], 6]))  # [1, 2, 3, 4, 5, 6]
    ```

    **send() — двусторонняя коммуникация:**
    ```python
    def accumulator():
        total = 0
        while True:
            value = yield total
            if value is not None:
                total += value

    gen = accumulator()
    next(gen)           # Инициализация, возвращает 0
    print(gen.send(10)) # 10
    print(gen.send(20)) # 30
    print(gen.send(5))  # 35
    ```

---

48. **Чистые функции и иммутабельность**

    **Чистая функция:**
    1. При одинаковых входных данных всегда возвращает одинаковый результат
    2. Не имеет побочных эффектов (не изменяет внешнее состояние)

    ```python
    # ЧИСТАЯ функция
    def add(a, b):
        return a + b

    # НЕЧИСТАЯ — зависит от внешнего состояния
    total = 0
    def add_to_total(x):
        global total
        total += x
        return total

    # НЕЧИСТАЯ — имеет побочный эффект
    def save_user(user):
        database.save(user)  # Изменяет внешний мир
        return user
    ```

    **Преимущества чистых функций:**
    - Легко тестировать
    - Легко понять (нет скрытых зависимостей)
    - Безопасно кэшировать (мемоизация)
    - Безопасно распараллеливать

    **Иммутабельность в Python:**
    ```python
    # Immutable: int, float, str, tuple, frozenset
    # Mutable: list, dict, set

    # Работа с immutable — создание нового объекта
    original = (1, 2, 3)
    modified = original + (4,)  # Новый tuple

    # "Иммутабельная" работа с mutable
    def add_item(lst, item):
        return [*lst, item]  # Возвращаем новый список

    original = [1, 2, 3]
    new_list = add_item(original, 4)  # original не изменён
    ```

    **Практические паттерны:**
    ```python
    # 1. Не мутировать аргументы
    # Плохо
    def process(items):
        items.sort()  # Мутирует входной список!
        return items

    # Хорошо
    def process(items):
        return sorted(items)  # Возвращает новый список

    # 2. Использовать dataclass(frozen=True)
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Point:
        x: float
        y: float

    p = Point(1, 2)
    # p.x = 3  # FrozenInstanceError!

    # "Изменение" через создание нового объекта
    from dataclasses import replace
    p2 = replace(p, x=3)  # Point(x=3, y=2)

    # 3. NamedTuple для простых случаев
    from typing import NamedTuple

    class User(NamedTuple):
        name: str
        age: int

    user = User("Alice", 30)
    # user.age = 31  # AttributeError
    ```

    **Когда иммутабельность не нужна:**
    - Производительность критична (создание объектов дорого)
    - Локальные изменения внутри функции
    - Работа с большими структурами данных (лучше мутация + копия на границе)

## 🔴 Практическая задача: Обработка огромного CSV файла

_Типичная задача на собеседовании, проверяющая понимание работы с памятью и производительностью._

49. **Задача: Есть CSV файл на 50GB с числами. Нужно выполнить математические преобразования над каждым числом и записать результат. Как это сделать эффективно?**

    Это комплексная задача, которая проверяет знание:
    - Работы с памятью и потоковой обработки
    - I/O операций
    - Выбора между CPU-bound и I/O-bound оптимизациями
    - Знания инструментов экосистемы Python

    ---

    ### Подход 1: Потоковая обработка (Streaming) — базовый и надёжный

    **Идея:** Читаем файл построчно, обрабатываем, сразу пишем результат. В памяти находится только одна строка.

    ```python
    import csv

    def process_row(row: list[str]) -> list[str]:
        """Математическое преобразование над числами в строке."""
        return [str(float(x) ** 2 + 10) for x in row]

    def process_csv_streaming(input_path: str, output_path: str) -> None:
        with open(input_path, 'r', newline='') as infile, \
             open(output_path, 'w', newline='') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:  # Итератор — одна строка в памяти
                processed = process_row(row)
                writer.writerow(processed)
    ```

    **Техническая подоплёка:**
    - `csv.reader` — итератор, не загружает весь файл
    - `for row in reader` — ленивое чтение, строка освобождается после обработки
    - Память: O(размер_одной_строки), независимо от размера файла
    - Время: O(n), где n — количество строк

    **Когда использовать:** Всегда начинайте с этого подхода. Он работает на любом железе.

    ---

    ### Подход 2: Генераторы — элегантная потоковая обработка

    **Идея:** Разделяем чтение, обработку и запись в отдельные генераторы. Код становится модульным и тестируемым.

    ```python
    from typing import Iterator
    import csv

    def read_rows(filepath: str) -> Iterator[list[str]]:
        """Генератор чтения строк."""
        with open(filepath, 'r', newline='') as f:
            reader = csv.reader(f)
            yield from reader

    def transform_rows(rows: Iterator[list[str]]) -> Iterator[list[str]]:
        """Генератор трансформации."""
        for row in rows:
            yield [str(float(x) ** 2 + 10) for x in row]

    def write_rows(rows: Iterator[list[str]], filepath: str) -> None:
        """Запись результата."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

    # Использование — pipeline из генераторов
    def process_csv_generators(input_path: str, output_path: str) -> None:
        rows = read_rows(input_path)
        transformed = transform_rows(rows)
        write_rows(transformed, output_path)
    ```

    **Техническая подоплёка:**
    - Генераторы создают "ленивый пайплайн" — данные текут через цепочку
    - `yield from` делегирует итерацию без накопления в памяти
    - Каждый шаг можно тестировать отдельно
    - Легко добавлять новые шаги (фильтрация, валидация)

    **Преимущество:** Чистая архитектура, легко расширять.

    ---

    ### Подход 3: Pandas с chunksize — для сложных преобразований

    **Идея:** Pandas умеет читать файл порциями (chunks). Получаем удобство DataFrame API без загрузки всего файла.

    ```python
    import pandas as pd

    def process_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
        """Векторизованные операции над chunk."""
        # Применяем операцию ко всем числовым колонкам
        numeric_cols = chunk.select_dtypes(include='number').columns
        chunk[numeric_cols] = chunk[numeric_cols] ** 2 + 10
        return chunk

    def process_csv_pandas(input_path: str, output_path: str,
                           chunksize: int = 100_000) -> None:
        # Читаем файл порциями
        chunks = pd.read_csv(input_path, chunksize=chunksize)

        # Первый chunk — записываем с заголовком
        first_chunk = next(chunks)
        process_chunk(first_chunk).to_csv(output_path, index=False)

        # Остальные — дописываем без заголовка
        for chunk in chunks:
            process_chunk(chunk).to_csv(
                output_path,
                mode='a',  # append mode
                header=False,
                index=False
            )
    ```

    **Техническая подоплёка:**
    - `chunksize=100_000` — читаем по 100K строк за раз
    - Каждый chunk — полноценный DataFrame
    - Векторизованные операции pandas работают через NumPy (C-код)
    - `**` и `+` над DataFrame — операция над всем массивом, не поэлементный цикл

    **Расчёт chunksize:**
    ```python
    # Эмпирическое правило:
    # chunksize = available_RAM / (row_size * 3)
    # Множитель 3 — запас для промежуточных операций

    # Для 8GB RAM, строка ~1KB:
    # chunksize = 8GB / (1KB * 3) ≈ 2.5 миллиона строк
    # Берём с запасом: 100K - 500K
    ```

    **Когда использовать:** Когда нужны сложные преобразования, группировки, или данные нужно анализировать, а не просто трансформировать.

    ---

    ### Подход 4: Multiprocessing — для CPU-bound преобразований

    **Идея:** Если математические операции тяжёлые (криптография, ML-инференс), распараллеливаем обработку по ядрам CPU.

    ```python
    import csv
    from multiprocessing import Pool, cpu_count
    from typing import Iterator
    from itertools import islice

    def process_batch(rows: list[list[str]]) -> list[list[str]]:
        """Обработка батча строк (выполняется в отдельном процессе)."""
        return [[str(float(x) ** 2 + 10) for x in row] for row in rows]

    def batched(iterable: Iterator, batch_size: int) -> Iterator[list]:
        """Группирует итератор в батчи."""
        iterator = iter(iterable)
        while batch := list(islice(iterator, batch_size)):
            yield batch

    def process_csv_multiprocessing(input_path: str, output_path: str,
                                     batch_size: int = 10_000) -> None:
        with open(input_path, 'r', newline='') as infile, \
             open(output_path, 'w', newline='') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            # Создаём пул процессов
            with Pool(processes=cpu_count()) as pool:
                # Обрабатываем батчи параллельно
                for processed_batch in pool.imap(process_batch, batched(reader, batch_size)):
                    writer.writerows(processed_batch)
    ```

    **Техническая подоплёка:**
    - `Pool(cpu_count())` — по процессу на каждое ядро
    - `pool.imap` — ленивый map, не загружает все результаты сразу
    - Каждый процесс имеет свой GIL — настоящий параллелизм
    - Данные сериализуются между процессами (pickle) — overhead

    **Важно:** Multiprocessing эффективен только если:
    - CPU-операции занимают значительно больше времени, чем I/O
    - `batch_size` достаточно большой, чтобы амортизировать overhead сериализации

    **Расчёт batch_size:**
    ```python
    # Слишком маленький batch — много overhead на сериализацию
    # Слишком большой — много памяти, долго ждать результат

    # Эмпирика: 1K-100K строк на batch
    # Профилируйте на реальных данных!
    ```

    ---

    ### Подход 5: Polars — современная альтернатива Pandas

    **Идея:** Polars написан на Rust, использует все ядра автоматически, работает с ленивыми вычислениями.

    ```python
    import polars as pl

    def process_csv_polars(input_path: str, output_path: str) -> None:
        # Ленивое чтение — ничего не загружается
        df = pl.scan_csv(input_path)

        # Определяем трансформации (ещё не выполняются)
        result = df.with_columns([
            (pl.col(col) ** 2 + 10).alias(col)
            for col in df.columns
        ])

        # Выполняем и сразу пишем в файл
        result.sink_csv(output_path)
    ```

    **Техническая подоплёка:**
    - `scan_csv` — создаёт LazyFrame, файл не читается
    - `with_columns` — декларативное описание трансформаций
    - `sink_csv` — streaming запись, данные текут через систему
    - Автоматическая параллелизация и оптимизация запросов

    **Преимущества Polars:**
    ```python
    # 1. Автопараллелизация — использует все ядра без настройки
    # 2. Query optimization — переупорядочивает операции для эффективности
    # 3. Streaming — может обрабатывать файлы больше RAM
    # 4. Rust backend — значительно быстрее pandas на многих операциях
    ```

    **Бенчмарк (примерный):**
    | Инструмент | 10GB файл | Память |
    |------------|-----------|--------|
    | Pandas (весь файл) | Crash | >10GB |
    | Pandas (chunks) | 5 мин | ~500MB |
    | Polars (lazy) | 1 мин | ~500MB |
    | Pure Python streaming | 8 мин | ~1MB |

    ---

    ### Подход 6: Memory-mapped files (mmap) — низкоуровневая оптимизация

    **Идея:** ОС отображает файл в виртуальную память. Мы работаем с файлом как с байтовым массивом, а ОС управляет загрузкой страниц.

    ```python
    import mmap
    import re

    def process_csv_mmap(input_path: str, output_path: str) -> None:
        with open(input_path, 'r+b') as f:
            # Отображаем файл в память
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

            with open(output_path, 'wb') as out:
                # Читаем построчно через mmap
                for line in iter(mm.readline, b''):
                    # Обрабатываем строку
                    values = line.decode().strip().split(',')
                    processed = [str(float(x) ** 2 + 10) for x in values]
                    out.write((','.join(processed) + '\n').encode())

            mm.close()
    ```

    **Техническая подоплёка:**
    - `mmap` — файл "виден" как массив байтов
    - ОС загружает только нужные страницы (обычно 4KB)
    - Повторный доступ к данным — из кэша ОС, без syscall
    - Полезно для произвольного доступа к большим файлам

    **Когда использовать:** Редко для CSV. Полезно когда:
    - Нужен random access к разным частям файла
    - Файл читается многократно
    - Несколько процессов читают один файл

    ---

    ### Подход 7: Dask — для по-настоящему больших данных

    **Идея:** Dask — это "ленивый pandas", который может распределять вычисления по кластеру или эффективно использовать один компьютер.

    ```python
    import dask.dataframe as dd

    def process_csv_dask(input_path: str, output_path: str) -> None:
        # Создаём ленивый DataFrame (ничего не загружается)
        df = dd.read_csv(input_path)

        # Определяем вычисления (не выполняются)
        for col in df.columns:
            df[col] = df[col] ** 2 + 10

        # Выполняем и записываем
        # Dask сам разобьёт на части и распараллелит
        df.to_csv(output_path, index=False, single_file=True)
    ```

    **Техническая подоплёка:**
    - Dask автоматически разбивает данные на партиции
    - Строит граф вычислений и оптимизирует его
    - Может работать на одной машине или на кластере
    - API совместим с pandas

    **Когда использовать:**
    - Данные не помещаются в память даже с chunking
    - Нужна обработка на кластере (Kubernetes, YARN)
    - Сложные аналитические запросы на больших данных

    ---

    ### Сравнение подходов

    | Подход | Память | Скорость | Сложность | Когда использовать |
    |--------|--------|----------|-----------|-------------------|
    | Streaming (csv) | O(1) | Средняя | Простая | Базовый вариант, всегда работает |
    | Генераторы | O(1) | Средняя | Средняя | Когда нужна модульность |
    | Pandas chunks | O(chunk) | Высокая | Средняя | Сложные трансформации |
    | Multiprocessing | O(batch) | Высокая* | Сложная | CPU-bound операции |
    | Polars | O(оптим.) | Очень высокая | Простая | Когда важна скорость |
    | mmap | O(page) | Средняя | Сложная | Random access |
    | Dask | O(partition) | Высокая | Средняя | Кластеры, >RAM данные |

    *Multiprocessing быстрее только для CPU-bound задач

    ---

    ### Что отвечать на собеседовании

    **Структура ответа:**

    1. **Уточнить требования:**
       - Размер файла и доступная RAM?
       - Насколько "тяжёлые" математические операции?
       - Нужно ли сохранять порядок строк?
       - Однократная обработка или регулярная задача?

    2. **Начать с простого:**
       > "Базовый подход — потоковая обработка через csv.reader. Это гарантированно работает на любом железе и не требует зависимостей."

    3. **Показать знание альтернатив:**
       > "Если операции CPU-intensive, можно добавить multiprocessing. Если нужна скорость и есть возможность — Polars или pandas с chunks."

    4. **Упомянуть trade-offs:**
       > "Multiprocessing добавляет overhead на сериализацию — нужно профилировать. Polars быстрее, но это дополнительная зависимость."

    **Красные флаги (чего НЕ говорить):**
    - "Загрузим весь файл в pandas" — показывает непонимание работы с памятью
    - "Используем threading для ускорения" — показывает непонимание GIL
    - Не упоминать chunking/streaming — ключевой концепт для больших данных

    **Бонусные очки:**
    - Упомянуть профилирование (`cProfile`, `memory_profiler`)
    - Спросить про формат данных (может быть Parquet эффективнее CSV?)
    - Предложить pipeline с промежуточным сохранением для отказоустойчивости
