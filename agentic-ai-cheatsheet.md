# Agentic AI — Шпаргалка для собеседования

## 1. Фундаментальные концепции

### AI Agent vs LLM-вызов
- **LLM-вызов**: input → output, одноразовая генерация
- **Agent**: автономный цикл reasoning + acting, сам решает когда остановиться
- Агент = LLM + Tools + Memory + Orchestration loop

### ReAct паттерн
- **Re**ason → **Act** → Observe → Reason...
- LLM "думает вслух" перед действием (chain-of-thought)
- Наблюдает результат → корректирует следующий шаг
- Останавливается когда задача решена или достигнут лимит

### Chain vs Agent vs Multi-Agent
| Тип | Поток управления | Когда использовать |
|-----|------------------|-------------------|
| Chain | Фиксированный, линейный | Предсказуемые пайплайны |
| Agent | Динамический, LLM решает | Неопределённые задачи |
| Multi-Agent | Несколько агентов координируются | Сложные домены, разделение ответственности |

### Tool Use / Function Calling
- LLM получает schema доступных tools в system prompt
- Генерирует structured output с именем tool + аргументы
- Runtime исполняет tool, результат возвращается в контекст
- LLM **не исполняет** код — только генерирует intent

---

## 2. Архитектурные паттерны

### Single Agent + Tools
- Один LLM, набор tools, memory
- Простейшая архитектура, подходит для 80% задач
- Ограничение: контекст, сложность координации

### Router / Supervisor
- **Router**: классифицирует запрос → направляет к специализированному агенту
- **Supervisor**: управляет execution, распределяет подзадачи
- Supervisor видит общую картину, агенты — только свою часть

### Hierarchical Agents
- Агенты верхнего уровня делегируют агентам нижнего
- Пример: Manager Agent → Research Agent + Writing Agent
- Trade-off: гибкость vs сложность отладки

### Collaborative Multi-Agent
- Агенты как "коллеги" с разными ролями
- Общаются через shared state или message passing
- Паттерны: debate, consensus, специализация по навыкам

### Human-in-the-Loop
- **Approval gates**: критичные действия требуют подтверждения
- **Feedback loops**: человек корректирует направление
- **Escalation**: агент признаёт неуверенность → передаёт человеку

---

## 3. Memory и State Management

### Short-term Memory
- Контекст текущей сессии (conversation history)
- Ограничен context window (4K-200K tokens)
- Стратегии: truncation, summarization, sliding window

### Long-term Memory
- **Vector stores**: семантический поиск по прошлым взаимодействиям
- **Knowledge bases**: структурированные факты о пользователе/домене
- **Episodic memory**: запоминание конкретных событий/решений

### Context Window Management
- **Summarization**: сжатие старых сообщений
- **Retrieval**: подгружать только релевантное
- **Hierarchical**: summary of summaries для длинных сессий

### Checkpointing
- Сохранение состояния агента между запусками
- Позволяет: восстановление после сбоя, pause/resume, debugging
- Что сохранять: conversation, intermediate results, tool outputs

---

## 4. Tool Design

### Принципы хороших Tools
- **Naming**: глагол + существительное (`search_documents`, `send_email`)
- **Description**: что делает, когда использовать, что возвращает
- **Schema**: строгая типизация параметров, примеры значений
- **Single responsibility**: один tool = одно действие
- **Идемпотентность** где возможно

### Error Handling
- Возвращать понятные ошибки (LLM должен понять что пошло не так)
- Retry с exponential backoff для transient failures
- Graceful degradation: альтернативный путь при недоступности tool

### Sandboxing и безопасность
- **Code execution**: изолированные контейнеры, timeout, resource limits
- **API calls**: whitelist endpoints, rate limiting, credential isolation
- **File access**: restricted paths, read-only где возможно

### Tool vs RAG
| Tool | RAG |
|------|-----|
| Действие/мутация | Получение информации |
| Внешние системы | Внутренняя knowledge base |
| Структурированный output | Текстовые chunks |

