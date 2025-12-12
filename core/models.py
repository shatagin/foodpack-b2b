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