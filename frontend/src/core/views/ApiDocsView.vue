<template>
  <div class="docs-page">
    <div class="docs-shell">
      <nav class="breadcrumbs" aria-label="Навигация">
        <router-link :to="authStore.isAuthenticated ? '/dashboard' : '/'">
          {{ authStore.isAuthenticated ? 'В приложение' : 'На главную' }}
        </router-link>
        <span aria-hidden="true">/</span>
        <span>Документация API</span>
      </nav>

      <header class="docs-header">
        <p class="eyebrow">CRM College · API</p>
        <h1>Документация сервисов</h1>
        <p>
          У проекта три самостоятельных FastAPI-сервиса. Общего Swagger нет: выберите нужный сервис,
          чтобы открыть его интерактивное описание методов.
        </p>
      </header>

      <main class="service-grid">
        <article v-for="service in services" :key="service.slug" class="service-card">
          <div class="card-top">
            <span class="service-number">{{ service.number }}</span>
            <span class="service-tag">{{ service.tag }}</span>
          </div>
          <h2>{{ service.name }}</h2>
          <p>{{ service.description }}</p>
          <div class="card-links">
            <a :href="service.docs">Открыть Swagger <span aria-hidden="true">↗</span></a>
            <a :href="service.schema" class="schema-link">OpenAPI JSON</a>
          </div>
        </article>
      </main>

      <p class="docs-note">
        Swagger показывает контракт API, но не отменяет проверку прав. Методы, требующие
        авторизации, вернут 401 или 403 без подходящих учётных данных. Если интерфейс Swagger не
        загружается из-за блокировки внешних ресурсов, схема доступна по ссылке OpenAPI JSON.
      </p>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../store/auth'

const authStore = useAuthStore()
const services = [
  {
    number: '01',
    slug: 'auth',
    tag: 'Доступ и пользователи',
    name: 'Auth',
    description: 'Вход, регистрация, пользователи, сессии и аудит.',
    docs: '/api/auth/docs',
    schema: '/api/auth/openapi.json'
  },
  {
    number: '02',
    slug: 'schedule',
    tag: 'Учебный процесс',
    name: 'Schedule',
    description: 'Расписание, группы, аудитории, участники и экспорт.',
    docs: '/api/schedule/docs',
    schema: '/api/schedule/openapi.json'
  },
  {
    number: '03',
    slug: 'techcard',
    tag: 'Планирование занятий',
    name: 'Techcard',
    description: 'Технологические карты и генерация документов.',
    docs: '/api/techcard/docs',
    schema: '/api/techcard/openapi.json'
  }
]
</script>

<style scoped>
.docs-page {
  --docs-accent: #755500;
  min-height: 100vh;
  padding: clamp(24px, 5vw, 72px);
  background: var(--bg-color);
  color: var(--text-primary);
}
:global(html[data-theme='dark']) .docs-page {
  --docs-accent: var(--primary-color);
}
.docs-shell {
  max-width: 1080px;
  margin: 0 auto;
}
.breadcrumbs {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: clamp(48px, 8vw, 110px);
}
.breadcrumbs a {
  color: var(--text-primary);
  text-decoration-color: var(--primary-color);
  text-underline-offset: 4px;
}
.docs-header {
  max-width: 660px;
  margin-bottom: 46px;
}
.eyebrow {
  color: var(--docs-accent);
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 16px;
}
h1 {
  font-size: clamp(2.4rem, 6vw, 4.6rem);
  line-height: 1.06;
  letter-spacing: -0.055em;
  margin: 0 0 18px;
}
.docs-header > p:last-child {
  color: var(--text-secondary);
  line-height: 1.7;
}
.service-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
.service-card {
  display: flex;
  flex-direction: column;
  min-height: 295px;
  padding: 26px;
  border: 1px solid var(--input-border);
  border-radius: 16px;
  background: var(--card-bg);
  box-shadow: var(--card-shadow);
}
.card-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  margin-bottom: 36px;
}
.service-number {
  color: var(--docs-accent);
  font-weight: 800;
}
.service-tag {
  font-size: 0.7rem;
  color: var(--text-secondary);
  text-align: right;
}
h2 {
  font-size: 1.45rem;
  margin: 0 0 8px;
}
.service-card > p {
  flex: 1;
  color: var(--text-secondary);
  line-height: 1.55;
  margin: 0 0 24px;
}
.card-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  align-items: center;
}
.card-links a {
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration-color: var(--primary-color);
  text-underline-offset: 4px;
}
.card-links .schema-link {
  color: var(--text-secondary);
  font-weight: 500;
}
a:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 4px;
}
.docs-note {
  margin-top: 30px;
  max-width: 760px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.7;
}
@media (max-width: 800px) {
  .service-grid {
    grid-template-columns: 1fr;
  }
  .service-card {
    min-height: 0;
  }
  .card-top {
    margin-bottom: 20px;
  }
}
</style>
