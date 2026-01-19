# Python + AI Engineer Interview - Short Version
## Quick Refresh Guide

---

# 🟢 LLM Fundamentals

## 1. Токены
- **Токен** ≈ 4 символа / 0.75 слова
- Оплата: input + output (разные цены)
- `tiktoken` для подсчёта

## 2. Context Window
- GPT-4o: 128K, Claude: 200K, Gemini: 2M
- **Lost in the Middle** — модель хуже помнит середину контекста
- Важное размещать в начале/конце

## 3. Temperature
- `0` — детерминированный (extraction, classification)
- `0.3-0.5` — сбалансированный (Q&A)
- `0.7-1.0` — креативный (writing)

## 4. Embeddings
- Вектор текста в многомерном пространстве
- Похожие тексты → близкие векторы
- Cosine similarity для сравнения
- `text-embedding-3-large` (3072 dims)

## 5. Streaming
- Улучшает UX, снижает perceived latency
- OpenAI: `stream=True`, iterate `chunk.choices[0].delta.content`
- Anthropic: `client.messages.stream()`, iterate `stream.text_stream`

## 6. Structured Output
- **JSON mode**: `response_format={"type": "json_object"}`
- **Function calling**: `response_format=PydanticModel` (OpenAI)
- **Anthropic**: `tools` + `tool_choice` для structured output

## 7. Azure vs OpenAI vs Anthropic
| | Azure | OpenAI | Anthropic |
|-|-------|--------|-----------|
| Enterprise | ✅ SOC2, HIPAA | ⚠️ | ✅ SOC2 |
| Data residency | ✅ | ❌ | ❌ |
| SLA | ✅ 99.9% | ❌ | ❌ |

---

# 🟡 RAG & Vector Search

## 8. RAG Architecture
```
Query → Embedding → Vector Search → Top-K → Rerank → LLM → Answer
```

## 9. Chunking
- **Fixed size**: просто, режет предложения
- **Recursive**: уважает структуру (\n\n, \n, .)
- **Semantic**: по смыслу (дороже, лучше)
- Overlap 10-20% для контекста

## 10. Azure AI Search
- **Hybrid search** = vector + keyword
- `VectorizedQuery` + `search_text`
- HNSW алгоритм для vector index

## 11. Reranking
- Vector search → Top 50 (recall)
- Reranker (cross-encoder) → Top 5 (precision)
- Cohere Rerank / Azure Semantic Ranker

## 12. Retrieval Metrics
- **Precision@K**: relevant в top-K / K
- **Recall@K**: найдено relevant / всего relevant
- **MRR**: 1 / позиция первого relevant

---

# 🟠 Agentic AI & Pydantic AI

## 13. Agent vs Chatbot vs Copilot
- **Chatbot**: Q→A, без tools
- **Copilot**: suggestions, user approves
- **Agent**: автономный, multi-step, tools

## 14. Pydantic AI Basics
```python
agent = Agent("openai:gpt-4o", result_type=MyModel)
result = agent.run_sync("query")
```

## 15. Dependencies (DI)
```python
@dataclass
class Deps:
    db: Database
    user_id: str

agent = Agent("openai:gpt-4o", deps_type=Deps)

@agent.tool
async def get_data(ctx: RunContext[Deps]) -> str:
    return await ctx.deps.db.query(ctx.deps.user_id)
```

## 16. Tools
```python
@agent.tool
async def my_tool(ctx: RunContext[Deps], param: str = Field(description="...")) -> str:
    return result
```
- `prepare=` для dynamic enable/disable
- `require_confirmation=True` для опасных

## 17. ReAct Pattern
```
Thought → Action → Observation → Thought → ... → Answer
```
Чередование reasoning и tool calls.

## 18. Function Calling: OpenAI vs Anthropic
| | OpenAI | Anthropic |
|-|--------|-----------|
| Response | `tool_calls` array | `tool_use` blocks |
| Args | JSON string (parse!) | Already dict |
| Result | `role: "tool"` | `tool_result` in user msg |

## 19. Multi-Agent Patterns
- **Sequential**: A → B → C
- **Hierarchical**: Manager delegates to Workers
- **Debate**: Pro vs Con → Judge

## 20. Agent Memory
- **Short-term**: `message_history=result.all_messages()`
- **Long-term**: Vector DB с memories, retrieve по query

## 21. Model Settings
```python
agent = Agent("openai:gpt-4o", retries=3, model_settings=ModelSettings(temperature=0))
```

## 22. Structured Output
```python
class Result(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)

agent = Agent("openai:gpt-4o", result_type=Result)
```

---

# 🔴 Production AI Systems

## 23. Observability (Logfire)
```python
logfire.configure()
logfire.instrument_pydantic_ai()
```
Track: latency, tokens, cost, errors

## 24. Prompt Injection Protection
- Input sanitization (regex patterns)
- Structured output (ограничивает actions)
- Data/instruction separation в промпте
- Output validation

## 25. Hallucination Mitigation
- Grounded generation (only from context)
- Require supporting quotes
- Self-consistency (multiple samples)
- Citation verification

## 26. Rate Limiting & Cost
- Track requests/min, tokens/min
- Cost = input_tokens × price + output_tokens × price
- Per-user limits

## 27. Caching
- **Exact cache**: hash(prompt) → response
- **Semantic cache**: similar embeddings → cached response
- **Prompt caching** (Anthropic): `cache_control: ephemeral` → 90% discount

## 28. When to Use What
| Approach | Use Case |
|----------|----------|
| RAG | Factual Q&A, docs, fresh data |
| Agents | Multi-step, tools, dynamic |
| Fine-tuning | Consistent style, domain terms |
| Prompts | Quick iteration, flexible |

## 29. Error Handling
- Retry + exponential backoff
- Fallback models (gpt-4o → gpt-4o-mini)
- Circuit breaker (N failures → stop calling)

## 30. Testing
```python
# Mock model
agent = Agent(TestModel())

# Eval dataset
@pytest.mark.parametrize("case", eval_cases)
async def test_eval(case):
    result = await agent.run(case["input"])
    assert keyword in result.data
```

## 31. Streaming
```python
async with agent.run_stream("query") as response:
    async for chunk in response.stream_text():
        print(chunk, end="")
```

## 32. Multi-model Routing
- Classifier (cheap) → route to specialist (expensive)
- Simple → gpt-4o-mini, Complex → gpt-4o, Code → Claude

## 33. Azure Patterns
- **Managed Identity**: `DefaultAzureCredential()`
- **Multi-region failover**: list of endpoints
- **AI Search integration**: hybrid search + semantic ranker

## 34. Advanced Pydantic AI
- `@agent.result_validator` — quality control
- `@agent.system_prompt` — dynamic prompts
- `Union[Success, Error, NeedInfo]` — multiple outcomes

## 35. Production Checklist
- ✅ Input validation, prompt injection protection
- ✅ Retry logic, circuit breaker, fallbacks
- ✅ Rate limiting, cost tracking, caching
- ✅ Logging, metrics, alerts
- ✅ Eval dataset, testing pipeline

---

# Quick Reference

```python
# Basic
agent = Agent("openai:gpt-4o", result_type=Output, deps_type=Deps)
result = await agent.run("query", deps=deps)

# Tool
@agent.tool
async def tool(ctx: RunContext[Deps], param: str) -> str:
    return ctx.deps.db.query(param)

# History
result2 = await agent.run("q2", message_history=result1.all_messages())

# Stream
async with agent.run_stream("q") as r:
    async for chunk in r.stream_text():
        print(chunk)
```

---

*Good luck!*
