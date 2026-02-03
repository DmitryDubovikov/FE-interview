# NerdWallet Technical Interview Solutions

> **Важно:** NerdWallet ценит не просто код, а **процесс рассуждения**, **коммуникацию** и **понимание trade-offs**. Объясняйте свои решения вслух!

---

## Задача 1: JSON Serializer

### Анализ задачи

**Что нужно сделать:** Написать функцию, которая конвертирует любой Python объект в JSON строку без использования встроенных библиотек.

**Уточняющие вопросы:**
1. Какие типы данных нужно поддерживать? (dict, list, str, int, float, bool, None — стандартный набор)
2. Как обрабатывать кастомные объекты (классы)? (Предположим — не поддерживаем или вызываем ошибку)
3. Какое поведение при циклических ссылках? (Вызывать исключение)
4. Нужно ли pretty-print с отступами? (Начнём с компактного формата)

### Пошаговое рассуждение

1. **Рекурсивная структура:** JSON по природе рекурсивен — объекты содержат другие объекты
2. **Диспетчеризация по типу:** Проверяем тип входа и вызываем соответствующий обработчик
3. **Отслеживание посещённых объектов:** Для обнаружения циклов используем `set` с `id()` объектов
4. **Экранирование строк:** Необходимо обрабатывать `"`, `\`, `\n`, `\t`, `\r` и другие

### Псевдокод

```
function serialize(value, visited_set):
    if value is None:
        return "null"
    if value is boolean:
        return "true" or "false"
    if value is number:
        return string(value)
    if value is string:
        return escape_and_quote(value)

    # Для объектов проверяем циклы
    if id(value) in visited_set:
        raise CircularReferenceError
    visited_set.add(id(value))

    if value is list:
        parts = [serialize(item, visited_set) for item in value]
        return "[" + ", ".join(parts) + "]"

    if value is dict:
        parts = [escape_and_quote(key) + ": " + serialize(val, visited_set)
                 for key, val in value.items()]
        return "{" + ", ".join(parts) + "}"

    visited_set.remove(id(value))  # backtrack
    raise UnsupportedTypeError
```

### Финальное решение

```python
class JSONSerializerError(Exception):
    """Base exception for JSON serializer"""
    pass


class CircularReferenceError(JSONSerializerError):
    """Raised when circular reference detected"""
    pass


class UnsupportedTypeError(JSONSerializerError):
    """Raised when unsupported type encountered"""
    pass


def json_serialize(value) -> str:
    """Serialize a Python object to JSON string."""
    return _serialize(value, set())


def _serialize(value, visited: set) -> str:
    """Internal recursive serializer with cycle detection."""

    # Primitives (immutable, no cycle risk)
    if value is None:
        return "null"

    if isinstance(value, bool):  # Must check before int (bool is subclass of int)
        return "true" if value else "false"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        # Handle special float values
        if value != value:  # NaN check
            raise UnsupportedTypeError("NaN is not valid JSON")
        if value == float('inf') or value == float('-inf'):
            raise UnsupportedTypeError("Infinity is not valid JSON")
        return str(value)

    if isinstance(value, str):
        return _escape_string(value)

    # Container types (mutable, need cycle detection)
    obj_id = id(value)
    if obj_id in visited:
        raise CircularReferenceError(
            f"Circular reference detected for object of type {type(value).__name__}"
        )

    visited.add(obj_id)

    try:
        if isinstance(value, dict):
            return _serialize_dict(value, visited)

        if isinstance(value, (list, tuple)):
            return _serialize_list(value, visited)

        raise UnsupportedTypeError(f"Cannot serialize type: {type(value).__name__}")

    finally:
        # Remove from visited after processing (backtracking)
        # This allows same object to appear in different branches
        visited.discard(obj_id)


def _escape_string(s: str) -> str:
    """Escape special characters and wrap in quotes."""
    # Mapping of characters that need escaping in JSON
    escape_map = {
        '"': '\\"',
        '\\': '\\\\',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '\b': '\\b',
        '\f': '\\f',
    }

    result = []
    for char in s:
        if char in escape_map:
            result.append(escape_map[char])
        elif ord(char) < 32:  # Control characters
            result.append(f'\\u{ord(char):04x}')
        else:
            result.append(char)

    return '"' + ''.join(result) + '"'


