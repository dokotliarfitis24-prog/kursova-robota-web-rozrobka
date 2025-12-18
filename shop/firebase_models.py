"""
Firebase models - заміна Django ORM моделей
"""
from datetime import datetime
from typing import Optional, Dict, List, Any
from shop.firebase_config import get_db


class FirebaseModel:
    """Базовий клас для роботи з Firestore"""
    collection_name = None
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        for key, value in kwargs.items():
            if key != 'id':
                setattr(self, key, value)
    
    @classmethod
    def get_collection(cls):
        """Отримати колекцію Firestore"""
        if not cls.collection_name:
            raise ValueError(f"collection_name не встановлено для {cls.__name__}")
        return get_db().collection(cls.collection_name)
    
    def save(self):
        """Зберегти документ в Firestore"""
        collection = self.get_collection()
        data = self.to_dict()
        
        if self.id:
            # Оновлення існуючого - використовуємо set з merge=True для безпечного оновлення
            doc_ref = collection.document(self.id)
            # Додаємо updated_at
            data['updated_at'] = datetime.now()
            # Використовуємо set з merge=True замість update для надійності
            doc_ref.set(data, merge=True)
        else:
            # Створення нового
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            _, doc_ref = collection.add(data)
            self.id = doc_ref.id
        
        return self
    
    def delete(self):
        """Видалити документ"""
        if self.id:
            self.get_collection().document(self.id).delete()
    
    def to_dict(self):
        """Конвертувати в словник для Firestore"""
        data = {}
        for key, value in self.__dict__.items():
            # Виключаємо id та приватні поля, але включаємо None значення для оновлення
            if key != 'id' and not key.startswith('_'):
                data[key] = value
        return data
    
    @classmethod
    def from_dict(cls, doc_id: str, data: Dict):
        """Створити об'єкт з даних Firestore"""
        if data is None:
            return None
        data = dict(data)  # Копія даних
        data['id'] = doc_id
        # Конвертація timestamp в datetime та числових типів
        for key, value in data.items():
            # Перевірка, чи це Firestore Timestamp (має метод to_datetime)
            if hasattr(value, 'to_datetime') and callable(getattr(value, 'to_datetime', None)):
                try:
                    data[key] = value.to_datetime()
                except:
                    # Якщо не вдалося конвертувати, залишаємо як є
                    pass
            # Конвертація Decimal або числових типів для price та stock
            elif key in ['price', 'total_price'] and value is not None:
                try:
                    # Конвертуємо в float для коректного відображення
                    # Може бути Decimal, int, float, або рядок
                    if hasattr(value, '__float__'):
                        data[key] = float(value)
                    elif isinstance(value, (int, float)):
                        data[key] = float(value)
                    elif isinstance(value, str):
                        data[key] = float(value)
                    else:
                        # Спробуємо конвертувати через str
                        data[key] = float(str(value))
                except (ValueError, TypeError) as e:
                    # Якщо не вдалося конвертувати, залишаємо як є
                    print(f"Warning: Could not convert {key} value {value} (type {type(value)}) to float: {e}")
                    pass
            elif key == 'stock' and value is not None:
                try:
                    # Конвертуємо в int для stock
                    data[key] = int(value)
                except (ValueError, TypeError):
                    pass
        return cls(**data)
    
    @classmethod
    def get_by_id(cls, doc_id: str):
        """Отримати документ за ID"""
        doc = cls.get_collection().document(doc_id).get()
        if doc.exists:
            return cls.from_dict(doc.id, doc.to_dict())
        return None
    
    @classmethod
    def get_all(cls, filters: Optional[List] = None, order_by: Optional[str] = None, 
                order_direction: Optional[str] = None, limit: Optional[int] = None):
        """Отримати всі документи з фільтрами"""
        query = cls.get_collection()
        
        if filters:
            # Використовуємо FieldFilter для уникнення попереджень
            try:
                from google.cloud.firestore_v1.base_query import FieldFilter
                for field, operator, value in filters:
                    field_filter = FieldFilter(field, operator, value)
                    query = query.where(filter=field_filter)
            except (ImportError, AttributeError, TypeError):
                # Якщо FieldFilter не доступний, використовуємо старий спосіб
                # Приховуємо попередження, оскільки це не критично
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    for field, operator, value in filters:
                        query = query.where(field, operator, value)
        
        if order_by:
            # Підтримка напрямку сортування
            if order_direction and order_direction.lower() == 'desc':
                from google.cloud.firestore_v1 import Query
                query = query.order_by(order_by, direction=Query.DESCENDING)
            else:
                query = query.order_by(order_by)
        
        if limit:
            query = query.limit(limit)
        
        docs = query.stream()
        return [cls.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    @classmethod
    def get_one(cls, filters: Optional[List] = None):
        """Отримати один документ"""
        results = cls.get_all(filters=filters, limit=1)
        return results[0] if results else None


class Category(FirebaseModel):
    """Категорія товарів"""
    collection_name = 'categories'
    
    def __init__(self, name: str = None, slug: str = None, description: str = None, 
                 image: str = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.slug = slug
        self.description = description or ''
        self.image = image


class Product(FirebaseModel):
    """Товар"""
    collection_name = 'products'
    
    WEAPON_TYPES = {
        'firearm': 'Вогнепальна зброя',
        'pneumatic': 'Пневматична зброя',
        'cold': 'Холодна зброя',
        'accessories': 'Аксесуари',
    }
    
    def __init__(self, name: str = None, slug: str = None, category_id: str = None,
                 description: str = None, weapon_type: str = None, manufacturer: str = None,
                 caliber: str = None, barrel_length: str = None, weight: str = None,
                 material: str = None, price: float = None, stock: int = 0,
                 image: str = None, image2: str = None, image3: str = None, image4: str = None,
                 is_active: bool = True, is_popular: bool = False, **kwargs):
        # Спочатку викликаємо super().__init__(**kwargs), який встановить всі поля з kwargs
        # (дані з Firestore передаються через kwargs)
        super().__init__(**kwargs)
        
        # Потім перезаписуємо значення з параметрів функції, якщо вони передані явно
        # (для випадків, коли створюємо новий об'єкт напряму)
        if name is not None:
            self.name = name
        if slug is not None:
            self.slug = slug
        if category_id is not None:
            self.category_id = category_id
        if description is not None:
            self.description = description
        elif not hasattr(self, 'description'):
            self.description = ''
        if weapon_type is not None:
            self.weapon_type = weapon_type
        if manufacturer is not None:
            self.manufacturer = manufacturer
        elif not hasattr(self, 'manufacturer'):
            self.manufacturer = ''
        if caliber is not None:
            self.caliber = caliber
        elif not hasattr(self, 'caliber'):
            self.caliber = ''
        if barrel_length is not None:
            self.barrel_length = barrel_length
        elif not hasattr(self, 'barrel_length'):
            self.barrel_length = ''
        if weight is not None:
            self.weight = weight
        elif not hasattr(self, 'weight'):
            self.weight = ''
        if material is not None:
            self.material = material
        elif not hasattr(self, 'material'):
            self.material = ''
        if price is not None:
            try:
                self.price = float(price)
            except (ValueError, TypeError):
                self.price = None
        if stock is not None:
            try:
                self.stock = int(stock)
            except (ValueError, TypeError):
                self.stock = 0
        if image is not None:
            self.image = image
        if image2 is not None:
            self.image2 = image2
        if image3 is not None:
            self.image3 = image3
        if image4 is not None:
            self.image4 = image4
        if 'is_active' not in kwargs:
            self.is_active = is_active
        if 'is_popular' not in kwargs:
            self.is_popular = is_popular
        
        # Після встановлення всіх значень переконуємося, що price та stock мають правильні типи
        # Це важливо, оскільки дані з Firestore можуть бути різних типів
        if hasattr(self, 'price') and self.price is not None:
            try:
                # Конвертуємо в float, навіть якщо це Decimal або інший тип
                self.price = float(self.price)
            except (ValueError, TypeError) as e:
                import sys
                print(f"Warning: Could not convert price {self.price} (type {type(self.price)}) to float: {e}", file=sys.stderr)
                self.price = None
        elif not hasattr(self, 'price'):
            self.price = None
            
        if hasattr(self, 'stock') and self.stock is not None:
            try:
                self.stock = int(self.stock)
            except (ValueError, TypeError):
                self.stock = 0
        elif not hasattr(self, 'stock'):
            self.stock = 0
    
    def get_category(self):
        """Отримати категорію товару"""
        if self.category_id:
            return Category.get_by_id(self.category_id)
        return None
    
    def get_weapon_type_display(self):
        """Отримати відображуване значення типу зброї"""
        return self.WEAPON_TYPES.get(self.weapon_type, self.weapon_type)


class Order(FirebaseModel):
    """Замовлення"""
    collection_name = 'orders'
    
    STATUS_CHOICES = {
        'pending': 'Очікує обробки',
        'processing': 'В обробці',
        'shipped': 'Відправлено',
        'delivered': 'Доставлено',
        'cancelled': 'Скасовано',
    }
    
    PAYMENT_CHOICES = {
        'cash_on_delivery': 'Післяплата',
        'online': 'Онлайн оплата',
    }
    
    def __init__(self, user_id: str = None, first_name: str = None, last_name: str = None,
                 email: str = None, phone: str = None, address: str = None,
                 city: str = None, postal_code: str = None, payment_method: str = 'cash_on_delivery',
                 status: str = 'pending', total_price: float = None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.postal_code = postal_code or ''
        self.payment_method = payment_method
        self.status = status
        self.total_price = total_price
    
    def get_status_display(self):
        """Отримати відображуване значення статусу"""
        return self.STATUS_CHOICES.get(self.status, self.status)
    
    def get_payment_method_display(self):
        """Отримати відображуване значення способу оплати"""
        return self.PAYMENT_CHOICES.get(self.payment_method, self.payment_method)
    
    def get_items(self):
        """Отримати елементи замовлення"""
        return OrderItem.get_all(filters=[('order_id', '==', self.id)])
    
    @property
    def items(self):
        """Property для сумісності з Django ORM"""
        return self.get_items()


class OrderItem(FirebaseModel):
    """Елемент замовлення"""
    collection_name = 'order_items'
    
    def __init__(self, order_id: str = None, product_id: str = None,
                 quantity: int = None, price: float = None, **kwargs):
        super().__init__(**kwargs)
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    def get_product(self):
        """Отримати товар"""
        if self.product_id:
            return Product.get_by_id(self.product_id)
        return None
    
    def get_cost(self):
        """Отримати вартість елемента"""
        return self.price * self.quantity
    
    @property
    def product(self):
        """Property для сумісності з Django ORM"""
        return self.get_product()


class Comment(FirebaseModel):
    """Коментар до товару"""
    collection_name = 'comments'
    
    def __init__(self, product_id: str = None, user_id: str = None, 
                 username: str = None, text: str = None, 
                 rating: int = None, is_approved: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.product_id = product_id
        self.user_id = user_id
        self.username = username or ''
        self.text = text or ''
        self.rating = rating  # Оцінка від 1 до 5
        self.is_approved = is_approved
    
    def get_product(self):
        """Отримати товар"""
        if self.product_id:
            return Product.get_by_id(self.product_id)
        return None
    
    def get_user(self):
        """Отримати користувача"""
        if self.user_id:
            return FirebaseUser.get_by_id(self.user_id)
        return None
    
    @property
    def product(self):
        """Property для сумісності"""
        return self.get_product()
    
    @property
    def user(self):
        """Property для сумісності"""
        return self.get_user()


class FirebaseUser(FirebaseModel):
    """Користувач (заміна Django User)"""
    collection_name = 'users'
    
    def __init__(self, username: str = None, email: str = None, password_hash: str = None,
                 first_name: str = None, last_name: str = None,
                 is_active: bool = True, is_staff: bool = False, is_superuser: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name or ''
        self.last_name = last_name or ''
        self.is_active = is_active
        self.is_staff = is_staff
        self.is_superuser = is_superuser
    
    @classmethod
    def get_by_username(cls, username: str):
        """Отримати користувача за username"""
        return cls.get_one(filters=[('username', '==', username)])
    
    @classmethod
    def get_by_email(cls, email: str):
        """Отримати користувача за email"""
        return cls.get_one(filters=[('email', '==', email)])
    
    def __str__(self):
        return self.username or self.email


class UserProfile(FirebaseModel):
    """Профіль користувача"""
    collection_name = 'user_profiles'
    
    def __init__(self, user_id: str = None, phone: str = None, address: str = None,
                 city: str = None, postal_code: str = None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.phone = phone or ''
        self.address = address or ''
        self.city = city or ''
        self.postal_code = postal_code or ''
    
    @classmethod
    def get_by_user_id(cls, user_id: str):
        """Отримати профіль за user_id"""
        return cls.get_one(filters=[('user_id', '==', user_id)])

