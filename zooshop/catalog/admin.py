from django.contrib import admin
from .models import Client, Employee, Product, Review, Client_order, Client_order_position
from django.db import connection


class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'phone',
        'address'
    )
    list_editable = (
        'phone',
        'address'
    )
    search_fields = ('first_name', 'last_name', )
    list_display_links = ('id',)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'position',
        'salary'
    )
    list_editable = (
        'position',
        'salary'
    )
    search_fields = ('first_name', 'last_name', )
    list_display_links = ('id',)


class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    inlines = (
        ReviewInline,
    )
    list_display = (
        'id',
        'name',
        'description',
        'category',
        'price',
        'available_number'
    )
    list_editable = (
        'description',
        'category',
        'price'
    )
    list_filter = ('category',)
    search_fields = ('name',)
    list_display_links = ('id',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'text',
        'rating'
    )
    list_editable = (
        'text',
        'rating'
    )
    list_filter = ('rating',)
    list_display_links = ('id',)
    empty_value_display = 'Нет текста отзыва'


class Client_orderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'date',
        'status',
        'price',
        'client',
        'employee'
    )
    list_editable = (
        'status',
        'price'
    )
    search_fields = ('client__first_name', 'client__last_name', )
    list_display_links = ('id',)


class Client_order_positionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'position_number',
        'product',
        'client_order'
    )
    list_editable = (
        'position_number',
    )
    search_fields = ('client_order', )
    list_display_links = ('id',)


admin.site.register(Client, ClientAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Client_order, Client_orderAdmin)
admin.site.register(Client_order_position, Client_order_positionAdmin)
