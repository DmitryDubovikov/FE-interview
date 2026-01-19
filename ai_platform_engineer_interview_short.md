# AI Platform Engineer - Краткая шпаргалка

## Python и FastAPI

**1. FastAPI: async/await, Depends, middleware**
- `async def` — не блокирует event loop при I/O
- `def` (sync) — запускается в threadpool
- `Depends()` — DI для переиспользования логики (db sessions, auth)
- `@app.middleware("http")` — обработка до/после endpoint

**2. Streaming: SSE vs WebSocket**
- SSE (`StreamingResponse`) — односторонний поток, проще, для LLM streaming
- WebSocket — двусторонний, для чатов, gaming
- SSE: `yield f"data: {json.dumps(data)}\n\n"`

**3. Pydantic v2**
- 5-50x быстрее (Rust-ядро)
- `model_dump()` вместо `dict()`
- `@field_validator`, `@model_validator` для валидации
- `BaseSettings` для env variables

**4. OpenAPI 3.1**
- FastAPI автогенерирует из Pydantic + type hints
- SDK генерация: `openapi-python-client generate`
- `/openapi.json` — spec endpoint

**5. Background tasks и lifespan**
- `BackgroundTasks` — после response (логирование, уведомления)
- `@asynccontextmanager` + `lifespan` — startup/shutdown (db pools, clients)
- Для надёжности → SQS/Celery

**6. Asyncio patterns**
- `asyncio.gather()` — параллельные запросы
- `asyncio.Semaphore(N)` — rate limiting
- `asyncio.timeout()` — таймауты
- `asyncio.TaskGroup()` — Python 3.11+

---

## AWS Compute

**7. Lambda vs ECS Fargate**
| | Lambda | Fargate |
|---|--------|---------|
| Cold start | Да (100ms-10s) | Нет |
| Timeout | 15 мин | Нет |
| Memory | 10 GB | 120 GB |
| Биллинг | Per-request | Per-second |

- Lambda: события, spiky нагрузка, короткие операции
- Fargate: постоянный трафик, WebSocket, ML модели

**8. API Gateway: REST vs HTTP API**
| | REST | HTTP |
|---|------|------|
| Цена | $3.50/M | $1.00/M |
| Latency | ~30ms | ~10ms |
| Caching | Да | Нет |
| WebSocket | Да | Нет |

**9. Lambda оптимизация**
- Layers — shared зависимости
- Импорты вне handler — один раз при cold start
- Provisioned Concurrency — для production с требованиями к latency

**10. ECS Fargate**
- Task Definition: CPU, memory, secrets, health check
- Service Discovery (Cloud Map): DNS для сервисов
- Auto-scaling: target tracking по CPU/memory

**11. VPC для serverless**
- Private subnet + NAT Gateway → интернет
- Security Groups — минимальные правила
- VPC Endpoints — дешевле NAT для AWS сервисов

**12. CloudFront + API Gateway**
- Edge locations — ближе к юзерам
- Кеширование GET
- DDoS protection (Shield)

---

## Очереди и Events

**13. SQS: Standard vs FIFO**
| | Standard | FIFO |
|---|----------|------|
| Throughput | Unlimited | 3000/sec |
| Ordering | Best-effort | Strict |
| Delivery | At-least-once | Exactly-once |

- Visibility Timeout — время на обработку
- DLQ — после N неудач
- Long polling (20s) — экономия

**14. Step Functions: Express vs Standard**
| | Standard | Express |
|---|----------|---------|
| Duration | 1 год | 5 мин |
| Pricing | Per transition | Per execution |
| History | 90 дней | Нет |

- Паттерны: Sequential, Parallel, Map (batch)
- Retry + Catch для error handling

**15. EventBridge**
- Event pattern matching по source, detail-type, detail
- Rules → Lambda/SQS targets
- Scheduler для cron jobs
- vs SQS: routing по содержимому, cross-account

**16. Выбор: SQS vs Step Functions vs EventBridge**
- SQS: простая очередь, batch
- Step Functions: complex workflows, ветвление
- EventBridge: event routing по содержимому

**17. Saga паттерн**
- Локальные транзакции + компенсирующие действия
- Choreography: через события
- Orchestration: Step Functions

---

## Производительность

**18. Caching: Redis vs Memcached**
| | Redis | Memcached |
|---|-------|-----------|
| Структуры | Rich | String only |
| Persistence | Да | Нет |
| Replication | Да | Нет |

- Cache-Aside: check → miss → compute → store
- CloudFront: Cache-Control headers

**19. Idempotency**
- Idempotency-Key header
- Redis lock для concurrent requests
- DB: UNIQUE constraint + ON CONFLICT

