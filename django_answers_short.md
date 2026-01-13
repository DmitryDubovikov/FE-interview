# Шпаргалка: Django Framework

## 1. Что такое Django?
- Высокоуровневый Python веб-фреймворк, "batteries included"
- Встроенные: ORM, админка, аутентификация, миграции
- Быстрая разработка безопасных масштабируемых приложений

---

## 2. Проблемы разработчиков

### N+1 Query Problem
- `select_related('author')` — для FK (JOIN)
- `prefetch_related('books')` — для M2M и reverse FK
- Без них: N+1 запросов в циклах

### Сложные запросы
- ORM не поддерживает: оконные функции, CTE, рекурсию напрямую
- Решения: `Window()`, `RawSQL`, `.raw()` для сложных случаев

---

## 3. Основы Django

### Модели и QuerySet
- `objects.all()` — все записи
- `filter()` / `exclude()` — фильтрация
- `get(pk=1)` — одна запись (или исключение)
- `order_by()` + срезы `[:10]`
- `values()` / `values_list()` — выборка полей

### Class-Based Views
- `ListView`, `CreateView`, `UpdateView`, `DeleteView`
- `model`, `fields`, `template_name`, `success_url`
- `form_valid()` — для кастомной логики

### Middleware
- Порядок в `MIDDLEWARE` важен!
- Цепочка: request → middleware → view → middleware → response
- `__init__` + `__call__` для кастомного middleware

### Signals
- `post_save`, `pre_delete`, `pre_save`
- `@receiver(signal, sender=Model)`
- Для: создания связанных объектов, очистки файлов, логирования

---

## 4. Желаемые улучшения

### Dependency Injection (как в FastAPI)
- Сейчас: нет встроенного DI
- Хотелось бы: `Depends()` для инжекции сессий, пользователей, настроек
- Автоматическое разрешение зависимостей во views
