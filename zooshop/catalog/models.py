from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


class BaseModel(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')

    class Meta:
        abstract = True


class Client(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='Пользователь'
    )
    phone = models.CharField(max_length=11, verbose_name='Телефон', blank=True)
    address = models.CharField(
        max_length=500, verbose_name='Адрес', blank=True
    )

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Employee(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name='Пользователь'
    )
    position = models.CharField(
        max_length=100, verbose_name='Должность', blank=True
    )
    salary = models.FloatField(verbose_name='Зарплата', blank=True)

    class Meta:
        verbose_name = 'сотрудник'
        verbose_name_plural = 'Сотрудники'

    def save(self, *args, **kwargs):
        if not self.user:
            self.user = User.objects.create(
                username=f"{self.first_name.lower()}_{self.last_name.lower()}",
                is_staff=True,
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Client_order(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Принят'),
        ('gathered', 'Собран'),
        ('delivered', 'Доставлен'),
        ('issued', 'Выдан'),
    ]
    date = models.DateField(verbose_name='Дата заказа')
    status = models.CharField(
        max_length=50,
        verbose_name='Статус заказа',
        choices=STATUS_CHOICES,
        default='accepted'
    )
    price = models.FloatField(verbose_name='Цена заказа')
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='client_orders',
        verbose_name='Клиент'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='client_orders',
        verbose_name='Сотрудник'
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('date',)

    def __str__(self):
        return 'Заказ клиента ' + str(self.client.pk) + ': ' + str(self.pk)


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.CharField(max_length=500, verbose_name='Описание')
    price = models.FloatField(verbose_name='Цена товара')
    category = models.CharField(
        max_length=50,
        verbose_name='Категория',
        blank=True
    )
    available_number = models.IntegerField(
        verbose_name='Доступное количество товара'
    )
    orders = models.ManyToManyField(
        Client_order,
        through='Client_order_position',
        verbose_name='Заказ'
    )

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Товар'
    )
    text = models.TextField(
        blank=True,
        verbose_name='Текст отзыва'
    )
    rating = models.IntegerField(
        verbose_name='Оценка',
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.product.name + ': ' + str(self.pk)


class Client_order_position(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='client_order_positions',
        verbose_name='Товар'
    )
    client_order = models.ForeignKey(
        Client_order,
        on_delete=models.CASCADE,
        related_name='client_order_positions',
        verbose_name='Заказ'
    )
    position_number = models.IntegerField(verbose_name='Количество товара')

    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return self.product.name + ': заказ ' + str(self.client_order.pk)


class ProductWithReviews(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.CharField(max_length=500, verbose_name='Описание')
    price = models.FloatField(verbose_name='Цена товара')
    text = models.TextField(
        blank=True,
        verbose_name='Текст отзыва'
    )
    rating = models.IntegerField(
        verbose_name='Оценка',
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    class Meta:
        managed = False
        db_table = 'product_with_reviews'
