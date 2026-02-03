# Topic 6: Technical Decisions

## 1. Core Speaking Chunks

### Responsibility Framing
- "I was the one who proposed…"
- "I led the decision-making process for…"
- "I owned the technical direction of…"
- "It was my call to…"
- "I drove the evaluation of…"

### Impact Statements
- "This reduced our deployment time by roughly 40%."
- "As a result, we cut infrastructure costs significantly."
- "The team velocity improved noticeably after that."
- "We went from weekly incidents to almost none."
- "This unlocked the ability to scale horizontally."

### Technical Explanation Starters
- "The core issue was…"
- "What we were dealing with was…"
- "The existing approach had limitations around…"
- "From a systems perspective, the bottleneck was…"
- "Architecturally, the problem came down to…"

### Cause → Effect
- "Because of X, we were seeing Y."
- "This led to frequent issues with…"
- "Once we switched, the situation improved because…"
- "The root cause turned out to be…"
- "That change directly addressed…"

### Trade-offs
- "We had to weigh X against Y."
- "The downside was increased complexity, but…"
- "It wasn't a perfect solution, however it was pragmatic."
- "We accepted some technical debt in exchange for…"
- "There were trade-offs, mainly around…"

### Reflection Phrases
- "Looking back, I would still make the same choice."
- "If I had to do it again, I might consider…"
- "One thing I learned from this was…"
- "In hindsight, the timing was right."
- "That decision shaped how I approach similar problems now."

---

## 2. Grammar Patterns for This Topic

### Pattern 1: Past Simple for Completed Decisions
**Use when:** Describing a specific decision that was made at a clear point in time.

- "We decided to migrate to Kubernetes in Q3."
- "I proposed using event sourcing instead of traditional CRUD."

### Pattern 2: Past Continuous + Past Simple for Context Setting
**Use when:** Showing what was happening when a decision was made.

- "We were hitting scaling limits, so I recommended splitting the monolith."
- "The team was struggling with deployment frequency, which led me to introduce CI/CD pipelines."

### Pattern 3: Present Perfect for Ongoing Impact
**Use when:** Connecting a past decision to current results.

- "Since we adopted that approach, we haven't had a single major outage."
- "That architecture has served us well for the past two years."

### Pattern 4: Conditional Structures for Trade-off Explanation
**Use when:** Explaining alternative paths and reasoning.

- "If we had chosen the managed service, we would have saved time but lost flexibility."
- "Had we not refactored early, scaling would have become a serious problem."

---

## 3. Short Monologue (30–60 seconds)

> One technical decision I'm particularly proud of was introducing event-driven architecture for our order processing system. We were running a synchronous monolith, and as traffic grew, we kept hitting timeouts and cascading failures. I proposed moving to an async model using message queues. It took some convincing because the team wasn't familiar with that pattern, but I put together a proof of concept and documented the trade-offs clearly. After we rolled it out, our error rate dropped by about 70%, and the system became much easier to scale. It also made our services more loosely coupled, which helped with independent deployments later on.

---

## 4. Long Monologue (2–4 minutes)

> I'd like to talk about a technical decision I made at my previous company that had a significant impact on how we handled data processing.
>
> **Context:** We had a data pipeline that processed customer transactions in near real-time. It was built as a single Python application running on a few EC2 instances. At first, it worked fine, but as the business grew, we started processing around 10 million events per day, and the system couldn't keep up. We were seeing delays of several hours, and sometimes jobs would fail entirely due to memory issues.
>
> **Problem:** The core problem was that the architecture wasn't designed for this scale. Everything ran sequentially, there was no proper retry mechanism, and if one component failed, the whole pipeline stopped. The team had been patching it for months, but it was clear we needed a fundamental change.
>
> **Solution:** I proposed migrating to a distributed stream processing approach using Apache Kafka and a set of smaller, specialized workers. The idea was to decouple ingestion from processing and allow horizontal scaling. I evaluated a few options, including AWS Kinesis and managed Kafka, and ultimately chose self-hosted Kafka because we needed more control over partitioning and retention policies.
>
> **My contribution:** I led the technical design, wrote the architecture decision record, and coordinated with the DevOps team on infrastructure. I also implemented the core consumer logic and set up monitoring with Prometheus and Grafana so we could track lag and throughput in real time. Beyond the technical work, I spent time aligning stakeholders—explaining why this investment was necessary and what risks we were mitigating.
>
> **Impact:** After the migration, processing latency dropped from hours to under five minutes. We were able to handle traffic spikes without manual intervention, and the failure rate went from a few incidents per week to nearly zero over six months. The new system also made it easier to add new processing steps without touching existing code.
>
> **Reflection:** This experience reinforced for me how important it is to make decisions based on actual constraints, not assumptions. I also learned that technical decisions are never purely technical—you have to bring people along and explain the reasoning clearly. That's something I try to do consistently now.

