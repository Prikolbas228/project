from django.urls import path
from .views import ProductsView, ProductDetailView, ShopsView, OrdersView, PublicView

urlpatterns = [
    path('public/', PublicView.as_view(), name='public'),
    path('products/', ProductsView.as_view(), name='products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('shops/', ShopsView.as_view(), name='shops'),
    path('orders/', OrdersView.as_view(), name='orders'),
]
