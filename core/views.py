from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, NewsPost, Request, Client, RequestStatus, RequestStatusLog
from .forms import RequestForm
from django.db.models import Q
from django.contrib.auth import get_user_model


def index(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            obj = create_request_from_form(form, request)
            obj.source_url = request.build_absolute_uri()
            obj.save()
            return redirect('/#request')
    else:
        form = RequestForm()

    return render(request, 'core/index.html', {'form': form})


def about(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            obj = create_request_from_form(form, request)
            obj.source_url = request.build_absolute_uri()
            obj.save()
            return redirect('/about/#request')
    else:
        form = RequestForm()

    return render(request, 'core/about.html', {'form': form})


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

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            obj = create_request_from_form(form, request, category=category)
            obj.category = category
            obj.product = product
            obj.source_url = request.build_absolute_uri()
            obj.save()
            return redirect(category.get_absolute_url())
    else:
        form = RequestForm()

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'core/category_detail.html', context)


def product_detail(request, category_slug: str, product_slug: str):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    product = get_object_or_404(Product, category=category, slug=product_slug, is_active=True)

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            obj = create_request_from_form(form, request, category=category, product=product)
            obj.category = category
            obj.product = product
            obj.source_url = request.build_absolute_uri()
            obj.save()
            return redirect(product.get_absolute_url())
    else:
        form = RequestForm()

    context = {
        'category': category,
        'product': product,
        'form': form,
    }
    return render(request, 'core/product_detail.html', context)


def page_not_found(request, exception):
    return render(request, 'core/404.html', status=404)


def category_detail(request, category_slug: str):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = category.products.filter(is_active=True)

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            obj = create_request_from_form(form, request)
            obj.category = category
            obj.source_url = request.build_absolute_uri()
            obj.save()
            return redirect(category.get_absolute_url())
    else:
        form = RequestForm()

    context = {
        'category': category,
        'products': products,
        'form': form,
    }
    return render(request, 'core/category_detail.html', context)


def news_list(request):
    posts = NewsPost.objects.filter(is_published=True)
    return render(request, 'core/news_list.html', {'posts': posts})


def news_detail(request, slug: str):
    post = get_object_or_404(NewsPost, slug=slug, is_published=True)
    return render(request, 'core/news_detail.html', {'post': post})


def search(request):
    q = (request.GET.get('q') or '').strip()

    products = Product.objects.none()
    news = NewsPost.objects.none()

    if q:
        products = (
            Product.objects
            .filter(is_active=True)
            .filter(
                Q(name__icontains=q) |
                Q(lead__icontains=q) |
                Q(description__icontains=q)
            )
            .select_related('category')
            .order_by('name')
        )

        news = (
            NewsPost.objects
            .filter(is_published=True)
            .filter(
                Q(title__icontains=q) |
                Q(excerpt__icontains=q) |
                Q(body__icontains=q)
            )
            .order_by('-published_at')
        )

    context = {
        'q': q,
        'products': products,
        'news': news,
    }
    return render(request, 'core/search.html', context)


def get_manager_group_for_category(category):
    if not category:
        return 'sales-manager'

    category_text = f'{category.slug} {category.name}'.lower()

    if 'komus' in category_text or 'комус' in category_text:
        return 'sales-manager-komus'

    if 'film' in category_text or 'плен' in category_text:
        return 'sales-manager-film'

    if 'glove' in category_text or 'перчат' in category_text:
        return 'sales-manager-gloves'

    return 'sales-manager'


def get_assigned_manager_for_category(category):
    group_name = get_manager_group_for_category(category)
    User = get_user_model()

    manager = (
        User.objects
        .filter(is_active=True, groups__name=group_name)
        .order_by('id')
        .first()
    )

    if manager:
        return manager

    if category and category.responsible_manager:
        return category.responsible_manager

    return (
        User.objects
        .filter(is_active=True, groups__name='sales-manager')
        .order_by('id')
        .first()
    )

def get_assigned_manager_for_category(category):
    group_name = get_manager_group_for_category(category)
    User = get_user_model()

    manager = (
        User.objects
        .filter(is_active=True, groups__name=group_name)
        .order_by('id')
        .first()
    )

    if manager:
        return manager

    if category and category.responsible_manager:
        return category.responsible_manager

    return (
        User.objects
        .filter(is_active=True, groups__name='sales-manager')
        .order_by('id')
        .first()
    )


def create_request_from_form(form, request, category=None, product=None):
    data = form.cleaned_data

    selected_category = category or (product.category if product else data.get('category'))
    assigned_manager = get_assigned_manager_for_category(selected_category)

    client, created = Client.objects.get_or_create(
        phone=data['phone'],
        defaults={
            'company_name': data['company_name'],
            'contact_person': data.get('contact_person', ''),
            'email': data.get('email', ''),
            'inn': data.get('inn', ''),
            'kpp': data.get('kpp', ''),
            'address': data.get('address', ''),
            'comment': data.get('comment', ''),
            'source': 'site',
        }
    )

    if not created:
        client.company_name = data['company_name']
        client.contact_person = data.get('contact_person', '')
        client.email = data.get('email', '')
        client.inn = data.get('inn', '')
        client.kpp = data.get('kpp', '')
        client.address = data.get('address', '')
        client.save(update_fields=[
            'company_name', 'contact_person', 'email',
            'inn', 'kpp', 'address', 'updated_at'
        ])

    request_status = RequestStatus.objects.filter(code='new', is_active=True).first()

    obj = Request.objects.create(
        client=client,
        request_status=request_status,
        assigned_manager=assigned_manager,
        name=data['company_name'],
        phone=data['phone'],
        email=data.get('email', ''),
        comment=data.get('comment', ''),
        category=selected_category,
        product=product,
        source_url=request.build_absolute_uri(),
    )

    if request_status:
        RequestStatusLog.objects.create(
            request=obj,
            old_status=None,
            new_status=request_status,
            comment='Заявка создана через форму сайта',
        )

    return obj