---

## 5. Orchestration Frameworks

### LangGraph
- State machine подход: nodes (actions) + edges (transitions)
- Conditional edges: LLM или логика решает следующий шаг
- Встроенный checkpointing, human-in-the-loop
- Когда: сложные workflows с ветвлением и циклами

### AutoGen
- Multi-agent conversations as first-class concept
- Агенты "общаются" друг с другом
- Хорош для: debate, peer review, collaborative reasoning

### CrewAI
- Role-based agents с goals и backstory
- "Crew" = команда агентов с распределёнными ролями
- Абстракция выше чем LangGraph, меньше контроля

### Pydantic AI
- Фокус на structured outputs и type safety
- Валидация ответов LLM против схемы
- Хорош для: extraction, form filling, API generation

### Framework vs Custom
**Framework когда:**
- Стандартные паттерны (RAG, simple agent)
- Быстрый прототип
- Команда знакомая с framework

**Custom когда:**
- Уникальные requirements
- Максимальный контроль над latency/cost
- Минимум зависимостей в production

---

## 6. Evaluation и Observability

### Тестирование агентов
- **Unit tests для tools**: mock inputs → expected outputs
- **Integration tests**: tool + real dependencies
- **E2E для workflows**: golden datasets с ожидаемыми результатами
- **LLM-as-judge**: другой LLM оценивает качество ответа

### Tracing и Debugging
- Логировать: каждый LLM call, tool call, state transition
- Trace ID сквозь весь workflow
- Инструменты: LangSmith, Arize, custom logging

### Ключевые метрики
- **Task completion rate**: % успешно завершённых задач
- **Token usage**: cost per task
- **Latency**: time-to-first-token, total completion time
- **Tool accuracy**: правильно ли выбран tool, корректны ли аргументы

### Hallucinations и Tool Misuse
- **Grounding**: требовать citations, проверять факты через tools
- **Guardrails**: валидация tool arguments перед execution
- **Confidence scoring**: LLM оценивает уверенность в ответе

---

## 7. Production Concerns

### Rate Limiting и Cost
- Token budgets per request/user/day
- Caching: одинаковые запросы → cached response
- Model routing: дешёвая модель для простых задач, дорогая для сложных
- Prompt optimization: меньше tokens = меньше cost

### Graceful Degradation
- Fallback models: если primary недоступен
- Cached responses для частых запросов
- Degraded mode: отключить non-critical tools
- Чёткие error messages пользователю

### Streaming в Agent Loops
- Stream промежуточные результаты пользователю
- Показывать "thinking" / текущий шаг
- Challenge: tool calls прерывают stream

### Idempotency и Retries
- Идемпотентные tools: безопасно повторять
- Retry tokens / request IDs для мутаций
- At-least-once vs exactly-once семантика

---

## 8. Практические кейсы

### Coding Assistants (Claude Code)
- Tools: file read/write, bash execution, search
- Challenge: безопасность code execution, контекст большой codebase
- Паттерн: iterative refinement (write → test → fix)

### Research Agents
- Pipeline: search → filter → read → synthesize → answer
- Multi-step retrieval: initial search → follow-up queries
- Challenge: quality vs speed trade-off

### Customer Support
- Router: classify intent → route to specialist agent
- Tools: knowledge base search, ticket creation, CRM lookup
- Human escalation для edge cases
- Challenge: handling frustrated users, knowing when to escalate

---

## Типичные вопросы и ответы

### Концептуальные

**Q: Чем agent отличается от chain?**

Chain — это фиксированная последовательность шагов, которая выполняется всегда одинаково: шаг A → шаг B → шаг C. Разработчик заранее определяет весь flow. Пример: получить вопрос → найти документы → сгенерировать ответ.

