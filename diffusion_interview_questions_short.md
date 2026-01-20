# Diffusion Interview Questions - Краткая версия

Основные идеи для быстрого повторения перед собеседованием.

---

## Frontend Core (Basic)

### TypeScript 5.5

**1. Что такое TypeScript и зачем он нужен?**
TypeScript — надмножество JavaScript с статической типизацией от Microsoft. Ошибки типов выявляются на этапе компиляции, а не в рантайме. Даёт улучшенную IDE-поддержку (автодополнение, рефакторинг), типы служат документацией, новые разработчики быстрее входят в проект. Любой валидный JS-код является валидным TS-кодом — можно мигрировать постепенно.

**2. В чём разница между `type` и `interface`?**
`interface` — для объектов и классов, поддерживает extends и declaration merging (можно дополнять интерфейс в разных местах). `type` — более гибкий: поддерживает union types (`string | number`), intersection (`A & B`), mapped types, примитивы и computed properties. Рекомендация: `interface` для публичных API и объектов, `type` для unions, intersections и сложных типов.

**3. Что такое Generics и как их применять?**
Generics позволяют создавать переиспользуемые компоненты, работающие с разными типами, сохраняя типобезопасность. Вместо `any` или отдельных функций для каждого типа — одна generic-функция: `function identity<T>(value: T): T`. TypeScript автоматически выводит тип. Используются в API-клиентах (`fetch<User>('/api/users')`), React-компонентах (`List<Product>`), утилитарных функциях. Можно добавлять constraints: `<T extends HasLength>`.

**4. Какие утилитарные типы чаще всего используются?**
`Partial<T>` — все поля становятся optional (для DTO обновления). `Required<T>` — все поля обязательные. `Pick<T, 'a' | 'b'>` — выбрать только указанные поля. `Omit<T, 'password'>` — исключить поля (публичный профиль без пароля). `Record<string, User>` — словарь с динамическими ключами. `ReturnType<typeof fn>` — тип возвращаемого значения функции. Можно комбинировать: `Partial<Pick<User, 'name' | 'email'>>`.

### Vite 7

**5. Почему Vite быстрее Webpack?**
Архитектурное отличие: Webpack бандлит всё приложение перед стартом dev-сервера, Vite использует native ESM — браузер сам запрашивает модули по требованию. Зависимости из node_modules пре-бандлятся через esbuild (в 10-100x быстрее Webpack) и кэшируются. На большом проекте Webpack стартует 30-60 секунд, Vite — менее секунды. HMR в Vite обновляет только изменённый модуль, не перестраивая весь граф.

**6. Как работает Hot Module Replacement (HMR) в Vite?**
Vite отслеживает изменения файлов через chokidar, при изменении отправляет сообщение браузеру через WebSocket. Браузер запрашивает обновлённый модуль и заменяет его в памяти. React Fast Refresh (через `@vitejs/plugin-react`) перерисовывает только изменившиеся компоненты, сохраняя state. HMR API: `import.meta.hot.accept()` для принятия обновлений, `dispose()` для очистки. Типичные проблемы: HMR ломается если компонент экспортирует не только React-компоненты.

**7. Как настроить Vite для production?**
Production-сборка принципиально отличается от dev: code splitting через `manualChunks` в rollupOptions (разделить vendor, router, query — при обновлении зависимости пользователи скачивают только изменившийся чанк). Tree shaking удаляет неиспользуемый код. Minification через esbuild (быстрее) или terser (больше контроля). Asset hashing в именах файлов для cache busting. `chunkSizeWarningLimit` для контроля размера чанков.

### Tailwind CSS 3.4

**8. Что такое utility-first подход и в чём его преимущества?**
Utility-first — стили применяются через множество маленьких классов (`p-4 bg-white rounded-lg`) вместо семантических (`.card`). Философия: стили и разметка неразрывно связаны, их объединение в компонентах упрощает поддержку. Преимущества: нет конфликтов имён (не нужен BEM), нет мёртвого CSS, консистентность из дизайн-системы, быстрая разработка без переключения между файлами. Недостатки: длинные списки классов, кривая обучения. Хорошо работает с компонентным подходом (React, Vue).

**9. Как настроить и кастомизировать Tailwind?**
В `tailwind.config.js`: `content` указывает какие файлы сканировать (критично — без этого классы не работают). `theme.extend` добавляет новые значения к существующим (цвета, шрифты, spacing, анимации) — рекомендуемый способ. `theme` напрямую полностью заменяет дефолтные значения. Плагины: `@tailwindcss/forms`, `@tailwindcss/typography`. Можно создавать кастомные утилиты через `addUtilities()`. Директива `@apply` для переиспользуемых компонентных классов.

