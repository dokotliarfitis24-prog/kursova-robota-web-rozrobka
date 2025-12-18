# Generated manually

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Назва')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='URL')),
                ('description', models.TextField(blank=True, verbose_name='Опис')),
                ('image', models.ImageField(blank=True, null=True, upload_to='categories/', verbose_name='Зображення')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
            ],
            options={
                'verbose_name': 'Категорія',
                'verbose_name_plural': 'Категорії',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Назва')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='URL')),
                ('description', models.TextField(verbose_name='Опис')),
                ('weapon_type', models.CharField(choices=[('firearm', 'Вогнепальна зброя'), ('pneumatic', 'Пневматична зброя'), ('cold', 'Холодна зброя'), ('accessories', 'Аксесуари')], max_length=20, verbose_name='Тип зброї')),
                ('manufacturer', models.CharField(blank=True, max_length=100, verbose_name='Виробник')),
                ('caliber', models.CharField(blank=True, max_length=50, verbose_name='Калібр')),
                ('barrel_length', models.CharField(blank=True, max_length=50, verbose_name='Довжина ствола')),
                ('weight', models.CharField(blank=True, max_length=50, verbose_name='Вага')),
                ('material', models.CharField(blank=True, max_length=100, verbose_name='Матеріал')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Ціна')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='Наявність')),
                ('image', models.ImageField(upload_to='products/', verbose_name='Головне зображення')),
                ('image2', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Зображення 2')),
                ('image3', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Зображення 3')),
                ('image4', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Зображення 4')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активний')),
                ('is_popular', models.BooleanField(default=False, verbose_name='Популярний')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='shop.category', verbose_name='Категорія')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товари',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='Ім\'я')),
                ('last_name', models.CharField(max_length=100, verbose_name='Прізвище')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('address', models.TextField(verbose_name='Адреса доставки')),
                ('city', models.CharField(max_length=100, verbose_name='Місто')),
                ('postal_code', models.CharField(blank=True, max_length=20, verbose_name='Поштовий індекс')),
                ('payment_method', models.CharField(choices=[('cash_on_delivery', 'Післяплата'), ('online', 'Онлайн оплата')], default='cash_on_delivery', max_length=20, verbose_name='Спосіб оплати')),
                ('status', models.CharField(choices=[('pending', 'Очікує обробки'), ('processing', 'В обробці'), ('shipped', 'Відправлено'), ('delivered', 'Доставлено'), ('cancelled', 'Скасовано')], default='pending', max_length=20, verbose_name='Статус')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Загальна сума')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Користувач')),
            ],
            options={
                'verbose_name': 'Замовлення',
                'verbose_name_plural': 'Замовлення',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('address', models.TextField(blank=True, verbose_name='Адреса')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='Місто')),
                ('postal_code', models.CharField(blank=True, max_length=20, verbose_name='Поштовий індекс')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Користувач')),
            ],
            options={
                'verbose_name': 'Профіль користувача',
                'verbose_name_plural': 'Профілі користувачів',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Кількість')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ціна')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.order', verbose_name='Замовлення')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Елемент замовлення',
                'verbose_name_plural': 'Елементи замовлення',
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['slug'], name='shop_produc_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['weapon_type'], name='shop_produc_weapon__idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_active', 'is_popular'], name='shop_produc_is_acti_idx'),
        ),
    ]