def _serialize_dict(d: dict, visited: set) -> str:
    """Serialize a dictionary to JSON object."""
    if not d:
        return "{}"

    pairs = []
    for key, val in d.items():
        # JSON keys must be strings
        if not isinstance(key, str):
            raise UnsupportedTypeError(f"Dict key must be string, got {type(key).__name__}")

        key_str = _escape_string(key)
        val_str = _serialize(val, visited)
        pairs.append(f"{key_str}: {val_str}")

    return "{" + ", ".join(pairs) + "}"


def _serialize_list(lst, visited: set) -> str:
    """Serialize a list/tuple to JSON array."""
    if not lst:
        return "[]"

    items = [_serialize(item, visited) for item in lst]
    return "[" + ", ".join(items) + "]"
```

### Сложность

| Метрика | Значение |
|---------|----------|
| **Time** | O(n) где n — общее количество элементов во всех вложенных структурах |
| **Space** | O(d) где d — максимальная глубина вложенности (стек рекурсии + visited set) |

### Edge Cases

- `bool` проверяется ДО `int` (bool — подкласс int в Python)
- `NaN` и `Infinity` не валидный JSON — выбрасываем исключение
- Ключи словаря должны быть строками
- Один и тот же объект может появляться в разных ветках (не цикл) — используем backtracking

---

## Задача 2: ETL System Design

### Анализ задачи

**Что нужно сделать:** Спроектировать систему, которая периодически читает данные из внешних источников, нормализует их и обновляет в БД.

**Уточняющие вопросы:**
1. Какой объём данных? (Тысячи записей? Миллионы?)
2. Как часто нужно обновлять? (Минуты? Часы? Дни?)
3. Сколько источников данных?
4. Требования к latency обновлений?
5. Допустима ли eventual consistency?

### Архитектура системы

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ETL SYSTEM ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  Source A    │    │  Source B    │    │  Source C    │
    │  (REST API)  │    │  (SFTP/CSV)  │    │  (Webhook)   │
    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────────────────────────────────────────────────┐
    │                   INGESTION LAYER                     │
    │  ┌─────────────────────────────────────────────────┐ │
    │  │  Adapters (one per source type)                 │ │
    │  │  - Rate limiting                                │ │
    │  │  - Retries with exponential backoff             │ │
    │  │  - Raw data validation                          │ │
    │  └─────────────────────────────────────────────────┘ │
    └──────────────────────────┬───────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │                    MESSAGE QUEUE                      │
    │              (Kafka / RabbitMQ / SQS)                 │
    │                                                       │
    │  - Decouples ingestion from processing               │
    │  - Provides durability and replay capability         │
    │  - Enables horizontal scaling of consumers           │
    └──────────────────────────┬───────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │                TRANSFORMATION LAYER                   │
    │  ┌─────────────────────────────────────────────────┐ │
    │  │  Worker Pool (stateless)                        │ │
    │  │  - Schema normalization                         │ │
    │  │  - Data enrichment                              │ │
    │  │  - Validation & cleansing                       │ │
    │  │  - Deduplication (idempotency keys)             │ │
    │  └─────────────────────────────────────────────────┘ │
    └──────────────────────────┬───────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │                   STORAGE LAYER                       │
    │  ┌────────────────┐    ┌────────────────────────────┐│
    │  │  Primary DB    │    │  Data Warehouse (optional) ││
    │  │  (PostgreSQL)  │    │  (Snowflake/BigQuery)      ││
    │  │                │    │                            ││
    │  │  - UPSERT ops  │    │  - Historical data         ││
    │  │  - Transactions│    │  - Analytics               ││
    │  └────────────────┘    └────────────────────────────┘│
    └──────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────┐
    │                  ORCHESTRATION LAYER                  │
    │                                                       │
    │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
    │  │  Scheduler  │  │  Dead Letter│  │  Monitoring  │  │
    │  │  (Airflow/  │  │  Queue      │  │  (Datadog/   │  │
    │  │   Celery)   │  │  (DLQ)      │  │   Grafana)   │  │
    │  └─────────────┘  └─────────────┘  └──────────────┘  │
    └──────────────────────────────────────────────────────┘
```

### Data Flow

