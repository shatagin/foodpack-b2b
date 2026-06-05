from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Слаг (URL)', unique=True)
    short_description = models.TextField('Краткое описание', blank=True)
    is_active = models.BooleanField('Активна', default=True)
    sort_order = models.PositiveIntegerField('Порядок сортировки', default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('category_detail', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория',
    )
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField('Слаг (URL)', unique=True)
    lead = models.TextField('Краткое описание', blank=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField(
        'Фото',
        upload_to='products/',
        blank=True,
        null=True,
    )
    is_active = models.BooleanField('Активен', default=True)
    sort_order = models.PositiveIntegerField('Порядок сортировки', default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('product_detail', args=[self.category.slug, self.slug])


class Client(models.Model):
    company_name = models.CharField('Компания', max_length=255)
    contact_person = models.CharField('Контактное лицо', max_length=255, blank=True)
    phone = models.CharField('Телефон', max_length=50)
    email = models.EmailField('E-mail', blank=True)
    inn = models.CharField('ИНН', max_length=20, blank=True)
    kpp = models.CharField('КПП', max_length=20, blank=True)
    address = models.TextField('Адрес', blank=True)
    comment = models.TextField('Комментарий', blank=True)
    source = models.CharField('Источник', max_length=120, blank=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['company_name']

    def __str__(self) -> str:
        if self.contact_person:
            return f'{self.company_name} — {self.contact_person}'
        return self.company_name


class RequestStatus(models.Model):
    name = models.CharField('Название', max_length=150)
    code = models.CharField('Код', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)

    is_initial = models.BooleanField('Начальный статус', default=False)
    is_final = models.BooleanField('Финальный статус', default=False)
    sort_order = models.PositiveIntegerField('Порядок сортировки', default=0)
    color = models.CharField('Цвет', max_length=30, blank=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Статус заявки'
        verbose_name_plural = 'Статусы заявок'
        ordering = ['sort_order', 'name']

    def __str__(self) -> str:
        return self.name


class Request(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_DONE, 'Закрыта'),
    ]

    name = models.CharField('Компания / имя', max_length=255)
    phone = models.CharField('Телефон', max_length=50)
    email = models.EmailField('E-mail', blank=True)
    comment = models.TextField('Комментарий', blank=True)

    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests',
        verbose_name='Категория',
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests',
        verbose_name='Товар',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests',
        verbose_name='Клиент',
    )

    request_status = models.ForeignKey(
        RequestStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests',
        verbose_name='Статус заявки',
    )

    source_url = models.URLField('Страница', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Заявка #{self.id} — {self.name}'


class RequestStatusLog(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.ForeignKey(RequestStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='old_logs')
    new_status = models.ForeignKey(RequestStatus, on_delete=models.SET_NULL, null=True, related_name='new_logs')
    changed_at = models.DateTimeField('Дата изменения', auto_now_add=True)
    comment = models.TextField('Комментарий', blank=True)
    change_reason = models.CharField('Причина изменения', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Лог изменения статуса заявки'
        verbose_name_plural = 'Логи изменения статусов заявок'
        ordering = ['-changed_at']


class NewsPost(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('Slug', max_length=255, unique=True, blank=True)
    excerpt = models.TextField('Кратко', blank=True)
    body = models.TextField('Текст', blank=True)

    is_published = models.BooleanField('Опубликовано', default=True)
    published_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/news/{self.slug}/'
