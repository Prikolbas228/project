from django.urls import path
from .views import (
    RolesView, BusinessElementsView,
    AccessRulesView, AccessRuleDetailView,
    UserRolesView, MyPermissionsView,
)

urlpatterns = [
    path('roles/', RolesView.as_view(), name='roles'),
    path('elements/', BusinessElementsView.as_view(), name='elements'),
    path('rules/', AccessRulesView.as_view(), name='rules'),
    path('rules/<uuid:pk>/', AccessRuleDetailView.as_view(), name='rule-detail'),
    path('user-roles/', UserRolesView.as_view(), name='user-roles'),
    path('my-permissions/', MyPermissionsView.as_view(), name='my-permissions'),
]
