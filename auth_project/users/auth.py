"""
Утилиты аутентификации: хеширование паролей (bcrypt) и JWT-токены.
Намеренно НЕ используем встроенные механизмы DRF — всё реализовано вручную.
"""
import jwt
import bcrypt
from datetime import datetime, timezone
from django.conf import settings


def hash_password(raw_password: str) -> str:
    """Хешируем пароль через bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(raw_password: str, hashed: str) -> bool:
    """Проверяем пароль против bcrypt-хеша."""
    return bcrypt.checkpw(raw_password.encode('utf-8'), hashed.encode('utf-8'))


def generate_access_token(user_id: str) -> str:
    """Создаём JWT access-токен с user_id в payload."""
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': str(user_id),
        'iat': now,
        'exp': now + settings.JWT_ACCESS_TOKEN_LIFETIME,
        'type': 'access',
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def generate_refresh_token(user_id: str) -> str:
    """Создаём JWT refresh-токен."""
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': str(user_id),
        'iat': now,
        'exp': now + settings.JWT_REFRESH_TOKEN_LIFETIME,
        'type': 'refresh',
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Декодируем JWT. Возвращаем payload или None при ошибке."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
