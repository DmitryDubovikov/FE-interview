# Soft Skills Interview Questions (Canary)

## Warm-up / Product Sense

1. Could you tell me about a product that you use a lot, but has something that annoys you or is difficult to use?
   - Follow-up: Not something you're building, just something you use every day
   - Follow-up: Why is latency high on SMS (если кандидат упомянет SMS)
   - Follow-up: Is this an issue with their UX, or is it an issue with the regulatory environment
   - Follow-up: Why would they use optimistic updates but wait to ask you for more information

**Идеи:**
- Notion — иногда тормозит на больших документах, offline режим ненадёжный
- Google Calendar — сложно найти свободное время для группы людей, приходится вручную сравнивать
- Spotify — рекомендации иногда застревают в одном жанре, сложно "сбросить" алгоритм
- YouTube — автоплей включает нерелевантные видео, история просмотров влияет на рекомендации слишком сильно

---

## Technical Experience

2. What about a software system that you've had to work with that was difficult - maybe something you owned or something you had to interact with in your job

**Идеи:**
- Django проект с устаревшей структурой — всё в одном app, circular imports, долго разбираться
- Сервис биллинга со сложной бизнес-логикой — много edge cases, каждое изменение требовало осторожности
- Интеграция с внешним API без sandbox — тестировать приходилось аккуратно, документация неполная
- Система уведомлений с несколькими каналами (email, push, SMS) — сложно дебажить почему не дошло

---

3. What's some code you've had to work with that you found annoying - maybe something internal, not a library
   - Follow-up: How would you resolve/fix it if you were going to fix it

**Идеи:**
- Fat views без сервисного слоя — бизнес-логика размазана по views, тяжело тестировать и переиспользовать
- Модели с property-методами которые делают запросы в БД — неочевидные N+1, сложно отследить
- Celery таски без идемпотентности — при retry дублировались emails, пришлось добавлять deduplication
- Тесты которые зависят от порядка выполнения — падали рандомно на CI, shared state между тестами

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
- Celery — distributed task queue для background jobs, интеграция с Django/Flask
- PostgreSQL — надёжная RDBMS, хорошо знаю индексы, EXPLAIN, оптимизацию запросов
- Redis — in-memory store для кэша, очередей, sessions, pub/sub

---

## Career & Growth

6. How has your perspective on engineering changed over the course of your career

**Идеи:**
- Раньше хотел написать идеальный код, теперь понимаю что важнее доставить value и итерировать
- Научился ценить простоту — легче поддерживать, легче онбордить новых людей
- Понял важность тестов не для coverage, а для уверенности при изменениях
- Стал больше думать о том как код будет читаться через полгода другим человеком

---

## Behavioral / Soft Skills

7. Tell me about a time when you received a piece of critical feedback
   - Follow-up: (уточнение если кандидат смешивает несколько примеров) These were two separate pieces of feedback, right

**Идеи:**
- Фидбек что мои PR слишком большие — научился разбивать на smaller chunks
- Сказали что на code review даю слишком много комментариев сразу — стал приоритизировать главное
- Менеджер отметил что мало делюсь контекстом с командой — начал писать короткие updates в Slack
- Коллега сказал что перебиваю на митингах — стал больше слушать и записывать мысли

---

8. Tell me about a time when you had a conflict with a coworker
   - Follow-up: What did the metrics tell you (если кандидат упоминает данные/метрики)

**Идеи:**
- Разное мнение о том как структурировать код — обсудили плюсы/минусы, выбрали вариант вместе
- Несогласие о приоритете багов vs фич — поговорили с PM, договорились о балансе
- Коллега хотел быстрый fix, я хотел proper solution — нашли компромисс с TODO и тикетом на рефакторинг
- Разногласие о naming conventions — вынесли на обсуждение команды, приняли решение голосованием

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
- Не бояться задавать вопросы — лучше спросить рано чем потратить день впустую
- Как пользоваться git эффективно — branching, rebasing, хорошие commit messages
- Как читать и понимать существующий код — важнее чем сразу писать новый
- Важность тестирования своих изменений локально перед PR

---

## Personal Growth / Curiosity

11. What's a memorable insight you had recently from maybe a book or something you listened to or a conversation you had
    - Follow-up: (переформулировка) What's an insight that you had recently from reading a book or an article or listening to a podcast, or maybe a conference

**Идеи:**
- Статья про technical debt — не весь debt плохой, иногда это осознанный trade-off
- Разговор с senior коллегой — важность документировать не что, а почему было принято решение
- Книга/блог про code review — фокус на обучении, а не на критике
- Подкаст про работу в distributed команде — overcommunication лучше чем недосказанность

---

## Closing

12. Do you have any questions for me

**Идеи:**
- Какой tech stack используете и планируете ли что-то менять
- Как устроена работа в команде — stand-ups, planning, retros
- Над чем работает команда сейчас, какие ближайшие цели
- Что вам лично нравится в работе здесь
