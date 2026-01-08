# Базовые Вопросы для Vue.js Собеседования

Этот список составлен для подготовки к собеседованиям на позицию Vue.js Developer. Только базовые вопросы без продвинутых тем.

## 1. Что такое Vue.js и в чем его основные преимущества?

Vue.js — это прогрессивный JavaScript-фреймворк для создания пользовательских интерфейсов. В отличие от монолитных фреймворков, Vue спроектирован так, чтобы его можно было внедрять постепенно.

**Основные преимущества:**
- **Прогрессивность** — можно использовать как библиотеку для части страницы или как полноценный фреймворк
- **Реактивность** — автоматическое отслеживание изменений данных и обновление DOM
- **Компонентный подход** — UI строится из переиспользуемых компонентов
- **Простота изучения** — низкий порог входа по сравнению с Angular
- **Отличная документация** — одна из лучших в экосистеме JavaScript

```js
// Простейший пример Vue 3
import { createApp, ref } from 'vue'

createApp({
  setup() {
    const count = ref(0)
    return { count }
  },
  template: `<button @click="count++">{{ count }}</button>`
}).mount('#app')
```

---

## 2. Что такое реактивность во Vue?

**Реактивность** — это механизм, который автоматически отслеживает изменения данных и обновляет DOM при их изменении.

**Как это работает в Vue 3:**
Vue использует JavaScript Proxy для перехвата операций чтения/записи свойств объекта.

```js
import { reactive, ref } from 'vue'

// reactive — для объектов
const state = reactive({
  count: 0,
  user: { name: 'John' }
})

// ref — для примитивов (и объектов тоже)
const count = ref(0)

// Изменяем — DOM обновляется автоматически
state.count++        // Реактивно
count.value++        // Для ref нужен .value в JavaScript
```

**Почему ref требует .value:**
- `ref` оборачивает значение в объект `{ value: ... }`
- Это нужно, потому что примитивы в JavaScript передаются по значению, а не по ссылке
- В шаблоне `.value` писать не нужно — Vue разворачивает автоматически

```vue
<template>
  <!-- В шаблоне .value не нужен -->
  <p>{{ count }}</p>
</template>

<script setup>
import { ref } from 'vue'
const count = ref(0)
// В JavaScript нужен .value
console.log(count.value)
</script>
```

---

## 3. В чем разница между `ref` и `reactive`?

| Критерий | ref | reactive |
|----------|-----|----------|
| Типы данных | Любые (примитивы и объекты) | Только объекты/массивы |
| Доступ в JS | Через `.value` | Напрямую |
| Доступ в шаблоне | Автоматический unwrap | Напрямую |
| Переприсвоение | Можно полностью заменить | Нельзя (потеряется реактивность) |

```js
import { ref, reactive } from 'vue'

// ref — универсальный
const count = ref(0)
const user = ref({ name: 'John' })

count.value = 5
user.value = { name: 'Jane' }  // Можно заменить весь объект

// reactive — только для объектов
const state = reactive({ count: 0 })

state.count = 5  // OK
state = { count: 10 }  // ОШИБКА! Потеря реактивности
```

**Когда что использовать:**
- `ref` — для примитивов и когда нужно переприсваивать целиком
- `reactive` — для сложных объектов, когда удобнее работать без `.value`

**Рекомендация:** Многие используют только `ref` для единообразия.

---

## 4. Что такое директивы во Vue?

**Директивы** — это специальные атрибуты с префиксом `v-`, которые применяют реактивное поведение к DOM-элементам.

**Встроенные директивы:**

```vue
<template>
  <!-- v-bind — привязка атрибутов (сокращение :) -->
  <img :src="imageUrl" :alt="imageAlt">

  <!-- v-on — обработка событий (сокращение @) -->
  <button @click="handleClick">Click</button>

  <!-- v-model — двусторонняя привязка -->
  <input v-model="searchQuery">

  <!-- v-if / v-else-if / v-else — условный рендеринг -->
  <p v-if="status === 'loading'">Loading...</p>
  <p v-else-if="status === 'error'">Error!</p>
  <p v-else>{{ data }}</p>

  <!-- v-show — переключение visibility -->
  <p v-show="isVisible">Видимый текст</p>

  <!-- v-for — рендеринг списков -->
  <li v-for="item in items" :key="item.id">
    {{ item.name }}
  </li>

  <!-- v-html — вставка HTML (осторожно с XSS!) -->
  <div v-html="htmlContent"></div>
</template>
```

