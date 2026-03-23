"""
Команда для заполнения БД тестовыми данными.
Запуск: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from users.models import User
from users.auth import hash_password
from access_control.models import Role, BusinessElement, AccessRoleRule, UserRole


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными (роли, объекты, правила, пользователи)'

    def handle(self, *args, **options):
        self.stdout.write('📦 Создаём роли...')
        roles = {}
        for name, desc in [
            ('admin', 'Полный доступ ко всем ресурсам'),
            ('manager', 'Управление товарами и заказами'),
            ('user', 'Доступ к своим данным и просмотр каталога'),
            ('guest', 'Только чтение публичных данных'),
        ]:
            role, _ = Role.objects.get_or_create(name=name, defaults={'description': desc})
            roles[name] = role
        self.stdout.write(self.style.SUCCESS('  ✓ Роли созданы'))

        self.stdout.write('📦 Создаём бизнес-объекты...')
        elements = {}
        for name, desc in [
            ('users', 'Управление пользователями'),
            ('products', 'Товары магазина'),
            ('shops', 'Магазины'),
            ('orders', 'Заказы'),
            ('access_rules', 'Правила доступа'),
        ]:
            el, _ = BusinessElement.objects.get_or_create(name=name, defaults={'description': desc})
            elements[name] = el
        self.stdout.write(self.style.SUCCESS('  ✓ Бизнес-объекты созданы'))

        self.stdout.write('📦 Создаём правила доступа...')
        rules_data = [
            # (role, element, read, read_all, create, update, update_all, delete, delete_all)
            ('admin',   'users',        True, True, True, True, True, True, True),
            ('admin',   'products',     True, True, True, True, True, True, True),
            ('admin',   'shops',        True, True, True, True, True, True, True),
            ('admin',   'orders',       True, True, True, True, True, True, True),
            ('admin',   'access_rules', True, True, True, True, True, True, True),

            ('manager', 'products',     True, True, True, True, True, True, False),
            ('manager', 'shops',        True, True, False, True, False, False, False),
            ('manager', 'orders',       True, True, True, True, True, False, False),
            ('manager', 'users',        True, True, False, False, False, False, False),

            ('user',    'products',     True, True, False, True, False, False, False),
            ('user',    'orders',       True, False, True, True, False, False, False),
            ('user',    'shops',        True, True, False, False, False, False, False),

            ('guest',   'products',     True, True, False, False, False, False, False),
            ('guest',   'shops',        True, True, False, False, False, False, False),
        ]

        for (role_name, el_name, r, ra, c, u, ua, d, da) in rules_data:
            AccessRoleRule.objects.update_or_create(
                role=roles[role_name],
                element=elements[el_name],
                defaults=dict(
                    read_permission=r, read_all_permission=ra,
                    create_permission=c,
                    update_permission=u, update_all_permission=ua,
                    delete_permission=d, delete_all_permission=da,
                )
            )
        self.stdout.write(self.style.SUCCESS('  ✓ Правила доступа созданы'))

        self.stdout.write('👤 Создаём тестовых пользователей...')
        test_users = [
            ('admin@example.com',   'Admin',   'Admin',   '', 'adminpass123',  'admin'),
            ('manager@example.com', 'Иван',    'Петров',  'Сергеевич', 'managerpass123', 'manager'),
            ('user@example.com',    'Мария',   'Иванова', 'Олеговна',  'userpass123',    'user'),
            ('guest@example.com',   'Алексей', 'Гостев',  '',          'guestpass123',   'guest'),
        ]

        for email, first, last, pat, pwd, role_name in test_users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'patronymic': pat,
                    'is_active': True,
                    'password': hash_password(pwd),
                }
            )
            UserRole.objects.get_or_create(user=user, role=roles[role_name])
            status_str = 'создан' if created else 'уже существует'
            self.stdout.write(f'  • {email} [{role_name}] — {status_str}')

        self.stdout.write(self.style.SUCCESS('\n✅ Тестовые данные успешно загружены!'))
        self.stdout.write('\nТестовые аккаунты:')
        self.stdout.write('  admin@example.com   / adminpass123   (роль: admin)')
        self.stdout.write('  manager@example.com / managerpass123 (роль: manager)')
        self.stdout.write('  user@example.com    / userpass123    (роль: user)')
        self.stdout.write('  guest@example.com   / guestpass123   (роль: guest)')
