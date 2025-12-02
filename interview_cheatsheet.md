# Frontend & React: Краткая Шпаргалка для Собеседований

## JavaScript Core

**Типы данных в JS?**
8 типов: 7 примитивов (string, number, boolean, null, undefined, symbol, bigint) и object.

**null vs undefined?**
undefined — переменная объявлена, но значение не присвоено; null — явно указанное "пустое" значение.

**== vs ===?**
`==` приводит типы перед сравнением, `===` сравнивает без приведения; всегда используй `===`.

**var vs let vs const?**
var — функциональная область видимости, всплывает; let/const — блочная область, TDZ; const запрещает переприсваивание.

**Hoisting?**
Механизм "подъёма" объявлений переменных и функций в начало области видимости до выполнения кода.

**map vs forEach?**
map возвращает новый массив с преобразованными элементами; forEach ничего не возвращает, используется для сайд-эффектов.

**Стрелочные функции vs обычные?**
Стрелочные не имеют своего this (берут из внешнего контекста), нет arguments, нельзя использовать как конструктор.

**Event Loop?**
Механизм, который следит за call stack и очередью задач: если стек пуст, берёт задачи из очереди; микрозадачи (Promise) выполняются раньше макрозадач (setTimeout).

**Замыкание (Closure)?**
Способность функции запоминать переменные из своей лексической области видимости, даже когда выполняется вне неё.

**this?**
Ссылается на объект, который вызывает функцию; call/apply вызывают с явным this, bind возвращает новую функцию с привязанным this.

**Прототипное наследование?**
Объекты наследуют свойства от других объектов через цепочку прототипов [[Prototype]]; поиск свойства идёт вверх по цепочке до null.

**Promise vs async/await?**
Promise — объект для асинхронных операций с .then(); async/await — синтаксический сахар для линейного написания асинхронного кода с обработкой ошибок через try/catch.

**Shallow vs Deep copy?**
Shallow (spread, Object.assign) копирует только первый уровень; Deep (structuredClone, JSON.parse/stringify) копирует все уровни вложенности.

## DOM & Browser

**querySelector vs getElementById?**
querySelector — универсальный CSS-селектор, возвращает первый элемент; getElementById — быстрее, только по ID.

**event.target vs event.currentTarget?**
target — элемент, где реально произошло событие; currentTarget — элемент, на котором висит обработчик.

**Event Bubbling vs Capturing?**
Capturing — событие идёт от window вниз к цели; Bubbling — от цели вверх к window; stopPropagation() останавливает всплытие.

**Делегирование событий?**
Один обработчик на родителе вместо множества на детях; экономит память, работает для динамически добавляемых элементов.

**localStorage vs sessionStorage vs cookies?**
localStorage — бессрочно, ~5MB; sessionStorage — до закрытия вкладки; cookies — 4KB, отправляются с каждым запросом на сервер.

## CSS

**Box Model?**
content → padding → border → margin; box-sizing: border-box включает padding и border в width/height.

**position: static/relative/absolute/fixed/sticky?**
static — в потоке; relative — в потоке, можно сдвигать; absolute — вне потока, относительно positioned-родителя; fixed — относительно viewport; sticky — "прилипает" при скролле.

**Как центрировать div?**
Flexbox: `display: flex; justify-content: center; align-items: center;` или Grid: `display: grid; place-items: center;`.

**display: none vs visibility: hidden vs opacity: 0?**
none — убирает из потока; hidden — невидим, но занимает место; opacity: 0 — прозрачен, занимает место, события работают.

**Flexbox vs Grid?**
Flexbox — одномерная раскладка (строка или колонка); Grid — двумерная (строки и колонки одновременно).

**Специфичность CSS?**
inline > #id > .class > tag; более специфичный селектор перебивает менее специфичный.

## React Core

**Virtual DOM?**
Лёгкая копия реального DOM в памяти; React сравнивает старое и новое дерево (diffing), затем применяет минимальные изменения к реальному DOM.