Agent работает в цикле "думаю → действую → наблюдаю". LLM сам решает, какой шаг выполнить следующим, нужно ли повторить действие, или задача уже решена. Агент может пойти разными путями в зависимости от промежуточных результатов. Это делает агентов гибкими, но менее предсказуемыми.

**Q: Когда НЕ нужен agent?**

Agent не нужен когда:
- Workflow полностью предсказуем (всегда одни и те же шаги в одном порядке)
- Нужна максимальная скорость и минимальная стоимость (chain дешевле — меньше LLM-вызовов)
- Требуется детерминированное поведение (для compliance, audit trails)
- Задача простая и не требует принятия решений на лету

Пример: пайплайн "классифицируй email → если spam, удали" — это chain. Не нужен агент, который будет "думать" над каждым письмом.

**Q: Как agent решает какой tool вызвать?**

В system prompt агенту передаётся список доступных tools с их описаниями и JSON-схемами параметров. Когда агент получает задачу, он:

1. **Анализирует задачу** (reasoning/chain-of-thought)
2. **Сопоставляет с описаниями tools** — какой tool подходит для текущего шага
3. **Генерирует structured output** — JSON с именем tool и аргументами

LLM не исполняет tool напрямую — он только генерирует "намерение". Runtime-код парсит этот JSON и вызывает реальную функцию. Результат возвращается в контекст, и агент решает что делать дальше.

Качество tool selection напрямую зависит от качества descriptions — поэтому их написание это искусство.

### Архитектурные

**Q: Single agent vs multi-agent — как выбрать?**

**Single agent** подходит когда:
- Задача не требует узкой специализации
- Все tools логически связаны (работа с одним доменом)
- Важна простота отладки и предсказуемость
- Достаточно одного context window

**Multi-agent** оправдан когда:
- Чёткое разделение доменов (например, research agent + writing agent + code agent)
- Нужны разные модели: дешёвая для рутины, дорогая для сложных решений
- Требуется параллелизм (агенты работают одновременно)
- Один контекст не вмещает всю нужную информацию

Практическое правило: начинайте с single agent. Переходите на multi-agent только когда упираетесь в конкретное ограничение (контекст, специализация, параллелизм).

**Q: Как масштабировать агента на большую codebase?**

Нельзя загрузить весь код в контекст — это дорого и неэффективно ("lost in the middle" problem). Решение — retrieval-augmented подход:

1. **Индексация**: разбить codebase на chunks, создать embeddings, сохранить в vector store
2. **Search**: по запросу агента найти релевантные файлы/функции
3. **Load context**: загрузить только нужные части кода

Дополнительные техники:
- **Hierarchical indexing**: сначала найти нужный модуль, потом файл, потом функцию
- **Code graph**: использовать AST для понимания связей между сущностями
- **Summaries**: хранить краткие описания модулей для быстрой навигации

**Q: Supervisor vs Router?**

**Router** — это stateless классификатор. Получает запрос, определяет категорию, направляет к нужному агенту. Не следит за выполнением, не знает что происходит после передачи. Простой и быстрый.

**Supervisor** — это менеджер, который:
- Разбивает задачу на подзадачи
- Распределяет их между агентами
- Следит за прогрессом выполнения
- Может переназначить задачу если агент "застрял"
- Собирает и агрегирует результаты

Router подходит для простого разделения потоков (support vs sales vs billing). Supervisor нужен когда задача требует координации и контроля качества.

### Memory

**Q: Как справляться с ограничением контекста?**

Несколько стратегий, часто используемых вместе:

1. **Summarization**: периодически сжимать старую часть диалога в краткое резюме. Теряем детали, но сохраняем суть.

2. **Selective retrieval**: не хранить всё в контексте, а подгружать по запросу. Vector search по истории разговора — достать только релевантные части.

3. **Sliding window**: держать последние N сообщений полностью, остальное — в виде summary.

4. **Hierarchical memory**: summary of summaries. Для очень длинных сессий — несколько уровней абстракции.

