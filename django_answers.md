# Django Framework Q&A

## 1. How would you define this framework in one/two lines?

Django — это высокоуровневый Python веб-фреймворк, следующий принципу "batteries included", который позволяет быстро создавать безопасные и масштабируемые веб-приложения с минимальным количеством кода благодаря встроенным ORM, админке, аутентификации и системе миграций.

---

## 2. What do developers struggle with this framework in your opinion?

### 2.1. N+1 Query Problem
```python
# Плохо — N+1 запросов
for book in Book.objects.all():
    print(book.author.name)  # Каждый раз новый запрос к БД

# Хорошо — 1 запрос с JOIN
for book in Book.objects.select_related('author'):
    print(book.author.name)

# Для ManyToMany и reverse FK — prefetch_related
for author in Author.objects.prefetch_related('books'):
    print([b.title for b in author.books.all()])  # Без доп. запросов
```

### 2.2. Асинхронность и Django ORM
```python
# Django ORM синхронный по своей природе
# Async views появились, но ORM всё ещё блокирующий

# Плохо — блокирует event loop
async def my_view(request):
    users = User.objects.all()  # Синхронный вызов!
    return JsonResponse({'count': len(users)})

# Хорошо — использование sync_to_async
from asgiref.sync import sync_to_async

async def my_view(request):
    users = await sync_to_async(list)(User.objects.all())
    return JsonResponse({'count': len(users)})
```

### 2.3. Сложные запросы и Raw SQL
```python
# Django ORM не всегда выразителен для сложных запросов
# Приходится использовать raw SQL или extra()

# Проблема: оконные функции, CTE, рекурсивные запросы
# Django ORM не поддерживает напрямую

# Workaround с RawSQL
from django.db.models import F, Window
from django.db.models.functions import Rank

# Ранжирование внутри категории — сложно без window functions
Article.objects.annotate(
    rank=Window(
        expression=Rank(),
        partition_by=[F('category')],
        order_by=F('views').desc()
    )
)

# Часто проще написать raw SQL
Article.objects.raw('''
    SELECT *, RANK() OVER (PARTITION BY category_id ORDER BY views DESC) as rank
    FROM articles
''')
```

### 2.4. Тестирование с fixtures и factory
```python
# Встроенные fixtures в JSON/YAML неудобны и хрупки
# fixtures/users.json — быстро устаревает при изменении моделей

# Приходится использовать factory_boy или model_bakery
import factory

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@test.com')

# В тестах
def test_user_creation():
    user = UserFactory()  # Создаёт реального пользователя
    user = UserFactory.build()  # Только объект без сохранения
```

---

## 3. What are the essential things that one needs to know to start using it?

### 3.1. Модели и QuerySet API
```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE)

# Основные методы QuerySet
Article.objects.all()                          # Все записи
Article.objects.filter(author_id=1)            # Фильтрация
Article.objects.exclude(title='Draft')         # Исключение
Article.objects.get(pk=1)                      # Одна запись
Article.objects.order_by('-published')[:10]    # Сортировка + срез
Article.objects.values('title', 'author__name') # Выборка полей
```

### 3.2. Class-Based Views и Generic Views
```python
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# CRUD за 20 строк
class ArticleListView(ListView):
    model = Article
    template_name = 'articles/list.html'
    context_object_name = 'articles'
    paginate_by = 20

class ArticleCreateView(CreateView):
    model = Article
    fields = ['title', 'content']
    success_url = reverse_lazy('article-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```

### 3.3. Middleware и Request/Response lifecycle
```python
# Понимание middleware критично для Django
# settings.py — порядок ВАЖЕН!
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'myapp.middleware.CustomMiddleware',  # Ваш middleware
]

# Кастомный middleware
class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        response['X-Request-Duration'] = str(duration)
        return response
```

### 3.4. Signals и decoupling
```python
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

# Автоматические действия при сохранении модели
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Очистка связанных данных
@receiver(pre_delete, sender=Article)
def cleanup_article_files(sender, instance, **kwargs):
    instance.image.delete(save=False)
    instance.attachments.all().delete()
```

---

## 4. What feature would you implement to improve the usage experience on this framework?

*Вдохновлено best practices из FastAPI, SQLAlchemy, SQLModel, Pydantic*

### 4.1. Декларативные API endpoints (вдохновлено FastAPI)
```python
# Сейчас DRF требует много boilerplate
# Желаемый API — как в FastAPI, но с Django ORM

from django.api import router, Query, Body
from pydantic import BaseModel

class ArticleCreate(BaseModel):
    title: str
    content: str

class ArticleResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True  # Работает с Django моделями

@router.post("/articles/", response_model=ArticleResponse)
async def create_article(
    data: ArticleCreate,
    user: User = Depends(get_current_user)
):
    article = await Article.objects.acreate(**data.model_dump(), author=user)
    return article

@router.get("/articles/")
async def list_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    search: str | None = Query(None)
):
    qs = Article.objects.all()
    if search:
        qs = qs.filter(title__icontains=search)
    return [a async for a in qs[(page-1)*limit:page*limit]]
```

### 4.2. Унифицированные модели (вдохновлено SQLModel)
```python
# SQLModel объединяет SQLAlchemy + Pydantic
# Желаемый API для Django — модель = схема валидации

from django.db import models
from typing import Annotated

class Article(models.Model):
    # Одна модель для БД, валидации и сериализации
    title: Annotated[str, models.CharField(max_length=200)]
    content: Annotated[str, models.TextField()]
    views: Annotated[int, models.IntegerField(default=0)]
    author: Annotated["User", models.ForeignKey('User', on_delete=models.CASCADE)]

    class Meta:
        # Автогенерация Pydantic схем
        generate_schemas = True

# Использование
article = Article(title="Test", content="...")  # Валидация при создании
article.model_dump()  # Сериализация как в Pydantic
Article.schema()  # JSON Schema для OpenAPI
```

### 4.3. Dependency Injection система (вдохновлено FastAPI)
```python
# Сейчас в Django нет встроенного DI
# Желаемый API

from django.depends import Depends, dependency

@dependency
async def get_db_session():
    async with AsyncSession() as session:
        yield session

@dependency
async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session)
) -> User:
    token = request.headers.get("Authorization")
    user = await session.get(User, decode_token(token).user_id)
    if not user:
        raise HTTPException(401)
    return user

@dependency
def get_settings() -> Settings:
    return Settings()

# View с автоматическим DI
async def create_article(
    request: Request,
    user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    # user и settings инжектируются автоматически
    ...
```

### 4.4. Query Builder с type safety (вдохновлено SQLAlchemy 2.0 + Prisma)
```python
# Типизированные запросы с автокомплитом IDE

from django.db.query import select, and_, or_

# SQLAlchemy 2.0 style
stmt = (
    select(Article)
    .where(Article.author_id == user.id)
    .where(Article.published == True)
    .order_by(Article.created_at.desc())
    .limit(10)
)
articles = await session.execute(stmt)

# Или Prisma-style API
articles = await Article.prisma.find_many(
    where={
        "author_id": user.id,
        "published": True,
        "OR": [
            {"title": {"contains": "Django"}},
            {"tags": {"some": {"name": "python"}}}
        ]
    },
    include={"author": True, "comments": {"take": 5}},
    order_by={"created_at": "desc"},
    take=10
)

# IDE знает все поля и подсказывает
# Ошибки типов ловятся до runtime
```
