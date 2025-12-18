# ВСІ МОДЕЛІ БІЛЬШЕ НЕ ВИКОРИСТОВУЮТЬСЯ - ДАНІ В FIREBASE
# Цей файл залишено для сумісності, але моделі не імпортуються

# Django models більше не потрібні - використовуємо Firebase Firestore
# Всі дані зберігаються в Firebase через shop.firebase_models

# Якщо потрібно використовувати Django models, розкоментуйте код нижче
# Але зараз всі дані в Firebase, тому моделі не потрібні

"""
# Старі Django models (не використовуються)

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Назва')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Опис')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Зображення')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    WEAPON_TYPES = [
        ('firearm', 'Вогнепальна зброя'),
        ('pneumatic', 'Пневматична зброя'),
        ('cold', 'Холодна зброя'),
        ('accessories', 'Аксесуари'),
    ]

    name = models.CharField(max_length=200, verbose_name='Назва')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категорія')
    description = models.TextField(verbose_name='Опис')
    weapon_type = models.CharField(max_length=20, choices=WEAPON_TYPES, verbose_name='Тип зброї')
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name='Виробник')
    caliber = models.CharField(max_length=50, blank=True, verbose_name='Калібр')
    barrel_length = models.CharField(max_length=50, blank=True, verbose_name='Довжина ствола')
    weight = models.CharField(max_length=50, blank=True, verbose_name='Вага')
    material = models.CharField(max_length=100, blank=True, verbose_name='Матеріал')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Ціна')
    stock = models.PositiveIntegerField(default=0, verbose_name='Наявність')
    image = models.ImageField(upload_to='products/', verbose_name='Головне зображення')
    image2 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Зображення 2')
    image3 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Зображення 3')
    image4 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Зображення 4')
    is_active = models.BooleanField(default=True, verbose_name='Активний')
    is_popular = models.BooleanField(default=False, verbose_name='Популярний')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує обробки'),
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    PAYMENT_CHOICES = [
        ('cash_on_delivery', 'Післяплата'),
        ('online', 'Онлайн оплата'),
    ]

    first_name = models.CharField(max_length=100, verbose_name='Ім\'я')
    last_name = models.CharField(max_length=100, verbose_name='Прізвище')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адреса доставки')
    city = models.CharField(max_length=100, verbose_name='Місто')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Поштовий індекс')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash_on_delivery', verbose_name='Спосіб оплати')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Загальна сума')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'Замовлення #{self.id} - {self.first_name} {self.last_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Замовлення')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Кількість')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна')

    class Meta:
        verbose_name = 'Елемент замовлення'
        verbose_name_plural = 'Елементи замовлення'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'


class UserProfile(models.Model):
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адреса')
    city = models.CharField(max_length=100, blank=True, verbose_name='Місто')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Поштовий індекс')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        verbose_name = 'Профіль користувача'
        verbose_name_plural = 'Профілі користувачів'

    def __str__(self):
        return f'Профіль (Firebase)'
"""
