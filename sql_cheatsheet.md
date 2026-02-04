# SQL — Шпаргалка для собеседования

## Основы SELECT

**Базовый синтаксис?**
```sql
SELECT column1, column2      -- что выбираем
FROM table_name              -- откуда
WHERE condition              -- фильтрация строк
ORDER BY column DESC/ASC     -- сортировка
LIMIT 10 OFFSET 5;           -- ограничение результата
```

**DISTINCT?**
Убирает дубликаты: `SELECT DISTINCT city FROM users;`

**Алиасы (AS)?**
Переименование колонок/таблиц: `SELECT name AS user_name FROM users u;`

**Операторы сравнения?**
- `=`, `<>` или `!=` — равно/не равно
- `<`, `>`, `<=`, `>=` — сравнение
- `LIKE 'A%'` — паттерн (`%` любые символы, `_` один символ)
- `IN (1, 2, 3)` — значение из списка
- `BETWEEN 10 AND 20` — диапазон (включительно)
- `IS NULL` / `IS NOT NULL` — проверка на NULL (не используй `= NULL`!)

---

## Агрегации

**Агрегатные функции?**
```sql
SELECT
    COUNT(*),           -- количество строк
    COUNT(column),      -- количество не-NULL значений
    COUNT(DISTINCT col),-- количество уникальных значений
    SUM(amount),        -- сумма
    AVG(amount),        -- среднее
    MIN(price),         -- минимум
    MAX(price)          -- максимум
FROM orders;
```

**GROUP BY?**
Группирует строки для агрегации:
```sql
SELECT city, COUNT(*) as user_count
FROM users
GROUP BY city;
```

**HAVING vs WHERE?**
WHERE фильтрует строки до группировки, HAVING — после:
```sql
SELECT city, COUNT(*) as cnt
FROM users
WHERE age > 18           -- фильтр строк
GROUP BY city
HAVING COUNT(*) > 100;   -- фильтр групп
```

---

## JOIN

**Типы JOIN?**

| JOIN | Результат |
|------|-----------|
| `INNER JOIN` | Только совпадающие строки из обеих таблиц |
| `LEFT JOIN` | Все из левой + совпадения из правой (NULL если нет) |
| `RIGHT JOIN` | Все из правой + совпадения из левой |
| `FULL OUTER JOIN` | Все из обеих таблиц |
| `CROSS JOIN` | Декартово произведение (каждый с каждым) |

**Синтаксис JOIN?**
```sql
SELECT u.name, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id
LEFT JOIN payments p ON o.id = p.order_id;
```

**Self-join?**
Соединение таблицы с самой собой (например, сотрудник → менеджер):
```sql
SELECT e.name, m.name as manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

**Найти записи без пары?**
```sql
-- Пользователи без заказов
SELECT u.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

---

## Подзапросы и CTE

**Подзапрос в WHERE?**
```sql
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);
```

**Подзапрос в SELECT?**
```sql
SELECT name,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count
FROM users u;
```

**Подзапрос в FROM?**
```sql
SELECT avg_amount FROM (
    SELECT user_id, AVG(amount) as avg_amount
    FROM orders GROUP BY user_id
) sub
WHERE avg_amount > 500;
```

**Correlated subquery?**
Подзапрос, который зависит от внешнего запроса (выполняется для каждой строки):
```sql
SELECT * FROM orders o1
WHERE amount > (
    SELECT AVG(amount) FROM orders o2
    WHERE o2.user_id = o1.user_id  -- связь с внешним запросом
);
```

**CTE (Common Table Expression)?**
Именованный временный результат — читабельнее подзапросов:
```sql
WITH high_spenders AS (
    SELECT user_id, SUM(amount) as total
    FROM orders
    GROUP BY user_id
    HAVING SUM(amount) > 10000
)
SELECT u.name, hs.total
FROM users u
JOIN high_spenders hs ON u.id = hs.user_id;
```

**Рекурсивный CTE?**
Для иерархий (дерево категорий, орг. структура):
```sql
WITH RECURSIVE subordinates AS (
    SELECT id, name, manager_id FROM employees WHERE id = 1  -- начало
    UNION ALL
    SELECT e.id, e.name, e.manager_id
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id               -- рекурсия
)
SELECT * FROM subordinates;
```

---

## Оконные функции

**Что это?**
Вычисления по группе строк без схлопывания в одну (в отличие от GROUP BY):
```sql
SELECT name, department, salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees;
-- Каждая строка сохраняется + добавляется среднее по отделу
```

