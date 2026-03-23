from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Role, BusinessElement, AccessRoleRule, UserRole
from .serializers import (
    RoleSerializer, BusinessElementSerializer,
    AccessRoleRuleSerializer, UserRoleSerializer
)
from .permissions import require_admin, require_auth, get_user_roles


class RolesView(APIView):
    """GET /api/access/roles/ — список ролей (только admin)."""

    @require_admin
    def get(self, request):
        roles = Role.objects.all()
        return Response(RoleSerializer(roles, many=True).data)

    @require_admin
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BusinessElementsView(APIView):
    """GET/POST /api/access/elements/ — объекты приложения (только admin)."""

    @require_admin
    def get(self, request):
        elements = BusinessElement.objects.all()
        return Response(BusinessElementSerializer(elements, many=True).data)

    @require_admin
    def post(self, request):
        serializer = BusinessElementSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccessRulesView(APIView):
    """GET/POST /api/access/rules/ — правила доступа (только admin)."""

    @require_admin
    def get(self, request):
        rules = AccessRoleRule.objects.select_related('role', 'element').all()
        return Response(AccessRoleRuleSerializer(rules, many=True).data)

    @require_admin
    def post(self, request):
        serializer = AccessRoleRuleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccessRuleDetailView(APIView):
    """GET/PATCH/DELETE /api/access/rules/<id>/ — управление конкретным правилом (admin)."""

    def get_object(self, pk):
        try:
            return AccessRoleRule.objects.select_related('role', 'element').get(pk=pk)
        except AccessRoleRule.DoesNotExist:
            return None

    @require_admin
    def get(self, request, pk):
        rule = self.get_object(pk)
        if not rule:
            return Response({'detail': 'Не найдено.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AccessRoleRuleSerializer(rule).data)

    @require_admin
    def patch(self, request, pk):
        rule = self.get_object(pk)
        if not rule:
            return Response({'detail': 'Не найдено.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AccessRoleRuleSerializer(rule, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    @require_admin
    def delete(self, request, pk):
        rule = self.get_object(pk)
        if not rule:
            return Response({'detail': 'Не найдено.'}, status=status.HTTP_404_NOT_FOUND)
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRolesView(APIView):
    """GET/POST /api/access/user-roles/ — назначение ролей пользователям (admin)."""

    @require_admin
    def get(self, request):
        user_roles = UserRole.objects.select_related('user', 'role').all()
        return Response(UserRoleSerializer(user_roles, many=True).data)

    @require_admin
    def post(self, request):
        serializer = UserRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyPermissionsView(APIView):
    """GET /api/access/my-permissions/ — мои роли и права (любой авторизованный)."""

    @require_auth
    def get(self, request):
        user = request.user
        roles = get_user_roles(user)
        user_role_objs = UserRole.objects.filter(user=user).values_list('role', flat=True)
        rules = AccessRoleRule.objects.filter(role__in=user_role_objs).select_related('role', 'element')
        return Response({
            'user': user.email,
            'roles': roles,
            'permissions': AccessRoleRuleSerializer(rules, many=True).data,
        })