**Модификаторы директив:**

```vue
<!-- Модификаторы событий -->
<form @submit.prevent="onSubmit">  <!-- preventDefault -->
<button @click.stop="onClick">     <!-- stopPropagation -->
<input @keyup.enter="onEnter">     <!-- только Enter -->

<!-- Модификаторы v-model -->
<input v-model.trim="text">        <!-- обрезать пробелы -->
<input v-model.number="age">       <!-- преобразовать в число -->
<input v-model.lazy="text">        <!-- обновлять на change, не input -->
```

---

## 5. В чем разница между `v-if` и `v-show`?

| Критерий | v-if | v-show |
|----------|------|--------|
| Как работает | Полностью добавляет/удаляет элемент из DOM | Переключает CSS `display: none` |
| Начальная стоимость | Низкая (если false, элемент не рендерится) | Высокая (всегда рендерится) |
| Стоимость переключения | Высокая (пересоздание элемента) | Низкая (только CSS) |
| Ленивость | Ленивый (рендерится при первом true) | Не ленивый |
| Поддержка `v-else` | Да | Нет |
| Работает с `<template>` | Да | Нет |

```vue
<template>
  <!-- v-if — полностью убирает из DOM -->
  <HeavyComponent v-if="showHeavy" />

  <!-- v-show — просто скрывает через CSS -->
  <Modal v-show="isModalOpen" />
</template>
```

**Когда что использовать:**
- `v-if` — когда условие меняется редко, или компонент тяжёлый и не нужен сразу
- `v-show` — когда условие переключается часто (модалки, табы, выпадающие меню)

---

## 6. Зачем нужен атрибут `key` при рендеринге списков?

`key` — уникальный идентификатор элемента в списке. Он помогает Vue эффективно обновлять DOM при изменении списка.

```vue
<template>
  <!-- ПРАВИЛЬНО — уникальный и стабильный key -->
  <li v-for="user in users" :key="user.id">
    {{ user.name }}
  </li>

  <!-- НЕПРАВИЛЬНО — index как key -->
  <li v-for="(user, index) in users" :key="index">
    {{ user.name }}
  </li>
</template>
```

**Почему индекс — плохой key:**

При добавлении элемента в начало списка:
```
До:    [0: Алиса, 1: Борис, 2: Вера]
После: [0: Новый, 1: Алиса, 2: Борис, 3: Вера]
```

Vue видит, что элемент с `key=0` изменился с "Алиса" на "Новый", и перерисовывает все элементы. С уникальным id Vue понимает, что добавился новый элемент, а остальные просто сдвинулись.

**Проблемы без правильного key:**
- Потеря состояния в компонентах (введённый текст, фокус)
- Неправильные анимации
- Лишние ререндеры

---

## 7. Что такое компоненты и как передавать данные между ними?

**Компонент** — это переиспользуемый блок UI со своей логикой, шаблоном и стилями.

**Способы передачи данных:**

### Props (родитель → ребёнок)

```vue
<!-- Parent.vue -->
<template>
  <ChildComponent :title="pageTitle" :count="5" />
</template>

<!-- ChildComponent.vue -->
<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  count: {
    type: Number,
    default: 0
  }
})
</script>

<template>
  <h1>{{ title }}</h1>
  <p>Count: {{ count }}</p>
</template>
```

### Emits (ребёнок → родитель)

```vue
<!-- ChildComponent.vue -->
<script setup>
const emit = defineEmits(['update', 'delete'])

function handleClick() {
  emit('update', { id: 1, value: 'new' })
}
</script>

<template>
  <button @click="handleClick">Update</button>
  <button @click="emit('delete', 1)">Delete</button>
</template>

<!-- Parent.vue -->
<template>
  <ChildComponent
    @update="handleUpdate"
    @delete="handleDelete"
  />
</template>
```

### v-model на компонентах

