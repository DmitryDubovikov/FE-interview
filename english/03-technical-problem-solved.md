# Technical Problem Solved

Speaking practice for senior software engineers.

---

## 1. Core Speaking Chunks

### Responsibility Framing
- "I was the technical lead on this initiative."
- "I owned the investigation and resolution end-to-end."
- "This fell under my area of responsibility."
- "I took the lead on debugging this issue."
- "My role was to identify the root cause and propose a fix."

### Setting the Scene
- "We were running into a critical issue in production."
- "The system started showing degraded performance."
- "We noticed intermittent failures in our pipeline."
- "This came up during a routine deployment."
- "The problem surfaced after we scaled to handle more traffic."

### Technical Explanation Starters
- "After digging into the logs, I found that…"
- "The root cause turned out to be…"
- "What was happening under the hood was…"
- "The issue stemmed from…"
- "Essentially, the problem was…"

### Cause → Effect
- "Because of this, downstream services started timing out."
- "This led to cascading failures across the system."
- "As a result, we saw a spike in error rates."
- "That caused our response times to increase significantly."
- "The consequence was that users experienced delays."

### Trade-offs
- "We had to balance speed of resolution against long-term stability."
- "There was a trade-off between a quick fix and a proper solution."
- "We could either patch it immediately or refactor the entire flow."
- "I weighed the risks and decided to…"
- "Given the constraints, we opted for…"

### Impact Statements
- "This reduced our error rate by roughly 80%."
- "We brought the latency down from 2 seconds to under 200 milliseconds."
- "The fix prevented further incidents for the following six months."
- "This saved the team several hours of manual intervention per week."
- "It directly improved the user experience for thousands of customers."

### Reflection Phrases
- "Looking back, I would have…"
- "The key takeaway for me was…"
- "What I learned from this was…"
- "If I had to do it again, I might…"
- "This reinforced my belief that…"

---

## 2. Grammar Patterns for This Topic

### Past Simple for Completed Actions
**What it is:** Simple past tense for actions that happened and finished.
**When to use:** Describing specific steps you took, decisions made, or outcomes achieved.

- "I identified the bottleneck in our database queries."
- "We deployed the fix on Friday and monitored it over the weekend."

### Past Continuous for Context Setting
**What it is:** Was/were + verb-ing to describe ongoing situations.
**When to use:** Setting the scene, explaining what was happening when the problem occurred.

- "The system was handling about 10,000 requests per second when we noticed the issue."
- "We were preparing for a major release when this bug surfaced."

### Past Perfect for Sequencing
**What it is:** Had + past participle to show something happened before another past event.
**When to use:** Explaining what had already happened or what had been tried before your solution.

- "Previous attempts had failed because they only addressed the symptoms."
- "By the time I joined the investigation, the team had already ruled out network issues."

### Conditional for Hypotheticals and Trade-offs
**What it is:** If + past, would + base verb (second conditional).
**When to use:** Discussing alternative approaches or what would have happened without your solution.

- "If we had ignored it, the system would have eventually crashed."
- "If we had more time, I would have implemented a more elegant solution."

---

## 3. Short Monologue (30–60 seconds)

> We had a production incident last year where our payment processing service started failing intermittently. I led the investigation and found that the issue was caused by connection pool exhaustion under high load. The service was creating new database connections faster than it could release them. I implemented connection pooling with proper timeout settings and added circuit breakers to prevent cascading failures. After the fix, we saw a 90% reduction in failed transactions. The system has been stable since then.

---

## 4. Long Monologue (2–4 minutes)

> I want to talk about a technical problem I solved at my previous company. We were running a distributed order management system that handled thousands of transactions per minute. One day, we started getting alerts about increased latency and timeouts in our order processing pipeline.
>
> The problem was that orders were getting stuck in a pending state, and our support team was getting flooded with customer complaints. This was directly affecting revenue because customers couldn't complete their purchases.
>
> I took ownership of the investigation. I started by analysing our monitoring dashboards and logs. Initially, it looked like a database issue because we were seeing slow query times. But after deeper analysis, I realised the actual root cause was different. We had a race condition in our event-driven architecture. Multiple workers were picking up the same order events and trying to process them simultaneously. This caused database locks and eventually led to connection timeouts.
>
> My solution had two parts. First, I implemented distributed locking using Redis to ensure that only one worker could process a given order at a time. Second, I added idempotency checks so that even if duplicate events were processed, the outcome would be consistent. I also improved our logging to make similar issues easier to diagnose in the future.
>
> I worked closely with our QA team to test the fix under load, and we deployed it gradually using feature flags. The rollout took about a week.
>
> The impact was significant. We reduced order processing failures by over 85%. Customer complaints related to stuck orders dropped to near zero. The solution also made our system more resilient to similar issues.
>
> The key learning for me was that the obvious symptom is often not the root cause. What looked like a database problem was actually a concurrency issue in our application layer. This reinforced the importance of thorough investigation before jumping to conclusions.

