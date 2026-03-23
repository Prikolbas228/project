# Auth System — Тестовое задание

Backend-приложение на **Django REST Framework** с собственной системой аутентификации и авторизации.

---

## Быстрый старт

```bash
pip install django djangorestframework bcrypt PyJWT

python manage.py migrate
python manage.py seed_data   # заполнить БД тестовыми данными
python manage.py runserver
```

> По умолчанию используется **SQLite**. Для PostgreSQL — см. `config/settings.py`, раздел `DATABASES`.

---

## Тестовые аккаунты

| Email | Пароль | Роль |
|---|---|---|
| admin@example.com | adminpass123 | admin |
| manager@example.com | managerpass123 | manager |
| user@example.com | userpass123 | user |
| guest@example.com | guestpass123 | guest |

---

## API Endpoints

### Аутентификация (`/api/auth/`)

| Метод | URL | Описание |
|---|---|---|
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/login/` | Логин → JWT токены |
| POST | `/api/auth/logout/` | Логаут (требует Bearer токен) |
| POST | `/api/auth/refresh/` | Обновить access-токен |
| GET | `/api/auth/profile/` | Мой профиль |
| PATCH | `/api/auth/profile/` | Обновить профиль |
| DELETE | `/api/auth/profile/delete/` | Мягкое удаление аккаунта |

### Управление доступом (`/api/access/`) — только для admin

| Метод | URL | Описание |
|---|---|---|
| GET/POST | `/api/access/roles/` | Роли |
| GET/POST | `/api/access/elements/` | Бизнес-объекты |
| GET/POST | `/api/access/rules/` | Правила доступа |
| GET/PATCH/DELETE | `/api/access/rules/<id>/` | Конкретное правило |
| GET/POST | `/api/access/user-roles/` | Назначение ролей |
| GET | `/api/access/my-permissions/` | Мои разрешения (для всех) |

### Бизнес-объекты (`/api/business/`)

| Метод | URL | Требуемое разрешение |
|---|---|---|
| GET | `/api/business/public/` | — |
| GET | `/api/business/products/` | products.read_all_permission |
| POST | `/api/business/products/` | products.create_permission |
| GET | `/api/business/products/<id>/` | products.read_permission |
| PATCH | `/api/business/products/<id>/` | products.update_all_permission |
| DELETE | `/api/business/products/<id>/` | products.delete_all_permission |
| GET | `/api/business/shops/` | shops.read_all_permission |
| GET | `/api/business/orders/` | orders.read_all_permission |
| POST | `/api/business/orders/` | orders.create_permission |

---

## Схема БД

```
users                  — пользователи (email, пароль bcrypt, is_active)
sessions               — (опционально) серверные сессии с cookie/sessionid

roles                  — роли: admin, manager, user, guest
business_elements      — объекты: users, products, shops, orders, access_rules
access_roles_rules     — правила: role_id + element_id + 7 bool-разрешений
user_roles             — M2M: user ↔ role
```

### Таблица `access_roles_rules`

```
role_id                FK → roles
element_id             FK → business_elements
read_permission        bool  — читать свои объекты
read_all_permission    bool  — читать все объекты
create_permission      bool  — создавать
update_permission      bool  — редактировать свои объекты
update_all_permission  bool  — редактировать все
delete_permission      bool  — удалять свои
delete_all_permission  bool  — удалять все
```

**Принцип**: `*_permission` — действие только над своими объектами (owner == user.id),  
`*_all_permission` — над всеми объектами системы.

---

## Как работает аутентификация

1. Пользователь отправляет `POST /api/auth/login/` → email + пароль
2. Сервер проверяет пароль через **bcrypt**
3. Генерируются два **JWT**-токена (`HS256`):
   - `access` — живёт 1 час
   - `refresh` — живёт 7 дней
4. При каждом запросе `JWTAuthMiddleware` читает заголовок `Authorization: Bearer <token>`, декодирует JWT и присваивает `request.user`
5. Если токен отсутствует или невалиден → `request.user = AnonymousUser`

### Коды ошибок
- `401 Unauthorized` — пользователь не аутентифицирован
- `403 Forbidden` — пользователь аутентифицирован, но нет прав

---

## Пример использования

```bash
# Логин
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"userpass123"}'

# Запрос с токеном
curl http://localhost:8000/api/business/products/ \
  -H "Authorization: Bearer <ваш_access_token>"

# Обновление токена
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<ваш_refresh_token>"}'
```
