# 🎉 Новые функции Auth Service

## ✅ Реализованные функции

### 1. 🔐 Управление активными сессиями

**Эндпоинты:**
- `GET /api/auth/sessions` - Список всех активных сессий пользователя
- `PUT /api/auth/sessions/{session_id}` - Обновление имени устройства
- `DELETE /api/auth/sessions/{session_id}` - Отзыв конкретной сессии
- `POST /api/auth/sessions/revoke-all` - Отзыв всех сессий кроме текущей

**Функциональность:**
- Просмотр всех активных сессий с информацией об IP, устройстве, времени создания и последнего использования
- Пометка текущей сессии
- Переименование устройств для удобства
- Отзыв конкретных сессий
- Массовый отзыв всех сессий кроме текущей

**Модель:**
- Добавлено поле `last_used_at` в `RefreshToken` для отслеживания активности
- Добавлено поле `device_name` для именования устройств

---

### 2. 🔍 Поиск и фильтрация пользователей

**Эндпоинт:**
- `GET /api/users?search=...&role=...&is_active=...&page=1&limit=20`

**Параметры:**
- `search` - Поиск по email или имени (case-insensitive)
- `role` - Фильтр по роли (admin, teacher, student, moderator)
- `is_active` - Фильтр по активности (true/false)
- `is_verified` - Фильтр по верификации (true/false)
- `page` - Номер страницы (начиная с 1)
- `limit` - Количество на странице (1-100)
- `sort` - Поле сортировки (created_at, email, full_name, last_login)
- `order` - Направление сортировки (asc/desc)

**Ответ:**
```json
{
  "users": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5
}
```

**Доступ:** Только для админов и модераторов

---

### 3. 📊 Аудит действий пользователей

**Эндпоинты:**
- `GET /api/users/{user_id}/audit-log` - История действий конкретного пользователя
- `GET /api/users/audit-log/all` - Все записи аудита с фильтрацией (только админы)

**Фильтры для всех записей:**
- `user_id` - Фильтр по пользователю
- `action` - Фильтр по типу действия
- `date_from` - Дата от (ISO format)
- `date_to` - Дата до (ISO format)
- `page`, `limit` - Пагинация

**Типы действий (AuditAction):**
- `password_change` - Смена пароля
- `role_change` - Изменение роли
- `profile_update` - Обновление профиля
- `email_change` - Изменение email
- `user_created` - Создание пользователя
- `user_deleted` - Удаление пользователя
- `user_activated` - Активация пользователя
- `user_deactivated` - Деактивация пользователя
- `permission_granted` - Выдача разрешения
- `permission_revoked` - Отзыв разрешения
- `session_revoked` - Отзыв сессии
- `login` - Вход в систему
- `logout` - Выход из системы

**Автоматическое логирование:**
- ✅ Регистрация пользователя
- ✅ Вход в систему
- ✅ Выход из системы
- ✅ Смена пароля
- ✅ Обновление профиля
- ✅ Изменение роли (админами)
- ✅ Отзыв сессий

**Модель:**
- `AuditLog` - хранит все действия с деталями, IP, User-Agent и временем

---

## 📝 Структура новых файлов

```
backend/auth/
├── services/
│   ├── session_service.py    # Управление сессиями
│   ├── search_service.py     # Поиск пользователей
│   └── audit_service.py      # Аудит действий
├── routers/
│   └── sessions.py           # Роутер для сессий
└── database/
    ├── models.py             # Обновлены модели (RefreshToken, AuditLog)
    └── schemas.py            # Новые схемы
```

---

## 🚀 Примеры использования

### Управление сессиями

```python
# Получить все сессии
GET /api/auth/sessions

# Переименовать устройство
PUT /api/auth/sessions/1
{
  "device_name": "Мой ноутбук"
}

# Отозвать сессию
DELETE /api/auth/sessions/1

# Отозвать все кроме текущей
POST /api/auth/sessions/revoke-all
```

### Поиск пользователей

```python
# Поиск по email
GET /api/users?search=ivan@example.com

# Фильтр по роли
GET /api/users?role=student&is_active=true

# С пагинацией
GET /api/users?page=2&limit=10&sort=created_at&order=desc
```

### Аудит

```python
# История действий пользователя
GET /api/users/1/audit-log?limit=50

# Все записи с фильтрацией
GET /api/users/audit-log/all?action=password_change&date_from=2024-01-01
```

---

## 🔄 Изменения в существующих эндпоинтах

Все существующие эндпоинты теперь автоматически логируют действия в аудит:
- `POST /api/auth/register` → `user_created`
- `POST /api/auth/login` → `login`
- `POST /api/auth/logout` → `logout`
- `POST /api/auth/change-password` → `password_change`
- `PUT /api/users/me` → `profile_update`
- `PUT /api/users/{id}` → `role_change` или `profile_update`

---

## ✨ Улучшения

1. **Автоматическое обновление last_used_at** при использовании refresh токена
2. **Интеграция аудита** во все критичные операции
3. **Гибкая фильтрация** пользователей с пагинацией
4. **Удобное управление сессиями** с именованием устройств

---

## 📊 Статистика

- **Добавлено эндпоинтов:** 7
- **Новых сервисов:** 3
- **Новых моделей:** 1 (AuditLog)
- **Обновлено моделей:** 1 (RefreshToken)
- **Новых схем:** 6

Все функции готовы к использованию! 🎉