**Зачем нужен key в списках?**
Помогает React идентифицировать элементы при изменениях; без уникального key возможны баги с состоянием и производительностью.

**Props vs State?**
Props — входные данные от родителя, read-only; State — внутреннее состояние компонента, можно менять через setState/useState.

**Жизненный цикл?**
Mounting (создание) → Updating (обновление при изменении props/state) → Unmounting (удаление); в хуках: useEffect с [] для mount, с зависимостями для update, return-функция для cleanup.

**JSX?**
Синтаксический сахар для React.createElement(); позволяет писать HTML-подобный код в JavaScript; компилируется Babel.

**Controlled vs Uncontrolled компоненты?**
Controlled — значение в React state, полный контроль через value + onChange; Uncontrolled — значение в DOM, доступ через ref.

**React.Fragment?**
Группирует элементы без добавления лишнего DOM-узла; короткий синтаксис: `<>...</>`.

**Почему нельзя мутировать state напрямую?**
React не узнает об изменении и не запустит ререндер; всегда используй setState/useState с новым объектом/массивом.

**Lifting State Up?**
Перемещение общего state в ближайшего общего предка для синхронизации между компонентами-соседями.

## React Hooks

**useEffect — массив зависимостей?**
[] — только при mount; [deps] — при изменении deps; без массива — после каждого рендера; return-функция — cleanup.

**useState батчинг?**
React группирует несколько setState в один ререндер; для последовательных обновлений используй функциональную форму: `setState(prev => prev + 1)`.

**useRef?**
Хранит мутабельное значение между рендерами без вызова ререндера; два use-case: доступ к DOM-элементам и хранение значений (timerId, предыдущие значения).

**useMemo vs useCallback?**
useMemo — мемоизирует результат вычисления; useCallback — мемоизирует функцию; используй только при реальных проблемах производительности.

**useReducer vs useState?**
useReducer — для сложного state с множеством способов обновления; работает как Redux: dispatch(action) → reducer(state, action) → newState.

**useLayoutEffect vs useEffect?**
useLayoutEffect выполняется синхронно после DOM-изменений, до paint; используй для измерений DOM и предотвращения мерцания.

**Правила хуков?**
Только на верхнем уровне (не в условиях/циклах) и только в React-функциях; порядок вызовов должен быть одинаковым между рендерами.

**Custom Hooks?**
Функция с именем use*, использующая другие хуки; способ переиспользовать логику между компонентами.

## React Advanced

**Context API?**
Передача данных через дерево без prop drilling; проблема — все потребители ререндерятся при любом изменении значения.

**React.memo?**
HOC для предотвращения лишних ререндеров через shallow comparison props; используй когда компонент часто ререндерится с теми же props.

**React.lazy + Suspense?**
Ленивая загрузка компонентов; `const Comp = lazy(() => import('./Comp'))` + `<Suspense fallback={<Loader/>}>`.

**Portals?**
Рендеринг в DOM-узел вне родительского компонента; для модалок, тултипов; события всё ещё всплывают через React-дерево.

**Error Boundary?**
Классовый компонент с getDerivedStateFromError/componentDidCatch для перехвата ошибок в дочернем дереве; не ловит ошибки в обработчиках событий и async-коде.

**Stale Closure в хуках?**
Функция "захватила" старое значение из замыкания; решение: функциональное обновление state или useRef для актуального значения.

**HOC vs Render Props vs Hooks?**
HOC/Render Props — старые паттерны переиспользования логики, приводят к wrapper hell; Hooks — современный способ, плоская структура.

## TypeScript

**interface vs type?**
interface — для объектов, поддерживает declaration merging; type — универсальнее (union, tuple), не мержится; для объектов предпочитай interface.

**any vs unknown?**
any отключает проверку типов; unknown требует проверки типа перед использованием — безопаснее.

**Generics?**
Типы-параметры для создания переиспользуемого типизированного кода: `function identity<T>(arg: T): T`.