**ROW_NUMBER, RANK, DENSE_RANK?**
```sql
SELECT name, salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_num,  -- 1,2,3,4,5
    RANK() OVER (ORDER BY salary DESC) as rank,           -- 1,2,2,4,5 (пропуск)
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense     -- 1,2,2,3,4 (без пропуска)
FROM employees;
```

**PARTITION BY?**
Разбивает на группы для отдельного вычисления:
```sql
-- Ранг внутри каждого отдела
SELECT name, department, salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank
FROM employees;
```

**LAG / LEAD?**
Доступ к предыдущей/следующей строке:
```sql
SELECT date, revenue,
    LAG(revenue, 1) OVER (ORDER BY date) as prev_revenue,   -- предыдущее значение
    LEAD(revenue, 1) OVER (ORDER BY date) as next_revenue,  -- следующее значение
    revenue - LAG(revenue) OVER (ORDER BY date) as diff     -- изменение
FROM sales;
```

**Агрегаты как оконные функции?**
```sql
SELECT date, amount,
    SUM(amount) OVER (ORDER BY date) as running_total,              -- накопительная сумма
    AVG(amount) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg
FROM orders;
```

**ROWS BETWEEN?**
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — от начала до текущей
- `ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING` — окно ±3 строки
- `ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING` — от текущей до конца

---

## Модификация данных

**INSERT?**
```sql
INSERT INTO users (name, email) VALUES ('John', 'john@mail.com');
INSERT INTO users (name, email) VALUES ('A', 'a@m.com'), ('B', 'b@m.com');  -- несколько
INSERT INTO archive SELECT * FROM orders WHERE date < '2024-01-01';        -- из SELECT
```

**UPDATE?**
```sql
UPDATE users SET status = 'active' WHERE created_at > '2024-01-01';
UPDATE orders o SET total = (SELECT SUM(price) FROM items i WHERE i.order_id = o.id);
```

**DELETE?**
```sql
DELETE FROM users WHERE last_login < '2023-01-01';
```

**UPSERT (INSERT ... ON CONFLICT)?**
PostgreSQL:
```sql
INSERT INTO users (id, name, email) VALUES (1, 'John', 'john@mail.com')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email;
```
MySQL: `INSERT ... ON DUPLICATE KEY UPDATE`

---

## Типичные задачи собеседований

**N-ая по величине зарплата?**
```sql
-- Способ 1: OFFSET
SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 2;  -- 3-я

-- Способ 2: оконная функция
SELECT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rnk
    FROM employees
) sub WHERE rnk = 3;
```

**Найти дубликаты?**
```sql
SELECT email, COUNT(*) as cnt
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

**Running total (накопительная сумма)?**
```sql
SELECT date, amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM orders;
```

**Year-over-year сравнение?**
```sql
SELECT
    EXTRACT(YEAR FROM date) as year,
    EXTRACT(MONTH FROM date) as month,
    SUM(revenue) as revenue,
    LAG(SUM(revenue)) OVER (ORDER BY EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date)) as prev_year
FROM sales
GROUP BY 1, 2;
```

**Top N в каждой группе?**
```sql
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rn
    FROM employees
) sub WHERE rn <= 3;  -- топ-3 по зарплате в каждом отделе
```

**Записи без пары (антиджоин)?**
```sql
SELECT u.* FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;  -- пользователи без заказов
```

**Pivot (строки в столбцы)?**
```sql
SELECT
    user_id,
    SUM(CASE WHEN month = 'Jan' THEN amount ELSE 0 END) as jan,
    SUM(CASE WHEN month = 'Feb' THEN amount ELSE 0 END) as feb,
    SUM(CASE WHEN month = 'Mar' THEN amount ELSE 0 END) as mar
FROM orders
GROUP BY user_id;
```

**Consecutive days (подряд идущие дни)?**
```sql
SELECT user_id, MIN(login_date) as streak_start, COUNT(*) as streak_length
FROM (
    SELECT user_id, login_date,
        login_date - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date)::int as grp
    FROM logins
) sub
GROUP BY user_id, grp
HAVING COUNT(*) >= 3;  -- серии от 3 дней
```

**Сотрудники с зарплатой выше менеджера?**
```sql
SELECT e.name as employee, e.salary, m.name as manager, m.salary as manager_salary
FROM employees e
JOIN employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```

**Удалить дубликаты (оставить одну запись)?**
```sql
-- PostgreSQL: удаляем все кроме минимального id
DELETE FROM users
WHERE id NOT IN (
    SELECT MIN(id)
    FROM users
    GROUP BY email
);