```
1. SCHEDULE TRIGGER
   │
   ├─── Cron job fires at configured interval
   │    (e.g., every 15 minutes)
   │
   ▼
2. INGESTION
   │
   ├─── Fetch data from external source
   ├─── Handle pagination (if API)
   ├─── Store raw response with timestamp
   ├─── Publish to message queue
   │
   ▼
3. TRANSFORMATION
   │
   ├─── Consumer picks up message
   ├─── Parse raw data
   ├─── Map to canonical schema
   ├─── Validate required fields
   ├─── Generate idempotency key
   │
   ▼
4. PERSISTENCE
   │
   ├─── Check if record exists (by idempotency key)
   ├─── UPSERT to database
   ├─── Update audit trail
   │
   ▼
5. COMPLETION
   │
   ├─── Acknowledge message
   ├─── Emit metrics
   └─── Log completion
```

### Ключевые компоненты

#### 1. Scheduler (Планировщик)
```python
# Пример: Celery Beat конфигурация
CELERYBEAT_SCHEDULE = {
    'ingest-source-a': {
        'task': 'etl.tasks.ingest',
        'schedule': crontab(minute='*/15'),  # каждые 15 минут
        'args': ('source_a',),
    },
    'ingest-source-b': {
        'task': 'etl.tasks.ingest',
        'schedule': crontab(hour='*/1'),  # каждый час
        'args': ('source_b',),
    },
}
```

#### 2. Idempotency (Идемпотентность)
```python
def generate_idempotency_key(source: str, record: dict) -> str:
    """
    Generate unique key for deduplication.
    Combination of source + natural key + timestamp bucket.
    """
    natural_key = record.get('id') or record.get('external_id')
    timestamp = record.get('updated_at', datetime.now().isoformat())

    content = f"{source}:{natural_key}:{timestamp}"
    return hashlib.sha256(content.encode()).hexdigest()


def upsert_record(record: dict, idempotency_key: str):
    """
    Upsert with conflict resolution.
    """
    db.execute("""
        INSERT INTO records (id, data, idempotency_key, updated_at)
        VALUES (%(id)s, %(data)s, %(key)s, NOW())
        ON CONFLICT (idempotency_key)
        DO UPDATE SET
            data = EXCLUDED.data,
            updated_at = NOW()
        WHERE records.updated_at < EXCLUDED.updated_at
    """, {'id': record['id'], 'data': record, 'key': idempotency_key})
```

#### 3. Error Handling & Retries
```python
@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    retry_backoff=True,      # exponential backoff
    retry_jitter=True,       # add randomness
)
def process_record(self, message: dict):
    try:
        transformed = transform(message)
        persist(transformed)
    except TransientError as e:
        # Retry for transient failures (network, timeouts)
        raise self.retry(exc=e)
    except PermanentError as e:
        # Send to Dead Letter Queue for manual review
        send_to_dlq(message, error=str(e))
        logger.error(f"Permanent failure: {e}")
```

### Trade-offs: Batch vs Streaming

| Аспект | Batch | Streaming |
|--------|-------|-----------|
| **Latency** | Минуты-часы | Секунды |
| **Complexity** | Проще | Сложнее |
| **Cost** | Ниже (можно spot instances) | Выше (always-on) |
| **Data freshness** | Eventual | Near real-time |
| **Error recovery** | Проще (переработать batch) | Сложнее |
| **Use case** | Отчёты, аналитика | Real-time dashboards |

**Рекомендация для NerdWallet:** Начать с batch (проще), добавить streaming для критичных источников по мере необходимости.

### Масштабирование

1. **Горизонтальное масштабирование workers:** Добавить больше consumer instances
2. **Партиционирование очереди:** По source или по первичному ключу
3. **Read replicas для БД:** Для read-heavy workloads
4. **Caching:** Redis для часто читаемых данных
5. **Sharding:** При очень больших объёмах данных

### Мониторинг

```yaml
# Ключевые метрики
metrics:
  - name: etl.records.processed
    type: counter
    labels: [source, status]

  - name: etl.processing.duration
    type: histogram
    labels: [source, stage]

  - name: etl.queue.depth
    type: gauge
    labels: [queue_name]

  - name: etl.errors
    type: counter
    labels: [source, error_type]

# Alerts
alerts:
  - name: HighErrorRate
    condition: rate(etl.errors[5m]) > 0.01
    severity: warning

  - name: QueueBacklog
    condition: etl.queue.depth > 10000
    severity: critical
```

