from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Админка
    path('admin/', admin.site.urls),

    # Главная
    path('', views.index, name='index'),

    # Служебные страницы
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('sitemap/', views.sitemap, name='sitemap'),

    # Каталог: категории и товары
    path('<slug:category_slug>/', views.category_detail, name='category_detail'),
    path(
        '<slug:category_slug>/<slug:product_slug>/',
        views.product_detail,
        name='product_detail',
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.page_not_found'


