"""
Система разграничения прав доступа (RBAC — Role-Based Access Control).

Схема БД:
  roles              — роли: admin, manager, user, guest
  business_elements  — объекты приложения: users, products, shops, orders, access_rules
  access_roles_rules — правила: что роль может делать с объектом
  user_roles         — связь пользователь ↔ роль (M2M через явную таблицу)
"""
import uuid
from django.db import models
from users.models import User


class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'
    GUEST = 'guest'

    ROLE_CHOICES = [
        (ADMIN, 'Администратор'),
        (MANAGER, 'Менеджер'),
        (USER, 'Пользователь'),
        (GUEST, 'Гость'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    """Объекты бизнес-приложения, к которым применяется контроль доступа."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'business_elements'

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    """
    Правила доступа: роль → объект → набор разрешений.

    *_permission    — разрешение на действие со своими объектами (owner == user)
    *_all_permission — разрешение на действие со всеми объектами
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='rules')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='rules')

    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        db_table = 'access_roles_rules'
        unique_together = ('role', 'element')

    def __str__(self):
        return f'{self.role.name} → {self.element.name}'


class UserRole(models.Model):
    """Связь пользователь ↔ роль."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')

    def __str__(self):
        return f'{self.user.email} → {self.role.name}'
