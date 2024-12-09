from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from catalog.models import Client_order, Client_order_position, Product, Client, Employee
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from catalog.forms import OrderStatusChangeForm, OrderSortForm, ReviewForm
from random import choice
from django.db import connection


def update_order_status(order_id, status):
    with connection.cursor() as cursor:
        cursor.callproc('UpdateOrderStatus', [order_id, status])


def edit_order_status(request, pk):
    order = get_object_or_404(Client_order, pk=pk)

    if request.method == 'POST':
        form = OrderStatusChangeForm(request.POST, instance=order)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            with connection.cursor() as cursor:
                cursor.callproc('UpdateOrderStatus', [pk, new_status])
            return redirect('cart:order_list')
    else:
        form = OrderStatusChangeForm(instance=order)

    return render(request, 'cart/edit_order_status.html', {'form': form, 'order': order})


@login_required
def order_list(request):
    user = request.user
    if user.is_staff:
        orders = Client_order.objects.filter(employee__user=user)
    else:
        orders = Client_order.objects.filter(client__user=user)
    form = OrderSortForm(request.GET)
    if form.is_valid():
        sort_by_date = form.cleaned_data.get('sort_by_date')
        sort_by_status = form.cleaned_data.get('sort_by_status')
        if sort_by_date == 'date_asc':
            orders = orders.order_by('date')
        elif sort_by_date == 'date_desc':
            orders = orders.order_by('-date')
        if sort_by_status == 'accepted':
            orders = orders.filter(status='accepted')
        elif sort_by_status == 'gathered':
            orders = orders.filter(status='gathered')
        elif sort_by_status == 'delivered':
            orders = orders.filter(status='delivered')
        elif sort_by_status == 'issued':
            orders = orders.filter(status='issued')
    context = {'page_obj': orders, 'form': form}
    return render(request, 'cart/order_list.html', context)


class OrderDetailView(DetailView):
    model = Client_order
    template_name = 'cart/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_positions = Client_order_position.objects.select_related('product').filter(client_order=self.object)
        context['object'] = self.object
        context['client_order_positions'] = order_positions

        if self.object.status == 'issued':
            context['form'] = ReviewForm()

        return context
    
    def post(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status == 'issued':
            form = ReviewForm(request.POST)
            if form.is_valid():
                product_id = request.POST.get('product_id')
                product = get_object_or_404(Product, pk=product_id)
                review = form.save(commit=False)
                review.product = product
                review.save()
                return redirect('cart:order_detail', pk=order.pk)

        return super().post(request, *args, **kwargs)


def get_discount(client_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT online_shop.get_discount(%s)", (client_id,))
        result = cursor.fetchone()
    return result[0]


@login_required
def cart_list(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'cart/cart_list.html', {'cart': cart, 'total_price': total_price})


@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart = request.session.get('cart', {})
    discount = get_discount(Client.objects.get(user=request.user).id)
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {'name': product.name,
                                 'price': product.price - product.price * discount / 100,
                                 'quantity': 1}
    request.session['cart'] = cart
    return redirect('cart:cart_list')


@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('cart:cart_list')


@login_required
def create_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart:cart_list')

    client = Client.objects.get(user=request.user.id)
    employees = Employee.objects.all()
    random_employee = choice(employees)
    order = Client_order.objects.create(
        date=timezone.now(),
        status='accepted',
        price=sum(item['price'] * item['quantity'] for item in cart.values()),
        client=client,
        employee=random_employee
    )

    for product_id, item in cart.items():
        Client_order_position.objects.create(
            client_order=order,
            product_id=product_id,
            position_number=item['quantity']
        )

    request.session['cart'] = {}
    return redirect('cart:order_detail', pk=order.pk)

@login_required
def increase_quantity(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart = request.session.get('cart', {})
    if str(product_id) in cart and cart[str(product_id)]['quantity'] < product.available_number:
        cart[str(product_id)]['quantity'] += 1
    request.session['cart'] = cart
    return redirect('cart:cart_list')


@login_required
def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] -= 1
        if cart[str(product_id)]['quantity'] <= 0:
            del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('cart:cart_list')
