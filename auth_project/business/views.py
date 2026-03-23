"""
Mock-Views для бизнес-объектов приложения.
Реальных таблиц нет — возвращаем тестовые данные.
Демонстрируют работу системы разграничения прав.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from access_control.permissions import require_permission, require_auth

MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Ноутбук Pro 15', 'price': 1299.99, 'owner_id': 'user-1'},
    {'id': 2, 'name': 'Механическая клавиатура', 'price': 149.99, 'owner_id': 'user-2'},
    {'id': 3, 'name': 'Монитор 4K', 'price': 699.99, 'owner_id': 'user-1'},
]

MOCK_SHOPS = [
    {'id': 1, 'name': 'TechStore Центр', 'city': 'Москва'},
    {'id': 2, 'name': 'GadgetWorld', 'city': 'Санкт-Петербург'},
]

MOCK_ORDERS = [
    {'id': 1, 'product_id': 1, 'customer': 'Иванов И.И.', 'status': 'shipped'},
    {'id': 2, 'product_id': 2, 'customer': 'Петров П.П.', 'status': 'pending'},
]


class ProductsView(APIView):
    """GET — список товаров. Требует read_all_permission на 'products'."""

    @require_permission('products', 'read_all_permission')
    def get(self, request):
        return Response({'products': MOCK_PRODUCTS})

    @require_permission('products', 'create_permission')
    def post(self, request):
        # В реальном приложении здесь создавался бы продукт
        return Response({'message': 'Товар создан (mock).', 'data': request.data}, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    """GET/PATCH/DELETE конкретного товара."""

    @require_permission('products', 'read_permission')
    def get(self, request, pk):
        product = next((p for p in MOCK_PRODUCTS if p['id'] == pk), None)
        if not product:
            return Response({'detail': 'Не найдено.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(product)

    @require_permission('products', 'update_all_permission')
    def patch(self, request, pk):
        return Response({'message': f'Товар {pk} обновлён (mock).', 'data': request.data})

    @require_permission('products', 'delete_all_permission')
    def delete(self, request, pk):
        return Response({'message': f'Товар {pk} удалён (mock).'})


class ShopsView(APIView):
    """GET — список магазинов."""

    @require_permission('shops', 'read_all_permission')
    def get(self, request):
        return Response({'shops': MOCK_SHOPS})


class OrdersView(APIView):
    """GET — список заказов."""

    @require_permission('orders', 'read_all_permission')
    def get(self, request):
        return Response({'orders': MOCK_ORDERS})

    @require_permission('orders', 'create_permission')
    def post(self, request):
        return Response({'message': 'Заказ создан (mock).', 'data': request.data}, status=status.HTTP_201_CREATED)


class PublicView(APIView):
    """GET — публичный эндпоинт, не требует аутентификации."""

    def get(self, request):
        return Response({
            'message': 'Добро пожаловать! Это публичный эндпоинт.',
            'authenticated': not hasattr(request.user, 'id') is False,
        })