```vue
<!-- Parent.vue -->
<template>
  <CustomInput v-model="searchQuery" />
  <!-- Эквивалентно: -->
  <CustomInput
    :modelValue="searchQuery"
    @update:modelValue="searchQuery = $event"
  />
</template>

<!-- CustomInput.vue -->
<script setup>
defineProps(['modelValue'])
defineEmits(['update:modelValue'])
</script>

<template>
  <input
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
  />
</template>
```

---

## 8. Что такое Composition API и чем он отличается от Options API?

**Options API** — классический подход Vue 2, где логика разбита по опциям (data, methods, computed, watch).

**Composition API** — новый подход Vue 3, где логика группируется по функциональности.

```vue
<!-- Options API -->
<script>
export default {
  data() {
    return {
      count: 0,
      user: null
    }
  },
  computed: {
    doubleCount() {
      return this.count * 2
    }
  },
  methods: {
    increment() {
      this.count++
    },
    async fetchUser() {
      this.user = await api.getUser()
    }
  },
  mounted() {
    this.fetchUser()
  }
}
</script>

<!-- Composition API -->
<script setup>
import { ref, computed, onMounted } from 'vue'

// Логика счётчика вместе
const count = ref(0)
const doubleCount = computed(() => count.value * 2)
function increment() {
  count.value++
}

// Логика пользователя вместе
const user = ref(null)
async function fetchUser() {
  user.value = await api.getUser()
}
onMounted(fetchUser)
</script>
```

**Преимущества Composition API:**
- Логика группируется по функциональности, а не по типу опции
- Легче переиспользовать логику через composables (аналог React hooks)
- Лучшая поддержка TypeScript
- Меньше «магии» (нет `this`)

**Когда использовать Options API:**
- Простые компоненты
- Легаси-проекты
- Команда привыкла к Vue 2

---

## 9. Что такое computed свойства?

**Computed** — это вычисляемые свойства, которые кэшируются и пересчитываются только при изменении зависимостей.

```vue
<script setup>
import { ref, computed } from 'vue'

const firstName = ref('John')
const lastName = ref('Doe')

// Computed с геттером
const fullName = computed(() => {
  console.log('computed вызван')  // Вызовется только при изменении имени
  return `${firstName.value} ${lastName.value}`
})

// Computed с геттером и сеттером
const fullNameWritable = computed({
  get() {
    return `${firstName.value} ${lastName.value}`
  },
  set(newValue) {
    const [first, last] = newValue.split(' ')
    firstName.value = first
    lastName.value = last
  }
})
</script>

<template>
  <p>{{ fullName }}</p>  <!-- Можно использовать много раз — пересчёт один -->
  <p>{{ fullName }}</p>
  <input v-model="fullNameWritable">
</template>
```

**Computed vs Methods:**

| Computed | Methods |
|----------|---------|
| Кэшируется | Вызывается каждый раз |
| Пересчёт только при изменении зависимостей | Вызов при каждом ререндере |
| Вызывается как свойство: `fullName` | Вызывается как функция: `getFullName()` |

```vue
<script setup>
// computed — кэшируется
const expensiveComputed = computed(() => {
  return heavyCalculation(data.value)  // Вызов только при изменении data
})

// method — вызывается каждый раз
function expensiveMethod() {
  return heavyCalculation(data.value)  // Вызов при каждом ререндере
}
</script>

<template>
  <!-- computed: один вызов heavyCalculation -->
  <p>{{ expensiveComputed }}</p>
  <p>{{ expensiveComputed }}</p>

  <!-- method: два вызова heavyCalculation! -->
  <p>{{ expensiveMethod() }}</p>
  <p>{{ expensiveMethod() }}</p>
</template>
```

---

## 10. Что такое watch и watchEffect?

**Watch** и **watchEffect** — способы реагировать на изменения реактивных данных.

### watch — следит за конкретными источниками

```vue
<script setup>
import { ref, watch } from 'vue'

const count = ref(0)
const user = ref({ name: 'John' })

// Следим за ref
watch(count, (newValue, oldValue) => {
  console.log(`count: ${oldValue} → ${newValue}`)
})

// Следим за вложенным свойством через геттер
watch(
  () => user.value.name,
  (newName) => {
    console.log(`name changed to ${newName}`)
  }
)

// Следим за несколькими источниками
watch([count, user], ([newCount, newUser], [oldCount, oldUser]) => {
  // ...
})

// Глубокое наблюдение за объектом
watch(user, (newUser) => {
  console.log('user changed', newUser)
}, { deep: true })

// Немедленный вызов при создании
watch(count, (newValue) => {
  console.log(newValue)
}, { immediate: true })
</script>
```