-- Или через CTE
WITH duplicates AS (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) as rn
    FROM users
)
DELETE FROM users WHERE id IN (SELECT id FROM duplicates WHERE rn > 1);
```

**Медиана?**
```sql
-- PostgreSQL
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) as median
FROM employees;

-- Универсальный способ
SELECT AVG(salary) as median FROM (
    SELECT salary FROM (
        SELECT salary, ROW_NUMBER() OVER (ORDER BY salary) as rn,
               COUNT(*) OVER () as cnt
        FROM employees
    ) sub
    WHERE rn IN (cnt/2, cnt/2 + 1)  -- для чётного кол-ва берём два средних
) mid;
```

**Первая покупка каждого пользователя?**
```sql
-- Способ 1: оконная функция
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) as rn
    FROM orders
) sub WHERE rn = 1;

-- Способ 2: коррелированный подзапрос
SELECT * FROM orders o1
WHERE created_at = (
    SELECT MIN(created_at) FROM orders o2 WHERE o2.user_id = o1.user_id
);

-- Способ 3: DISTINCT ON (PostgreSQL)
SELECT DISTINCT ON (user_id) *
FROM orders
ORDER BY user_id, created_at;
```

**Пропуски в последовательности (gaps)?**
```sql
-- Найти пропущенные id
SELECT prev_id + 1 as gap_start, id - 1 as gap_end
FROM (
    SELECT id, LAG(id) OVER (ORDER BY id) as prev_id
    FROM orders
) sub
WHERE id - prev_id > 1;
```

**Retention: вернувшиеся на следующий день?**
```sql
SELECT
    t1.login_date,
    COUNT(DISTINCT t1.user_id) as day_users,
    COUNT(DISTINCT t2.user_id) as retained_users,
    ROUND(100.0 * COUNT(DISTINCT t2.user_id) / COUNT(DISTINCT t1.user_id), 2) as retention_rate
FROM logins t1
LEFT JOIN logins t2 ON t1.user_id = t2.user_id
    AND t2.login_date = t1.login_date + INTERVAL '1 day'
GROUP BY t1.login_date;
```

**Пользователи с покупками каждый месяц года?**
```sql
SELECT user_id
FROM orders
WHERE EXTRACT(YEAR FROM created_at) = 2024
GROUP BY user_id
HAVING COUNT(DISTINCT EXTRACT(MONTH FROM created_at)) = 12;
```

**Товары, которые покупали вместе?**
```sql
SELECT o1.product_id as product_1, o2.product_id as product_2, COUNT(*) as times_bought_together
FROM order_items o1
JOIN order_items o2 ON o1.order_id = o2.order_id AND o1.product_id < o2.product_id
GROUP BY o1.product_id, o2.product_id
ORDER BY times_bought_together DESC
LIMIT 10;
```

**Cumulative percentage (доля от общего)?**
```sql
SELECT
    category,
    revenue,
    SUM(revenue) OVER (ORDER BY revenue DESC) as cumulative,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER (), 2) as cumulative_pct
FROM category_sales;
```

**Пересечение диапазонов дат (конфликты бронирований)?**
```sql
SELECT a.id, b.id, a.start_date, a.end_date, b.start_date, b.end_date
FROM bookings a
JOIN bookings b ON a.id < b.id
    AND a.room_id = b.room_id
    AND a.start_date < b.end_date
    AND a.end_date > b.start_date;  -- условие пересечения
```

**Active users (DAU/MAU)?**
```sql
-- DAU
SELECT login_date, COUNT(DISTINCT user_id) as dau
FROM logins
GROUP BY login_date;

-- MAU
SELECT DATE_TRUNC('month', login_date) as month, COUNT(DISTINCT user_id) as mau
FROM logins
GROUP BY 1;

-- DAU/MAU ratio (stickiness)
WITH dau AS (
    SELECT login_date, COUNT(DISTINCT user_id) as daily_users
    FROM logins GROUP BY 1
),
mau AS (
    SELECT DATE_TRUNC('month', login_date) as month, COUNT(DISTINCT user_id) as monthly_users
    FROM logins GROUP BY 1
)
SELECT d.login_date, d.daily_users, m.monthly_users,
    ROUND(100.0 * d.daily_users / m.monthly_users, 2) as stickiness
FROM dau d
JOIN mau m ON DATE_TRUNC('month', d.login_date) = m.month;
```

**Процентили по группам?**
```sql
SELECT department, salary,
    NTILE(4) OVER (PARTITION BY department ORDER BY salary) as quartile,
    PERCENT_RANK() OVER (PARTITION BY department ORDER BY salary) as percentile
