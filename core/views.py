from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def index(request):
    return render(request, 'core/index.html')


def about(request):
    return render(request, 'core/about.html')


def contacts(request):
    return render(request, 'core/contacts.html')


def sitemap(request):
    categories = (
        Category.objects
        .filter(is_active=True)
        .prefetch_related('products')
        .order_by('sort_order', 'name')
    )

    static_pages = [
        {'title': 'Главная', 'url': '/'},
        {'title': 'О компании', 'url': '/about/'},
        {'title': 'Контакты', 'url': '/contacts/'},
    ]

    context = {
        'categories': categories,
        'static_pages': static_pages,
    }
    return render(request, 'core/sitemap.html', context)


def category_detail(request, category_slug: str):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_active=True,
    )
    products = category.products.filter(is_active=True)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'core/category_detail.html', context)


def product_detail(request, category_slug: str, product_slug: str):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_active=True,
    )
    product = get_object_or_404(
        Product,
        category=category,
        slug=product_slug,
        is_active=True,
    )

    context = {
        'category': category,
        'product': product,
    }
    return render(request, 'core/product_detail.html', context)


def page_not_found(request, exception):
    return render(request, 'core/404.html', status=404)