### watchEffect — автоматически отслеживает зависимости

```vue
<script setup>
import { ref, watchEffect } from 'vue'

const count = ref(0)
const multiplier = ref(2)

// Автоматически следит за count и multiplier
watchEffect(() => {
  console.log(`Result: ${count.value * multiplier.value}`)
})
// Вызовется сразу при создании!
</script>
```

**Сравнение watch и watchEffect:**

| watch | watchEffect |
|-------|-------------|
| Явно указываем что отслеживать | Автоматически собирает зависимости |
| Не выполняется сразу (без `immediate`) | Выполняется сразу |
| Получаем старое и новое значение | Только текущее значение |
| Ленивый (lazy) | Энергичный (eager) |

---

## 11. Что такое жизненный цикл компонента Vue?

Каждый компонент проходит через несколько этапов существования.

**Основные хуки жизненного цикла:**

```vue
<script setup>
import {
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted
} from 'vue'

// СОЗДАНИЕ
// setup() выполняется первым (мы уже внутри него)

// МОНТИРОВАНИЕ
onBeforeMount(() => {
  // Перед вставкой в DOM
  // DOM ещё не доступен
})

onMounted(() => {
  // Компонент вставлен в DOM
  // Можно работать с DOM, запускать запросы
  console.log('mounted')
})

// ОБНОВЛЕНИЕ
onBeforeUpdate(() => {
  // Перед обновлением DOM
})

onUpdated(() => {
  // DOM обновлён
})

// УДАЛЕНИЕ
onBeforeUnmount(() => {
  // Перед удалением из DOM
})

onUnmounted(() => {
  // Компонент удалён
  // Очистка: таймеры, подписки, слушатели событий
})
</script>
```

**Порядок выполнения:**
```
setup()
  ↓
onBeforeMount
  ↓
onMounted  ←  Можно работать с DOM
  ↓
[При изменении данных]
  ↓
onBeforeUpdate
  ↓
onUpdated
  ↓
[При удалении компонента]
  ↓
onBeforeUnmount
  ↓
onUnmounted  ←  Очистка ресурсов
```

**Типичные случаи использования:**

```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const data = ref(null)

// Загрузка данных при монтировании
onMounted(async () => {
  data.value = await fetchData()
})

// Очистка подписок при размонтировании
onMounted(() => {
  const unsubscribe = subscribe()

  onUnmounted(() => {
    unsubscribe()
  })
})
</script>
```

---

## 12. Что такое слоты (slots)?

**Слоты** — механизм для передачи шаблонного контента в компоненты.

### Базовый слот

```vue
<!-- Card.vue -->
<template>
  <div class="card">
    <slot></slot>  <!-- Сюда вставится контент -->
  </div>
</template>

<!-- Использование -->
<Card>
  <h2>Заголовок</h2>
  <p>Контент карточки</p>
</Card>
```

### Именованные слоты

```vue
<!-- Layout.vue -->
<template>
  <header>
    <slot name="header"></slot>
  </header>
  <main>
    <slot></slot>  <!-- default слот -->
  </main>
  <footer>
    <slot name="footer"></slot>
  </footer>
</template>

<!-- Использование -->
<Layout>
  <template #header>
    <h1>Шапка сайта</h1>
  </template>

  <p>Основной контент (попадёт в default слот)</p>

  <template #footer>
    <p>Подвал сайта</p>
  </template>
</Layout>
```

### Scoped слоты (слоты с данными)

```vue
<!-- UserList.vue -->
<template>
  <ul>
    <li v-for="user in users" :key="user.id">
      <slot :user="user" :index="index">
        <!-- Fallback контент -->
        {{ user.name }}
      </slot>
    </li>
  </ul>
</template>

<!-- Использование -->
<UserList :users="users">
  <template #default="{ user, index }">
    <span>{{ index + 1 }}. {{ user.name }} ({{ user.email }})</span>
  </template>
</UserList>
```

**Зачем нужны scoped слоты:**
Позволяют родителю решать как рендерить данные, при этом данные приходят из дочернего компонента.

---

## 13. Что такое provide/inject?

