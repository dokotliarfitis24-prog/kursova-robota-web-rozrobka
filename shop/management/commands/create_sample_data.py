from django.core.management.base import BaseCommand
from shop.firebase_models import Category, Product


class Command(BaseCommand):
    help = 'Створює тестові дані для магазину'

    def handle(self, *args, **options):
        self.stdout.write('Створення тестових даних в Firebase Firestore...')

        # Створення категорій
        categories_data = [
            {'name': 'Вогнепальна зброя', 'slug': 'firearms', 'description': 'Пістолети, рушниці, карабіни'},
            {'name': 'Пневматична зброя', 'slug': 'pneumatic', 'description': 'Пневматичні пістолети та рушниці'},
            {'name': 'Холодна зброя', 'slug': 'cold-weapons', 'description': 'Ножі, мечі, кинджали'},
            {'name': 'Аксесуари', 'slug': 'accessories', 'description': 'Боєприпаси, кобури, оптика'},
        ]

        categories = {}
        for cat_data in categories_data:
            # Перевіряємо, чи категорія вже існує
            existing = Category.get_one(filters=[('slug', '==', cat_data['slug'])])
            if existing:
                categories[cat_data['slug']] = existing
                self.stdout.write(f'Категорія вже існує: {existing.name}')
            else:
                category = Category(**cat_data)
                category.save()
                categories[cat_data['slug']] = category
                self.stdout.write(self.style.SUCCESS(f'Створено категорію: {category.name}'))

        # Створення товарів
        products_data = [
            {
                'name': 'Пістолет Glock 17',
                'slug': 'glock-17',
                'category': categories['firearms'],
                'weapon_type': 'firearm',
                'manufacturer': 'Glock',
                'caliber': '9x19mm',
                'price': 25000.00,
                'stock': 5,
                'is_popular': True,
                'description': 'Надійний пістолет для самооборони та службового використання.',
            },
            {
                'name': 'Рушниця Benelli M4',
                'slug': 'benelli-m4',
                'category': categories['firearms'],
                'weapon_type': 'firearm',
                'manufacturer': 'Benelli',
                'caliber': '12 калібр',
                'price': 45000.00,
                'stock': 3,
                'is_popular': True,
                'description': 'Самозарядна рушниця для полювання та спорту.',
            },
            {
                'name': 'Пневматичний пістолет Gamo PT-85',
                'slug': 'gamo-pt-85',
                'category': categories['pneumatic'],
                'weapon_type': 'pneumatic',
                'manufacturer': 'Gamo',
                'caliber': '4.5mm',
                'price': 3500.00,
                'stock': 10,
                'is_popular': True,
                'description': 'Пневматичний пістолет для тренувань та розваг.',
            },
            {
                'name': 'Ніж тактичний Cold Steel',
                'slug': 'cold-steel-tactical',
                'category': categories['cold-weapons'],
                'weapon_type': 'cold',
                'manufacturer': 'Cold Steel',
                'material': 'Нержавіюча сталь',
                'price': 2500.00,
                'stock': 15,
                'is_popular': True,
                'description': 'Надійний тактичний ніж для виживання.',
            },
            {
                'name': 'Кобура шкіряна',
                'slug': 'leather-holster',
                'category': categories['accessories'],
                'weapon_type': 'accessories',
                'manufacturer': 'Generic',
                'material': 'Шкіра',
                'price': 800.00,
                'stock': 20,
                'description': 'Якісна шкіряна кобура для пістолета.',
            },
        ]

        for prod_data in products_data:
            # Отримуємо category_id
            category = prod_data.pop('category')
            category_id = category.id if hasattr(category, 'id') else category
            
            # Перевіряємо, чи товар вже існує
            existing = Product.get_one(filters=[('slug', '==', prod_data['slug'])])
            if existing:
                self.stdout.write(f'Товар вже існує: {existing.name}')
            else:
                # Додаємо category_id
                prod_data['category_id'] = category_id
                # Додаємо image (обов'язкове поле)
                if 'image' not in prod_data:
                    prod_data['image'] = ''  # Порожнє значення, можна додати пізніше
                
                product = Product(**prod_data)
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Створено товар: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Тестові дані успішно створено!'))