**Partial, Pick, Omit, Record?**
Partial — все поля опциональны; Pick — выбрать поля; Omit — исключить поля; Record — объект с заданными ключами и значениями.

**Type Guards?**
typeof для примитивов, instanceof для классов, кастомные с `is`: `function isFish(pet): pet is Fish`.

**Union vs Intersection?**
Union (A | B) — значение одного из типов; Intersection (A & B) — значение соответствует обоим типам.

## State Management

**Server State vs Client State?**
Server — данные с API (кэширование, синхронизация, React Query/SWR); Client — UI состояние (модалки, формы, useState/Zustand).

**React Query/SWR — зачем?**
Кэширование, дедупликация запросов, автоматическое обновление, состояния loading/error из коробки, stale-while-revalidate.

**Zustand vs Redux Toolkit?**
RTK — больше возможностей, бойлерплейт; Zustand — минималистичный (~1KB), без Provider, простой API.

**Optimistic Updates?**
Мгновенное обновление UI до ответа сервера; при ошибке — откат к предыдущему состоянию.

**Selectors — зачем?**
Выборка минимально нужных данных из стора; предотвращает лишние ререндеры при изменении других частей state.

## Performance

**Debounce vs Throttle?**
Debounce — вызов после паузы (поиск по вводу); Throttle — не чаще чем раз в N мс (скролл).

**Lazy Loading?**
Загрузка ресурсов по требованию; изображения: `loading="lazy"`; компоненты: React.lazy + Suspense.

**Reflow vs Repaint?**
Reflow — пересчёт геометрии (дорого); Repaint — перерисовка пикселей; анимируй только transform и opacity.

**Core Web Vitals?**
LCP (загрузка, <2.5с) — оптимизируй критический контент; CLS (стабильность, <0.1) — резервируй место; INP (отзывчивость, <200мс) — разбивай долгие задачи.

**Виртуализация списков?**
Рендеринг только видимых элементов + буфер; для 10000+ элементов используй @tanstack/react-virtual или react-window.

**Tree Shaking?**
Удаление неиспользуемого кода при сборке; работает только с ES Modules (import/export), не с CommonJS.

## Security

**XSS защита в React?**
React автоматически экранирует значения; dangerouslySetInnerHTML отключает защиту — санитизируй через DOMPurify.

**Где хранить токены?**
localStorage уязвим к XSS; httpOnly cookies защищены от XSS, но уязвимы к CSRF (используй SameSite + CSRF-токен).

**CORS?**
Браузерная защита от cross-origin запросов; сервер должен разрешить домен через заголовки Access-Control-Allow-Origin.

## Tooling

**Vite vs Webpack?**
Vite использует нативные ES Modules в dev — мгновенный старт; Webpack бандлит всё перед запуском — медленнее на больших проектах.

**ESLint vs Prettier?**
ESLint — поиск ошибок и проблем кода; Prettier — форматирование; используй eslint-config-prettier для совместной работы.

**pnpm vs npm vs yarn?**
pnpm — экономит место (глобальный store + симлинки), строгая структура; npm/yarn — плоская структура с hoisting.

## SSR/Next.js

**SSR vs CSR?**
CSR — JS рендерит на клиенте (медленный FCP, плохой SEO); SSR — сервер отдаёт готовый HTML (быстрый FCP, хороший SEO, нужна hydration).

**Server Components vs Client Components?**
Server — рендерятся только на сервере, не в бандле, прямой доступ к БД; Client (`'use client'`) — нужны для useState, useEffect, onClick.

## Testing

**Unit vs Integration vs E2E?**
Unit — изолированные функции/хуки; Integration — компонент с зависимостями; E2E — полный flow в браузере.

**React Testing Library — философия?**
Тестируй поведение, не реализацию; ищи элементы как пользователь (getByRole, getByText), не по селекторам.

**MSW vs Jest mocks?**
MSW мокает на уровне сети — тесты ближе к реальности; Jest mocks — на уровне функций, более хрупкие.
