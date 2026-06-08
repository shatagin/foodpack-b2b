from django.contrib import admin
from .models import Category, Product, Request, NewsPost, Client, RequestStatus, RequestStatusLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'responsible_manager', 'is_active', 'sort_order')
    list_editable = ('responsible_manager', 'is_active', 'sort_order')
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
    list_display = (
        'id',
        'created_at',
        'request_status',
        'assigned_manager',
        'name',
        'phone',
        'email',
        'category',
        'product',
        'client_inn',
        'client_kpp',
    )
    list_filter = (
        'request_status',
        'assigned_manager',
        'created_at',
        'category',
    )
    search_fields = (
        'name',
        'phone',
        'email',
        'comment',
        'client__company_name',
        'client__contact_person',
        'client__phone',
        'client__email',
        'client__inn',
        'client__kpp',
        'client__address',
    )
    readonly_fields = (
        'created_at',
        'source_url',
        'client_company_name',
        'client_contact_person',
        'client_inn',
        'client_kpp',
        'client_address',
    )
    ordering = ('-created_at',)
    list_select_related = (
        'client',
        'category',
        'product',
        'request_status',
        'assigned_manager',
    )

    fieldsets = (
        ('Заявка', {
            'fields': (
                'request_status',
                'assigned_manager',
                'category',
                'product',
                'comment',
                'source_url',
                'created_at',
            )
        }),
        ('Контактные данные из заявки', {
            'fields': (
                'name',
                'phone',
                'email',
            )
        }),
        ('Данные клиента', {
            'fields': (
                'client',
                'client_company_name',
                'client_contact_person',
                'client_inn',
                'client_kpp',
                'client_address',
            )
        }),
    )

    def client_company_name(self, obj):
        return obj.client.company_name if obj.client else '-'
    client_company_name.short_description = 'Компания клиента'

    def client_contact_person(self, obj):
        return obj.client.contact_person if obj.client else '-'
    client_contact_person.short_description = 'Контактное лицо'

    def client_inn(self, obj):
        return obj.client.inn if obj.client else '-'
    client_inn.short_description = 'ИНН'

    def client_kpp(self, obj):
        return obj.client.kpp if obj.client else '-'
    client_kpp.short_description = 'КПП'

    def client_address(self, obj):
        return obj.client.address if obj.client else '-'
    client_address.short_description = 'Адрес'


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'published_at', 'is_published', 'title')
    list_filter = ('is_published', 'published_at')
    search_fields = ('title', 'excerpt', 'body')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'contact_person',
        'phone',
        'email',
        'inn',
        'kpp',
        'created_at',
    )
    search_fields = (
        'company_name',
        'contact_person',
        'phone',
        'email',
        'inn',
        'kpp',
        'address',
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RequestStatus)
class RequestStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_initial', 'is_final', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')


@admin.register(RequestStatusLog)
class RequestStatusLogAdmin(admin.ModelAdmin):
    list_display = ('request', 'old_status', 'new_status', 'changed_at')
    readonly_fields = ('changed_at',)