**provide/inject** — механизм для передачи данных от предка к потомкам без пробрасывания через каждый уровень (аналог Context в React).

```vue
<!-- Grandparent.vue (предок) -->
<script setup>
import { provide, ref } from 'vue'

const theme = ref('dark')
const setTheme = (newTheme) => {
  theme.value = newTheme
}

// Предоставляем данные всем потомкам
provide('theme', theme)
provide('setTheme', setTheme)

// Или одним объектом
provide('themeContext', {
  theme,
  setTheme
})
</script>

<!-- DeepChild.vue (потомок на любом уровне вложенности) -->
<script setup>
import { inject } from 'vue'

// Получаем данные
const theme = inject('theme')
const setTheme = inject('setTheme')

// Со значением по умолчанию
const theme = inject('theme', 'light')
</script>

<template>
  <div :class="theme">
    <button @click="setTheme('light')">Light</button>
    <button @click="setTheme('dark')">Dark</button>
  </div>
</template>
```

**Сравнение с props:**

| Props | provide/inject |
|-------|----------------|
| Явная передача на каждом уровне | Неявная передача через дерево |
| Легко отследить поток данных | Сложнее понять откуда данные |
| Для связи родитель-ребёнок | Для глубокой вложенности |

**Когда использовать:**
- Тема приложения
- Текущий пользователь
- Конфигурация
- Избегание prop drilling

---

## 14. Что такое Vue Router и как он работает?

**Vue Router** — официальная библиотека маршрутизации для Vue.js.

### Базовая настройка

```js
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import About from '@/views/About.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About },
  { path: '/user/:id', component: () => import('@/views/User.vue') }  // Ленивая загрузка
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')
```

### Использование в компонентах

```vue
<template>
  <nav>
    <!-- Декларативная навигация -->
    <router-link to="/">Home</router-link>
    <router-link :to="{ name: 'user', params: { id: 1 } }">User</router-link>
  </nav>

  <!-- Сюда рендерится текущий маршрут -->
  <router-view />
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()  // Для навигации
const route = useRoute()    // Для чтения текущего маршрута

// Программная навигация
function goToUser(id) {
  router.push(`/user/${id}`)
  // или
  router.push({ name: 'user', params: { id } })
}

// Чтение параметров
console.log(route.params.id)
console.log(route.query.search)
console.log(route.path)
</script>
```

### Вложенные маршруты

```js
const routes = [
  {
    path: '/user/:id',
    component: User,
    children: [
      { path: '', component: UserHome },        // /user/:id
      { path: 'profile', component: UserProfile }, // /user/:id/profile
      { path: 'posts', component: UserPosts }     // /user/:id/posts
    ]
  }
]
```

```vue
<!-- User.vue -->
<template>
  <div>
    <h1>User {{ $route.params.id }}</h1>
    <router-view />  <!-- Вложенные маршруты рендерятся здесь -->
  </div>
</template>
```

---

## 15. Что такое Pinia и зачем нужен state management?

**Pinia** — официальная библиотека управления состоянием для Vue (замена Vuex).

**Зачем нужен state management:**
- Общие данные между несвязанными компонентами
- Централизованное хранение состояния приложения
- Удобство отладки (DevTools)
- Персистентность состояния

### Создание store

```js
// stores/counter.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Composition API стиль (рекомендуется)
export const useCounterStore = defineStore('counter', () => {
  // state
  const count = ref(0)
  const name = ref('Counter')

  // getters
  const doubleCount = computed(() => count.value * 2)

  // actions
  function increment() {
    count.value++
  }

  async function incrementAsync() {
    await new Promise(resolve => setTimeout(resolve, 1000))
    count.value++
  }

  return { count, name, doubleCount, increment, incrementAsync }
})
```

### Использование в компонентах

```vue
<script setup>
import { useCounterStore } from '@/stores/counter'
import { storeToRefs } from 'pinia'

const counterStore = useCounterStore()

// Для реактивного извлечения state/getters используйте storeToRefs
const { count, doubleCount } = storeToRefs(counterStore)

// Actions можно деструктурировать напрямую
const { increment, incrementAsync } = counterStore
</script>

<template>
  <p>Count: {{ count }}</p>
  <p>Double: {{ doubleCount }}</p>
  <button @click="increment">+1</button>
  <button @click="incrementAsync">+1 (async)</button>
</template>
```

