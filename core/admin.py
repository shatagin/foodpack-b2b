from django.contrib import admin

from .models import (
    Category,
    Product,
    Request,
    NewsPost,
    Client,
    RequestStatus,
    RequestStatusLog,
)


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


class RequestStatusLogInline(admin.TabularInline):
    model = RequestStatusLog
    extra = 0
    can_delete = False
    fields = (
        'old_status',
        'new_status',
        'changed_at',
        'comment',
        'change_reason',
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    inlines = (RequestStatusLogInline,)

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

    actions = (
        'mark_as_in_progress',
        'mark_as_done',
        'assign_to_current_manager',
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

    def _bulk_update_status(self, request, queryset, status_code, fallback_status, message):
        status_defaults = {
            Request.STATUS_IN_PROGRESS: {
                'name': 'В работе',
                'is_initial': False,
                'is_final': False,
                'sort_order': 20,
                'color': 'warning',
                'is_active': True,
            },
            Request.STATUS_DONE: {
                'name': 'Закрыта',
                'is_initial': False,
                'is_final': True,
                'sort_order': 30,
                'color': 'success',
                'is_active': True,
            },
        }

        request_status, created = RequestStatus.objects.get_or_create(
            code=status_code,
            defaults=status_defaults[fallback_status],
        )

        if not request_status.is_active:
            request_status.is_active = True
            request_status.save(update_fields=['is_active'])

        updated_count = 0

        for obj in queryset.select_related('request_status'):
            old_status = obj.request_status

            obj.request_status = request_status
            obj.status = fallback_status
            obj.save(update_fields=['request_status', 'status'])

            if old_status is None or old_status.id != request_status.id:
                RequestStatusLog.objects.create(
                    request=obj,
                    old_status=old_status,
                    new_status=request_status,
                    comment=message,
                    change_reason=f'Массовое действие в админ-панели. Пользователь: {request.user.get_username()}',
                )

            updated_count += 1

        self.message_user(request, f'Обработано заявок: {updated_count}.')

    @admin.action(description='Перевести выбранные заявки в работу')
    def mark_as_in_progress(self, request, queryset):
        self._bulk_update_status(
            request,
            queryset,
            status_code='in_progress',
            fallback_status=Request.STATUS_IN_PROGRESS,
            message='Заявка переведена в работу через массовое действие',
        )

    @admin.action(description='Закрыть выбранные заявки')
    def mark_as_done(self, request, queryset):
        self._bulk_update_status(
            request,
            queryset,
            status_code='done',
            fallback_status=Request.STATUS_DONE,
            message='Заявка закрыта через массовое действие',
        )

    @admin.action(description='Назначить выбранные заявки на текущего пользователя')
    def assign_to_current_manager(self, request, queryset):
        updated_count = queryset.update(assigned_manager=request.user)
        self.message_user(request, f'Назначено заявок: {updated_count}.')

    def save_model(self, request, obj, form, change):
        old_status = None
        status_changed = False

        if change and obj.pk:
            old_obj = (
                Request.objects
                .filter(pk=obj.pk)
                .select_related('request_status')
                .first()
            )

            if old_obj:
                old_status = old_obj.request_status
                status_changed = old_obj.request_status_id != obj.request_status_id

        super().save_model(request, obj, form, change)

        if not change and obj.request_status_id:
            RequestStatusLog.objects.create(
                request=obj,
                old_status=None,
                new_status=obj.request_status,
                comment='Заявка создана через административную панель',
                change_reason=f'Пользователь: {request.user.get_username()}',
            )

        if change and status_changed:
            RequestStatusLog.objects.create(
                request=obj,
                old_status=old_status,
                new_status=obj.request_status,
                comment='Статус заявки изменен через административную панель',
                change_reason=f'Пользователь: {request.user.get_username()}',
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
    list_display = (
        'request',
        'old_status',
        'new_status',
        'changed_at',
        'change_reason',
    )
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = (
        'request__name',
        'request__phone',
        'request__email',
        'comment',
        'change_reason',
    )
    readonly_fields = (
        'request',
        'old_status',
        'new_status',
        'changed_at',
        'comment',
        'change_reason',
    )

    def has_add_permission(self, request):
        return False