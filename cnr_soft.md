# Soft Skills Interview Questions (Canary)

## Warm-up / Product Sense

1. Could you tell me about a product that you use a lot, but has something that annoys you or is difficult to use?
   - Follow-up: Not something you're building, just something you use every day
   - Follow-up: Why is latency high on SMS (если кандидат упомянет SMS)
   - Follow-up: Is this an issue with their UX, or is it an issue with the regulatory environment
   - Follow-up: Why would they use optimistic updates but wait to ask you for more information

**Идеи:**
- I often find that many apps make it hard to find the features I use the most. Important buttons are hidden in menus, and I waste time searching for them.

It would be great if apps had a customizable or automatically generated home screen that shows my frequent actions or recent activity. This would make the experience faster and more personal.

---

## Technical Experience

2. What about a software system that you've had to work with that was difficult - maybe something you owned or something you had to interact with in your job

**Идеи:**
I’ve often worked with systems where it’s unclear how to get started. The setup README is outdated or incomplete, so a new engineer has to guess steps or ask around.

Another common issue is that some internal actions — like adding a new role or creating a feature flag — require non-obvious manual steps that aren’t documented anywhere. This slows people down and makes onboarding harder.

I would fix it by creating clear, up-to-date documentation and making it part of the development process.

For internal actions like adding roles or feature flags, I’d either automate them with scripts/tools or document the steps in one place.

---

3. What's some code you've had to work with that you found annoying - maybe something internal, not a library
   - Follow-up: How would you resolve/fix it if you were going to fix it

**Идеи:**
I’ve worked with Django views where everything is in one place — validation, business logic, and database queries all mixed together. It becomes hard to test, maintain, or extend.

To fix it, I’d separate concerns: move business logic into a service layer, keep validation in serializers/forms, and keep data access in managers or repository-style helpers.
---

4. What's your favorite project you've ever worked on

**Идеи:**
- Рефакторинг API для мобильного приложения — упростил структуру, ускорил response time, команда была довольна
- Автоматизация deployment процесса — сократил время релиза, меньше ручной работы, меньше ошибок
- Интеграция платёжной системы — много нюансов, но результат видимый для бизнеса
- Background job система для отчётов — пользователи перестали ждать, async обработка, хороший UX

---

## Deep Dive on Framework/Library

5. Can you pick a framework or library that you're very familiar with
   - Follow-up: Give me a one sentence description of [framework]
   - Follow-up: I don't know anything about [framework]. What are the key concepts I need to understand if I wanted to use it effectively
   - Follow-up: What's the most complicated thing about [framework]
   - Follow-up: What are some trade-offs with [framework]
   - Follow-up: What would you change about [framework] or what bothers you about it

**Идеи:**
- Django — batteries-included, ORM/admin/auth из коробки, conventions over configuration

MTV architecture — Models, Templates, Views define data, UI, and request handling.

ORM — lets you work with the database using Python classes instead of raw SQL.

Apps & project structure — every feature is an “app” that stays modular and reusable.

Admin — auto-generated UI for managing data.

Middleware — request/response processing layers.

---

## Career & Growth

6. How has your perspective on engineering changed over the course of your career

**Идеи:**
I used to focus on “perfect code,” now I care more about delivering value and iterating fast.

I learned to prioritize simplicity because it makes onboarding and maintenance easier.

And I now see tests as a safety net for confident changes, not just a coverage metric.

---

## Behavioral / Soft Skills

7. Tell me about a time when you received a piece of critical feedback
   - Follow-up: (уточнение если кандидат смешивает несколько примеров) These were two separate pieces of feedback, right

**Идеи:**
I got feedback that I was moving too fast and sometimes skipped small details that later caused minor issues. After that, I started adding an extra self-review step before submitting PRs.

---

8. Tell me about a time when you had a conflict with a coworker
   - Follow-up: What did the metrics tell you (если кандидат упоминает данные/метрики)

**Идеи:**
I had a conflict once when a new coworker kept adding unrelated changes into his own pull requests, mixing refactoring and small fixes with the main task. It made reviews slow and hard to follow. I talked to him directly and asked to keep PRs focused. He understood after the conversation, and the issue was resolved without escalation.

---

## Technical Decisions

9. Why did you choose to use a new DB versus just extending your existing DB (контекстный вопрос если кандидат упоминает выбор БД)

**Идеи:**
- Добавили Redis для кэширования — PostgreSQL справлялся, но хотели снизить нагрузку на основную БД
- Elasticsearch для поиска — нужен был full-text search с фильтрами, проще чем строить на PostgreSQL
- Отдельная read replica — разделили read/write нагрузку для отчётов
- Redis для rate limiting — нужны были быстрые atomic операции, не хотели нагружать основную БД

---

## Mentorship

10. If you're mentoring an engineer, what things do you make sure that they understand early on

**Идеи:**
Clarity first — ask questions, confirm assumptions, don’t start coding until the task is fully clear.

Small, focused PRs — easier to review, easier to test, easier to roll back.

Simplicity wins — choose the simplest solution that works before adding abstractions.

Communicate early — surface blockers, risks, or doubts right away, not at the end.

---

## Personal Growth / Curiosity

11. What's a memorable insight you had recently from maybe a book or something you listened to or a conversation you had
    - Follow-up: (переформулировка) What's an insight that you had recently from reading a book or an article or listening to a podcast, or maybe a conference

**Идеи:**
A memorable insight I had recently comes from Thinking, Fast and Slow by Daniel Kahneman. It reminded me that we all have two ways of thinking: fast, intuitive decisions and slow, deliberate reasoning. I realized that in engineering and product decisions, it’s easy to rely on intuition, but taking a moment to slow down and think deliberately often prevents mistakes and leads to better outcomes.

---

## Closing

12. Do you have any questions for me

**Идеи:**
- Какой tech stack используете и планируете ли что-то менять
- Как устроена работа в команде — stand-ups, planning, retros
- Над чем работает команда сейчас, какие ближайшие цели
- Что вам лично нравится в работе здесь