**20. Rate limiting**
- Token Bucket: INCR + EXPIRE (Redis)
- Sliding Window: ZSET с timestamps
- API Gateway: ThrottlingRateLimit, UsagePlans

**21. Request deduplication**
- Content hash → Redis (5 min window)
- SQS FIFO: MessageDeduplicationId
- PostgreSQL: advisory lock / ON CONFLICT

**22. Circuit Breaker**
- CLOSED → OPEN (много ошибок) → HALF_OPEN (timeout) → CLOSED
- pybreaker: fail_max, reset_timeout
- Fallback на другого провайдера

**23. Policy-based routing**
- Feature Flags: user override или % rollout
- A/B Testing: consistent hashing по user_id
- Canary: API Gateway weighted routing

---

## Базы данных

**24. DynamoDB**
- Single-Table Design: PK + SK для разных entity types
- GSI: другой partition key, eventually consistent
- LSI: тот же PK, другой SK, только при создании
- On-Demand vs Provisioned

**25. Aurora Serverless v2**
- Автомасштабирование ACU (0.5-128)
- Для: переменная нагрузка, dev/staging
- Стандартная Aurora: стабильная высокая нагрузка

**26. ElastiCache**
- Sessions: Redis setex с TTL
- Caching: Read-Through, Write-Through
- Cluster Mode: shards + replicas

**27. Redshift**
- Serverless: async query execution
- COPY from S3 (Parquet)
- Spectrum: query S3 напрямую

---

## Observability

**28. CloudWatch**
- Structured JSON logging
- Logs Insights: SQL-like queries
- Custom Metrics: put_metric_data
- Alarms → SNS

**29. Datadog APM**
- patch_all() — auto-instrument
- tracer.trace() — custom spans
- statsd: increment, gauge, histogram

**30. X-Ray vs Datadog**
| | X-Ray | Datadog |
|---|-------|---------|
| AWS | Native | Extension |
| Цена | Per trace | Subscription |
| Dashboards | Basic | Rich |

- X-Ray: только AWS, минимальный budget
- Datadog: multi-cloud, rich alerting

---

## LLM и AI

**31. Amazon Bedrock**
- Модели: Claude, Titan, Llama, Mistral
- `invoke_model()` / `invoke_model_with_response_stream()`
- Embeddings: Titan, Cohere
- Fine-tuning: `create_model_customization_job()`

**32. OpenAI vs Bedrock vs Gemini**
| | OpenAI | Bedrock | Gemini |
|---|--------|---------|--------|
| Context | 128K | 200K (Claude) | 1M |
| AWS | Via API | Native | Via API |

- OpenAI: лучший общий выбор
- Bedrock: AWS-native, multi-model
- Gemini: longest context

**33. Semantic caching**
- Embed query → найти похожие → вернуть cached response
- Threshold: 0.92-0.95 similarity
- Для: FAQ, повторяющиеся вопросы
- НЕ для: персонализация, time-sensitive

**34. Vector databases**
| | Pinecone | pgvector | OpenSearch |
|---|----------|----------|------------|
| Тип | Managed | Extension | Self/Managed |
| Scale | Billions | Millions | Billions |
| Hybrid search | Да | Нет | Да |

**35. RAG архитектура**
```
Query → Embed → Vector Search → Rerank → Context Assembly → LLM → Response
```
- Chunk с overlap
- Metadata filtering
- Reranking для relevance
- Цитирование источников

**36. Prompt management**
- Prompt Registry: версионирование, параметры
- A/B Testing: consistent hashing по user_id
- Storage: DynamoDB, PostgreSQL

**37. LLM evaluation**
- Relevance: LLM-as-judge (1-5)
- Groundedness: факты из контекста
- Correctness: сравнение с reference
- Pipeline: test set → generate → evaluate → aggregate

---

## Security и CI/CD

**38. Security**
- IAM: Least privilege, конкретные actions + resources
- Secrets Manager: GetSecretValue, автоматическая ротация
- KMS: encrypt/decrypt, envelope encryption для больших данных

**39. CI/CD**
- SAM: `sam build` → `sam deploy`
- GitHub Actions: test → build → deploy
- CDK Pipeline: synth → staging → manual approval → prod
- Preview environments для PR

**40. API Security**
- JWT: JWKS validation, audience, issuer check
- API Keys: Usage Plans с quotas
- WAF: rate limiting, SQLi, bad inputs
- Security Headers: HSTS, CSP, X-Frame-Options

---

## Вопросы к интервьюеру

- Сколько ML vs platform engineers?
- Какие LLM провайдеры?
- Какой объём запросов к LLM в день?
- Как справляетесь с rate limits?
- Используете fine-tuning или только prompting?

**Red flags:**
- Нет мониторинга LLM качества
- Промпты в коде
- Нет fallback провайдера
