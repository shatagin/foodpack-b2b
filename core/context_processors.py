from .models import Category


def catalog_categories(request):
    return {
        'menu_categories': Category.objects.filter(is_active=True).order_by('sort_order', 'name')
    }

