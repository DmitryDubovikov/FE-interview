# Топ-40 Вопросов для AI Platform Engineer Собеседования

Шпаргалка для подготовки к собеседованиям на позицию AI Platform Engineer (Middle/Senior). Вопросы охватывают: Python/FastAPI, AWS Serverless, Event-Driven архитектуру, LLM-платформы, Observability, Security.

## 🟢 Python и FastAPI

1. **FastAPI: async/await, Depends, middleware**

   **async/await** — FastAPI построен на Starlette и полностью поддерживает асинхронность. Async handlers освобождают event loop во время I/O операций.

   ```python
   from fastapi import FastAPI, Depends, Request
   from contextlib import asynccontextmanager

   # Async endpoint
   @app.get("/users/{user_id}")
   async def get_user(user_id: int):
       user = await db.fetch_user(user_id)  # Non-blocking I/O
       return user

   # Sync endpoint — FastAPI запустит в threadpool
   @app.get("/cpu-heavy")
   def compute():
       return heavy_computation()  # Не блокирует event loop
   ```

   **Depends** — система dependency injection для переиспользования логики:

   ```python
   async def get_db():
       db = AsyncSession()
       try:
           yield db
       finally:
           await db.close()

   async def get_current_user(
       token: str = Header(),
       db: AsyncSession = Depends(get_db)
   ):
       user = await db.get(User, token=token)
       if not user:
           raise HTTPException(401, "Invalid token")
       return user

   @app.get("/me")
   async def read_me(user: User = Depends(get_current_user)):
       return user
   ```

   **Middleware** — обработка запросов до/после endpoint:

   ```python
   @app.middleware("http")
   async def add_request_id(request: Request, call_next):
       request_id = request.headers.get("X-Request-ID", str(uuid4()))
       request.state.request_id = request_id
       response = await call_next(request)
       response.headers["X-Request-ID"] = request_id
       return response
   ```

---

2. **Streaming responses в FastAPI (SSE, WebSocket)**

   **Server-Sent Events (SSE)** — односторонний поток от сервера к клиенту:

   ```python
   from fastapi.responses import StreamingResponse
   import asyncio

   async def event_generator():
       while True:
           data = await get_new_data()
           yield f"data: {json.dumps(data)}\n\n"
           await asyncio.sleep(1)

   @app.get("/stream")
   async def stream_events():
       return StreamingResponse(
           event_generator(),
           media_type="text/event-stream"
       )
   ```

   **Streaming для LLM ответов:**

   ```python
   async def stream_llm_response(prompt: str):
       async for chunk in llm_client.stream(prompt):
           yield f"data: {json.dumps({'text': chunk})}\n\n"
       yield "data: [DONE]\n\n"

   @app.post("/chat/stream")
   async def chat_stream(request: ChatRequest):
       return StreamingResponse(
           stream_llm_response(request.prompt),
           media_type="text/event-stream"
       )
   ```

   **WebSocket** — двусторонняя коммуникация:

   ```python
   from fastapi import WebSocket, WebSocketDisconnect

   @app.websocket("/ws/chat")
   async def websocket_chat(websocket: WebSocket):
       await websocket.accept()
       try:
           while True:
               data = await websocket.receive_text()
               response = await process_message(data)
               await websocket.send_text(response)
       except WebSocketDisconnect:
           logger.info("Client disconnected")
   ```

   **Когда что использовать:**
   - SSE: уведомления, streaming LLM, real-time обновления (проще)
   - WebSocket: чат, gaming, bidirectional communication

---

3. **Pydantic v2: валидация, сериализация, настройки**

   **Pydantic v2** — быстрее в 5-50x благодаря Rust-ядру (pydantic-core).

   ```python
   from pydantic import BaseModel, Field, field_validator, model_validator
   from pydantic_settings import BaseSettings

   class ChatMessage(BaseModel):
       role: str = Field(..., pattern="^(user|assistant|system)$")
       content: str = Field(..., min_length=1, max_length=100000)

       model_config = {
           "str_strip_whitespace": True,
           "validate_default": True
       }

   class ChatRequest(BaseModel):
       messages: list[ChatMessage]
       model: str = "gpt-4"
       temperature: float = Field(default=0.7, ge=0, le=2)
       max_tokens: int | None = Field(default=None, gt=0)

       @field_validator("messages")
       @classmethod
       def validate_messages(cls, v):
           if not v:
               raise ValueError("Messages cannot be empty")
           return v

       @model_validator(mode="after")
       def validate_model(self):
           if self.model.startswith("o1") and self.temperature != 1:
               raise ValueError("o1 models require temperature=1")
           return self
   ```

   **Settings с env variables:**

   ```python
   class Settings(BaseSettings):
       openai_api_key: str
       aws_region: str = "us-east-1"
       debug: bool = False

       model_config = {
           "env_file": ".env",
           "env_prefix": "APP_"
       }

   settings = Settings()  # Читает APP_OPENAI_API_KEY из .env
   ```

   **Сериализация:**

   ```python
   # model_dump() вместо dict() в v2
   data = request.model_dump(exclude_none=True)

   # Кастомная сериализация
   class User(BaseModel):
       password: str = Field(exclude=True)  # Не включать в JSON
   ```

---

4. **OpenAPI 3.1: спецификация и генерация SDK**

   FastAPI автоматически генерирует OpenAPI 3.1 схему из Pydantic моделей и type hints.

   ```python
   from fastapi import FastAPI, Query, Path

   app = FastAPI(
       title="AI Platform API",
       version="1.0.0",
       description="API for LLM interactions",
       openapi_tags=[
           {"name": "chat", "description": "Chat completions"},
           {"name": "embeddings", "description": "Text embeddings"}
       ]
   )

   @app.post("/chat/completions", tags=["chat"], response_model=ChatResponse)
   async def create_chat_completion(
       request: ChatRequest,
       api_key: str = Header(..., description="API key for authentication")
   ) -> ChatResponse:
       """
       Create a chat completion.

       - **messages**: List of messages in the conversation
       - **model**: Model to use for completion
       """
       ...
   ```

   **Генерация SDK:**

   ```bash
   # Получить OpenAPI spec
   curl http://localhost:8000/openapi.json > openapi.json

   # Генерация Python SDK
   openapi-python-client generate --path openapi.json

   # Генерация TypeScript SDK
   npx openapi-typescript-codegen --input openapi.json --output ./sdk
   ```

   **Кастомизация схемы:**

   ```python
   class ChatRequest(BaseModel):
       model_config = {
           "json_schema_extra": {
               "examples": [{
                   "messages": [{"role": "user", "content": "Hello"}],
                   "model": "gpt-4"
               }]
           }
       }
   ```

---

5. **Background tasks и lifespan events**

   **Background Tasks** — для операций после отправки response:

   ```python
   from fastapi import BackgroundTasks

   async def log_request(request_id: str, duration: float):
       await analytics.log(request_id, duration)

   async def send_notification(user_id: str, message: str):
       await notification_service.send(user_id, message)

   @app.post("/orders")
   async def create_order(
       order: OrderRequest,
       background_tasks: BackgroundTasks
   ):
       result = await process_order(order)
       # Выполнится ПОСЛЕ отправки response
       background_tasks.add_task(log_request, result.id, result.duration)
       background_tasks.add_task(send_notification, order.user_id, "Order created")
       return result
   ```

   **Lifespan Events** — инициализация и cleanup:

   ```python
   from contextlib import asynccontextmanager

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Startup
       app.state.db = await create_db_pool()
       app.state.redis = await aioredis.from_url("redis://localhost")
       app.state.llm_client = AsyncOpenAI()

       yield  # Приложение работает

       # Shutdown
       await app.state.db.close()
       await app.state.redis.close()

   app = FastAPI(lifespan=lifespan)

   @app.get("/health")
   async def health(request: Request):
       return {"db": await request.app.state.db.ping()}
   ```

   **Когда Background Tasks vs очереди:**
   - Background Tasks: быстрые операции, не критично если потеряются при перезапуске
   - SQS/Celery: долгие операции, нужна надёжность, retry, мониторинг

---

6. **Async programming: asyncio patterns для высоконагруженных API**

   **Concurrent requests с gather:**

   ```python
   import asyncio

   async def enrich_user_data(user_id: str):
       # Параллельные запросы
       profile, orders, recommendations = await asyncio.gather(
           fetch_profile(user_id),
           fetch_orders(user_id),
           fetch_recommendations(user_id)
       )
       return {**profile, "orders": orders, "recommendations": recommendations}
   ```

   **Semaphore для rate limiting:**

   ```python
   semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests

   async def call_external_api(data):
       async with semaphore:
           return await http_client.post(url, json=data)

   # 100 запросов, но max 10 одновременно
   results = await asyncio.gather(*[call_external_api(d) for d in data_list])
   ```

   **Timeout handling:**

   ```python
   async def fetch_with_timeout(url: str, timeout: float = 5.0):
       try:
           async with asyncio.timeout(timeout):
               return await http_client.get(url)
       except asyncio.TimeoutError:
           raise HTTPException(504, "Upstream timeout")
   ```

   **TaskGroup (Python 3.11+):**

   ```python
   async def process_batch(items: list):
       results = []
       async with asyncio.TaskGroup() as tg:
           for item in items:
               task = tg.create_task(process_item(item))
               results.append(task)
       return [t.result() for t in results]
   ```

   **Антипаттерны:**
   - `await` в цикле вместо `gather` — последовательное выполнение
   - Блокирующий код в async функции — используй `run_in_executor`
   - Создание нового event loop — используй существующий

