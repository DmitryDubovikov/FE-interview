# System Design — Speaking Guide

## 1. Core Speaking Chunks

### Responsibility Framing
- "I was responsible for designing the overall architecture of…"
- "I led the system design phase for…"
- "My role was to define the high-level components and their interactions."
- "I owned the technical design from requirements gathering to implementation."

### Impact Statements
- "This design allowed us to scale from X to Y users without major refactoring."
- "The architecture reduced latency by roughly 40 percent."
- "We achieved 99.9 percent uptime after migrating to the new design."
- "This approach cut infrastructure costs by about 30 percent."

### Technical Explanation Starters
- "At a high level, the system works like this…"
- "Let me walk you through the main components."
- "The core idea behind this design is…"
- "Essentially, we have three main layers…"
- "The data flows from… through… to…"

### Cause → Effect
- "Because we needed to handle bursty traffic, we introduced a message queue."
- "Since consistency was critical, we opted for synchronous replication."
- "Given the read-heavy workload, we added a caching layer."
- "Due to strict latency requirements, we moved to an event-driven model."

### Trade-offs
- "The trade-off here was between consistency and availability."
- "We sacrificed some storage efficiency for faster query times."
- "This added complexity, but it gave us much better fault tolerance."
- "We accepted eventual consistency in exchange for higher throughput."
- "The downside was increased operational overhead."

### Reflection Phrases
- "Looking back, I would probably approach the caching strategy differently."
- "One thing I learned from this project is the importance of…"
- "If I were to redesign this today, I would consider…"
- "What I took away from this experience is…"
- "In hindsight, we underestimated the complexity of…"

### Clarification and Structure
- "To give you some context…"
- "Let me break this down into smaller parts."
- "There are essentially two aspects to consider here."
- "Before I dive into the solution, let me explain the constraints."

---

## 2. Grammar Patterns for This Topic

### Pattern 1: Past Simple for Completed Design Decisions
**Structure:** Subject + past simple verb + object/complement
**When to use:** Describing concrete decisions made during the design process.

- "We chose PostgreSQL because we needed strong consistency."
- "I proposed a microservices architecture to improve team autonomy."

### Pattern 2: Past Continuous for Ongoing Context
**Structure:** Subject + was/were + verb-ing
**When to use:** Setting the scene or describing circumstances during design work.

- "At the time, we were handling about 10,000 requests per second."
- "The team was growing rapidly, so we needed clearer service boundaries."

### Pattern 3: Conditionals for Trade-offs and Alternatives
**Structure:** If + past simple, would + base verb (Type 2) / If + had + past participle, would have + past participle (Type 3)
**When to use:** Discussing hypothetical alternatives or reflecting on decisions.

- "If we had chosen a NoSQL database, we would have lost transactional guarantees."
- "If latency were not a concern, I would use a simpler synchronous approach."

### Pattern 4: Passive Voice for System Behavior
**Structure:** Subject + is/was + past participle (+ by agent)
**When to use:** Describing how the system works without emphasizing who does it.

- "Requests are routed through a load balancer before reaching the application servers."
- "Events are processed asynchronously by a pool of workers."

### Pattern 5: Present Simple for Explaining Architecture
**Structure:** Subject + present simple verb
**When to use:** Describing how a system currently works or general design principles.

- "The API gateway handles authentication and rate limiting."
- "Each microservice owns its own database to ensure loose coupling."

---

## 3. Short Monologue (30–60 seconds)

> I recently designed a real-time notification system for a fintech platform. The main challenge was delivering messages to millions of users with minimal latency while keeping costs reasonable.
>
> I proposed an event-driven architecture using Kafka for message ingestion and a fan-out service that pushes notifications through WebSockets. We also added Redis for connection state management.
>
> The result was sub-second delivery for 95 percent of notifications, and we could scale horizontally by adding more consumer instances. The design handled a 5x traffic spike during a product launch without any issues.

---

## 4. Long Monologue (2–4 minutes)

> I'd like to talk about a system design project I led at my previous company. We were building a document processing platform for enterprise clients. The system needed to handle PDF uploads, extract text using OCR, run various analyses, and store the results for search and retrieval.
>
> The main challenge was that document processing is computationally expensive and unpredictable in duration. Some documents took seconds, others took minutes. We also had strict SLAs — clients expected results within a reasonable timeframe, and we couldn't afford to lose any documents.
>
> I designed an asynchronous pipeline architecture. When a user uploads a document, the API stores the file in S3 and publishes an event to an SQS queue. A pool of worker services picks up these events, processes the documents, and writes results to a PostgreSQL database. We used DynamoDB for tracking job status because we needed fast, frequent updates.
>
> My specific contribution was defining the service boundaries and the retry logic. I introduced a dead-letter queue for failed jobs and built a small admin service to inspect and replay them. I also worked closely with the infrastructure team to set up auto-scaling based on queue depth.
>
> The impact was significant. We reduced average processing time by 60 percent compared to the previous synchronous approach. The system handled 50,000 documents per day at peak, and our error rate dropped below 0.1 percent. We also cut infrastructure costs because workers scaled down during off-peak hours.
>
> What I learned from this project is that designing for failure is just as important as designing for success. The retry mechanisms and observability we built in saved us many times when third-party OCR services had intermittent issues.

