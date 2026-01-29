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
> Chain — фиксированный flow. Agent — динамический, LLM решает следующий шаг.

**Q: Когда НЕ нужен agent?**
> Когда workflow предсказуемый, детерминированный. Chain дешевле и надёжнее.

**Q: Как agent решает какой tool вызвать?**
> Tool descriptions в prompt + reasoning. LLM генерирует structured output с tool name и args.

### Архитектурные

**Q: Single agent vs multi-agent — как выбрать?**
> Single: проще, дешевле, достаточно для большинства задач. Multi: чёткое разделение доменов, разные модели для разных задач, параллелизм.

**Q: Как масштабировать агента на большую codebase?**
> Retrieval-augmented подход: индексация → search → load relevant context. Не пытаться впихнуть всё в контекст.

**Q: Supervisor vs Router?**
> Router: stateless классификация. Supervisor: управляет execution, может переназначать, видит progress.

### Memory

**Q: Как справляться с ограничением контекста?**
> Summarization, retrieval релевантного, hierarchical memory. Не хранить всё — хранить важное.

**Q: Когда нужна long-term memory?**
> Персонализация, learning from feedback, multi-session continuity.

### Production

**Q: Как тестировать агентов?**
> Unit tests для tools, golden datasets для e2e, LLM-as-judge для quality, monitoring в production.

**Q: Как контролировать стоимость?**
> Token budgets, caching, model routing, prompt optimization. Measure first.

**Q: Как обрабатывать failures?**
> Retry с backoff, fallback models, graceful degradation, чёткие error messages.

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