**10. Как работает JIT-компиляция в Tailwind?**
До JIT полный Tailwind CSS занимал ~3.7MB, в production через purge оставалось ~10KB. JIT генерирует CSS только для используемых классов на лету: сканирует файлы из `content`, находит классы через regex, генерирует CSS. Революционная возможность — arbitrary values: `w-[137px]`, `bg-[#1da1f2]`, `[mask-image:linear-gradient(...)]`. Dev-бандл теперь равен production. Все варианты (`hover:`, `focus:`, `dark:`) доступны без конфигурации.

**11. Как организовать responsive design в Tailwind?**
Mobile-first подход: стили без префикса применяются ко всем размерам, `sm:`/`md:`/`lg:`/`xl:` означают "от этого breakpoint и выше" (соответствует `@media (min-width: ...)`). Breakpoints: sm=640px, md=768px, lg=1024px, xl=1280px. Пример: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`. Типичная ошибка: `md:flex` без `flex` для мобильных — элемент скрыт на мобильных. Для скрытия/показа: `hidden md:block` (скрыть на мобильных, показать на md+).

---

## Frontend Advanced (Intermediate)

### TanStack Query (React Query)

**12. В чём разница между серверным и клиентским состоянием?**
Клиентское состояние (открыта ли модалка, выбранный таб) — синхронное, предсказуемое, полностью под контролем фронтенда. Серверное состояние (список пользователей, детали заказа) — асинхронное, может устареть, требует синхронизации с источником правды на сервере. Проблема смешивания: если хранить серверные данные в Redux, вы сами отвечаете за загрузку, кэширование, инвалидацию, ретраи, дедупликацию. TanStack Query решает это из коробки.

**13. Как работают useQuery и useMutation?**
`useQuery` — "подписка на данные" для GET-запросов. Возвращает `data`, `isLoading`, `isFetching`, `isError`, `refetch`. Ключевые параметры: `queryKey` (массив зависимостей), `staleTime`, `gcTime`, `enabled` (для отложенных запросов). `useMutation` — для POST/PUT/DELETE, изменение данных на сервере. Возвращает `mutate()`, `isPending`. В `onSuccess` инвалидируем связанные queries через `queryClient.invalidateQueries()`. Важно: `queryKey` должен включать все переменные запроса.

**14. В чём разница между staleTime и gcTime?**
`staleTime` — срок годности данных. Пока не истёк, данные "свежие" и refetch не происходит. Default: 0 (сразу stale, refetch при каждом монтировании). `gcTime` (раньше cacheTime) — сколько держать данные в кэше после размонтирования компонента. Default: 5 минут. Позволяет показать stale данные сразу при возврате на страницу, пока идёт refetch. Рекомендации: статичные данные (справочники) — `staleTime: Infinity`, часто меняющиеся — маленькое значение.

**15. Как реализовать Optimistic Updates?**
Обновляем UI до ответа сервера для мгновенной обратной связи (лайк, чекбокс). `onMutate`: отменить исходящие refetch-запросы, сохранить предыдущее значение, оптимистично обновить кэш через `setQueryData`. `onError`: откатить к сохранённому значению, показать toast. `onSettled`: синхронизировать через `invalidateQueries`. Когда НЕ использовать: операции с низкой вероятностью успеха (платежи), сложные бизнес-валидации, когда откат запутает пользователя.

**16. Как работает кэширование и инвалидация?**
Query keys работают как пути в файловой системе: `['todos']` — корень, `['todos', 'detail', 1]` — конкретный элемент. `invalidateQueries(['todos'])` инвалидирует все вложенные ключи. `setQueryData` — прямое обновление кэша (для optimistic updates). `prefetchQuery` — загрузка заранее (при hover на ссылку). `removeQueries` — полное удаление из кэша. `exact: true` — только точное совпадение ключа.

### ShadCN/UI + Radix UI

**17. Что такое headless UI компоненты?**
Headless UI содержит только логику и accessibility (управление состоянием, keyboard navigation, ARIA-атрибуты, focus trap), без стилей. Решает проблему традиционных UI-библиотек (Material UI, Bootstrap), где переопределение стилей превращается в борьбу с CSS-специфичностью. Особенно важно для: модальных окон (focus trap, escape), dropdown/select (keyboard navigation, typeahead), tabs (ARIA roles), tooltip (позиционирование).

**18. Какие преимущества у Radix UI?**
Наиболее полный набор headless-компонентов с качественной документацией. Accessibility из коробки (ARIA, keyboard, screen reader, focus management). Compound components паттерн (`Select.Root`, `Select.Trigger`, `Select.Content`) даёт гибкость в структуре. `Portal` рендерит контент в конце body (правильный z-index). `asChild` позволяет использовать свой элемент. Data-атрибуты (`data-state="open"`) для стилизации состояний в CSS. Работает в controlled и uncontrolled режимах.

**19. Как работает ShadCN/UI?**
ShadCN/UI — не npm-пакет, а коллекция copy-paste компонентов на базе Radix UI + Tailwind CSS. Компоненты копируются в проект командой `npx shadcn-ui add button` — код становится вашим, полный контроль и кастомизация. Нет версионирования и автоматических обновлений — это и плюс (независимость), и минус (больше кода для поддержки). Использует `class-variance-authority` (cva) для создания вариантов компонентов (default, destructive, outline, ghost).

### React Router

**20. Как работают Nested Routes и Outlet?**
Вложенные маршруты создают иерархическую структуру с общими layout-компонентами. Думайте о роутах как о матрёшках: внешняя — RootLayout (header, footer), внутри — DashboardLayout (sidebar), ещё внутри — конкретная страница. `<Outlet />` показывает, где рендерить дочерний контент. Layout routes без path — только оборачивают дочерние в layout, не добавляют сегмент в URL. Устраняет дублирование общих элементов на каждой странице.

**21. Что такое Loaders и Actions в React Router 6.4+?**
Loaders — загрузка данных ДО рендера компонента (вдохновлено Remix). Традиционный подход: компонент рендерится → useEffect → loading → данные → контент. С Loaders: данные готовы к моменту рендера, нет "моргания". `useLoaderData()` для получения данных. Actions — обработка форм (POST/PUT/DELETE), `<Form>` автоматически вызывает action и ревалидирует loaders. Параллельная загрузка для вложенных routes, автоматическая отмена при уходе со страницы.

**22. Как реализовать Protected Routes?**
ProtectedRoute — wrapper-компонент, проверяющий авторизацию. Показывает loading пока состояние auth загружается (не мелькать редиректом!). Если не авторизован — `<Navigate to="/login" state={{ from: location }} replace />` с сохранением intended URL. После успешного логина — `navigate(from, { replace: true })`. Layout route без path для защиты группы роутов — все дочерние автоматически защищены. Не проверяйте auth в каждом компоненте отдельно.

**23. Как работать с параметрами и навигацией?**
`useParams<{ id: string }>()` — path params (`/products/:id`) для идентификации ресурса. `useSearchParams()` — query params (`?sort=price&page=2`) для опциональных модификаторов (сортировка, фильтрация, пагинация). `useNavigate()` — программная навигация: `navigate('/path')`, `navigate(-1)` для "назад", `{ state: {...} }` для данных не в URL. `Link` — простая навигация, `NavLink` — с автоматическим highlight активного пункта через `className={({ isActive }) => ...}`.

---

## Backend & Database (Intermediate)

### SQLAlchemy 2.0

**24. В чём разница между SQLAlchemy ORM и Core?**
SQLAlchemy — две библиотеки в одной. Core — низкоуровневый SQL toolkit, работа с Row-объектами, полный контроль над SQL, выше производительность. ORM — object-relational mapper поверх Core, работа с mapped-классами, автоматический SQL, удобно для CRUD. Когда ORM: создание, чтение, обновление, удаление объектов, работа со связями. Когда Core: сложные аналитические запросы с множеством JOIN, bulk-операции, оптимизация. Можно смешивать в одном проекте.

**25. Как работает Session и паттерн Unit of Work?**
Session — "рабочая область", отслеживающая все изменения объектов. Unit of Work (паттерн Фаулера): вместо SQL на каждое изменение, Session накапливает их и применяет оптимально при commit. Состояния объектов: transient (создан, не в session), pending (add(), не в БД), persistent (в БД, отслеживается), detached (был persistent, session закрыта). `flush()` — отправить SQL, транзакция открыта (полезно для auto-generated ID до commit). `commit()` — flush + commit транзакции.

**26. Как настроить связи и что такое lazy loading?**
`relationship()` с `back_populates` для двусторонних связей. Lazy loading — связанные объекты загружаются при обращении к атрибуту. Стратегии: `select` (default) — отдельный SELECT, опасность N+1 в циклах. `joined` — JOIN в основном запросе, хорошо для one-to-one/many-to-one. `selectin` — один SELECT с IN, лучше для one-to-many. `raise` — запретить ленивую загрузку. Best practice: `lazy='raise'` по умолчанию + явный `joinedload()`/`selectinload()` в запросах — предсказуемая загрузка.

**27. Как использовать Async SQLAlchemy?**
FastAPI асинхронный, синхронный SQLAlchemy блокирует event loop. `create_async_engine('postgresql+asyncpg://...')` с async-драйвером (asyncpg для PostgreSQL). `AsyncSession` из `async_sessionmaker`. Особенности: lazy loading не работает — нужны явные options, `expire_on_commit=False` чтобы объекты оставались доступны после commit, только async методы (`await session.execute()`, `await session.get()`). FastAPI интеграция через `Depends(get_db)` с `async with async_session() as session: yield session`.

**28. Что такое N+1 проблема и как её решить?**
Для загрузки N связанных объектов выполняется 1+N запросов: 1 для основных + N для связей каждого. 100 пользователей × 1 запрос на посты = 101 запрос вместо 1-2. Обнаружить: `echo=True` в engine, профилировщики. Решения: `joinedload(User.posts)` — JOIN, хорошо для небольших связей, но дублирует данные при one-to-many. `selectinload(User.posts)` — два запроса (SELECT + SELECT ... WHERE id IN), лучше для one-to-many. `subqueryload` — через подзапрос, когда IN-список слишком большой.

### Pydantic

**29. Как работает валидация данных в Pydantic?**
Декларативная валидация через типы Python: `name: str = Field(min_length=1, max_length=100)`. Автоматическая конвертация типов (строка "123" → int 123). `field_validator` для кастомной логики и трансформации (`email.lower()`). `model_validator(mode='after')` для валидации нескольких полей (start_date < end_date). `ValidationError` — структурированная ошибка со списком всех проблем. FastAPI интеграция — автогенерация OpenAPI схемы.

**30. Как управлять настройками приложения через Pydantic?**
`BaseSettings` из pydantic-settings: чтение из env-переменных и .env файлов, валидация при старте (приложение не запустится с неправильным конфигом), типизация (`database_pool_size: int` вместо `int(os.getenv(...))`). `SecretStr` — не выводится в логах. `env_prefix='APP_'` избегает конфликтов с системными переменными. Computed properties для сложных значений. `@lru_cache` для `get_settings()` — настройки читаются один раз.

**31. Как работает сериализация и десериализация?**
Типичный flow: SQLAlchemy ORM → Pydantic model → JSON API. `from_attributes=True` (раньше `orm_mode`) для парсинга ORM-объектов. `model_dump()` в dict, `model_dump_json()` в JSON строку. `by_alias=True` — использовать alias в выводе. Alias для snake_case в Python ↔ camelCase в API: `full_name: str = Field(alias='name')`. `field_serializer` для кастомной сериализации (datetime → строка в нужном формате).

**32. Как использовать кастомные валидаторы и Field?**
`mode='before'` — до парсинга типа, получаете "сырые" данные, можете преобразовать. `mode='after'` (default) — после парсинга, данные уже валидны по типу. `mode='wrap'` — вокруг всего процесса, перехват и изменение поведения. Annotated типы — современный подход: `PositiveInt = Annotated[int, Gt(0)]`, composable переиспользуемые типы. `model_validator` для проверок зависящих от нескольких полей. `Field(examples=['...'])` для OpenAPI документации.

### PostgreSQL + Aurora

**33. Какие типы индексов есть в PostgreSQL?**
B-tree (99% случаев) — универсальный для `=`, `<`, `>`, `BETWEEN`, ORDER BY. GIN (Generalized Inverted Index) — для "содержит" операций: массивы (`@>`), JSONB, полнотекстовый поиск (`@@`). GiST — геоданные (PostGIS). Hash — только `=`, редко нужен. BRIN — очень большие таблицы с физической корреляцией (логи с timestamp). Partial index (`WHERE status = 'active'`) — только для части данных, меньше размер. Составной индекс работает слева направо. `EXPLAIN ANALYZE` для проверки использования.

**34. Что такое ACID и как работают транзакции?**
**A**tomicity — всё или ничего, **C**onsistency — валидные состояния, **I**solation — параллельные транзакции изолированы, **D**urability — после commit данные сохранены. Уровни изоляции: READ COMMITTED (default в PostgreSQL) — видны только закоммиченные, REPEATABLE READ — данные не меняются в рамках транзакции, SERIALIZABLE — полная изоляция. Trade-off: выше изоляция → больше блокировок → ниже производительность. SERIALIZABLE для финансовых операций, но готовьтесь к ретраям при конфликтах.

**35. Чем Aurora отличается от обычного PostgreSQL?**
Ключевое отличие — storage отделён от compute: распределённая система с 6 копиями в 3 AZ. Автоматический failover < 30 секунд без потери данных. До 15 read replicas с общим хранилищем (минимальный lag < 100ms). Storage auto-scaling до 128 TB. Когда Aurora: высокие требования к доступности (99.99%+), автоматический failover критичен, данные растут непредсказуемо. Когда обычный RDS: бюджет ограничен (~20% дороже), нужны специфические расширения, планируете миграцию с AWS.

**36. Как настроить Connection Pooling?**
Создание соединения занимает 20-100ms (TCP, auth, SSL). Пул держит готовые соединения, запрос берёт из пула мгновенно. SQLAlchemy: `pool_size` (базовое количество, 5-10), `max_overflow` (дополнительные при пике), `pool_timeout` (ожидание свободного), `pool_recycle` (пересоздавать через N секунд, важно для Aurora/RDS), `pool_pre_ping` (проверять перед использованием). PgBouncer — внешний pooler для serverless, микросервисов, нескольких приложений к одной БД.

### Alembic

**37. Как работают миграции и версионирование схемы?**
Alembic — "git для схемы БД", стандарт для SQLAlchemy. Хранит текущую версию в таблице `alembic_version`, каждая миграция имеет ID и ссылку на предыдущую (цепочка). `alembic upgrade head` — применить все миграции, `alembic downgrade -1` — откатить последнюю. Зачем: воспроизводимость (новый разработчик получает актуальную схему), история изменений, откат при проблемах, автоматическое применение в CI/CD. `env.py` импортирует модели для autogenerate.

**38. В чём разница между autogenerate и ручными миграциями?**
`alembic revision --autogenerate` сравнивает модели с БД. Обнаруживает: добавление/удаление таблиц и колонок, изменение типов (с ограничениями), индексы, constraints. НЕ обнаруживает: переименование (видит как drop + create), изменение данных, server_default. Ручная миграция нужна для: `op.rename_table()`, `op.alter_column(..., new_column_name=...)`, data migrations (`op.execute('UPDATE ...')`), expand/contract паттерна для миграций без даунтайма.

**39. Как безопасно откатывать миграции?**
Всегда писать `downgrade()`, даже если "никогда не понадобится". Для необратимых операций (DROP COLUMN с данными) — явный `raise NotImplementedError('Data loss would occur')`. Production workflow: `alembic upgrade head --sql > migration.sql` для ревью, тест на staging с копией production данных, бэкап production БД, применить в maintenance window, мониторить ошибки. Разделяйте schema и data миграции.

---

## Infrastructure & DevOps (Advanced)

### Docker

**40. В чём разница между контейнерами и виртуальными машинами?**
VM эмулирует полный компьютер с собственной ОС через гипервизор. Контейнер — изолированный процесс, использующий ядро хост-системы (namespace, cgroups). Практические последствия: контейнер запускается за секунды (просто процесс), VM — за минуты (загрузка ОС). Сотни контейнеров vs десятки VM на одном хосте. Размер: МБ vs ГБ. VM более изолированы (разные ядра). Контейнеры — для микросервисов, CI/CD, dev-окружений. VM — для разных ОС, максимальной изоляции.

**41. Какие best practices для написания Dockerfile?**
Конкретные теги (`python:3.11-slim-bookworm`, не `latest`). Non-root user для безопасности. Копировать зависимости отдельно от кода — кэширование слоёв (изменился код, зависимости из кэша). Группировать RUN команды (`apt-get update && apt-get install && rm -rf /var/lib/apt/lists/*`). `.dockerignore` для `.git`, `__pycache__`, `node_modules`. ENTRYPOINT + CMD. Типичные ошибки: `COPY . .` в начале инвалидирует весь кэш, секреты в ENV видны в `docker inspect`.

**42. Как работают multi-stage builds?**
Разделение сборки и runtime для уменьшения размера образа. Stage 1 (builder): Node.js + npm install + npm run build. Stage 2 (production): nginx + `COPY --from=builder /app/dist`. Финальный образ содержит только последний stage — нет node_modules, компиляторов, build tools. Результат: 100MB вместо 1GB+. Дополнительные преимущества: меньше уязвимостей (меньше пакетов), секреты сборки не попадают в финальный образ.

**43. Как работает Docker Compose?**
Описывает несколько сервисов в одном YAML: app, db, redis, worker. `depends_on` с `condition: service_healthy` — app стартует после готовности БД. `healthcheck` для проверки готовности. `volumes` — named volumes для персистентности БД, bind mounts для hot reload. `networks` — изоляция, DNS по имени сервиса (`db:5432`, не `localhost`). Override файлы: base + dev + prod. Команды: `docker compose up -d`, `logs -f`, `exec app bash`.

**44. Как работают volumes и networking в Docker?**
Контейнер эфемерен — при удалении данные теряются. Named volumes (`docker volume create`) — персистентность для БД. Bind mounts (`-v /host:/container`) — hot reload в dev. tmpfs — в памяти, не персистентно. Networking: bridge (default) — изолированная сеть, контейнеры общаются по имени (DNS). host — сеть хоста напрямую, нет изоляции. Типичная ошибка: `localhost` для связи между контейнерами — это сам контейнер. Нужно имя сервиса: `postgresql://db:5432`.

### AWS Services

**45. Какие типы EC2 инстансов существуют?**
Naming: `c7i.xlarge` — compute optimized, 7th gen, Intel, xlarge size. Семейства: t3/t4g — burstable (dev, небольшие web-сервера), m6i/m7i — balanced (общего назначения), c6i/c7i — compute (CPU-интенсивные), r6i/r7i — memory (кэширование, БД), i3/i4i — storage (NoSQL), g4dn/p4d — GPU (ML). Graviton (ARM: t4g, m7g) — 20-40% лучше цена/производительность для Linux workloads. Security Groups — stateful firewall: минимум портов, никогда 0.0.0.0/0 для SSH.

**46. Какие классы хранения есть в S3?**
Standard — частый доступ ($$$). Standard-IA — редкий доступ, минимум 30 дней ($$). One Zone-IA — одна AZ, минимум 30 дней ($). Glacier Instant — ms retrieval, 90 дней. Glacier Flexible — min-hours retrieval, 90 дней. Deep Archive — hours retrieval, 180 дней (самый дешёвый). Lifecycle policies автоматически переводят объекты: логи 30+ дней → Standard-IA, 90+ дней → Glacier, 365 дней → удалить. Без lifecycle легко забыть про петабайты логов в Standard.

**47. Как работает Amazon ECR?**
Managed Docker registry с IAM интеграцией (не нужны отдельные credentials для pull в ECS/EKS). Сканирование уязвимостей (image scanning). Lifecycle policies — автоматически удалять старые образы ("Keep last 10 images"), иначе счёт за storage растёт. Immutable tags — защита от случайного перезаписывания production образа. Аутентификация: `aws ecr get-login-password | docker login`. Низкая latency (данные в вашем регионе).

**48. Как использовать EventBridge для event-driven архитектуры?**
Serverless event bus для связи микросервисов без прямых зависимостей. Сервис публикует событие ("Order Created"), EventBridge маршрутизирует в Lambda, SQS, Step Functions по правилам. Преимущества над SQS/SNS: фильтрация по содержимому события (не только по топику), schema registry, Archive & Replay для debugging. Типичный паттерн: fan-out — одно событие запускает несколько обработчиков (email Lambda, inventory SQS, fulfillment Step Functions).

**49. В чём разница между SSM Parameter Store и Secrets Manager?**
Parameter Store — бесплатный (standard tier до 10K параметров), key-value storage, нет встроенной ротации. Для: feature flags, endpoints, конфигурация, всё что не "настоящий секрет". Secrets Manager — $0.40/secret/month, автоматическая ротация паролей (RDS credentials), cross-account доступ. Для: пароли БД, API keys, токены — всё что нужно ротировать или имеет высокую ценность. `SecureString` в Parameter Store тоже шифрует через KMS, но без ротации.

### Nginx

**50. Как настроить Nginx как reverse proxy?**
Зачем: SSL termination (приложение получает HTTP), статические файлы (nginx эффективнее Python/Node), буферизация (медленные клиенты не блокируют воркеры), security headers централизованно, load balancing. Ключевые заголовки: `X-Real-IP` — реальный IP клиента, `X-Forwarded-For` — цепочка прокси, `X-Forwarded-Proto` — оригинальный протокол для редиректов. `try_files $uri $uri/ /index.html` — SPA fallback для client-side routing.

**51. Как настроить load balancing?**
`upstream backend { server app1:8000; server app2:8000; }`. Алгоритмы: round-robin (default, по очереди), `least_conn` (на менее загруженный), `ip_hash` (sticky sessions, один клиент → один сервер). `weight=3` для распределения по весам. Health checks: `max_fails=3 fail_timeout=30s` — исключить упавший сервер. `server app3:8000 backup` — использовать только при падении основных. `keepalive 32` — постоянные соединения с backend, экономит TCP handshakes.

**52. Как работает SSL/TLS termination?**
HTTPS расшифровывается на nginx, plain HTTP передаётся backend в приватной сети. Преимущества: централизованное управление сертификатами, backend не тратит CPU на криптографию, проще debugging. Let's Encrypt для сертификатов. Важные настройки: `ssl_protocols TLSv1.2 TLSv1.3`, HSTS header (`Strict-Transport-Security`), OCSP Stapling, session cache. Когда нужен end-to-end TLS: compliance требования, zero-trust архитектура.

---

## Integrations & AI (Specialized)

### Playwright

**53. Чем Playwright отличается от Selenium и Cypress?**
Playwright использует CDP (Chrome DevTools Protocol) напрямую, без WebDriver как Selenium. Auto-waiting из коробки — нет flaky тестов. Реальные движки: Chromium, Firefox, WebKit (Safari). Встроенная параллельность, multi-tab/window поддержка, полная network interception. Codegen для записи тестов, trace viewer для отладки. Selenium актуален для legacy, экзотических браузеров, non-JS команд. Cypress — только JS, ограниченный multi-tab, но хорош для component testing.

**54. Как использовать Page Object Model?**
POM инкапсулирует локаторы и действия в классах страниц. Без POM: селекторы разбросаны по тестам, изменился id кнопки → правишь 50 тестов. С POM: локаторы как properties (`this.submitButton = page.locator('...')`), методы для действий (`async login(email, password)`). Тесты читают как бизнес-логику. Используйте `data-testid` вместо хрупких CSS-селекторов. Page Objects могут возвращать другие Page Objects: `loginPage.login() → DashboardPage`.

**55. Как работает auto-waiting и локаторы?**
Проблема Selenium: элемент появляется через 100ms, Selenium сразу ищет → не находит → тест падает. Playwright: каждое действие (`click`, `fill`) ждёт пока элемент attached, visible, stable, enabled, receives events. Локаторы — "рецепт" поиска, вычисляются заново при каждом действии (важно для динамических страниц). Strict mode: если найдено >1 элемента — ошибка. Рекомендуемые методы: `getByRole`, `getByLabel`, `getByTestId`. Web-first assertions с retry: `await expect(button).toBeVisible()`.

**56. Как настроить параллельное выполнение тестов?**
`fullyParallel: true` в конфиге — все тесты параллельно. `workers` — количество (в CI обычно 2-4). Projects для разных браузеров могут выполняться параллельно. `test.describe.configure({ mode: 'serial' })` для зависимых тестов (checkout flow). Sharding для CI: разделить сьют между runners. `retries` для flaky тестов. `trace: 'on-first-retry'`, `screenshot: 'only-on-failure'` для debugging. `webServer` для автозапуска dev server.

### Microsoft Graph API

**57. Как работает OAuth 2.0 авторизация для Graph API?**
Delegated permissions — от имени пользователя, нужен sign-in UI, для interactive приложений. Application permissions — от имени приложения (daemon/background services), Client Credentials flow, не требует пользователя. MSAL (Microsoft Authentication Library) инкапсулирует сложности: кэширование токенов, refresh, retry. Security: client secret только в env/Secrets Manager, минимальные permissions, регулярная ротация.

**58. Как работать с почтой через Graph API?**
OData query parameters: `$filter` (фильтрация), `$select` (выбор полей), `$orderby` (сортировка), `$top` (лимит). Не грузите все 1000 писем когда нужны 10. Вложения: маленькие (<3MB) inline в base64, большие требуют отдельного запроса `/{attachment_id}/$value`. Возможности: чтение с фильтрацией, скачивание вложений, отправка (HTML, вложения), управление папками и правилами.

**59. Как использовать batching для оптимизации запросов?**
Без batching: 100 пользователей = 100 HTTP-запросов. С batching: 5 запросов по 20. Отправляем POST на `$batch` с массивом запросов (до 20). Каждый выполняется независимо (может успеть или упасть). Экономия в latency огромная. Альтернатива для синхронизации — Delta queries: получаете только изменившиеся объекты с последнего запроса.

### Google Vertex AI & Document AI

**60. Как использовать Gemini модели в Vertex AI?**
Vertex AI — enterprise-платформа с GCP интеграцией (IAM, VPC, audit logging). Gemini — multimodal (текст + изображения + видео + аудио), long context до 1M токенов, structured output с JSON schema, function calling. Gemini Pro — максимальное качество, дорогой. Gemini Flash — быстрый, дешёвый, для простых задач. Начните с Flash, переходите на Pro если качество недостаточно. `GenerativeModel('gemini-2.5-pro')`, `generate_content()`, `stream=True` для streaming.

**61. Какие best practices для Prompt Engineering?**
Чёткие инструкции с форматом ответа ("Respond with only the category name"). Few-shot examples — показать что хотите (3-5 примеров). Chain of Thought — "Think through this step by step" для сложных задач. Role prompting — "You are an expert X" задаёт контекст. Output format specification — "Return as JSON in this exact format". Типичные ошибки: размытые инструкции, нет примеров, много в одном prompt. Итеративный процесс: начните просто → смотрите результат → уточняйте.

**62. Как работает Document AI?**
Специализированный сервис для извлечения данных из документов (PDF, изображения). Процессоры: OCR (базовый), Form Parser (ключ-значение из форм), Invoice Parser (vendor, total, line items), Custom Document Extractor (train на своих документах). Результат включает bounding boxes и confidence scores. Document AI vs LLM: структурированные документы с известным форматом — Document AI, произвольные документы где нужно "понимание" — LLM.

**63. Как настроить Workload Identity Federation?**
Аутентификация AWS/Azure/GitHub в GCP без service account ключей. AWS/GitHub выдаёт токен → обмен на GCP credentials через STS → short-lived access. Преимущества: нет долгоживущих ключей для утечки, нет ротации, audit trail, granular access по AWS role / GitHub repo. Типичные сценарии: CI/CD из GitHub Actions в GCP, cross-cloud AWS Lambda → GCP BigQuery, Kubernetes Workload Identity.

### Airtable

**64. Как использовать Airtable API и какие есть лимиты?**
Критические лимиты: **5 req/sec** (легко упереться!), 100 записей на страницу (нужна пагинация), **10 записей в batch** (не 100!), 100K записей на базу (Free/Plus). Rate limiting: exponential backoff при 429, batch операции, кэширование для read-heavy. Когда хорош: быстрый MVP, non-tech редактируют данные, конфигурации. pyairtable: `table.all(formula="...", sort=[...])`, `batch_create()`.

**65. Когда использовать Airtable vs традиционную БД?**
Airtable: MVP/прототипы, внутренние инструменты, non-tech пользователи, конфигурации, данные редко меняются, до 100K записей, 5 req/sec достаточно. PostgreSQL: высокая нагрузка, сложные JOIN, транзакции (ACID), миллионы записей, production приложения. Сигналы на переход: rate limits проблема, нужны сложные запросы, нужна консистентность. Гибридный подход: Airtable как UI + PostgreSQL как основная БД с синхронизацией.

---

## Quick Tips

- **TypeScript:** `interface` для публичных API, `type` для unions/intersections
- **Vite:** Native ESM в dev, Rollup в prod, esbuild для pre-bundling
- **Tailwind:** Mobile-first, `sm:` = "от 640px и выше", JIT для arbitrary values
- **TanStack Query:** staleTime=0 по умолчанию = всегда refetch, queryKey как массив зависимостей
- **Radix:** Compound components, data-state для стилизации, Portal для z-index
- **React Router:** Loaders загружают данные ДО рендера, nested routes для layouts
- **SQLAlchemy:** `lazy='raise'` + явный joinedload/selectinload предотвращает N+1
- **Pydantic:** `from_attributes=True` для ORM, `SecretStr` не выводится в логах
- **PostgreSQL:** B-tree для 99% случаев, GIN для JSONB/массивов, `EXPLAIN ANALYZE`
- **Docker:** Multi-stage builds уменьшают размер в 10x, копируй зависимости отдельно
- **AWS:** Graviton дешевле, S3 Lifecycle policies обязательны, Secrets Manager для ротации
- **Nginx:** X-Real-IP для реального IP клиента, try_files для SPA
- **Playwright:** Auto-waiting решает flaky tests, getByRole/getByTestId рекомендуются
- **Graph API:** MSAL для OAuth, batching до 20 запросов, Delta queries для синхронизации
- **Vertex AI:** Flash для скорости/цены, Pro для качества, few-shot examples важны