---

## 5. Technical Variation

> Let me walk you through the architecture of a document processing system I designed. The system ingests PDFs via a REST API backed by a Node.js service running on EKS. Files are stored in S3 with server-side encryption, and upload events trigger an SQS message.
>
> The processing layer consists of Python workers using Celery, deployed as a Kubernetes deployment with horizontal pod autoscaling tied to SQS queue depth. Each worker pulls a message, downloads the file from S3, runs Tesseract OCR, and performs NLP analysis using spaCy.
>
> For data storage, I chose PostgreSQL with read replicas for the processed content and metadata. We used DynamoDB for job state tracking because we needed single-digit millisecond reads for status polling. Search functionality was powered by Elasticsearch, with documents indexed after processing completes.
>
> The key trade-off was between processing throughput and cost. We could have used GPU instances for faster OCR, but the cost-benefit analysis showed that CPU-based processing with more parallelism was more economical for our workload profile. We also accepted eventual consistency between the primary database and Elasticsearch, which meant search results could lag by a few seconds.
>
> For observability, I set up distributed tracing with Jaeger and metrics collection with Prometheus. Each document carried a correlation ID through the entire pipeline, which made debugging straightforward.
>
> The system processed 50,000 documents daily with p99 latency under 3 minutes and 99.9 percent success rate.

---

## 6. Business-Oriented Variation

> I'd like to describe a system I designed that had a direct impact on our business operations. We were building a document processing platform for enterprise clients in the legal and financial sectors. These clients were spending significant time manually reviewing documents, and they needed an automated solution.
>
> The business requirement was clear: reduce document processing time from hours to minutes while maintaining accuracy. Our clients were willing to pay a premium for faster turnaround, so there was a strong revenue opportunity.
>
> I designed an automated pipeline that could handle high volumes without manual intervention. The key business consideration was reliability — our clients couldn't afford to lose documents or have inconsistent results. I built in multiple safeguards, including automatic retries and a review queue for edge cases.
>
> From a cost perspective, I optimized the architecture for variable workloads. Instead of paying for always-on infrastructure, we used auto-scaling to match capacity with demand. This reduced our infrastructure costs by about 30 percent compared to initial estimates.
>
> The business outcomes were strong. We onboarded three enterprise clients within the first quarter after launch. Processing time dropped by 60 percent, which became a key selling point. Client satisfaction scores improved because they received results faster and with fewer errors.
>
> I also worked with the product team to add usage analytics, which helped account managers identify upsell opportunities. We could show clients exactly how many documents they processed and demonstrate the time savings.
>
> The main lesson for me was that technical decisions always have business implications. Choosing the right level of reliability and the right cost structure made the difference between a technically sound system and a commercially successful product.

---

## 7. Improvisation Map

### Key Ideas to Cover
- **Context:** What system, what company, what domain
- **Scale:** Users, requests, data volume
- **Core problem:** Why was design needed, what constraints existed
- **High-level architecture:** Main components, how they connect
- **Key decisions:** Database choice, sync vs async, monolith vs microservices
- **Trade-offs:** What you gained, what you sacrificed
- **Your role:** What you specifically did
- **Outcome:** Measurable results
- **Learning:** What you would do differently

### Optional Branches (Pick Based on Interview Focus)
- Deep dive into specific component (caching, queuing, database)
- Scaling story (how it evolved as load increased)
- Failure handling and resilience
- Team collaboration and communication
- Cost optimization decisions
- Security considerations

### Fallback Phrases If Stuck
- "Let me think about how to explain this clearly…"
- "To put it simply…"
- "The main point here is…"
- "What's most relevant is…"
- "I can go deeper into any of these areas if you'd like."
- "Does that answer your question, or should I focus on a specific part?"

---

## 8. Common Follow-up Questions

1. "How would this system handle a 10x increase in traffic?"

2. "What happens if the message queue goes down?"

3. "Why did you choose [specific technology] over [alternative]?"

4. "How did you ensure data consistency across services?"

5. "What were the main bottlenecks, and how did you address them?"

6. "How would you redesign this system knowing what you know now?"

7. "How did you handle security and access control in this architecture?"

---

*Generated for system design interview preparation. Practice these monologues, then adapt freely in real conversations.*
