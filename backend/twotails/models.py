from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class Role(models.Model):
    name = models.CharField("Название роли", max_length=20, unique=True)

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

class User(AbstractUser):
    def get_default_role():
        return Role.objects.get(name='user')
    role = models.ForeignKey(Role, verbose_name="Роль", on_delete=models.SET_DEFAULT, default=get_default_role)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def account_age(self):
        time_on_site = timezone.now() - self.date_joined
        days_on_site = time_on_site.days
        years, days = divmod(days_on_site, 365)
        return f'{years} лет и {days} дней'

class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    address_line = models.CharField("Адрес", max_length=120)
    city = models.CharField("Город", max_length=20)
    is_main = models.BooleanField("Основной адрес", default=False)

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

class Supplier(models.Model):
    name = models.CharField("Название поставщика", max_length=120)
    email = models.EmailField("Электронная почта", unique=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

        permissions = [
            ("confirm_supply", "Может подтверждать поставку"),
            ("cancel_supply", "Может отменять поставку"),
            ("change_order_item_status", "Может менять статус поставки"), 
            ("can_edit_delivery_items", "Может редактировать состав поставки"),
            ("view_own_deliveries", "Может просматривать свои поставки"),
            ("view_own_products", "Может просматривать свои товары"),
            ("view_own_orders", "Может просматривать заказы с его товарами"),
            ("view_own_sales_report", "Может просматривать отчёты по своим продажам"),
        ]
class Supply(models.Model):
    supplier = models.ForeignKey(Supplier, verbose_name="Поставщик", on_delete=models.CASCADE, related_name="supplies")
    date = models.DateField("Дата поставки", auto_now_add=True)

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"

class SupplyItem(models.Model):
    supply = models.ForeignKey(Supply, verbose_name="Поставка", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', verbose_name="Товар", on_delete=models.CASCADE )
    quantity = models.PositiveIntegerField("Количество")

    class Meta:
        verbose_name = "Элемент поставки"
        verbose_name_plural = "Элементы поставки"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.last_delivery_quantity = self.quantity
        self.product.current_quantity += self.quantity
        self.product.save()

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ("rejected", "Отклонена"),
        ('assembling', 'Сборка'),
        ('in_progress', 'В пути'),
        ('received', 'Исполнена'),
        ('canceled', 'Отменена'),
    ]
    status = models.CharField("Статус", max_length=11, choices=STATUS_CHOICES, default='pending')
    delivery_date = models.DateTimeField("Дата и время доставки", auto_now_add=True)
    supplier = models.ForeignKey(Supplier, verbose_name="Поставщик",null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставки"

class Category(models.Model):
    name = models.CharField("Название категории", max_length=25)
    parent = models.ForeignKey('self', verbose_name="Родительская категория", on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Product(models.Model):
    name = models.CharField("Название товара", max_length=120)
    description = models.TextField("Описание")
    manufactured_by = models.DateField("Дата изготовления", default=timezone.now)
    expiration_days = models.PositiveIntegerField("Срок годности", default=30)
    last_delivery_quantity = models.PositiveIntegerField("Количество в последней поставке", default=0)
    current_quantity = models.PositiveIntegerField("Текущее количество", default=0)
    purchase_price = models.IntegerField("Закупочная цена")
    sale_price = models.PositiveIntegerField("Цена продажи")
    manufacturer = models.CharField("Производитель", max_length=100)
    supplier = models.ForeignKey(Supplier, verbose_name="Поставщик", on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.SET_NULL, null=True)
    promotions = models.ManyToManyField('Promotion', verbose_name="Акции", through='ProductPromotion')
    has_discount = models.BooleanField("Скидка", default=False)
    discount_percent = models.PositiveIntegerField("Процент скидки", default=0)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def is_usable(self):
        return self.manufactured_by + timedelta(days = self.expiration_days) >= timezone.now()
    def discount_percentage(self):
        category = self.category
        while category.parent and category.parent.name != 'Питание':
            category = category.parent
        expiration_date = self.manufactured_by + timedelta(days=self.expiration_days)
        days_left = (expiration_date - timezone.now().date()).days
        if days_left > 100:
            self.discount_percent = 5
        elif days_left > 80:
            self.discount_percent = 10
        elif days_left > 60:
            self.discount_percent = 15
        elif days_left > 30:
            self.discount_percent = 30
        else:
            self.discount_percent = 70
        return self.discount_percent

class DeliveryItem(models.Model):
    delivery = models.ForeignKey(Delivery, verbose_name="Доставка", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField("Количество")

    class Meta:
        verbose_name = "Элемент доставки"
        verbose_name_plural = "Элементы доставки"

class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    created_at = models.DateTimeField("Создан", default=timezone.now)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('converted', 'Конвертированная'),
        ('abandoned', 'Брошенная')
    ]
    status = models.CharField("Статус", max_length=9, choices=STATUS_CHOICES)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name="Корзина", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество")

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField("Создан", default=timezone.now)
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('cancelled', 'Отменён'),
    ]
    status = models.CharField("Статус", max_length=9, choices=STATUS_CHOICES)
    total_amount = models.FloatField("Общая сумма")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name="Заказ", on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField("Количество")
    price_at_purchase = models.FloatField("Цена на момент покупки")

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

class Promotion(models.Model):
    name = models.CharField("Название акции", max_length=50)
    description = models.TextField("Описание")
    discount_percent = models.PositiveIntegerField("Процент скидки")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    is_active = models.BooleanField("Активна")

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
    

class ProductPromotion(models.Model):
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    promotion = models.ForeignKey(Promotion, verbose_name="Акция", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Товар-акция"
        verbose_name_plural = "Товары-акции"