---

## Задача 3: Task Scheduler Service

### Анализ задачи

**Что нужно сделать:** Сервис, который принимает задачи с timestamp и выполняет их в указанное время.

**Уточняющие вопросы:**
1. Какая точность нужна? (Секунды? Миллисекунды?)
2. Какой объём задач? (Тысячи в день? Миллионы?)
3. Нужна ли персистентность при перезапуске?
4. Какие гарантии выполнения? (at-least-once vs exactly-once?)
5. Можно ли задачи отменять?

### API Design

```yaml
openapi: 3.0.0
info:
  title: Task Scheduler API
  version: 1.0.0

paths:
  /tasks:
    post:
      summary: Create a scheduled task
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [execute_at, payload]
              properties:
                execute_at:
                  type: string
                  format: date-time
                  description: When to execute the task (ISO 8601)
                payload:
                  type: object
                  description: Task-specific data
                callback_url:
                  type: string
                  format: uri
                  description: Webhook URL to call on execution
                idempotency_key:
                  type: string
                  description: Client-provided key for deduplication
      responses:
        201:
          description: Task created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'

    get:
      summary: List tasks
      parameters:
        - name: status
          in: query
          schema:
            enum: [pending, running, completed, failed, cancelled]
        - name: from
          in: query
          schema:
            type: string
            format: date-time
        - name: to
          in: query
          schema:
            type: string
            format: date-time
      responses:
        200:
          description: List of tasks

  /tasks/{task_id}:
    get:
      summary: Get task details
      responses:
        200:
          description: Task details

    delete:
      summary: Cancel a task
      responses:
        204:
          description: Task cancelled

components:
  schemas:
    Task:
      type: object
      properties:
        id:
          type: string
          format: uuid
        status:
          enum: [pending, running, completed, failed, cancelled]
        execute_at:
          type: string
          format: date-time
        created_at:
          type: string
          format: date-time
        executed_at:
          type: string
          format: date-time
          nullable: true
        payload:
          type: object
        retry_count:
          type: integer
        error:
          type: string
          nullable: true
```

### Data Model

```sql
CREATE TABLE scheduled_tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key VARCHAR(255) UNIQUE,

    -- Scheduling
    execute_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Status
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),

    -- Execution tracking
    executed_at     TIMESTAMP WITH TIME ZONE,
    completed_at    TIMESTAMP WITH TIME ZONE,
    locked_by       VARCHAR(255),  -- Worker ID that picked up the task
    locked_at       TIMESTAMP WITH TIME ZONE,

    -- Task data
    payload         JSONB NOT NULL,
    callback_url    VARCHAR(2048),

    -- Retry handling
    retry_count     INTEGER DEFAULT 0,
    max_retries     INTEGER DEFAULT 3,
    last_error      TEXT,

    -- Indexes for efficient polling
    INDEX idx_execute_at_status (execute_at, status) WHERE status = 'pending',
    INDEX idx_locked_at (locked_at) WHERE status = 'running'
);
```

### Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    TASK SCHEDULER SERVICE                        │
└─────────────────────────────────────────────────────────────────┘

                         ┌───────────────┐
                         │   API Server  │
                         │   (FastAPI)   │
                         └───────┬───────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
           ┌──────────┐   ┌──────────┐   ┌──────────┐
           │ Scheduler│   │ Scheduler│   │ Scheduler│
           │ Worker 1 │   │ Worker 2 │   │ Worker N │
           └────┬─────┘   └────┬─────┘   └────┬─────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     PostgreSQL      │
                    │  (scheduled_tasks)  │
                    │                     │
                    │  + Priority Queue   │
                    │    (in-memory)      │
                    └─────────────────────┘
```

### Scheduler Worker Logic

```python
import heapq
import threading
import time
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass(order=True)
class ScheduledTask:
    """Task wrapper for priority queue ordering."""
    execute_at: datetime
    task_id: str = field(compare=False)
    payload: dict = field(compare=False)
    callback_url: Optional[str] = field(compare=False)


