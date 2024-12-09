from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('', views.cart_list, name='cart_list'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('create_order/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>',
         views.OrderDetailView.as_view(),
         name='order_detail'),
    path('orders/<int:pk>/edit/', views.edit_order_status, name='edit_order_status'),
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
]
