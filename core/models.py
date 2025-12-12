from django.db import models
from django.urls import reverse


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

    source_url = models.URLField('Страница', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Заявка #{self.id} — {self.name}'
