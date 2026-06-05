from django.contrib import admin
from .models import Category, Product, Request, NewsPost, Client, RequestStatus, RequestStatusLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_display = ('name', 'slug', 'responsible_manager', 'is_active', 'sort_order')
    list_editable = ('responsible_manager', 'is_active', 'sort_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active', 'sort_order')
    list_filter = ('category', 'is_active')
    list_editable = ('is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'lead')


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'status', 'name', 'phone', 'email', 'category', 'product')
    list_filter = ('status', 'created_at', 'category')
    search_fields = ('name', 'phone', 'email', 'comment')
    readonly_fields = ('created_at', 'source_url')
    ordering = ('-created_at',)
    list_display = (
        'id', 'created_at', 'request_status', 'assigned_manager',
        'name', 'phone', 'email', 'category', 'product'
    )
    list_filter = ('request_status', 'assigned_manager', 'created_at', 'category')


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'published_at', 'is_published', 'title')
    list_filter = ('is_published', 'published_at')
    search_fields = ('title', 'excerpt', 'body')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'phone', 'email', 'created_at')
    search_fields = ('company_name', 'contact_person', 'phone', 'email', 'inn')


@admin.register(RequestStatus)
class RequestStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_initial', 'is_final', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')


@admin.register(RequestStatusLog)
class RequestStatusLogAdmin(admin.ModelAdmin):
    list_display = ('request', 'old_status', 'new_status', 'changed_at')
    readonly_fields = ('changed_at',)
