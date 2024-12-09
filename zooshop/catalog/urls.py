from django.urls import path
from . import views


app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('reviews/<int:pk>/', views.review_list, name='review_list')
]
