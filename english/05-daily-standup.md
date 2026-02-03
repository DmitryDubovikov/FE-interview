# 5. Daily Standup

## 1. Core Speaking Chunks (25 items)

### Responsibility Framing
- "Yesterday I focused on…"
- "Today my priority is…"
- "I'm currently working on…"
- "I picked up the task for…"
- "I've been investigating…"

### Progress Updates
- "I managed to complete…"
- "I made good progress on…"
- "I'm about halfway through…"
- "I wrapped up the implementation of…"
- "I got it to a working state, but still need to…"

### Blockers & Dependencies
- "I'm blocked on…"
- "I'm waiting for…"
- "I need input from…"
- "Before I can proceed, I need…"
- "There's a dependency on…"

### Technical Explanation Starters
- "The approach I'm taking is…"
- "I ran into an issue with…"
- "It turned out that…"
- "The root cause was…"
- "I had to adjust the approach because…"

### Cause → Effect
- "Because of that, I had to…"
- "That means we can now…"
- "This unblocked…"

### Reflection & Planning
- "If everything goes well, I should be able to…"
- "I'll need another day to…"
- "I might need to sync with [name] about…"

---

## 2. Grammar Patterns for This Topic

### Pattern 1: Present Perfect for Recent Completions
**Structure:** have/has + past participle
**When to use:** To report completed work with relevance to now.

- "I've finished the API endpoint."
- "I've pushed the changes for review."

### Pattern 2: Present Continuous for Ongoing Work
**Structure:** am/is/are + verb-ing
**When to use:** To describe what you're currently doing or planning for today.

- "I'm working on the database migration."
- "I'm still debugging the authentication flow."

### Pattern 3: Past Simple for Yesterday's Actions
**Structure:** verb in past tense
**When to use:** To report specific completed actions from yesterday.

- "Yesterday I reviewed the PR and left comments."
- "I identified the issue in the caching layer."

### Pattern 4: Going to / Will for Plans
**Structure:** going to + base verb / will + base verb
**When to use:** To state today's intentions or predictions.

- "Today I'm going to finish the unit tests."
- "I'll sync with the frontend team after this."

---

## 3. Short Monologue (30–60 seconds)

> Yesterday I focused on the user authentication service. I completed the password reset flow and pushed it for review. I also fixed a bug in the session handling that was causing intermittent logouts.
>
> Today I'm going to address the review comments and then move on to the rate limiting feature. I need to check the requirements with the product team first.
>
> No blockers at the moment, but I might need a quick sync with Maria about the API contract for rate limiting.

---

## 4. Long Monologue (2–4 minutes)

> Let me give a bit more context on what I've been working on this sprint.
>
> So the main task I picked up was improving the reliability of our notification service. We'd been getting complaints from users that some notifications were arriving late or not at all, especially during peak hours.
>
> Yesterday I spent most of the day investigating the root cause. I looked at the logs and metrics, and it turned out the issue was in how we were handling message acknowledgements in our queue consumer. Under high load, some messages were being reprocessed multiple times, which caused delays and duplicates.
>
> I identified a race condition in the acknowledgement logic. The consumer was acknowledging messages before the downstream processing was fully complete. So if the service restarted or timed out, messages would get lost or retried incorrectly.
>
> I refactored the consumer to use explicit acknowledgements only after successful processing. I also added a dead-letter queue for failed messages so we can inspect them later instead of losing them silently.
>
> I managed to get a working version deployed to staging yesterday evening. Initial tests look good — the duplicate rate dropped significantly and latency is more stable.
>
> Today I'm going to run more load tests to validate the fix under realistic conditions. I also want to add some alerting around the dead-letter queue so we get notified if messages start failing.
>
> One thing I learned from this is the importance of idempotent message handling. Even with the fix, there's still a small chance of duplicates in edge cases, so I'm planning to propose adding idempotency keys as a follow-up task.
>
> No blockers right now. I should have the load test results by end of day, and if everything looks good, we can plan the production rollout for tomorrow.

---

## 5. Technical Variation

> Yesterday I focused on debugging the notification service reliability issues.
>
> The architecture is a standard event-driven setup: we have a FastAPI service consuming from RabbitMQ, processing notification events, and dispatching them via SNS to multiple channels — email, push, SMS.
>
> The problem was in the prefetch and acknowledgement configuration. We were using auto-ack with a high prefetch count, which meant the consumer could pull hundreds of messages but lose them on restart before processing.
>
> I switched to manual acknowledgements with a prefetch of one. Now each message is only acked after the SNS publish call returns successfully. I also configured a dead-letter exchange with a TTL-based retry mechanism — failed messages go to DLX, wait 30 seconds, then get requeued for one retry before going to a permanent dead-letter queue.
>
> I added structured logging with correlation IDs so we can trace a notification from ingestion to delivery. I also set up CloudWatch alarms on the DLQ depth and consumer lag metrics.
>
> The trade-off is slightly lower throughput — we're processing about 20% fewer messages per second now — but the reliability improvement is significant. Duplicate rate went from around 3% to under 0.1% in staging.
>
> Today I'm running load tests with Locust to simulate peak traffic patterns. If the p99 latency stays under 500ms, we're good to ship.

---

## 6. Business-Oriented Variation

> I've been working on a reliability issue that was directly affecting user experience and retention.
>
> The problem was that some users weren't receiving important notifications — things like password resets, payment confirmations, order updates. Customer support was getting tickets about this, and we saw it reflected in NPS feedback as well.
>
> I investigated and found that our notification system was dropping messages under high load. About 3% of notifications were either delayed or lost entirely.
>
> I implemented a fix that ensures every notification is properly delivered, even if there's a temporary failure. We now have visibility into failed notifications and can retry them automatically.
>
> The business impact is clear: notification reliability went from about 97% to over 99.9%. That means fewer support tickets, better user trust, and we can now confidently use notifications for time-sensitive communications like flash sales or security alerts.
>
> The fix required about three days of work. No additional infrastructure costs — we just configured the existing components differently.
>
> Today I'm validating the fix with load testing. If it holds up, we can deploy to production tomorrow, which aligns well with the marketing campaign launching next week.

---

## 7. Improvisation Map

### Key Ideas to Cover
- What I did yesterday (specific task)
- What I'm doing today (clear priority)
- Any blockers or dependencies
- Brief context if needed

### Optional Branches
- Root cause if asked
- Technical approach
- Impact or business value
- Timeline or next steps
- Who I need to coordinate with

### Fallback Phrases If Stuck
- "Let me think… the main thing is…"
- "To summarize…"
- "The short version is…"
- "Essentially what happened was…"
- "I can go into more detail if helpful, but the key point is…"

### Structure Template
1. **Yesterday:** One or two sentences on completed work
2. **Today:** Clear statement of priority
3. **Blockers:** State clearly or say "No blockers"
4. **Optional:** Quick context or coordination needs

---

## 8. Common Follow-up Questions

1. "Can you explain the technical approach you took?"

2. "How did you identify the root cause?"

3. "What's the impact of this change on system performance?"

4. "Are there any risks with the current approach?"

5. "How long until this is ready for production?"

6. "Do you need any help or support from the team?"

7. "How does this relate to the sprint goal?"