FROM employees;
```

**MoM (Month-over-Month) рост?**
```sql
WITH monthly AS (
    SELECT DATE_TRUNC('month', date) as month, SUM(revenue) as revenue
    FROM sales GROUP BY 1
)
SELECT month, revenue,
    LAG(revenue) OVER (ORDER BY month) as prev_month,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) /
          LAG(revenue) OVER (ORDER BY month), 2) as mom_growth_pct
FROM monthly;
```

**Найти "острова" (группы подряд идущих значений)?**
```sql
-- Найти периоды когда сервер был down (status = 'down')
SELECT MIN(check_time) as down_start, MAX(check_time) as down_end, COUNT(*) as duration
FROM (
    SELECT check_time, status,
        ROW_NUMBER() OVER (ORDER BY check_time) -
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY check_time) as grp
    FROM server_status
) sub
WHERE status = 'down'
GROUP BY grp;
```

**Второй максимум без оконных функций?**
```sql
-- Способ 1: подзапрос
SELECT MAX(salary) FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- Способ 2: LIMIT OFFSET
SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;

-- Способ 3: NOT IN
SELECT MAX(salary) FROM employees
WHERE salary NOT IN (SELECT MAX(salary) FROM employees);
```

**Разница между текущей и следующей записью?**
```sql
SELECT id, value,
    LEAD(value) OVER (ORDER BY id) - value as diff_to_next,
    value - LAG(value) OVER (ORDER BY id) as diff_from_prev
FROM measurements;
```

---

## Производительность

**EXPLAIN / EXPLAIN ANALYZE?**
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@mail.com';
```
- `Seq Scan` — полный перебор таблицы (медленно на больших таблицах)
- `Index Scan` — использование индекса (быстро)
- `actual time` — реальное время выполнения

**Когда индексы помогают?**
- Колонки в WHERE, JOIN, ORDER BY
- Колонки с высокой селективностью (много уникальных значений)
- Покрывающие индексы (все нужные колонки в индексе)

**Когда индексы НЕ помогают?**
- Маленькие таблицы (seq scan быстрее)
- Низкая селективность (пол: M/F — индекс бесполезен)
- Функции на колонке: `WHERE UPPER(name) = 'JOHN'` — индекс на name не сработает
- `LIKE '%text'` — поиск с % в начале

**N+1 проблема?**
Один запрос на список + N запросов на детали каждого элемента.
Решение: JOIN или batch-запросы (`WHERE id IN (...)`).

**Оптимизация JOIN?**
- Меньшую таблицу ставить первой (хотя оптимизатор обычно сам разберётся)
- Индексы на колонках JOIN
- Избегать функций в условии JOIN

---

## Типичные вопросы и ответы

**WHERE vs HAVING?**
WHERE фильтрует строки до GROUP BY, HAVING — группы после. В HAVING можно использовать агрегатные функции.

**UNION vs UNION ALL?**
UNION убирает дубликаты (дороже), UNION ALL оставляет все строки.

**DELETE vs TRUNCATE?**
DELETE — можно с WHERE, логирует каждую строку, можно откатить. TRUNCATE — удаляет всё, быстрее, сбрасывает автоинкремент.

**DROP vs TRUNCATE vs DELETE?**
DROP — удаляет таблицу целиком. TRUNCATE — очищает данные, структура остаётся. DELETE — удаляет строки по условию.

**Primary Key vs Unique?**
PK: одна на таблицу, не NULL, кластерный индекс. Unique: может быть несколько, допускает NULL.

**Поведение NULL?**
- `NULL = NULL` → NULL (не TRUE!)
- `NULL <> 1` → NULL
- `COUNT(column)` игнорирует NULL, `COUNT(*)` — нет
- `SUM/AVG` игнорируют NULL
- `ORDER BY` — NULL в начале или конце (зависит от СУБД)
- Для проверки: `IS NULL` / `IS NOT NULL`

**INNER JOIN vs LEFT JOIN — что быстрее?**
Зависит от данных и индексов. INNER JOIN может быть быстрее, если отфильтровывает много строк.

**Нормализация?**
- 1NF: атомарные значения (нет массивов в ячейках)
- 2NF: нет частичной зависимости от составного ключа
- 3NF: нет транзитивных зависимостей (не-ключевые поля зависят только от ключа)

**Индекс на несколько колонок?**
Композитный индекс работает слева направо: индекс на (a, b, c) поможет в WHERE a=1, WHERE a=1 AND b=2, но НЕ в WHERE b=2 AND c=3.

**Транзакции ACID?**
- Atomicity — всё или ничего
- Consistency — данные валидны до и после
- Isolation — транзакции не видят незакоммиченные изменения друг друга
- Durability — закоммиченное сохранится даже при сбое