---

## 🟢 AWS Compute и Networking

7. **Lambda vs ECS Fargate: когда что выбрать**

   | Критерий | Lambda | ECS Fargate |
   |----------|--------|-------------|
   | Модель | Function-as-a-Service | Container-as-a-Service |
   | Масштабирование | Автоматическое, per-request | Автоматическое, task-based |
   | Cold start | Есть (100ms - 10s) | Нет (контейнер всегда running) |
   | Max timeout | 15 минут | Неограничен |
   | Биллинг | Per-invocation + duration | Per-second (vCPU + memory) |
   | Max memory | 10 GB | 120 GB |
   | Networking | VPC optional | VPC required |

   **Выбирай Lambda:**
   - Событийная обработка (S3, SQS, API Gateway)
   - Непредсказуемая нагрузка с простоями
   - Короткие операции (< 15 мин)
   - Нужна максимальная экономия при низком трафике

   **Выбирай ECS Fargate:**
   - Постоянный трафик (cheaper at scale)
   - Long-running processes
   - Нужен полный контроль над runtime
   - WebSocket, gRPC, streaming
   - Большие ML модели в памяти

   ```python
   # Lambda handler
   def handler(event, context):
       return {"statusCode": 200, "body": json.dumps(result)}

   # ECS — обычное FastAPI приложение
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

8. **API Gateway: REST vs HTTP API, throttling, caching**

   | Критерий | REST API | HTTP API |
   |----------|----------|----------|
   | Цена | $3.50/million | $1.00/million |
   | Latency | ~30ms overhead | ~10ms overhead |
   | Features | Полный набор | Базовый |
   | Caching | Да | Нет |
   | WebSocket | Да | Нет |
   | Request validation | Да | Нет |
   | API Keys | Да | Да |

   **Throttling:**

   ```yaml
   # SAM template
   Resources:
     ApiGateway:
       Type: AWS::Serverless::Api
       Properties:
         StageName: prod
         MethodSettings:
           - HttpMethod: "*"
             ResourcePath: "/*"
             ThrottlingBurstLimit: 1000
             ThrottlingRateLimit: 500  # requests/sec
   ```

   **Caching (REST API only):**

   ```yaml
   MethodSettings:
     - HttpMethod: GET
       ResourcePath: /users/{id}
       CachingEnabled: true
       CacheTtlInSeconds: 300
   ```

   **Когда REST API:**
   - Нужен caching
   - Request/response validation
   - WebSocket support
   - Usage plans и API keys с quotas

   **Когда HTTP API:**
   - Простой API, важна цена
   - JWT авторизация (встроенная)
   - Минимальная latency критична

---

9. **Lambda: layers, cold starts, provisioned concurrency**

   **Lambda Layers** — shared код между функциями:

   ```bash
   # Создание layer с зависимостями
   mkdir -p python/lib/python3.11/site-packages
   pip install -t python/lib/python3.11/site-packages openai boto3
   zip -r layer.zip python
   aws lambda publish-layer-version \
       --layer-name ai-dependencies \
       --zip-file fileb://layer.zip
   ```

   ```yaml
   # SAM template
   MyFunction:
     Type: AWS::Serverless::Function
     Properties:
       Layers:
         - !Ref DependenciesLayer
         - arn:aws:lambda:us-east-1:123456789:layer:ai-dependencies:1
   ```

   **Cold Start оптимизация:**

   ```python
   # ПЛОХО: импорт внутри handler
   def handler(event, context):
       import pandas as pd  # Cold start каждый раз
       ...

   # ХОРОШО: импорт вне handler
   import pandas as pd  # Один раз при cold start

   # Инициализация клиентов вне handler
   bedrock = boto3.client("bedrock-runtime")

   def handler(event, context):
       return bedrock.invoke_model(...)
   ```

   **Provisioned Concurrency:**

   ```yaml
   MyFunction:
     Type: AWS::Serverless::Function
     Properties:
       AutoPublishAlias: live
       ProvisionedConcurrencyConfig:
         ProvisionedConcurrentExecutions: 10
   ```

   - Функции "прогреты" и готовы
   - Платишь за provisioned instances даже без трафика
   - Используй для production API с требованиями к latency

---

10. **ECS Fargate: task definitions, service discovery, auto-scaling**

    **Task Definition:**

    ```json
    {
      "family": "ai-platform-api",
      "cpu": "1024",
      "memory": "2048",
      "networkMode": "awsvpc",
      "containerDefinitions": [{
        "name": "api",
        "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/ai-api:latest",
        "portMappings": [{"containerPort": 8000}],
        "environment": [
          {"name": "ENV", "value": "production"}
        ],
        "secrets": [
          {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
        ],
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "/ecs/ai-platform",
            "awslogs-region": "us-east-1"
          }
        },
        "healthCheck": {
          "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
          "interval": 30,
          "timeout": 5,
          "retries": 3
        }
      }]
    }
    ```

    **Service Discovery (Cloud Map):**

    ```yaml
    # Сервисы находят друг друга по DNS
    # api.prod.local -> private IP of ECS task
    ServiceDiscovery:
      Type: AWS::ServiceDiscovery::Service
      Properties:
        Name: api
        NamespaceId: !Ref PrivateNamespace
        DnsConfig:
          DnsRecords:
            - Type: A
              TTL: 10
    ```

    **Auto-scaling:**

    ```yaml
    ScalingTarget:
      Type: AWS::ApplicationAutoScaling::ScalableTarget
      Properties:
        MinCapacity: 2
        MaxCapacity: 20
        ResourceId: !Sub service/${Cluster}/${Service}
        ScalableDimension: ecs:service:DesiredCount

    ScalingPolicy:
      Type: AWS::ApplicationAutoScaling::ScalingPolicy
      Properties:
        PolicyType: TargetTrackingScaling
        TargetTrackingScalingPolicyConfiguration:
          TargetValue: 70
          PredefinedMetricSpecification:
            PredefinedMetricType: ECSServiceAverageCPUUtilization
          ScaleInCooldown: 60
          ScaleOutCooldown: 60
    ```

---

11. **VPC, Security Groups, NAT Gateway для serverless**

    **VPC для Lambda/Fargate:**

    ```
    ┌─────────────────────────────────────────────────────────────┐
    │ VPC (10.0.0.0/16)                                           │
    │  ┌─────────────────────┐  ┌─────────────────────┐          │
    │  │ Public Subnet       │  │ Public Subnet       │          │
    │  │ 10.0.1.0/24 (AZ-a)  │  │ 10.0.2.0/24 (AZ-b)  │          │
    │  │  ┌──────────────┐   │  │  ┌──────────────┐   │          │
    │  │  │ NAT Gateway  │   │  │  │ NAT Gateway  │   │          │
    │  │  └──────────────┘   │  │  └──────────────┘   │          │
    │  └─────────────────────┘  └─────────────────────┘          │
    │  ┌─────────────────────┐  ┌─────────────────────┐          │
    │  │ Private Subnet      │  │ Private Subnet      │          │
    │  │ 10.0.3.0/24 (AZ-a)  │  │ 10.0.4.0/24 (AZ-b)  │          │
    │  │  ┌──────┐ ┌──────┐  │  │  ┌──────┐ ┌──────┐  │          │
    │  │  │Lambda│ │Fargate│  │  │  │Lambda│ │Fargate│  │          │
    │  │  └──────┘ └──────┘  │  │  └──────┘ └──────┘  │          │
    │  └─────────────────────┘  └─────────────────────┘          │
    └─────────────────────────────────────────────────────────────┘
    ```

    **Security Groups:**

    ```yaml
    LambdaSG:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupDescription: Lambda security group
        VpcId: !Ref VPC
        SecurityGroupEgress:
          - IpProtocol: tcp
            FromPort: 443
            ToPort: 443
            CidrIp: 0.0.0.0/0  # HTTPS to internet
          - IpProtocol: tcp
            FromPort: 5432
            ToPort: 5432
            DestinationSecurityGroupId: !Ref DatabaseSG  # PostgreSQL

    DatabaseSG:
      Type: AWS::EC2::SecurityGroup
      Properties:
        SecurityGroupIngress:
          - IpProtocol: tcp
            FromPort: 5432
            ToPort: 5432
            SourceSecurityGroupId: !Ref LambdaSG  # Только от Lambda
    ```

    **NAT Gateway** — для доступа в интернет из private subnet:
    - Lambda/Fargate в private subnet → NAT Gateway → Internet
    - Дорого (~$45/month per NAT + data transfer)
    - Альтернатива: VPC Endpoints для AWS сервисов (S3, DynamoDB, Secrets Manager)

---

12. **CloudFront + API Gateway: edge optimization**

    **Архитектура:**

    ```
    User → CloudFront Edge → Regional API Gateway → Lambda/Fargate
                ↓
           Cache (if enabled)
    ```

    **CloudFront перед API Gateway:**

    ```yaml
    CloudFrontDistribution:
      Type: AWS::CloudFront::Distribution
      Properties:
        DistributionConfig:
          Origins:
            - DomainName: !Sub "${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com"
              Id: ApiGatewayOrigin
              CustomOriginConfig:
                OriginProtocolPolicy: https-only
          DefaultCacheBehavior:
            TargetOriginId: ApiGatewayOrigin
            ViewerProtocolPolicy: redirect-to-https
            CachePolicyId: !Ref CachePolicy
            OriginRequestPolicyId: !Ref OriginRequestPolicy
          PriceClass: PriceClass_100  # US, Canada, Europe
    ```

    **Cache Policy для API:**

    ```yaml
    CachePolicy:
      Type: AWS::CloudFront::CachePolicy
      Properties:
        CachePolicyConfig:
          Name: api-cache-policy
          DefaultTTL: 60
          MaxTTL: 300
          MinTTL: 0
          ParametersInCacheKeyAndForwardedToOrigin:
            HeadersConfig:
              HeaderBehavior: whitelist
              Headers:
                - Authorization  # Разный кеш для разных users
            QueryStringsConfig:
              QueryStringBehavior: all  # Включить query params в cache key
            CookiesConfig:
              CookieBehavior: none
    ```

    **Преимущества:**
    - Edge locations ближе к пользователям (снижение latency)
    - Кеширование GET запросов
    - DDoS protection (AWS Shield)
    - Custom domain + SSL certificate

---

## 🟡 Очереди и Event-Driven архитектура

13. **SQS: стандартные vs FIFO, visibility timeout, DLQ**

    | Критерий | Standard Queue | FIFO Queue |
    |----------|----------------|------------|
    | Throughput | Unlimited | 3000 msg/sec (with batching) |
    | Ordering | Best-effort | Strict FIFO |
    | Delivery | At-least-once | Exactly-once |
    | Deduplication | Нет | 5-minute window |

    **Visibility Timeout:**

    ```python
    # Сообщение "невидимо" пока обрабатывается
    # Если consumer упал — сообщение вернётся в очередь

    sqs = boto3.client('sqs')

    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        VisibilityTimeout=60,  # 60 секунд на обработку
        WaitTimeSeconds=20  # Long polling
    )

    for message in response.get('Messages', []):
        try:
            process(message)
            # Успех — удаляем
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
        except Exception:
            # Не удаляем — вернётся в очередь после visibility timeout
            pass
    ```

    **Dead Letter Queue (DLQ):**

    ```yaml
    MainQueue:
      Type: AWS::SQS::Queue
      Properties:
        RedrivePolicy:
          deadLetterTargetArn: !GetAtt DLQ.Arn
          maxReceiveCount: 3  # После 3 попыток → в DLQ

    DLQ:
      Type: AWS::SQS::Queue
      Properties:
        MessageRetentionPeriod: 1209600  # 14 days
    ```

    **Best practices:**
    - Long polling (WaitTimeSeconds=20) — экономит деньги
    - Batch operations — до 10 сообщений за раз
    - Idempotent consumers — сообщение может прийти дважды

---

14. **Step Functions: Express vs Standard, паттерны оркестрации**

    | Критерий | Standard | Express |
    |----------|----------|---------|
    | Длительность | До 1 года | До 5 минут |
    | Цена | Per state transition | Per execution + duration |
    | Execution history | Да (90 дней) | Нет (только CloudWatch) |
    | Exactly-once | Да | At-least-once |
    | Use case | Long-running workflows | High-volume, short |

    **Паттерн: Sequential steps**

    ```json
    {
      "StartAt": "ExtractText",
      "States": {
        "ExtractText": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:extract",
          "Next": "AnalyzeSentiment"
        },
        "AnalyzeSentiment": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:analyze",
          "End": true
        }
      }
    }
    ```

    **Паттерн: Parallel processing**

    ```json
    {
      "Type": "Parallel",
      "Branches": [
        {"StartAt": "ProcessImages", "States": {...}},
        {"StartAt": "ProcessText", "States": {...}},
        {"StartAt": "ProcessMetadata", "States": {...}}
      ],
      "Next": "AggregateResults"
    }
    ```

    **Паттерн: Map (batch processing)**

    ```json
    {
      "Type": "Map",
      "ItemsPath": "$.documents",
      "MaxConcurrency": 10,
      "Iterator": {
        "StartAt": "ProcessDocument",
        "States": {
          "ProcessDocument": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:...:process",
            "End": true
          }
        }
      }
    }
    ```

    **Error handling:**

    ```json
    {
      "Type": "Task",
      "Resource": "...",
      "Retry": [
        {
          "ErrorEquals": ["States.TaskFailed"],
          "IntervalSeconds": 2,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "HandleError"
        }
      ]
    }
    ```

---

15. **EventBridge: rules, event patterns, scheduler**

    **Event Pattern matching:**

    ```python
    # Событие
    {
        "source": "ai-platform",
        "detail-type": "ChatCompletion",
        "detail": {
            "model": "gpt-4",
            "tokens": 1500,
            "status": "success"
        }
    }
    ```

    ```yaml
    # Rule: только успешные completions с GPT-4
    EventRule:
      Type: AWS::Events::Rule
      Properties:
        EventPattern:
          source:
            - ai-platform
          detail-type:
            - ChatCompletion
          detail:
            model:
              - prefix: "gpt-4"
            status:
              - success
        Targets:
          - Arn: !GetAtt ProcessorLambda.Arn
            Id: processor
    ```

    **Публикация событий:**

    ```python
    import boto3

    events = boto3.client('events')

    events.put_events(Entries=[{
        'Source': 'ai-platform',
        'DetailType': 'ChatCompletion',
        'Detail': json.dumps({
            'model': 'gpt-4',
            'tokens': 1500,
            'status': 'success',
            'user_id': 'user-123'
        }),
        'EventBusName': 'ai-platform-bus'
    }])
    ```

    **EventBridge Scheduler:**

    ```yaml
    # Cron job каждый час
    HourlySchedule:
      Type: AWS::Scheduler::Schedule
      Properties:
        ScheduleExpression: "rate(1 hour)"
        Target:
          Arn: !GetAtt CleanupLambda.Arn
          RoleArn: !GetAtt SchedulerRole.Arn
        FlexibleTimeWindow:
          Mode: "OFF"
    ```

    **Когда EventBridge vs SQS:**
    - EventBridge: event routing, content-based filtering, cross-account
    - SQS: guaranteed delivery, retry logic, batch processing

---

16. **Async job orchestration: выбор между SQS, Step Functions, EventBridge**

    | Сценарий | Решение |
    |----------|---------|
    | Простая очередь задач | SQS + Lambda |
    | Fan-out (1 → много) | SNS + SQS |
    | Complex workflow с ветвлением | Step Functions |
    | Event routing по содержимому | EventBridge |
    | Long-running ML training | Step Functions Standard |
    | High-volume short tasks | Step Functions Express / SQS |

    **Пример: AI Pipeline**

    ```
    User Request
         ↓
    API Gateway → Lambda (validate)
         ↓
    EventBridge (route by request type)
         ↓
    ┌────────────────┬─────────────────┬──────────────────┐
    │ Chat           │ Embedding       │ Image Generation │
    │ (Step Express) │ (Lambda direct) │ (Step Standard)  │
    └────────────────┴─────────────────┴──────────────────┘
         ↓                   ↓                   ↓
    Response Queue (SQS) → Webhook/Polling
    ```

    ```python
    # EventBridge routing
    {
        "source": ["ai-platform"],
        "detail-type": ["AIRequest"],
        "detail": {
            "type": ["chat"]  # → Step Functions Express
        }
    }

    {
        "detail": {
            "type": ["image"]  # → Step Functions Standard (long-running)
        }
    }
    ```

---

17. **Паттерн Saga для распределённых транзакций**

    **Проблема:** Транзакция охватывает несколько сервисов. Нет распределённого ACID.

    **Saga** — последовательность локальных транзакций с компенсирующими действиями:

    ```
    CreateOrder → ReserveCredits → CallLLM → ChargeCredits → Complete
         ↓             ↓             ↓            ↓
    (compensate)  ReleaseCredits  (no-op)   RefundCredits
    ```

    **Choreography (через события):**

    ```python
    # Order Service
    async def create_order(order):
        await db.save(order)
        await events.publish("OrderCreated", order)

    # Credits Service listens to OrderCreated
    @subscribe("OrderCreated")
    async def reserve_credits(event):
        try:
            await credits.reserve(event.user_id, event.amount)
            await events.publish("CreditsReserved", event)
        except InsufficientCredits:
            await events.publish("CreditsFailed", event)

    # Order Service listens to CreditsFailed
    @subscribe("CreditsFailed")
    async def cancel_order(event):
        await db.update(event.order_id, status="cancelled")
    ```

    **Orchestration (Step Functions):**

    ```json
    {
      "StartAt": "CreateOrder",
      "States": {
        "CreateOrder": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:createOrder",
          "Next": "ReserveCredits",
          "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "OrderFailed"}]
        },
        "ReserveCredits": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:reserveCredits",
          "Next": "CallLLM",
          "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "CancelOrder"}]
        },
        "CallLLM": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:callLLM",
          "Next": "ChargeCredits",
          "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "ReleaseCredits"}]
        },
        "ReleaseCredits": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:releaseCredits",
          "Next": "CancelOrder"
        },
        "CancelOrder": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:cancelOrder",
          "Next": "OrderFailed"
        },
        "OrderFailed": {"Type": "Fail"}
      }
    }
    ```

---

## 🟡 Производительность и надёжность

18. **Caching strategies: ElastiCache Redis/Memcached, CloudFront**

    | Критерий | Redis | Memcached |
    |----------|-------|-----------|
    | Структуры данных | Rich (lists, sets, sorted sets) | String only |
    | Persistence | Да (RDB, AOF) | Нет |
    | Replication | Да | Нет |
    | Clustering | Да | Да |
    | Use case | Sessions, leaderboards, queues | Simple caching |

    **Cache-Aside с Redis:**

    ```python
    import redis.asyncio as redis

    cache = redis.Redis(host='elasticache-endpoint', decode_responses=True)

    async def get_llm_response(prompt_hash: str, prompt: str):
        # Check cache
        cached = await cache.get(f"llm:{prompt_hash}")
        if cached:
            return json.loads(cached)

        # Cache miss → call LLM
        response = await llm_client.complete(prompt)

        # Store with TTL
        await cache.setex(
            f"llm:{prompt_hash}",
            3600,  # 1 hour
            json.dumps(response)
        )
        return response
    ```

    **CloudFront для API responses:**

    ```python
    @app.get("/models")
    async def list_models():
        # Cache-Control header → CloudFront caches
        return Response(
            content=json.dumps(models),
            headers={
                "Cache-Control": "public, max-age=300",  # 5 min
                "ETag": calculate_etag(models)
            }
        )
    ```

    **Многоуровневое кеширование:**
    ```
    Client → CloudFront (edge) → API Gateway (regional) → Redis → Database
    ```

---

19. **Idempotency: реализация для API endpoints**

    **Idempotency Key pattern:**

    ```python
    from fastapi import Header, HTTPException
    import hashlib

    @app.post("/chat/completions")
    async def create_completion(
        request: ChatRequest,
        idempotency_key: str = Header(None)
    ):
        # Generate key from request if not provided
        if not idempotency_key:
            idempotency_key = hashlib.sha256(
                request.model_dump_json().encode()
            ).hexdigest()

        cache_key = f"idempotency:{idempotency_key}"

        # Check if already processed
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Lock to prevent concurrent duplicate processing
        lock = await redis.set(
            f"lock:{idempotency_key}",
            "1",
            nx=True,  # Only if not exists
            ex=30     # 30 sec lock
        )
        if not lock:
            raise HTTPException(409, "Request in progress")

        try:
            # Process request
            result = await process_completion(request)

            # Store result (24 hours)
            await redis.setex(cache_key, 86400, json.dumps(result))
            return result
        finally:
            await redis.delete(f"lock:{idempotency_key}")
    ```

    **Database-level idempotency:**

    ```python
    async def create_transaction(tx_id: str, amount: float):
        try:
            # UNIQUE constraint на tx_id
            await db.execute(
                "INSERT INTO transactions (id, amount, status) VALUES ($1, $2, 'pending')",
                tx_id, amount
            )
        except UniqueViolation:
            # Already exists — return existing
            return await db.fetchone(
                "SELECT * FROM transactions WHERE id = $1", tx_id
            )
    ```

---

20. **Rate limiting: token bucket, sliding window, API Gateway throttling**

    **Token Bucket (Redis):**

    ```python
    async def check_rate_limit(user_id: str, limit: int = 100, window: int = 60):
        key = f"ratelimit:{user_id}"

        # Lua script for atomic operation
        script = """
        local current = redis.call('INCR', KEYS[1])
        if current == 1 then
            redis.call('EXPIRE', KEYS[1], ARGV[1])
        end
        return current
        """

        current = await redis.eval(script, 1, key, window)

        if current > limit:
            raise HTTPException(
                429,
                "Rate limit exceeded",
                headers={"Retry-After": str(window)}
            )

        return limit - current  # Remaining requests
    ```

    **Sliding Window (more accurate):**

    ```python
    async def sliding_window_limit(user_id: str, limit: int, window: int):
        now = time.time()
        key = f"ratelimit:{user_id}"

        # Remove old entries, add new, count
        async with redis.pipeline() as pipe:
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(uuid4()): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            results = await pipe.execute()

        count = results[2]
        if count > limit:
            raise HTTPException(429, "Rate limit exceeded")
    ```

    **API Gateway Throttling:**

    ```yaml
    # Per-method throttling
    MethodSettings:
      - HttpMethod: POST
        ResourcePath: /chat/completions
        ThrottlingRateLimit: 10    # requests/sec steady state
        ThrottlingBurstLimit: 20   # max burst

    # Usage Plans
    UsagePlan:
      Type: AWS::ApiGateway::UsagePlan
      Properties:
        Quota:
          Limit: 10000
          Period: MONTH
        Throttle:
          RateLimit: 100
          BurstLimit: 200
    ```

---

21. **Request deduplication: паттерны и реализация**

    **Content-based deduplication:**

    ```python
    import hashlib

    def generate_request_hash(request: ChatRequest) -> str:
        # Нормализуем и хешируем
        content = json.dumps(request.model_dump(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @app.post("/chat/completions")
    async def create_completion(request: ChatRequest):
        request_hash = generate_request_hash(request)

        # Deduplication window (5 minutes)
        dedup_key = f"dedup:{request_hash}"

        existing = await redis.get(dedup_key)
        if existing:
            return json.loads(existing)

        result = await process_request(request)
        await redis.setex(dedup_key, 300, json.dumps(result))
        return result
    ```

    **SQS FIFO deduplication:**

    ```python
    sqs.send_message(
        QueueUrl=fifo_queue_url,
        MessageBody=json.dumps(message),
        MessageGroupId=user_id,
        MessageDeduplicationId=hashlib.sha256(
            json.dumps(message).encode()
        ).hexdigest()
    )
    # SQS игнорирует дубликаты в течение 5 минут
    ```

    **Database-level (PostgreSQL):**

    ```sql
    -- Advisory lock на время обработки
    SELECT pg_advisory_xact_lock(hashtext('request:' || $1));

    -- Или INSERT ... ON CONFLICT
    INSERT INTO processed_requests (hash, result, created_at)
    VALUES ($1, $2, NOW())
    ON CONFLICT (hash) DO UPDATE SET accessed_at = NOW()
    RETURNING result;
    ```

---

22. **Circuit Breaker: реализация и интеграция**

    **Состояния:**
    ```
    CLOSED → слишком много ошибок → OPEN
       ↑                              ↓
       └───── успех ←──── HALF_OPEN ←┘ (после timeout)
    ```

    **Реализация с pybreaker:**

    ```python
    from pybreaker import CircuitBreaker, CircuitBreakerError

    # Настройка breaker
    llm_breaker = CircuitBreaker(
        fail_max=5,           # Открыть после 5 ошибок
        reset_timeout=30,     # Попробовать снова через 30 сек
        exclude=[ValueError]  # Не считать бизнес-ошибки
    )

    @llm_breaker
    async def call_llm(prompt: str):
        return await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

    @app.post("/chat")
    async def chat(request: ChatRequest):
        try:
            return await call_llm(request.prompt)
        except CircuitBreakerError:
            # Circuit open — fallback
            return await call_fallback_llm(request.prompt)
    ```

    **Интеграция с AWS:**

    ```python
    # Circuit breaker per service
    breakers = {
        "bedrock": CircuitBreaker(fail_max=3, reset_timeout=60),
        "openai": CircuitBreaker(fail_max=5, reset_timeout=30),
    }

    async def call_with_fallback(request: ChatRequest):
        providers = ["openai", "bedrock"]

        for provider in providers:
            try:
                return await breakers[provider].call_async(
                    call_provider, provider, request
                )
            except CircuitBreakerError:
                continue

        raise HTTPException(503, "All providers unavailable")
    ```

---

23. **Policy-based routing: feature flags, A/B testing, canary**

    **Feature Flags с LaunchDarkly/custom:**

    ```python
    from typing import Optional

    class FeatureFlags:
        def __init__(self, redis_client):
            self.redis = redis_client

        async def is_enabled(
            self,
            flag: str,
            user_id: str,
            default: bool = False
        ) -> bool:
            # Check user-specific override
            user_flag = await self.redis.get(f"flag:{flag}:user:{user_id}")
            if user_flag is not None:
                return user_flag == "1"

            # Check percentage rollout
            rollout = await self.redis.get(f"flag:{flag}:rollout")
            if rollout:
                # Consistent hashing for user
                hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
                return (hash_val % 100) < int(rollout)

            return default

    flags = FeatureFlags(redis)

    @app.post("/chat")
    async def chat(request: ChatRequest, user: User = Depends(get_user)):
        if await flags.is_enabled("use_gpt4_turbo", user.id):
            model = "gpt-4-turbo"
        else:
            model = "gpt-4"
        ...
    ```

    **A/B Testing:**

    ```python
    async def get_experiment_variant(
        experiment: str,
        user_id: str,
        variants: list[str]
    ) -> str:
        # Consistent assignment
        hash_input = f"{experiment}:{user_id}"
        hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        variant_index = hash_val % len(variants)

        # Log assignment for analysis
        await analytics.log_assignment(experiment, user_id, variants[variant_index])

        return variants[variant_index]

    # Usage
    variant = await get_experiment_variant(
        "prompt_style",
        user.id,
        ["concise", "detailed", "conversational"]
    )
    ```

    **Canary Deployment (API Gateway):**

    ```yaml
    # Weighted routing
    ApiGatewayStage:
      Type: AWS::ApiGateway::Stage
      Properties:
        DeploymentId: !Ref NewDeployment
        CanarySetting:
          PercentTraffic: 10  # 10% to canary
          UseStageCache: false
    ```

---

## 🟡 Базы данных

24. **DynamoDB: single-table design, GSI/LSI, capacity modes**

    **Single-Table Design:**

    ```
    PK              | SK                  | Data
    ----------------|---------------------|------------------
    USER#123        | PROFILE             | {name, email, ...}
    USER#123        | USAGE#2024-01       | {tokens: 5000}
    USER#123        | USAGE#2024-02       | {tokens: 3000}
    ORG#abc         | METADATA            | {name, plan, ...}
    ORG#abc         | MEMBER#user123      | {role: admin}
    ```

    ```python
    # Получить профиль пользователя
    table.get_item(Key={"PK": "USER#123", "SK": "PROFILE"})

    # Получить всё по пользователю
    table.query(KeyConditionExpression="PK = :pk", ExpressionAttributeValues={":pk": "USER#123"})

    # Получить usage за период
    table.query(
        KeyConditionExpression="PK = :pk AND SK BETWEEN :start AND :end",
        ExpressionAttributeValues={
            ":pk": "USER#123",
            ":start": "USAGE#2024-01",
            ":end": "USAGE#2024-12"
        }
    )
    ```

    **GSI vs LSI:**

    | | GSI | LSI |
    |---|-----|-----|
    | Partition Key | Другой | Тот же |
    | Sort Key | Любой | Другой |
    | Создание | В любое время | Только при создании таблицы |
    | Consistency | Eventually | Strong possible |
    | Capacity | Отдельная | Shared with table |

    **Capacity Modes:**

    - **On-Demand:** платишь за запросы, автоматическое масштабирование
    - **Provisioned:** задаёшь RCU/WCU, дешевле при стабильной нагрузке

    ```yaml
    DynamoDBTable:
      Type: AWS::DynamoDB::Table
      Properties:
        BillingMode: PAY_PER_REQUEST  # On-demand
        # или
        BillingMode: PROVISIONED
        ProvisionedThroughput:
          ReadCapacityUnits: 100
          WriteCapacityUnits: 50
    ```

---

25. **Aurora vs RDS: когда выбрать Aurora Serverless v2**

    **Aurora Serverless v2:**

    | Критерий | RDS | Aurora | Aurora Serverless v2 |
    |----------|-----|--------|----------------------|
    | Масштабирование | Manual | Read replicas | Автоматическое (ACU) |
    | Min cost | Instance 24/7 | Instance 24/7 | 0.5 ACU (~$43/month) |
    | Max scale | Upgrade instance | 15 replicas | 128 ACU |
    | Failover | ~60 sec | ~30 sec | ~30 sec |
    | Storage | EBS | Distributed | Distributed |

    **Когда Aurora Serverless v2:**
    - Переменная нагрузка (dev/staging, spiky traffic)
    - Не хочешь управлять capacity
    - Новые проекты с неизвестным трафиком

    ```yaml
    AuroraCluster:
      Type: AWS::RDS::DBCluster
      Properties:
        Engine: aurora-postgresql
        EngineMode: provisioned
        ServerlessV2ScalingConfiguration:
          MinCapacity: 0.5  # Minimum ACUs
          MaxCapacity: 16   # Maximum ACUs

    AuroraInstance:
      Type: AWS::RDS::DBInstance
      Properties:
        DBClusterIdentifier: !Ref AuroraCluster
        DBInstanceClass: db.serverless
    ```

    **Когда стандартная Aurora:**
    - Стабильная высокая нагрузка (дешевле provisioned)
    - Нужен полный контроль над instance type
    - Требуется предсказуемая производительность

---

26. **ElastiCache: caching patterns, session storage**

    **Session Storage:**

    ```python
    from fastapi import Request, Response
    from uuid import uuid4

    SESSION_TTL = 86400  # 24 hours

    async def get_session(request: Request) -> dict:
        session_id = request.cookies.get("session_id")
        if session_id:
            data = await redis.get(f"session:{session_id}")
            if data:
                return json.loads(data)
        return {}

    async def save_session(response: Response, session: dict) -> str:
        session_id = str(uuid4())
        await redis.setex(
            f"session:{session_id}",
            SESSION_TTL,
            json.dumps(session)
        )
        response.set_cookie("session_id", session_id, httponly=True, secure=True)
        return session_id
    ```

    **Caching Patterns:**

    ```python
    # Read-Through с fallback
    async def get_user_with_cache(user_id: str) -> User:
        cache_key = f"user:{user_id}"

        # Try cache
        cached = await redis.get(cache_key)
        if cached:
            return User.model_validate_json(cached)

        # Cache miss → DB
        user = await db.get_user(user_id)
        if user:
            await redis.setex(cache_key, 300, user.model_dump_json())

        return user

    # Write-Through
    async def update_user(user_id: str, data: dict):
        user = await db.update_user(user_id, data)
        await redis.setex(f"user:{user_id}", 300, user.model_dump_json())
        return user

    # Cache Invalidation
    async def delete_user(user_id: str):
        await db.delete_user(user_id)
        await redis.delete(f"user:{user_id}")
    ```

    **Cluster Mode:**

    ```yaml
    ElastiCacheCluster:
      Type: AWS::ElastiCache::ReplicationGroup
      Properties:
        ReplicationGroupDescription: AI Platform Cache
        Engine: redis
        CacheNodeType: cache.r6g.large
        NumNodeGroups: 3        # Shards
        ReplicasPerNodeGroup: 2 # Replicas per shard
        AutomaticFailoverEnabled: true
    ```

---

27. **Redshift: Data Warehouse, Redshift Serverless, интеграция с S3**

    **Redshift Serverless:**

    ```python
    import boto3

    redshift_data = boto3.client('redshift-data')

    # Async query execution
    response = redshift_data.execute_statement(
        WorkgroupName='ai-platform-workgroup',
        Database='analytics',
        Sql="""
            SELECT
                model,
                DATE_TRUNC('day', created_at) as day,
                COUNT(*) as requests,
                SUM(tokens) as total_tokens,
                AVG(latency_ms) as avg_latency
            FROM llm_requests
            WHERE created_at > CURRENT_DATE - INTERVAL '30 days'
            GROUP BY 1, 2
            ORDER BY day DESC
        """
    )

    query_id = response['Id']

    # Poll for results
    while True:
        status = redshift_data.describe_statement(Id=query_id)
        if status['Status'] == 'FINISHED':
            break
        await asyncio.sleep(1)

    results = redshift_data.get_statement_result(Id=query_id)
    ```

    **COPY from S3:**

    ```sql
    -- Загрузка данных из S3
    COPY llm_requests
    FROM 's3://ai-platform-data/requests/'
    IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftS3Role'
    FORMAT AS PARQUET;

    -- UNLOAD to S3
    UNLOAD ('SELECT * FROM llm_requests WHERE created_at > ''2024-01-01''')
    TO 's3://ai-platform-exports/requests_2024/'
    IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftS3Role'
    FORMAT AS PARQUET
    PARTITION BY (model);
    ```

    **Spectrum (query S3 directly):**

    ```sql
    -- External schema для S3 data lake
    CREATE EXTERNAL SCHEMA spectrum_schema
    FROM DATA CATALOG
    DATABASE 'ai_platform_lake'
    IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftSpectrumRole';

    -- Query S3 данные напрямую
    SELECT model, COUNT(*)
    FROM spectrum_schema.raw_requests
    WHERE year = 2024 AND month = 1
    GROUP BY model;
    ```

---

## 🟠 Observability

28. **CloudWatch: Logs Insights, Metrics, Alarms, dashboards**

    **Structured Logging:**

    ```python
    import logging
    import json

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "message": record.getMessage(),
                "request_id": getattr(record, "request_id", None),
                "user_id": getattr(record, "user_id", None),
                "duration_ms": getattr(record, "duration_ms", None)
            }
            return json.dumps(log_data)

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    # Usage
    logger.info("Request completed", extra={
        "request_id": "abc123",
        "user_id": "user456",
        "duration_ms": 150
    })
    ```

    **CloudWatch Logs Insights:**

    ```sql
    -- Latency percentiles
    fields @timestamp, @message
    | filter @message like /Request completed/
    | stats
        avg(duration_ms) as avg_latency,
        pct(duration_ms, 50) as p50,
        pct(duration_ms, 95) as p95,
        pct(duration_ms, 99) as p99
        by bin(5m)

    -- Error analysis
    fields @timestamp, @message, error_type, user_id
    | filter level = "ERROR"
    | stats count(*) as error_count by error_type
    | sort error_count desc
    | limit 10
    ```

    **Custom Metrics:**

    ```python
    import boto3

    cloudwatch = boto3.client('cloudwatch')

    cloudwatch.put_metric_data(
        Namespace='AIplatform',
        MetricData=[{
            'MetricName': 'TokensUsed',
            'Value': tokens_count,
            'Unit': 'Count',
            'Dimensions': [
                {'Name': 'Model', 'Value': model_name},
                {'Name': 'Environment', 'Value': 'production'}
            ]
        }]
    )
    ```

    **Alarms:**

    ```yaml
    HighErrorRateAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: high-error-rate
        MetricName: 5XXError
        Namespace: AWS/ApiGateway
        Statistic: Sum
        Period: 60
        EvaluationPeriods: 3
        Threshold: 10
        ComparisonOperator: GreaterThanThreshold
        AlarmActions:
          - !Ref AlertSNSTopic
    ```

---

29. **Datadog: APM, distributed tracing, custom metrics**

    **APM Integration:**

    ```python
    from ddtrace import tracer, patch_all
    from ddtrace.contrib.fastapi import TraceMiddleware

    # Auto-instrument libraries
    patch_all()

    app = FastAPI()
    app.add_middleware(TraceMiddleware)

    @app.post("/chat")
    async def chat(request: ChatRequest):
        # Automatic span created
        with tracer.trace("llm.call", service="ai-platform") as span:
            span.set_tag("model", request.model)
            response = await call_llm(request)
            span.set_tag("tokens", response.usage.total_tokens)
        return response
    ```

    **Custom Metrics:**

    ```python
    from datadog import statsd

    # Counter
    statsd.increment('ai_platform.requests', tags=['model:gpt-4', 'status:success'])

    # Gauge
    statsd.gauge('ai_platform.queue_depth', queue.size())

    # Histogram
    statsd.histogram('ai_platform.latency', latency_ms, tags=['endpoint:chat'])

    # Distribution (for percentiles)
    statsd.distribution('ai_platform.tokens_used', tokens, tags=['model:gpt-4'])
    ```

    **Distributed Tracing:**

    ```python
    # Propagate trace context to downstream services
    from ddtrace import tracer

    @app.post("/orchestrate")
    async def orchestrate(request: Request):
        # Get current trace context
        span = tracer.current_span()
        headers = {
            "x-datadog-trace-id": str(span.trace_id),
            "x-datadog-parent-id": str(span.span_id)
        }

        # Pass to downstream service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://embedding-service/embed",
                headers=headers,
                json=data
            )
    ```

---

30. **X-Ray vs Datadog APM: трейсинг в serverless архитектуре**

    | Критерий | X-Ray | Datadog APM |
    |----------|-------|-------------|
    | Интеграция с AWS | Native | Через agent/extension |
    | Цена | Pay per trace | Subscription |
    | Lambda support | Built-in | Lambda extension |
    | Custom instrumentation | SDK | SDK + auto-instrument |
    | Dashboards | Basic | Rich |
    | Alerting | CloudWatch | Built-in |

    **X-Ray в Lambda:**

    ```python
    from aws_xray_sdk.core import xray_recorder, patch_all

    patch_all()  # Auto-instrument boto3, requests, etc.

    @xray_recorder.capture('process_request')
    def handler(event, context):
        # Subsegment for custom code
        with xray_recorder.in_subsegment('call_llm') as subsegment:
            subsegment.put_annotation('model', 'gpt-4')
            response = call_llm(event['prompt'])
            subsegment.put_metadata('response', response)
        return response
    ```

    **Datadog Lambda Extension:**

    ```yaml
    # SAM template
    MyFunction:
      Type: AWS::Serverless::Function
      Properties:
        Layers:
          - arn:aws:lambda:us-east-1:464622532012:layer:Datadog-Python311:latest
        Environment:
          Variables:
            DD_API_KEY: !Ref DatadogApiKey
            DD_SITE: datadoghq.com
            DD_TRACE_ENABLED: true
            DD_SERVERLESS_LOGS_ENABLED: true
    ```

    **Когда X-Ray:**
    - Только AWS сервисы
    - Минимальный budget
    - Простые требования к трейсингу

    **Когда Datadog:**
    - Multi-cloud или hybrid
    - Нужны богатые dashboards и alerting
    - APM + logs + metrics в одном месте
    - Команда уже использует Datadog

---

## 🟠 LLM Платформы и AI

31. **Amazon Bedrock: модели, inference, fine-tuning**

    **Доступные модели:**
    - Anthropic Claude (3.5 Sonnet, 3 Opus, 3 Haiku)
    - Amazon Titan (Text, Embeddings, Image)
    - Meta Llama 3
    - Mistral
    - Cohere
    - Stability AI (images)

    **Invoke Model:**

    ```python
    import boto3
    import json

    bedrock = boto3.client('bedrock-runtime')

    # Claude
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        contentType='application/json',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": "Explain quantum computing"}
            ]
        })
    )
    result = json.loads(response['body'].read())

    # Streaming
    response = bedrock.invoke_model_with_response_stream(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({...})
    )
    for event in response['body']:
        chunk = json.loads(event['chunk']['bytes'])
        print(chunk['delta']['text'], end='')
    ```

    **Embeddings:**

    ```python
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v2:0',
        body=json.dumps({
            "inputText": "What is machine learning?",
            "dimensions": 1024,
            "normalize": True
        })
    )
    embedding = json.loads(response['body'].read())['embedding']
    ```

    **Fine-tuning (Custom Models):**

    ```python
    bedrock = boto3.client('bedrock')

    # Create fine-tuning job
    response = bedrock.create_model_customization_job(
        jobName='my-fine-tune-job',
        customModelName='my-custom-claude',
        baseModelIdentifier='anthropic.claude-3-haiku-20240307-v1:0',
        trainingDataConfig={
            's3Uri': 's3://my-bucket/training-data.jsonl'
        },
        outputDataConfig={
            's3Uri': 's3://my-bucket/output/'
        },
        hyperParameters={
            'epochCount': '2',
            'batchSize': '8',
            'learningRate': '0.00001'
        }
    )
    ```

---

32. **OpenAI API vs Bedrock vs Gemini: сравнение и выбор**

    | Критерий | OpenAI | Bedrock | Gemini |
    |----------|--------|---------|--------|
    | Лучшие модели | GPT-4o, o1 | Claude 3.5 | Gemini 1.5 Pro |
    | Pricing model | Per token | Per token | Per token |
    | Multi-modal | Да (vision, audio) | Да (varies by model) | Да |
    | Context window | 128K (GPT-4o) | 200K (Claude) | 1M (Gemini) |
    | AWS Integration | Via API | Native | Via API |
    | Data residency | US/EU regions | AWS regions | Google regions |
    | Fine-tuning | Да | Да | Да |
    | Embeddings | Ada-002, 3-small/large | Titan, Cohere | Gecko |

    **Multi-provider setup:**

    ```python
    from abc import ABC, abstractmethod

    class LLMProvider(ABC):
        @abstractmethod
        async def complete(self, messages: list, **kwargs) -> str:
            pass

    class OpenAIProvider(LLMProvider):
        async def complete(self, messages, **kwargs):
            response = await openai_client.chat.completions.create(
                model=kwargs.get('model', 'gpt-4o'),
                messages=messages
            )
            return response.choices[0].message.content

    class BedrockProvider(LLMProvider):
        async def complete(self, messages, **kwargs):
            response = await asyncio.to_thread(
                bedrock.invoke_model,
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": messages,
                    "max_tokens": kwargs.get('max_tokens', 1024)
                })
            )
            return json.loads(response['body'].read())['content'][0]['text']

    # Router
    async def get_completion(messages, provider: str = "openai"):
        providers = {
            "openai": OpenAIProvider(),
            "bedrock": BedrockProvider(),
            "gemini": GeminiProvider()
        }
        return await providers[provider].complete(messages)
    ```

    **Выбор:**
    - **OpenAI:** лучший общий выбор, отличный API, быстрые итерации
    - **Bedrock:** AWS-native, data residency, multiple models
    - **Gemini:** longest context, Google ecosystem

---

33. **Semantic caching: как и когда использовать**

    **Концепция:** Кешировать ответы LLM на семантически похожие запросы.

    ```python
    import numpy as np
    from openai import AsyncOpenAI

    client = AsyncOpenAI()

    class SemanticCache:
        def __init__(self, similarity_threshold: float = 0.95):
            self.threshold = similarity_threshold
            self.cache = {}  # {embedding: response}
            self.embeddings = []  # List of cached embeddings

        async def get_embedding(self, text: str) -> list[float]:
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding

        def cosine_similarity(self, a: list, b: list) -> float:
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        async def get(self, query: str) -> str | None:
            query_embedding = await self.get_embedding(query)

            for cached_emb, response in self.cache.items():
                similarity = self.cosine_similarity(query_embedding, cached_emb)
                if similarity >= self.threshold:
                    return response

            return None

        async def set(self, query: str, response: str):
            embedding = await self.get_embedding(query)
            self.cache[tuple(embedding)] = response

    cache = SemanticCache(similarity_threshold=0.92)

    @app.post("/chat")
    async def chat(request: ChatRequest):
        # Check semantic cache
        cached = await cache.get(request.messages[-1].content)
        if cached:
            return {"response": cached, "cached": True}

        # Call LLM
        response = await llm.complete(request.messages)

        # Cache response
        await cache.set(request.messages[-1].content, response)

        return {"response": response, "cached": False}
    ```

    **Когда использовать:**
    - FAQ, повторяющиеся вопросы
    - Высокий трафик с похожими запросами
    - Снижение latency важнее 100% актуальности

    **Когда НЕ использовать:**
    - Персонализированные ответы
    - Время-чувствительные данные
    - Низкий объём уникальных запросов

---

34. **Vector databases: Pinecone, pgvector, OpenSearch**

    | Критерий | Pinecone | pgvector | OpenSearch |
    |----------|----------|----------|------------|
    | Тип | Managed SaaS | PostgreSQL extension | Managed/Self-hosted |
    | Setup | Минуты | В существующей DB | Часы |
    | Scale | Billions of vectors | Millions | Billions |
    | Hybrid search | Да | Нет (отдельно) | Да |
    | Filtering | Metadata filters | SQL WHERE | Query DSL |
    | Cost | Per-vector pricing | DB cost only | Instance-based |

    **Pinecone:**

    ```python
    from pinecone import Pinecone

    pc = Pinecone(api_key="...")
    index = pc.Index("ai-platform")

    # Upsert
    index.upsert(vectors=[
        {"id": "doc1", "values": embedding, "metadata": {"source": "faq"}},
    ])

    # Query
    results = index.query(
        vector=query_embedding,
        top_k=10,
        filter={"source": {"$eq": "faq"}},
        include_metadata=True
    )
    ```

    **pgvector:**

    ```python
    # Setup
    await db.execute("CREATE EXTENSION IF NOT EXISTS vector")
    await db.execute("""
        CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding vector(1536),
            metadata JSONB
        )
    """)
    await db.execute("CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)")

    # Insert
    await db.execute(
        "INSERT INTO documents (content, embedding, metadata) VALUES ($1, $2, $3)",
        content, embedding, metadata
    )

    # Query
    results = await db.fetch("""
        SELECT content, metadata, 1 - (embedding <=> $1) as similarity
        FROM documents
        WHERE metadata->>'source' = 'faq'
        ORDER BY embedding <=> $1
        LIMIT 10
    """, query_embedding)
    ```

    **OpenSearch:**

    ```python
    from opensearchpy import OpenSearch

    client = OpenSearch(hosts=[{"host": "...", "port": 443}])

    # Create index with knn
    client.indices.create("documents", body={
        "settings": {"index.knn": True},
        "mappings": {
            "properties": {
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 1536,
                    "method": {"name": "hnsw", "engine": "nmslib"}
                }
            }
        }
    })

    # Search
    response = client.search(index="documents", body={
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": 10
                }
            }
        }
    })
    ```

---

35. **RAG архитектура: компоненты и best practices**

    **Архитектура:**

    ```
    User Query
         ↓
    Query Processing (rewrite, expand)
         ↓
    Embedding Model
         ↓
    Vector Search ──→ Retrieved Documents
         ↓                    ↓
    Reranker (optional)      │
         ↓                    │
    Context Assembly ←────────┘
         ↓
    LLM Generation
         ↓
    Response
    ```

    **Implementation:**

    ```python
    from dataclasses import dataclass

    @dataclass
    class RAGConfig:
        chunk_size: int = 512
        chunk_overlap: int = 50
        top_k: int = 5
        rerank: bool = True
        max_context_tokens: int = 4000

    class RAGPipeline:
        def __init__(self, config: RAGConfig):
            self.config = config
            self.embedder = OpenAIEmbeddings()
            self.vector_store = PineconeStore()
            self.reranker = CohereReranker()  # Optional
            self.llm = ChatOpenAI(model="gpt-4o")

        async def query(self, question: str) -> str:
            # 1. Embed query
            query_embedding = await self.embedder.embed(question)

            # 2. Retrieve candidates
            candidates = await self.vector_store.search(
                query_embedding,
                top_k=self.config.top_k * 2 if self.config.rerank else self.config.top_k
            )

            # 3. Rerank (optional)
            if self.config.rerank:
                candidates = await self.reranker.rerank(
                    question, candidates, top_k=self.config.top_k
                )

            # 4. Build context
            context = self._build_context(candidates)

            # 5. Generate response
            prompt = f"""Answer based on the context below.

Context:
{context}

Question: {question}

Answer:"""

            return await self.llm.complete(prompt)

        def _build_context(self, docs: list) -> str:
            context_parts = []
            total_tokens = 0

            for doc in docs:
                doc_tokens = len(doc.content.split()) * 1.3  # Rough estimate
                if total_tokens + doc_tokens > self.config.max_context_tokens:
                    break
                context_parts.append(doc.content)
                total_tokens += doc_tokens

            return "\n\n---\n\n".join(context_parts)
    ```

    **Best Practices:**
    - Chunk с overlap для сохранения контекста
    - Metadata filtering перед vector search
    - Reranking для улучшения relevance
    - Цитирование источников в ответе
    - Fallback при низком confidence

---

36. **Prompt management: версионирование, A/B тестирование**

    **Prompt Registry:**

    ```python
    from pydantic import BaseModel
    from datetime import datetime

    class PromptTemplate(BaseModel):
        id: str
        name: str
        version: str
        template: str
        model: str
        parameters: dict  # temperature, max_tokens, etc.
        created_at: datetime
        metadata: dict  # tags, owner, etc.

    class PromptRegistry:
        def __init__(self, storage):
            self.storage = storage  # DynamoDB, PostgreSQL, etc.

        async def get_prompt(
            self,
            name: str,
            version: str = "latest"
        ) -> PromptTemplate:
            if version == "latest":
                return await self.storage.get_latest(name)
            return await self.storage.get(name, version)

        async def create_version(
            self,
            name: str,
            template: str,
            model: str,
            parameters: dict
        ) -> PromptTemplate:
            # Auto-increment version
            latest = await self.storage.get_latest(name)
            new_version = f"v{int(latest.version[1:]) + 1}" if latest else "v1"

            prompt = PromptTemplate(
                id=f"{name}:{new_version}",
                name=name,
                version=new_version,
                template=template,
                model=model,
                parameters=parameters,
                created_at=datetime.utcnow(),
                metadata={}
            )
            await self.storage.save(prompt)
            return prompt

    # Usage
    registry = PromptRegistry(DynamoDBStorage())

    prompt = await registry.get_prompt("customer_support", "v3")
    response = await llm.complete(
        prompt.template.format(query=user_query),
        model=prompt.model,
        **prompt.parameters
    )
    ```

    **A/B Testing:**

    ```python
    class PromptExperiment:
        def __init__(self, name: str, variants: dict[str, str]):
            self.name = name
            self.variants = variants  # {"control": "v1", "treatment": "v2"}

        def get_variant(self, user_id: str) -> str:
            # Consistent hashing
            hash_val = int(hashlib.md5(f"{self.name}:{user_id}".encode()).hexdigest(), 16)
            variant_keys = list(self.variants.keys())
            return variant_keys[hash_val % len(variant_keys)]

    experiment = PromptExperiment(
        "support_prompt_test",
        {"control": "v2", "treatment": "v3"}
    )

    @app.post("/chat")
    async def chat(request: ChatRequest, user: User = Depends(get_user)):
        variant = experiment.get_variant(user.id)
        prompt_version = experiment.variants[variant]
        prompt = await registry.get_prompt("customer_support", prompt_version)

        # Log for analysis
        await analytics.log_experiment(
            experiment="support_prompt_test",
            variant=variant,
            user_id=user.id
        )

        response = await llm.complete(prompt.template.format(...))
        return response
    ```

---

37. **LLM evaluation pipelines: метрики качества, автоматизация**

    **Метрики:**

    ```python
    from dataclasses import dataclass
    from typing import Callable

    @dataclass
    class EvalResult:
        metric: str
        score: float
        details: dict

    class LLMEvaluator:
        def __init__(self):
            self.metrics: dict[str, Callable] = {}

        def register_metric(self, name: str, func: Callable):
            self.metrics[name] = func

        async def evaluate(
            self,
            query: str,
            response: str,
            reference: str = None,
            context: list[str] = None
        ) -> list[EvalResult]:
            results = []
            for name, func in self.metrics.items():
                score = await func(query, response, reference, context)
                results.append(EvalResult(metric=name, score=score, details={}))
            return results

    # Built-in metrics
    async def relevance_score(query, response, reference, context):
        """LLM-as-judge for relevance"""
        judge_prompt = f"""Rate the relevance of the response to the query on a scale of 1-5.

Query: {query}
Response: {response}

Rating (1-5):"""
        rating = await llm.complete(judge_prompt)
        return float(rating.strip()) / 5

    async def groundedness_score(query, response, reference, context):
        """Check if response is grounded in context"""
        if not context:
            return None

        prompt = f"""Check if the response is factually supported by the context.

Context: {' '.join(context)}
Response: {response}

Score (0-1):"""
        return float(await llm.complete(prompt))

    async def answer_correctness(query, response, reference, context):
        """Compare with reference answer"""
        if not reference:
            return None

        prompt = f"""Compare the response with the reference answer.

Reference: {reference}
Response: {response}

Similarity score (0-1):"""
        return float(await llm.complete(prompt))
    ```

    **Evaluation Pipeline:**

    ```python
    import asyncio
    from datetime import datetime

    class EvalPipeline:
        def __init__(self, evaluator: LLMEvaluator, storage):
            self.evaluator = evaluator
            self.storage = storage

        async def run_eval(
            self,
            test_set: list[dict],  # [{"query": ..., "reference": ..., "context": ...}]
            model_config: dict,
            experiment_name: str
        ) -> dict:
            results = []

            for item in test_set:
                # Generate response
                response = await llm.complete(
                    item["query"],
                    **model_config
                )

                # Evaluate
                scores = await self.evaluator.evaluate(
                    query=item["query"],
                    response=response,
                    reference=item.get("reference"),
                    context=item.get("context")
                )

                results.append({
                    "query": item["query"],
                    "response": response,
                    "scores": {r.metric: r.score for r in scores}
                })

            # Aggregate
            summary = self._aggregate_results(results)

            # Store
            await self.storage.save_eval_run({
                "experiment": experiment_name,
                "timestamp": datetime.utcnow().isoformat(),
                "model_config": model_config,
                "summary": summary,
                "details": results
            })

            return summary

        def _aggregate_results(self, results: list) -> dict:
            metrics = {}
            for r in results:
                for metric, score in r["scores"].items():
                    if score is not None:
                        metrics.setdefault(metric, []).append(score)

            return {
                metric: {
                    "mean": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
                for metric, scores in metrics.items()
            }
    ```

---

## 🟠 Security и CI/CD

38. **Security best practices: IAM, Secrets Manager, KMS**

    **IAM Least Privilege:**

    ```yaml
    # Lambda role — минимальные права
    LambdaRole:
      Type: AWS::IAM::Role
      Properties:
        AssumeRolePolicyDocument:
          Statement:
            - Effect: Allow
              Principal:
                Service: lambda.amazonaws.com
              Action: sts:AssumeRole
        Policies:
          - PolicyName: LambdaPolicy
            PolicyDocument:
              Statement:
                # Только конкретные действия на конкретных ресурсах
                - Effect: Allow
                  Action:
                    - bedrock:InvokeModel
                  Resource:
                    - arn:aws:bedrock:*::foundation-model/anthropic.claude-*
                - Effect: Allow
                  Action:
                    - secretsmanager:GetSecretValue
                  Resource:
                    - !Ref OpenAISecret
                - Effect: Allow
                  Action:
                    - dynamodb:GetItem
                    - dynamodb:PutItem
                  Resource:
                    - !GetAtt UsageTable.Arn
    ```

    **Secrets Manager:**

    ```python
    import boto3
    from functools import lru_cache

    @lru_cache()
    def get_secret(secret_name: str) -> dict:
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])

    # В Lambda — кешируем между invocations
    OPENAI_KEY = get_secret("ai-platform/openai")["api_key"]

    # Rotation
    # Secrets Manager может автоматически ротировать секреты
    # Lambda rotation function обновляет секрет в источнике
    ```

    **KMS для шифрования:**

    ```python
    import boto3

    kms = boto3.client('kms')

    # Encrypt sensitive data
    def encrypt_pii(data: str, key_id: str) -> bytes:
        response = kms.encrypt(
            KeyId=key_id,
            Plaintext=data.encode()
        )
        return response['CiphertextBlob']

    def decrypt_pii(ciphertext: bytes, key_id: str) -> str:
        response = kms.decrypt(
            KeyId=key_id,
            CiphertextBlob=ciphertext
        )
        return response['Plaintext'].decode()

    # Envelope encryption для больших данных
    def encrypt_large_data(data: bytes, key_id: str) -> tuple:
        # Генерируем data key
        response = kms.generate_data_key(
            KeyId=key_id,
            KeySpec='AES_256'
        )

        # Шифруем данные с plaintext key
        from cryptography.fernet import Fernet
        import base64

        fernet = Fernet(base64.urlsafe_b64encode(response['Plaintext']))
        encrypted = fernet.encrypt(data)

        # Возвращаем encrypted data key + encrypted data
        return response['CiphertextBlob'], encrypted
    ```

---

39. **CI/CD для serverless: SAM, CDK, GitHub Actions**

    **SAM Pipeline:**

    ```yaml
    # .github/workflows/deploy.yml
    name: Deploy

    on:
      push:
        branches: [main]

    jobs:
      deploy:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4

          - uses: actions/setup-python@v5
            with:
              python-version: '3.11'

          - name: Install dependencies
            run: |
              pip install -r requirements.txt
              pip install pytest pytest-asyncio

          - name: Run tests
            run: pytest tests/ -v

          - name: Configure AWS
            uses: aws-actions/configure-aws-credentials@v4
            with:
              aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
              aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              aws-region: us-east-1

          - name: SAM Build
            run: sam build

          - name: SAM Deploy
            run: |
              sam deploy \
                --stack-name ai-platform-${{ github.ref_name }} \
                --capabilities CAPABILITY_IAM \
                --no-confirm-changeset \
                --parameter-overrides Environment=${{ github.ref_name }}
    ```

    **CDK Pipeline:**

    ```python
    # cdk/pipeline_stack.py
    from aws_cdk import (
        Stack,
        pipelines,
        aws_codepipeline_actions as actions
    )

    class PipelineStack(Stack):
        def __init__(self, scope, id, **kwargs):
            super().__init__(scope, id, **kwargs)

            pipeline = pipelines.CodePipeline(
                self, "Pipeline",
                synth=pipelines.ShellStep(
                    "Synth",
                    input=pipelines.CodePipelineSource.git_hub(
                        "org/repo", "main"
                    ),
                    commands=[
                        "npm install -g aws-cdk",
                        "pip install -r requirements.txt",
                        "pytest tests/",
                        "cdk synth"
                    ]
                )
            )

            # Staging
            pipeline.add_stage(
                AIplatformStage(self, "Staging", env=staging_env),
                pre=[pipelines.ShellStep("IntegrationTests", commands=["..."])]
            )

            # Production with manual approval
            pipeline.add_stage(
                AIplatformStage(self, "Production", env=prod_env),
                pre=[pipelines.ManualApprovalStep("PromoteToProd")]
            )
    ```

    **Feature Branch Deployments:**

    ```yaml
    # Deploy preview environment for PRs
    on:
      pull_request:
        types: [opened, synchronize]

    jobs:
      preview:
        runs-on: ubuntu-latest
        steps:
          - name: Deploy Preview
            run: |
              STACK_NAME="ai-platform-pr-${{ github.event.pull_request.number }}"
              sam deploy --stack-name $STACK_NAME ...

          - name: Comment PR
            uses: actions/github-script@v7
            with:
              script: |
                github.rest.issues.createComment({
                  issue_number: context.issue.number,
                  body: '🚀 Preview: https://pr-${{ github.event.pull_request.number }}.ai-platform.dev'
                })
    ```

---

40. **API Security: OAuth 2.0, JWT, API keys, WAF**

    **JWT Validation:**

    ```python
    from fastapi import Depends, HTTPException, Security
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    import jwt
    from jwt import PyJWKClient

    security = HTTPBearer()

    # JWKS для Cognito/Auth0
    jwks_client = PyJWKClient("https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxx/.well-known/jwks.json")

    async def verify_token(
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        token = credentials.credentials

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience="api-client-id",
                issuer="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxx"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(401, f"Invalid token: {e}")

    @app.get("/protected")
    async def protected_route(user: dict = Depends(verify_token)):
        return {"user_id": user["sub"]}
    ```

    **API Keys с Usage Plans (API Gateway):**

    ```yaml
    ApiKey:
      Type: AWS::ApiGateway::ApiKey
      Properties:
        Enabled: true
        Name: customer-123-key

    UsagePlan:
      Type: AWS::ApiGateway::UsagePlan
      Properties:
        UsagePlanName: standard
        Throttle:
          RateLimit: 100
          BurstLimit: 200
        Quota:
          Limit: 10000
          Period: MONTH
        ApiStages:
          - ApiId: !Ref Api
            Stage: prod

    UsagePlanKey:
      Type: AWS::ApiGateway::UsagePlanKey
      Properties:
        KeyId: !Ref ApiKey
        KeyType: API_KEY
        UsagePlanId: !Ref UsagePlan
    ```

    **WAF Rules:**

    ```yaml
    WebACL:
      Type: AWS::WAFv2::WebACL
      Properties:
        DefaultAction:
          Allow: {}
        Rules:
          # Rate limiting
          - Name: RateLimitRule
            Priority: 1
            Statement:
              RateBasedStatement:
                Limit: 1000
                AggregateKeyType: IP
            Action:
              Block: {}
            VisibilityConfig:
              SampledRequestsEnabled: true
              CloudWatchMetricsEnabled: true
              MetricName: RateLimitRule

          # SQL Injection
          - Name: SQLiRule
            Priority: 2
            Statement:
              ManagedRuleGroupStatement:
                VendorName: AWS
                Name: AWSManagedRulesSQLiRuleSet
            OverrideAction:
              None: {}

          # Known bad inputs
          - Name: BadInputsRule
            Priority: 3
            Statement:
              ManagedRuleGroupStatement:
                VendorName: AWS
                Name: AWSManagedRulesKnownBadInputsRuleSet
            OverrideAction:
              None: {}
    ```

    **Security Headers:**

    ```python
    from fastapi import FastAPI
    from starlette.middleware.base import BaseHTTPMiddleware

    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = "default-src 'self'"
            return response

    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    ```

---

## Бонус: Вопросы к интервьюеру

**Про команду и процессы:**
- Как устроена команда? Сколько ML engineers vs platform engineers?
- Какие LLM провайдеры используете? Планируете ли менять?
- Как выглядит процесс от идеи до продакшена для новой AI-фичи?

**Про технологии:**
- Какой основной tech stack для inference?
- Как решаете проблему latency для real-time AI?
- Используете ли fine-tuning или только prompting?

**Про масштаб:**
- Какой объём запросов к LLM в день?
- Как справляетесь с rate limits провайдеров?
- Какие главные технические challenges сейчас?

**Red flags:**
- "У нас нет мониторинга LLM качества"
- "Мы храним все промпты в коде"
- "Один провайдер, fallback не нужен"