**Pinia vs Vuex:**

| Pinia | Vuex |
|-------|------|
| Нет mutations (только actions) | Mutations + Actions |
| Поддержка Composition API | Только Options API |
| Полная поддержка TypeScript | Ограниченная |
| Модульный по умолчанию | Требует настройки модулей |
| Легче и проще | Больше boilerplate |

---

## 16. Как обрабатывать формы во Vue?

### Базовая работа с формами

```vue
<script setup>
import { ref, reactive } from 'vue'

// Используя ref для отдельных полей
const email = ref('')
const password = ref('')

// Или reactive для формы целиком
const form = reactive({
  email: '',
  password: '',
  remember: false
})

function handleSubmit() {
  console.log(form)
  // отправка на сервер
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <input
      v-model="form.email"
      type="email"
      placeholder="Email"
    >

    <input
      v-model="form.password"
      type="password"
      placeholder="Password"
    >

    <label>
      <input v-model="form.remember" type="checkbox">
      Remember me
    </label>

    <button type="submit">Login</button>
  </form>
</template>
```

### Модификаторы v-model

```vue
<template>
  <!-- .lazy — обновление на change вместо input -->
  <input v-model.lazy="message">

  <!-- .number — преобразование в число -->
  <input v-model.number="age" type="number">

  <!-- .trim — удаление пробелов по краям -->
  <input v-model.trim="username">
</template>
```

### Разные типы инпутов

```vue
<script setup>
import { ref } from 'vue'

const selected = ref('')
const multiSelected = ref([])
const checked = ref(false)
const checkedNames = ref([])
const picked = ref('')
</script>

<template>
  <!-- Select -->
  <select v-model="selected">
    <option value="">Выберите</option>
    <option value="a">A</option>
    <option value="b">B</option>
  </select>

  <!-- Multiple select -->
  <select v-model="multiSelected" multiple>
    <option value="a">A</option>
    <option value="b">B</option>
  </select>

  <!-- Checkbox (boolean) -->
  <input type="checkbox" v-model="checked">

  <!-- Checkbox (массив значений) -->
  <input type="checkbox" value="John" v-model="checkedNames">
  <input type="checkbox" value="Jane" v-model="checkedNames">

  <!-- Radio -->
  <input type="radio" value="one" v-model="picked">
  <input type="radio" value="two" v-model="picked">
</template>
```

---

## 17. Как работают асинхронные компоненты?

**Асинхронные компоненты** загружаются только когда они нужны (code splitting).

```vue
<script setup>
import { defineAsyncComponent } from 'vue'

// Базовое использование
const AsyncModal = defineAsyncComponent(() =>
  import('./components/Modal.vue')
)

// С опциями загрузки
const AsyncDashboard = defineAsyncComponent({
  loader: () => import('./components/Dashboard.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,  // Показать loading после 200ms
  timeout: 3000  // Таймаут загрузки
})
</script>

<template>
  <AsyncModal v-if="showModal" />
  <Suspense>
    <AsyncDashboard />
    <template #fallback>
      <LoadingSpinner />
    </template>
  </Suspense>
</template>
```

### Suspense (экспериментальный)

```vue
<template>
  <Suspense>
    <!-- Основной контент с async setup -->
    <template #default>
      <AsyncComponent />
    </template>

    <!-- Fallback пока загружается -->
    <template #fallback>
      <div>Loading...</div>
    </template>
  </Suspense>
</template>
```

```vue
<!-- AsyncComponent.vue -->
<script setup>
// async setup — компонент будет ждать resolve
const data = await fetchData()
</script>
```

---

## 18. Как стилизовать компоненты во Vue?

### Scoped стили

```vue
<template>
  <div class="card">
    <h1>Title</h1>
  </div>
</template>

<style scoped>
/* Стили применяются только к этому компоненту */
.card {
  padding: 20px;
}

/* Для стилизации дочерних компонентов используйте :deep() */
.card :deep(.child-class) {
  color: red;
}
</style>
```

### CSS Modules

```vue
<template>
  <div :class="$style.card">
    <h1 :class="[$style.title, $style.large]">Title</h1>
  </div>
</template>

<style module>
.card {
  padding: 20px;
}

.title {
  font-weight: bold;
}

.large {
  font-size: 24px;
}
</style>
```

