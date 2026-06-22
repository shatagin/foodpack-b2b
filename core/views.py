from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from .forms import RequestForm
from .models import Category, Client, NewsPost, Product, Request, RequestStatus, RequestStatusLog

from django.db import transaction
from .services import send_preliminary_offer


REQUEST_SUCCESS_MESSAGE = 'Заявка успешно отправлена. Менеджер свяжется с вами в ближайшее время.'
REQUEST_ERROR_MESSAGE = 'Проверьте корректность заполнения формы.'


def is_ajax_request(request):
    return (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('accept', '')
    )


def serialize_form_errors(form):
    return {
        field: [str(error) for error in errors]
        for field, errors in form.errors.items()
    }


def request_form_error_response(form):
    return JsonResponse(
        {
            'ok': False,
            'message': REQUEST_ERROR_MESSAGE,
            'errors': serialize_form_errors(form),
        },
        status=422,
    )


def request_form_success_response(obj=None):
    data = {
        'ok': True,
        'message': REQUEST_SUCCESS_MESSAGE,
    }

    if obj is not None:
        data['request_id'] = obj.id

    return JsonResponse(data)


def process_request_form(request, success_url, category=None, product=None):
    form = RequestForm(request.POST)

    if form.is_valid():
        if form.cleaned_data.get('middle_name'):
            if is_ajax_request(request):
                return form, request_form_success_response()

            add_request_success_message(request)
            return form, redirect(success_url)

        selected_category = form.cleaned_data.get('category') or category

        obj = create_request_from_form(
            form,
            request,
            category=selected_category,
            product=product,
        )

        transaction.on_commit(
            lambda request_id=obj.id: send_preliminary_offer(request_id)
        )

        if is_ajax_request(request):
            return form, request_form_success_response(obj)

        add_request_success_message(request)
        return form, redirect(success_url)

    if is_ajax_request(request):
        return form, request_form_error_response(form)

    return form, None


def add_request_success_message(request):
    messages.success(request, REQUEST_SUCCESS_MESSAGE)


def index(request):
    if request.method == 'POST':
        form, response = process_request_form(request, '/#request')
        if response:
            return response
    else:
        form = RequestForm()

    return render(request, 'core/index.html', {'form': form})


def about(request):
    if request.method == 'POST':
        form, response = process_request_form(request, '/about/#request')
        if response:
            return response
    else:
        form = RequestForm()

    return render(request, 'core/about.html', {'form': form})


def contacts(request):
    if request.method == 'POST':
        form, response = process_request_form(request, '/contacts/#request')
        if response:
            return response
    else:
        form = RequestForm()

    return render(request, 'core/contacts.html', {'form': form})


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
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = category.products.filter(is_active=True).order_by('sort_order', 'name')

    if request.method == 'POST':
        form, response = process_request_form(
            request,
            category.get_absolute_url(),
            category=category,
        )
        if response:
            return response
    else:
        form = RequestForm(initial={'category': category.pk})

    context = {
        'category': category,
        'products': products,
        'form': form,
    }
    return render(request, 'core/category_detail.html', context)


def product_detail(request, category_slug: str, product_slug: str):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    product = get_object_or_404(Product, category=category, slug=product_slug, is_active=True)

    if request.method == 'POST':
        form, response = process_request_form(
            request,
            product.get_absolute_url(),
            category=category,
            product=product,
        )
        if response:
            return response
    else:
        form = RequestForm(initial={'category': category.pk})

    context = {
        'category': category,
        'product': product,
        'form': form,
    }
    return render(request, 'core/product_detail.html', context)


def page_not_found(request, exception):
    return render(request, 'core/404.html', status=404)


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

    category_name = category.name.lower().replace('ё', 'е')

    if 'комус' in category_name:
        return 'sales-manager-komus'
    if 'перчат' in category_name:
        return 'sales-manager-gloves'
    if 'плен' in category_name:
        return 'sales-manager-film'

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


def create_request_from_form(form, request, category=None, product=None):
    data = form.cleaned_data

    selected_category = data.get('category') or category
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
            'company_name',
            'contact_person',
            'email',
            'inn',
            'kpp',
            'address',
            'updated_at',
        ])

    request_status = RequestStatus.objects.filter(code='new', is_active=True).first()

    if request_status is None:
        request_status = RequestStatus.objects.filter(is_initial=True, is_active=True).first()

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