class TaskScheduler:
    """
    In-memory scheduler with database persistence.

    Uses min-heap (priority queue) for O(log n) insert and O(1) peek.
    Polls database periodically to sync with other workers.
    """

    def __init__(self, db, worker_id: str = None):
        self.db = db
        self.worker_id = worker_id or str(uuid.uuid4())[:8]
        self.heap: list[ScheduledTask] = []
        self.heap_lock = threading.Lock()
        self.running = False

    def start(self):
        """Start the scheduler worker."""
        self.running = True

        # Thread 1: Poll database for new tasks
        self.poll_thread = threading.Thread(target=self._poll_database)
        self.poll_thread.start()

        # Thread 2: Execute due tasks
        self.execute_thread = threading.Thread(target=self._execute_tasks)
        self.execute_thread.start()

    def stop(self):
        """Graceful shutdown."""
        self.running = False
        self.poll_thread.join()
        self.execute_thread.join()

    def _poll_database(self):
        """
        Periodically fetch pending tasks from database.
        Implements distributed locking to avoid duplicate execution.
        """
        while self.running:
            try:
                # Fetch tasks due in next 60 seconds that aren't locked
                tasks = self.db.execute("""
                    UPDATE scheduled_tasks
                    SET
                        status = 'running',
                        locked_by = %(worker_id)s,
                        locked_at = NOW()
                    WHERE id IN (
                        SELECT id FROM scheduled_tasks
                        WHERE status = 'pending'
                          AND execute_at <= NOW() + INTERVAL '60 seconds'
                          AND (locked_by IS NULL OR locked_at < NOW() - INTERVAL '5 minutes')
                        ORDER BY execute_at
                        LIMIT 100
                        FOR UPDATE SKIP LOCKED
                    )
                    RETURNING id, execute_at, payload, callback_url
                """, {'worker_id': self.worker_id})

                with self.heap_lock:
                    for task in tasks:
                        heapq.heappush(self.heap, ScheduledTask(
                            execute_at=task['execute_at'],
                            task_id=task['id'],
                            payload=task['payload'],
                            callback_url=task['callback_url']
                        ))

            except Exception as e:
                logger.error(f"Poll error: {e}")

            time.sleep(1)  # Poll every second

    def _execute_tasks(self):
        """
        Execute tasks when their time comes.
        Uses condition variable to avoid busy waiting.
        """
        while self.running:
            task = None

            with self.heap_lock:
                if self.heap:
                    # Peek at next task
                    next_task = self.heap[0]
                    if next_task.execute_at <= datetime.now():
                        task = heapq.heappop(self.heap)

            if task:
                self._execute_task(task)
            else:
                time.sleep(0.1)  # Small sleep if no task ready

    def _execute_task(self, task: ScheduledTask):
        """Execute a single task with error handling."""
        try:
            # Execute the task (e.g., call webhook)
            if task.callback_url:
                response = requests.post(
                    task.callback_url,
                    json=task.payload,
                    timeout=30
                )
                response.raise_for_status()

            # Mark as completed
            self.db.execute("""
                UPDATE scheduled_tasks
                SET status = 'completed',
                    executed_at = NOW(),
                    completed_at = NOW()
                WHERE id = %(task_id)s
            """, {'task_id': task.task_id})

            logger.info(f"Task {task.task_id} completed")

        except Exception as e:
            self._handle_failure(task, e)

    def _handle_failure(self, task: ScheduledTask, error: Exception):
        """Handle task failure with retry logic."""
        self.db.execute("""
            UPDATE scheduled_tasks
            SET
                status = CASE
                    WHEN retry_count < max_retries THEN 'pending'
                    ELSE 'failed'
                END,
                retry_count = retry_count + 1,
                last_error = %(error)s,
                locked_by = NULL,
                locked_at = NULL,
                execute_at = CASE
                    WHEN retry_count < max_retries
                    THEN execute_at + (INTERVAL '1 minute' * POWER(2, retry_count))
                    ELSE execute_at
                END
            WHERE id = %(task_id)s
        """, {'task_id': task.task_id, 'error': str(error)})
