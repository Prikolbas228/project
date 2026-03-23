from rest_framework import serializers
from .models import Role, BusinessElement, AccessRoleRule, UserRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = ['id', 'name', 'description']


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    element_name = serializers.ReadOnlyField(source='element.name')

    class Meta:
        model = AccessRoleRule
        fields = [
            'id', 'role', 'role_name', 'element', 'element_name',
            'read_permission', 'read_all_permission',
            'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission',
        ]


class UserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_email', 'role', 'role_name', 'assigned_at']
