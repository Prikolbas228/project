"""
Кастомный Middleware: до обработки любого запроса определяем пользователя
из JWT-токена в заголовке Authorization: Bearer <token>
и присваиваем его request.user.
"""
from django.contrib.auth.models import AnonymousUser
from .auth import decode_token


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = AnonymousUser()
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            payload = decode_token(token)

            if payload and payload.get('type') == 'access':
                from users.models import User
                try:
                    user = User.objects.get(id=payload['user_id'], is_active=True)
                    request.user = user
                except User.DoesNotExist:
                    pass

        response = self.get_response(request)
        return response