---

## 5. Technical Variation

> The decision I want to describe involves re-architecting a high-throughput data pipeline from a monolithic batch processor to a distributed streaming system.
>
> **Initial state:** We had a single-threaded Python application pulling data from PostgreSQL, transforming it, and writing to S3. It used cron-based scheduling and had no fault tolerance. Memory usage was unpredictable, and we frequently saw OOM kills under load.
>
> **Technical constraints:** We needed to support 10 million+ events daily with sub-10-minute latency. The system had to handle backpressure gracefully, support exactly-once semantics where possible, and remain observable.
>
> **Evaluation:** I assessed three options: AWS Kinesis with Lambda consumers, managed Confluent Kafka, and self-hosted Kafka on Kubernetes. Kinesis was ruled out due to shard limitations and cost at our scale. Managed Kafka was attractive but lacked the partition control we needed. Self-hosted Kafka on EKS gave us flexibility for tuning retention, replication factor, and consumer group rebalancing.
>
> **Implementation:** I designed a topology with three Kafka topics—raw events, enriched events, and dead-letter. Consumers were written in Python using the confluent-kafka library with manual offset commits to ensure at-least-once delivery. We used Kubernetes HPA to scale consumers based on lag metrics exposed via Prometheus. State management for enrichment was handled with Redis, and the final output went to S3 via a Kafka Connect sink.
>
> **Outcome:** P99 latency dropped from 4 hours to 3 minutes. Consumer lag stayed under 1,000 messages even during peak. We reduced on-call incidents related to this system by over 80%.
>
> **Technical learning:** The main insight was around partition strategy—initially we partitioned by customer ID, which caused hot partitions. Re-partitioning by event type balanced the load more evenly.

---

## 6. Business-Oriented Variation

> I'd like to share a decision that had a direct impact on business operations and customer experience.
>
> **Business context:** Our company processes financial transactions for e-commerce clients. Timely data processing is critical because our clients rely on near real-time reporting for fraud detection and inventory management. Delays in our pipeline meant delays in their decision-making.
>
> **The problem:** Our existing system couldn't keep up with growth. Processing delays reached several hours during peak periods, which led to client complaints and put renewals at risk. The operations team was spending significant time on manual recovery, which wasn't sustainable.
>
> **The decision:** I proposed investing in a modern streaming architecture. I built a business case showing that the engineering cost would be offset within two quarters through reduced operational overhead and improved client retention. I also highlighted the competitive advantage—most of our competitors offered next-day reporting, while we could offer near real-time.
>
> **Stakeholder alignment:** I presented the plan to product leadership and finance, focusing on client impact and cost-benefit rather than technical details. I addressed concerns about timeline and risk by proposing a phased rollout starting with lower-priority data streams.
>
> **Outcome:** After the rollout, we reduced processing time from hours to minutes. Client satisfaction scores for data timeliness improved measurably. Two enterprise clients specifically mentioned this capability during renewal discussions. On the cost side, we reduced the need for overnight manual monitoring, which freed up engineering capacity for feature work.
>
> **Takeaway:** This reinforced that technical decisions need to be framed in business terms. When you can tie a system improvement to revenue protection or customer value, it's much easier to get buy-in and resources.

---

## 7. Improvisation Map

### Key Ideas to Cover
- What the decision was (one sentence)
- Why it was needed (problem or constraint)
- What options you considered
- What you chose and why
- Your personal role
- The outcome (quantified if possible)
- What you learned or would do differently

### Optional Branches
- Deep dive into technical trade-offs (if interviewer is technical)
- Stakeholder communication challenges (if behavioral focus)
- Team dynamics and how you got buy-in
- Mistakes or course corrections along the way
- How the decision aged over time

### Fallback Phrases If Stuck
- "Let me give you a concrete example…"
- "To put it simply…"
- "The main trade-off was between…"
- "What I focused on was…"
- "In the end, what mattered most was…"
- "I can go deeper into the technical side if helpful."

---

## 8. Common Follow-up Questions

1. What other options did you consider, and why did you rule them out?

2. How did you get buy-in from the rest of the team?

3. What was the biggest risk, and how did you mitigate it?

4. If you had more time or resources, what would you have done differently?

5. How did you measure success after the decision was implemented?

6. Was there any pushback, and how did you handle it?

7. How has that decision held up over time?

---

*Practice each section separately, then combine. Start with chunks, build to short monologue, then expand freely using the improvisation map.*