---

## 5. Technical Variation

> I'd like to describe a concurrency issue I resolved in a distributed event-driven system. Our architecture consisted of multiple microservices communicating through Kafka. The order service consumed events from a topic partitioned by customer ID.
>
> We observed that under high throughput, certain orders were entering a deadlock state. After instrumenting the code with additional tracing, I identified that multiple consumer instances were processing duplicate events due to a rebalancing issue during deployments. These duplicate processing attempts resulted in database row-level locks contending with each other, causing connection pool exhaustion in our PostgreSQL cluster.
>
> I implemented a solution using Redis-based distributed locks with a TTL of 30 seconds. Each worker would acquire a lock on the order ID before processing. I also added idempotency keys stored in a separate Redis cluster with a 24-hour expiration window. For the database layer, I optimised our transaction isolation level and added proper retry logic with exponential backoff.
>
> We tested the fix using Locust for load testing, simulating 5x our normal traffic. I deployed the changes incrementally using our feature flag system, starting with 5% of traffic and gradually increasing over several days while monitoring error rates and latency percentiles.
>
> Post-deployment metrics showed P99 latency dropped from 2.3 seconds to 180 milliseconds. Failed transaction rate went from 3.2% to under 0.1%. The solution has handled multiple traffic spikes since then without issues.

---

## 6. Business-Oriented Variation

> I'd like to share an example of how I solved a problem that was directly impacting our business metrics. We operate an e-commerce platform, and we started seeing a concerning trend: our checkout completion rate was dropping. The finance team flagged that we were losing an estimated 50,000 euros per day in failed transactions.
>
> I led the technical investigation and worked closely with our product and customer support teams to understand the full scope. Customers were reporting that their orders would get stuck, and they'd either abandon the purchase or contact support, which created additional operational costs.
>
> After identifying the technical root cause—a race condition in our order processing—I designed a solution that prioritised both reliability and minimal disruption to the business. I coordinated with stakeholders to plan a phased rollout that wouldn't require downtime during peak shopping hours.
>
> The business impact was measurable and immediate. Within two weeks of full deployment, our checkout completion rate increased by 12%. Customer support tickets related to order issues decreased by 75%, which freed up our support team to focus on higher-value interactions. Based on our analytics, we estimated the fix recovered approximately 40,000 euros per day in previously lost revenue.
>
> Beyond the immediate financial impact, this also improved customer trust. Our NPS scores for the checkout experience improved in the following quarter. From a strategic perspective, this fix gave us confidence to pursue a marketing campaign that would drive higher traffic, knowing our system could handle it reliably.

---

## 7. Improvisation Map

### Key Points to Cover (in rough order)
- What was the system / context
- What was the problem / symptom
- Why it mattered (business or technical impact)
- How you investigated
- What was the root cause
- What solution you implemented
- What was the result / impact
- What you learned

### Optional Branches (expand if time allows)
- Alternative solutions you considered and why you rejected them
- How you collaborated with other teams
- Monitoring and observability improvements
- How you tested the fix before deployment
- Long-term architectural changes that followed

### Fallback Phrases (if you get stuck)
- "Let me take a step back and explain the context…"
- "The key point here is…"
- "To summarise the impact…"
- "What's important to understand is…"
- "In practical terms, this meant…"
- "So essentially…"

### Bridging Phrases (to buy thinking time)
- "That's a great question, let me think about how to explain this clearly."
- "There are a few aspects to this…"
- "I want to make sure I explain this accurately…"

---

## 8. Common Follow-up Questions

1. "How did you prioritise this issue against other work?"

2. "What would you do differently if you faced this problem again?"

3. "How did you ensure the fix didn't introduce new issues?"

4. "Were there any disagreements in the team about the approach?"

5. "How did you communicate the issue and resolution to non-technical stakeholders?"

6. "What monitoring or alerting did you put in place afterwards?"

7. "How long did it take from identifying the issue to deploying the fix?"

---

*Practice the short monologue until it feels natural. Then use the improvisation map to vary your delivery each time.*
