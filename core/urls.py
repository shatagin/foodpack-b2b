from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Главная
    path('', views.index, name='index'),

    # Служебные страницы
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),

    # Каталог: категории и товары
    path('<slug:category_slug>/', views.category_detail, name='category_detail'),
    path(
        '<slug:category_slug>/<slug:product_slug>/',
        views.product_detail,
        name='product_detail',
    ),
]