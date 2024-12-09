from .models import Product, ProductWithReviews
from .forms import ProductSortForm
from django.views.generic import DetailView
from django.shortcuts import render


def product_list(request):
    products = Product.objects.all()
    form = ProductSortForm(request.GET)
    if form.is_valid():
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    context = {'form': form,
               'page_obj': products}
    return render(request, 'catalog/product_list.html', context)


def review_list(request, pk):
    reviews = ProductWithReviews.objects.filter(id=pk)
    product = Product.objects.get(id=pk)
    context = {'reviews': reviews, 'price': product.price, 'description': product.description, 'name': product.name}
    return render(request, 'catalog/review_list.html', context)


class ProductDetailView(DetailView):
    model = Product