```

### Гарантии выполнения

| Гарантия | Реализация | Trade-off |
|----------|------------|-----------|
| **At-least-once** | Retry на failure, ack после успеха | Возможны дубликаты |
| **At-most-once** | Ack сразу после получения | Возможна потеря |
| **Exactly-once** | Idempotency key + transactional outbox | Сложнее, медленнее |

**Рекомендация:** At-least-once + idempotency на стороне клиента.

### Восстановление после сбоев

```python
def recover_stale_tasks():
    """
    Called on worker startup.
    Recovers tasks that were locked but never completed.
    """
    db.execute("""
        UPDATE scheduled_tasks
        SET
            status = 'pending',
            locked_by = NULL,
            locked_at = NULL
        WHERE status = 'running'
          AND locked_at < NOW() - INTERVAL '5 minutes'
    """)
```

---

## Задача 4: LRU Cache

### Анализ задачи

**Что нужно сделать:** Реализовать кэш с вытеснением наименее недавно использованных элементов.

**Уточняющие вопросы:**
1. Какие типы ключей/значений? (Любые hashable ключи, любые значения)
2. Нужна ли thread safety? (Концептуально обсудим)
3. Нужен ли TTL для записей? (Как расширение)
4. Что делать при capacity=0? (Ничего не хранить)

### Выбор структур данных

Для O(1) операций нужны две структуры:

1. **HashMap (dict):** O(1) доступ по ключу
2. **Doubly Linked List:** O(1) вставка/удаление в любом месте

```
┌──────────────────────────────────────────────────────────────────┐
│                         LRU CACHE STRUCTURE                       │
└──────────────────────────────────────────────────────────────────┘

    HashMap (key → node reference)
    ┌─────────────────────────────┐
    │  "a" → Node(a)              │
    │  "b" → Node(b)              │
    │  "c" → Node(c)              │
    └─────────────────────────────┘

    Doubly Linked List (ordered by recency)

    HEAD                                               TAIL
    (dummy)                                           (dummy)
      │                                                  │
      ▼                                                  ▼
    ┌────┐    ┌────┐    ┌────┐    ┌────┐    ┌────┐   ┌────┐
    │    │◄──►│ c  │◄──►│ b  │◄──►│ a  │◄──►│    │   │    │
    │HEAD│    │    │    │    │    │    │    │TAIL│   │    │
    └────┘    └────┘    └────┘    └────┘    └────┘   └────┘
                 │         │         │
              Newest    Middle    Oldest
              (MRU)               (LRU)

    On access: Move node to front (after HEAD)
    On eviction: Remove node before TAIL
```

### Псевдокод

```
class LRUCache:
    initialize(capacity):
        self.capacity = capacity
        self.cache = HashMap()
        self.head = DummyNode()  # Most recently used
        self.tail = DummyNode()  # Least recently used
        head.next = tail
        tail.prev = head

    get(key):
        if key not in cache:
            return NOT_FOUND
        node = cache[key]
        move_to_front(node)  # Mark as recently used
        return node.value

    put(key, value):
        if key in cache:
            node = cache[key]
            node.value = value
            move_to_front(node)
        else:
            if len(cache) >= capacity:
                evict_lru()
            node = new Node(key, value)
            cache[key] = node
            add_to_front(node)

    move_to_front(node):
        remove_node(node)
        add_to_front(node)

    remove_node(node):
        node.prev.next = node.next
        node.next.prev = node.prev

    add_to_front(node):
        node.next = head.next
        node.prev = head
        head.next.prev = node
        head.next = node

    evict_lru():
        lru_node = tail.prev
        remove_node(lru_node)
        del cache[lru_node.key]
```

### Финальное решение

```python
from typing import TypeVar, Generic, Optional, Dict
from threading import RLock

K = TypeVar('K')
V = TypeVar('V')


class Node(Generic[K, V]):
    """Doubly linked list node."""
    __slots__ = ('key', 'value', 'prev', 'next')

    def __init__(self, key: K = None, value: V = None):
        self.key = key
        self.value = value
        self.prev: Optional[Node[K, V]] = None
        self.next: Optional[Node[K, V]] = None