5. **Structured extraction**: вместо хранения сырого текста — извлекать ключевые факты в структурированном виде (JSON, knowledge graph).

Главный принцип: хранить не всё подряд, а то, что действительно важно для текущей задачи.

**Q: Когда нужна long-term memory?**

Long-term memory (персистентная, между сессиями) нужна в случаях:

- **Персонализация**: помнить предпочтения пользователя, стиль общения, прошлые решения
- **Continuity**: продолжать работу с того места, где остановились (например, многодневный проект)
- **Learning from feedback**: если пользователь исправил агента — запомнить на будущее
- **Accumulation of knowledge**: агент собирает информацию о домене со временем
- **Audit и compliance**: требуется хранить историю действий

Если каждая сессия независима и пользователи анонимны — long-term memory скорее всего не нужна.

### Production

**Q: Как тестировать агентов?**

Многоуровневый подход:

1. **Unit tests для tools**: каждый tool тестируется изолированно. Mock inputs → проверяем outputs. Это детерминированные тесты, они быстрые и надёжные.

2. **Integration tests**: tool + реальные зависимости (база данных, API). Проверяем что tool корректно работает с внешним миром.

3. **E2E тесты с golden datasets**: набор типовых задач с ожидаемыми результатами. Прогоняем агента, сравниваем с эталоном. Учитываем что LLM недетерминирован — проверяем семантику, не exact match.

4. **LLM-as-judge**: используем другую (или ту же) модель для оценки качества. "Этот ответ полностью решает задачу пользователя? Оцени от 1 до 5."

5. **Monitoring в production**: метрики успешности, latency, стоимость. A/B тесты для сравнения версий.

**Q: Как контролировать стоимость?**

1. **Token budgets**: лимиты на запрос, на пользователя, на день. Жёсткие ограничения, агент не может их превысить.

2. **Caching**: одинаковые или похожие запросы → cached response. Semantic caching для похожих по смыслу запросов.

3. **Model routing**: дешёвая модель (GPT-3.5, Haiku) для простых задач, дорогая (GPT-4, Opus) только для сложных. Классификатор на входе определяет сложность.

4. **Prompt optimization**: убрать лишнее из system prompt, сжать примеры, использовать более компактные форматы.

5. **Early stopping**: если агент "зациклился" — прерывать после N итераций.

Главное: сначала измерить, потом оптимизировать. Без метрик не понятно где bottleneck.

**Q: Как обрабатывать failures?**

1. **Retry с exponential backoff**: для transient failures (timeout, rate limit). 1s → 2s → 4s → ... Не забыть про jitter.

2. **Fallback models**: если основная модель недоступна — переключиться на резервную. Может быть медленнее или менее точной, но работает.

3. **Graceful degradation**: отключить non-critical features. Например, если search tool недоступен — работать только с тем что в контексте.

4. **Circuit breaker**: если tool постоянно падает — временно отключить его, чтобы не тратить ресурсы на retry.

5. **Clear error messages**: пользователь должен понять что произошло и что делать. "Сервис временно недоступен, попробуйте позже" лучше чем "Internal error".

### Red Flags (что не говорить)

- "Агент сам всё решит" — нужен контроль и guardrails
- "Используем самую умную модель везде" — это дорого и медленно
- "Framework X решает все проблемы" — всегда trade-offs
- "Тестировать сложно, просто в prod" — technical debt и incidents

---

## Ключевые Trade-offs

| Выбор | Плюсы | Минусы |
|-------|-------|--------|
| Больше tools | Гибкость | Confusion для LLM, сложнее prompt |
| Больше агентов | Специализация | Координация, latency, cost |
| Длинный контекст | Больше информации | Cost, "lost in the middle" |
| Строгие guardrails | Безопасность | False positives, UX friction |
| Подробные descriptions | Точнее tool selection | Больше tokens в каждом запросе |
