from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import AnonymousUser

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UpdateUserSerializer
from .auth import check_password, generate_access_token, generate_refresh_token, decode_token
from access_control.permissions import require_auth


class RegisterView(APIView):
    """POST /api/auth/register/ — регистрация нового пользователя."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response({
            'message': 'Регистрация прошла успешно.',
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """POST /api/auth/login/ — вход по email + пароль, возвращает JWT."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Неверный email или пароль.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'detail': 'Аккаунт деактивирован.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'detail': 'Неверный email или пароль.'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = generate_access_token(user.id)
        refresh_token = generate_refresh_token(user.id)

        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': UserSerializer(user).data,
        })


class RefreshView(APIView):
    """POST /api/auth/refresh/ — обновление access-токена через refresh."""

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh-токен обязателен.'}, status=status.HTTP_400_BAD_REQUEST)

        payload = decode_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return Response({'detail': 'Недействительный или истёкший refresh-токен.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_401_UNAUTHORIZED)

        new_access = generate_access_token(user.id)
        return Response({'access': new_access})


class LogoutView(APIView):
    """POST /api/auth/logout/ — выход из системы."""

    @require_auth
    def post(self, request):
        # При использовании stateless JWT logout на сервере — клиент просто
        # удаляет токен. Здесь можно добавить blacklist токенов при необходимости.
        return Response({'message': 'Вы успешно вышли из системы.'})


class ProfileView(APIView):
    """GET/PATCH /api/auth/profile/ — просмотр и обновление профиля."""

    @require_auth
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @require_auth
    def patch(self, request):
        serializer = UpdateUserSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class DeleteAccountView(APIView):
    """DELETE /api/auth/profile/ — мягкое удаление аккаунта."""

    @require_auth
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': 'Аккаунт деактивирован. Вы больше не можете войти в систему.'})
