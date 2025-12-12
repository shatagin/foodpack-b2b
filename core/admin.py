from django.contrib import admin
from .models import Category, Product, Request


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


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