class LRUCache(Generic[K, V]):
    """
    Least Recently Used (LRU) Cache implementation.

    Time Complexity:
        - get(): O(1)
        - put(): O(1)

    Space Complexity: O(capacity)

    Thread Safety: Basic locking provided via RLock.
    For high-concurrency, consider sharding or lock-free structures.
    """

    def __init__(self, capacity: int):
        """Initialize LRU cache with given capacity."""
        self.capacity = max(0, capacity)
        self.cache: Dict[K, Node[K, V]] = {}

        # Dummy head and tail for simpler edge case handling
        self.head: Node[K, V] = Node()
        self.tail: Node[K, V] = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

        # Thread safety
        self._lock = RLock()

    def get(self, key: K) -> Optional[V]:
        """Retrieve value for key, marking it as recently used."""
        with self._lock:
            if key not in self.cache:
                return None

            node = self.cache[key]
            self._move_to_front(node)
            return node.value

    def put(self, key: K, value: V) -> None:
        """Insert or update a key-value pair."""
        if self.capacity <= 0:
            return

        with self._lock:
            if key in self.cache:
                # Update existing
                node = self.cache[key]
                node.value = value
                self._move_to_front(node)
            else:
                # Insert new
                if len(self.cache) >= self.capacity:
                    self._evict_lru()

                node = Node(key, value)
                self.cache[key] = node
                self._add_to_front(node)

    def delete(self, key: K) -> bool:
        """Remove a key from the cache."""
        with self._lock:
            if key not in self.cache:
                return False

            node = self.cache[key]
            self._remove_node(node)
            del self.cache[key]
            return True

    def __len__(self) -> int:
        """Return current number of items in cache."""
        return len(self.cache)

    def __contains__(self, key: K) -> bool:
        """Check if key exists (without affecting LRU order)."""
        return key in self.cache

    # ========== Private Methods ==========

    def _add_to_front(self, node: Node[K, V]) -> None:
        """Add node right after head (most recently used position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: Node[K, V]) -> None:
        """Remove node from its current position."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_front(self, node: Node[K, V]) -> None:
        """Move existing node to front (mark as recently used)."""
        self._remove_node(node)
        self._add_to_front(node)

    def _evict_lru(self) -> None:
        """Remove the least recently used item (node before tail)."""
        lru_node = self.tail.prev
        if lru_node is self.head:
            return  # Empty cache

        self._remove_node(lru_node)
        del self.cache[lru_node.key]
```

### Сложность

| Операция | Time | Space |
|----------|------|-------|
| `get()` | O(1) | - |
| `put()` | O(1) | - |
| `delete()` | O(1) | - |
| **Total** | - | O(capacity) |

### Thread Safety

Текущая реализация использует `RLock` (reentrant lock):
- **Pros:** Простота, корректность
- **Cons:** Contention при высокой нагрузке

**Улучшения для production:**
1. **Sharded cache:** Несколько LRU кэшей с хэшированием ключа
2. **Read-write lock:** Позволяет параллельное чтение
3. **Lock-free structures:** CAS-based для максимальной производительности

```python
# Пример sharded cache
class ShardedLRUCache:
    def __init__(self, capacity: int, num_shards: int = 16):
        self.shards = [
            LRUCache(capacity // num_shards)
            for _ in range(num_shards)
        ]
        self.num_shards = num_shards

    def _get_shard(self, key) -> LRUCache:
        return self.shards[hash(key) % self.num_shards]

    def get(self, key):
        return self._get_shard(key).get(key)

    def put(self, key, value):
        self._get_shard(key).put(key, value)
```

### Production Improvements

1. **TTL (Time To Live):**
```python
@dataclass
class Node:
    key: K
    value: V
    expires_at: Optional[datetime] = None

def get(self, key):
    node = self.cache.get(key)
    if node and node.expires_at and datetime.now() > node.expires_at:
        self.delete(key)
        return None
    return node.value if node else None
```

2. **Metrics:**
```python
class LRUCacheWithMetrics(LRUCache):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.hits = 0
        self.misses = 0

    def get(self, key):
        result = super().get(key)
        if result is not None:
            self.hits += 1
        else:
            self.misses += 1
        return result

    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
```

---

## Общие советы для NerdWallet интервью

1. **Всегда задавайте уточняющие вопросы** перед тем как начать кодить
2. **Думайте вслух** — объясняйте свой thought process
3. **Начинайте с простого решения**, потом оптимизируйте
4. **Обсуждайте trade-offs** — нет идеального решения
5. **Не забывайте про edge cases** — пустые входы, граничные значения
6. **Тестирование** — покажите как бы вы тестировали код
7. **Не паникуйте если не успеваете** — процесс важнее результата
