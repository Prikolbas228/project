"""
Декораторы и утилиты для проверки прав доступа.
Используются во views вместо DRF permission_classes.
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import AnonymousUser

from .models import UserRole, AccessRoleRule, BusinessElement


def require_auth(func):
    """Декоратор: пользователь должен быть аутентифицирован (401 иначе)."""
    @wraps(func)
    def wrapper(view_or_self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser) or not request.user.is_active:
            return Response(
                {'detail': 'Аутентификация не выполнена. Предоставьте действующий токен.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return func(view_or_self, request, *args, **kwargs)
    return wrapper


def get_user_roles(user):
    """Возвращает список названий ролей пользователя."""
    return list(
        UserRole.objects.filter(user=user).values_list('role__name', flat=True)
    )


def has_permission(user, element_name: str, permission: str) -> bool:
    """
    Проверяет, есть ли у пользователя указанное разрешение на объект.

    element_name: имя объекта (например, 'products')
    permission: одно из полей AccessRoleRule (например, 'read_permission')
    """
    if isinstance(user, AnonymousUser):
        return False

    roles = UserRole.objects.filter(user=user).values_list('role', flat=True)
    if not roles:
        return False

    try:
        element = BusinessElement.objects.get(name=element_name)
    except BusinessElement.DoesNotExist:
        return False

    rules = AccessRoleRule.objects.filter(role__in=roles, element=element)
    for rule in rules:
        if getattr(rule, permission, False):
            return True
    return False


def require_permission(element_name: str, permission: str):
    """
    Декоратор-фабрика для проверки конкретного разрешения.
    401 — не аутентифицирован, 403 — нет доступа.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(view_or_self, request, *args, **kwargs):
            if isinstance(request.user, AnonymousUser):
                return Response(
                    {'detail': 'Аутентификация не выполнена.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if not has_permission(request.user, element_name, permission):
                return Response(
                    {'detail': f'Доступ запрещён. Требуется разрешение: {permission} на {element_name}.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            return func(view_or_self, request, *args, **kwargs)
        return wrapper
    return decorator


def require_admin(func):
    """Декоратор: только пользователи с ролью admin."""
    @wraps(func)
    def wrapper(view_or_self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return Response({'detail': 'Аутентификация не выполнена.'}, status=status.HTTP_401_UNAUTHORIZED)
        roles = get_user_roles(request.user)
        if 'admin' not in roles:
            return Response(
                {'detail': 'Доступ запрещён. Требуется роль администратора.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return func(view_or_self, request, *args, **kwargs)
    return wrapper