### Динамические классы и стили

```vue
<template>
  <!-- Объект -->
  <div :class="{ active: isActive, disabled: isDisabled }"></div>

  <!-- Массив -->
  <div :class="[baseClass, { active: isActive }]"></div>

  <!-- Динамические стили -->
  <div :style="{ color: textColor, fontSize: fontSize + 'px' }"></div>

  <!-- v-bind в CSS (Vue 3.2+) -->
  <div class="text">Hello</div>
</template>

<script setup>
import { ref } from 'vue'
const textColor = ref('red')
</script>

<style scoped>
.text {
  color: v-bind(textColor);
}
</style>
```

---

## 19. Как работать с Template Refs?

**Template Refs** — способ получить прямую ссылку на DOM-элемент или экземпляр дочернего компонента.

```vue
<script setup>
import { ref, onMounted } from 'vue'

// Создаём ref с тем же именем, что и в шаблоне
const inputRef = ref(null)
const childRef = ref(null)

onMounted(() => {
  // DOM-элемент доступен после монтирования
  inputRef.value.focus()

  // Для компонента — доступ к публичным методам/свойствам
  childRef.value.someMethod()
})
</script>

<template>
  <input ref="inputRef" />
  <ChildComponent ref="childRef" />
</template>
```

### defineExpose — что дочерний компонент открывает наружу

```vue
<!-- ChildComponent.vue -->
<script setup>
import { ref } from 'vue'

const count = ref(0)
const privateData = ref('secret')

function increment() {
  count.value++
}

function reset() {
  count.value = 0
}

// Только эти свойства/методы будут доступны через ref
defineExpose({
  count,
  increment,
  reset
})
</script>
```

### Refs в v-for

```vue
<script setup>
import { ref, onMounted } from 'vue'

const itemRefs = ref([])

onMounted(() => {
  console.log(itemRefs.value)  // массив DOM-элементов
})
</script>

<template>
  <li v-for="item in list" ref="itemRefs">
    {{ item }}
  </li>
</template>
```

---

## 20. Какие модификаторы событий существуют?

Vue предоставляет модификаторы для удобной обработки событий.

### Модификаторы событий

```vue
<template>
  <!-- .stop — event.stopPropagation() -->
  <button @click.stop="handleClick">Click</button>

  <!-- .prevent — event.preventDefault() -->
  <form @submit.prevent="onSubmit">...</form>

  <!-- .capture — использовать режим capture -->
  <div @click.capture="handleClick">...</div>

  <!-- .self — только если target === currentTarget -->
  <div @click.self="handleClick">...</div>

  <!-- .once — сработает только один раз -->
  <button @click.once="doOnce">Click once</button>

  <!-- .passive — для улучшения производительности scroll -->
  <div @scroll.passive="onScroll">...</div>

  <!-- Можно комбинировать -->
  <a @click.stop.prevent="doSomething">Link</a>
</template>
```

### Модификаторы клавиш

```vue
<template>
  <!-- Конкретные клавиши -->
  <input @keyup.enter="submit">
  <input @keyup.tab="onTab">
  <input @keyup.delete="onDelete">  <!-- Delete и Backspace -->
  <input @keyup.esc="cancel">
  <input @keyup.space="onSpace">
  <input @keyup.up="onUp">
  <input @keyup.down="onDown">
  <input @keyup.left="onLeft">
  <input @keyup.right="onRight">

  <!-- Системные модификаторы -->
  <input @keyup.ctrl.enter="submit">  <!-- Ctrl + Enter -->
  <div @click.ctrl="onClick">Ctrl + Click</div>
  <div @click.alt="onClick">Alt + Click</div>
  <div @click.shift="onClick">Shift + Click</div>
  <div @click.meta="onClick">Cmd/Win + Click</div>

  <!-- .exact — точное сочетание клавиш -->
  <button @click.ctrl.exact="onCtrlClick">Ctrl only</button>
</template>
```

### Модификаторы мыши

```vue
<template>
  <div @click.left="onLeftClick">Left click</div>
  <div @click.right="onRightClick">Right click</div>
  <div @click.middle="onMiddleClick">Middle click</div>
</template>
```
