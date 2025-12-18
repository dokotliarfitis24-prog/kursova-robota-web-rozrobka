"""
Адмін-панель для Firebase
"""
import re
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .firebase_auth import is_staff, is_superuser

from .firebase_models import Category, Product, Order, OrderItem, UserProfile, FirebaseUser, Comment
from .firebase_config import get_db
from .cloudinary_utils import upload_image, delete_image


def generate_slug(text):
    """Генерація slug з тексту"""
    if not text:
        return ''
    # Перетворюємо на нижній регістр
    slug = text.lower().strip()
    # Замінюємо кирилицю на латиницю (базові символи)
    cyrillic_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'є': 'ye',
        'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k',
        'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
        'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh',
        'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'Ye',
        'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y', 'К': 'K',
        'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S',
        'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh',
        'Щ': 'Shch', 'Ь': '', 'Ы': 'Y', 'Ъ': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    for cyr, lat in cyrillic_to_latin.items():
        slug = slug.replace(cyr, lat)
    # Видаляємо спеціальні символи, залишаємо тільки букви, цифри, пробіли та дефіси
    slug = re.sub(r'[^\w\s-]', '', slug)
    # Замінюємо пробіли та підкреслення на дефіси
    slug = re.sub(r'[\s_-]+', '-', slug)
    # Видаляємо дефіси на початку та в кінці
    slug = slug.strip('-')
    return slug


def is_admin(request):
    """Перевірка, чи користувач адміністратор"""
    return is_staff(request)


def firebase_admin_home(request):
    """Головна сторінка адмін-панелі Firebase"""
    categories_count = len(Category.get_all())
    products_count = len(Product.get_all())
    orders_count = len(Order.get_all())
    profiles_count = len(FirebaseUser.get_all())
    
    # Підрахунок коментарів, що очікують модерації
    from datetime import datetime
    all_comments = Comment.get_all()
    pending_comments_count = len([c for c in all_comments if not getattr(c, 'is_approved', False)])
    
    context = {
        'categories_count': categories_count,
        'products_count': products_count,
        'orders_count': orders_count,
        'profiles_count': profiles_count,
        'pending_comments_count': pending_comments_count,
    }
    return render(request, 'admin/firebase_admin_home.html', context)


def firebase_categories(request):
    """Керування категоріями"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            category_id = request.POST.get('category_id')
            category = Category.get_by_id(category_id)
            if category:
                category.delete()
                messages.success(request, 'Категорію видалено')
        # ВАЖЛИВО: спочатку перевіряємо edit, потім add
        elif request.POST.get('edit') or 'edit' in request.POST:
            category_id = request.POST.get('category_id')
            if not category_id:
                messages.error(request, 'ID категорії не вказано')
                return redirect('firebase_admin:categories')
            
            category = Category.get_by_id(category_id)
            if not category:
                messages.error(request, 'Категорію не знайдено')
                return redirect('firebase_admin:categories')
            
            # Зберігаємо ID перед оновленням
            original_id = category.id
            
            # Обробка завантаження нового зображення
            if 'image' in request.FILES:
                result = upload_image(request.FILES['image'], folder='categories')
                if result:
                    category.image = result.get('secure_url') or result.get('url')
            elif request.POST.get('image_url'):
                category.image = request.POST.get('image_url')
            
            category.name = request.POST.get('name')
            category.slug = request.POST.get('slug')
            category.description = request.POST.get('description', '')
            
            # Переконуємося, що ID збережено
            category.id = original_id
            category.save()
            messages.success(request, 'Категорію оновлено')
        elif request.POST.get('add') or 'add' in request.POST:
            # Перевірка, чи це не редагування (якщо є category_id, це редагування)
            if request.POST.get('category_id'):
                messages.error(request, 'Помилка: виявлено ID при додаванні')
                return redirect('firebase_admin:categories')
            
            # Обробка завантаження зображення категорії
            image_url = ''
            if 'image' in request.FILES:
                result = upload_image(request.FILES['image'], folder='categories')
                if result:
                    image_url = result.get('secure_url') or result.get('url')
            elif request.POST.get('image_url'):
                image_url = request.POST.get('image_url')
            
            category = Category(
                name=request.POST.get('name'),
                slug=request.POST.get('slug'),
                description=request.POST.get('description', ''),
                image=image_url,
            )
            category.save()
            messages.success(request, 'Категорію створено')
        return redirect('firebase_admin:categories')
    
    categories = Category.get_all()
    return render(request, 'admin/firebase_categories.html', {'categories': categories})


def firebase_products(request):
    """Список товарів"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    products = Product.get_all()
    categories = Category.get_all()
    
    # Створюємо словник категорій для швидкого пошуку
    categories_dict = {cat.id: cat.name for cat in categories}
    
    return render(request, 'admin/firebase_products.html', {
        'products': products,
        'categories': categories,
        'categories_dict': categories_dict,
    })


def firebase_product_add(request):
    """Додавання нового товару"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    categories = Category.get_all()
    
    if request.method == 'POST':
        try:
            # Обробка зображень
            image_url = ''
            if 'image' in request.FILES:
                result = upload_image(request.FILES['image'], folder='products')
                if result:
                    image_url = result.get('secure_url') or result.get('url')
            elif request.POST.get('image_url'):
                image_url = request.POST.get('image_url')
            
            image2_url = ''
            if 'image2' in request.FILES:
                result = upload_image(request.FILES['image2'], folder='products')
                if result:
                    image2_url = result.get('secure_url') or result.get('url')
            elif request.POST.get('image2_url'):
                image2_url = request.POST.get('image2_url')
            
            image3_url = ''
            if 'image3' in request.FILES:
                result = upload_image(request.FILES['image3'], folder='products')
                if result:
                    image3_url = result.get('secure_url') or result.get('url')
            elif request.POST.get('image3_url'):
                image3_url = request.POST.get('image3_url')
            
            image4_url = ''
            if 'image4' in request.FILES:
                result = upload_image(request.FILES['image4'], folder='products')
                if result:
                    image4_url = result.get('secure_url') or result.get('url')
            elif request.POST.get('image4_url'):
                image4_url = request.POST.get('image4_url')
            
            # Генерація slug, якщо не вказано
            name = request.POST.get('name', '').strip()
            slug = request.POST.get('slug', '').strip()
            if not slug and name:
                slug = generate_slug(name)
            
            # Створюємо товар
            product = Product(
                name=name,
                slug=slug,
                category_id=request.POST.get('category_id'),
                description=request.POST.get('description', ''),
                weapon_type='accessories',  # За замовчуванням, для сумісності з існуючими даними
                manufacturer=request.POST.get('manufacturer', ''),
                caliber=request.POST.get('caliber', ''),
                barrel_length=request.POST.get('barrel_length', ''),
                weight=request.POST.get('weight', ''),
                material=request.POST.get('material', ''),
                price=float(request.POST.get('price', 0) or 0),
                stock=int(request.POST.get('stock', 0) or 0),
                image=image_url,
                image2=image2_url,
                image3=image3_url,
                image4=image4_url,
                is_active=request.POST.get('is_active') == 'on',
                is_popular=request.POST.get('is_popular') == 'on',
            )
            product.save()
            messages.success(request, 'Товар успішно створено')
            return redirect('firebase_admin:products')
        except Exception as e:
            messages.error(request, f'Помилка створення товару: {str(e)}')
    
    return render(request, 'admin/firebase_product_form.html', {
        'categories': categories,
        'product': None,
        'form_title': 'Додати товар',
    })


def firebase_product_edit(request, product_id):
    """Редагування товару - переписано з нуля"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    product = Product.get_by_id(product_id)
    if not product:
        messages.error(request, 'Товар не знайдено')
        return redirect('firebase_admin:products')
    
    categories = Category.get_all()
    
    if request.method == 'POST':
        try:
            # Отримуємо дані з форми
            name = request.POST.get('name', '').strip()
            slug = request.POST.get('slug', '').strip()
            category_id = request.POST.get('category_id', '').strip()
            description = request.POST.get('description', '').strip()
            manufacturer = request.POST.get('manufacturer', '').strip()
            caliber = request.POST.get('caliber', '').strip()
            barrel_length = request.POST.get('barrel_length', '').strip()
            weight = request.POST.get('weight', '').strip()
            material = request.POST.get('material', '').strip()
            
            # Обробка ціни - переконуємося що це float
            try:
                price_str = request.POST.get('price', '0').strip()
                price = float(price_str) if price_str else 0.0
            except (ValueError, TypeError):
                price = 0.0
            
            # Обробка наявності
            try:
                stock_str = request.POST.get('stock', '0').strip()
                stock = int(stock_str) if stock_str else 0
            except (ValueError, TypeError):
                stock = 0
            
            # Генерація slug, якщо не вказано
            if not slug and name:
                slug = generate_slug(name)
            
            # Оновлюємо основні поля
            product.name = name
            product.slug = slug
            product.category_id = category_id
            product.description = description
            product.manufacturer = manufacturer
            product.caliber = caliber
            product.barrel_length = barrel_length
            product.weight = weight
            product.material = material
            product.price = price
            product.stock = stock
            product.is_active = request.POST.get('is_active') == 'on'
            product.is_popular = request.POST.get('is_popular') == 'on'
            
            # Обробка зображень
            if 'image' in request.FILES:
                result = upload_image(request.FILES['image'], folder='products')
                if result:
                    product.image = result.get('secure_url') or result.get('url')
            elif request.POST.get('image_url'):
                product.image = request.POST.get('image_url').strip()
            
            if 'image2' in request.FILES:
                result = upload_image(request.FILES['image2'], folder='products')
                if result:
                    product.image2 = result.get('secure_url') or result.get('url')
            elif request.POST.get('image2_url'):
                product.image2 = request.POST.get('image2_url').strip()
            
            if 'image3' in request.FILES:
                result = upload_image(request.FILES['image3'], folder='products')
                if result:
                    product.image3 = result.get('secure_url') or result.get('url')
            elif request.POST.get('image3_url'):
                product.image3 = request.POST.get('image3_url').strip()
            
            if 'image4' in request.FILES:
                result = upload_image(request.FILES['image4'], folder='products')
                if result:
                    product.image4 = result.get('secure_url') or result.get('url')
            elif request.POST.get('image4_url'):
                product.image4 = request.POST.get('image4_url').strip()
            
            product.save()
            messages.success(request, 'Товар успішно оновлено')
            return redirect('firebase_admin:products')
        except Exception as e:
            messages.error(request, f'Помилка оновлення товару: {str(e)}')
    
    # Підготовка даних для відображення в шаблоні
    # Переконуємося, що всі числові поля мають правильні типи
    # Використовуємо getattr для безпечного доступу до атрибутів, які можуть не існувати
    
    # Отримуємо price і конвертуємо в рядок для відображення
    price_value = getattr(product, 'price', None)
    if price_value is not None:
        try:
            price_str = str(float(price_value))
        except (ValueError, TypeError):
            price_str = '0.00'
    else:
        price_str = '0.00'
    
    # Отримуємо stock
    stock_value = getattr(product, 'stock', None)
    if stock_value is not None:
        try:
            stock_str = str(int(stock_value))
        except (ValueError, TypeError):
            stock_str = '0'
    else:
        stock_str = '0'
    
    form_data = {
        'id': getattr(product, 'id', ''),
        'name': getattr(product, 'name', '') or '',
        'slug': getattr(product, 'slug', '') or '',
        'category_id': getattr(product, 'category_id', '') or '',
        'description': getattr(product, 'description', '') or '',
        'manufacturer': getattr(product, 'manufacturer', '') or '',
        'caliber': getattr(product, 'caliber', '') or '',
        'barrel_length': getattr(product, 'barrel_length', '') or '',
        'weight': getattr(product, 'weight', '') or '',
        'material': getattr(product, 'material', '') or '',
        'price': price_str,  # Явно конвертуємо в рядок
        'stock': stock_str,  # Явно конвертуємо в рядок
        'image': getattr(product, 'image', '') or '',
        'image2': getattr(product, 'image2', '') or '',
        'image3': getattr(product, 'image3', '') or '',
        'image4': getattr(product, 'image4', '') or '',
        'is_active': bool(getattr(product, 'is_active', True)),
        'is_popular': bool(getattr(product, 'is_popular', False)),
    }
    
    return render(request, 'admin/firebase_product_form.html', {
        'categories': categories,
        'product': product,  # Залишаємо оригінальний об'єкт для сумісності
        'form_data': form_data,  # Додаємо підготовлені дані
        'form_title': 'Редагувати товар',
    })


def firebase_product_delete(request, product_id):
    """Видалення товару"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    if request.method == 'POST':
        product = Product.get_by_id(product_id)
        if product:
            product.delete()
            messages.success(request, 'Товар успішно видалено')
        else:
            messages.error(request, 'Товар не знайдено')
    
    return redirect('firebase_admin:products')


def firebase_orders(request):
    """Керування замовленнями"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    if request.method == 'POST' and 'update_status' in request.POST:
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.get_by_id(order_id)
        if order:
            order.status = new_status
            order.save()
            messages.success(request, 'Статус замовлення оновлено')
        return redirect('firebase_admin:orders')
    
    orders = Order.get_all()
    orders = sorted(orders, key=lambda x: x.created_at if hasattr(x, 'created_at') else None, reverse=True)
    return render(request, 'admin/firebase_orders.html', {'orders': orders})


def firebase_order_detail(request, order_id):
    """Деталі замовлення для адміністратора"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    try:
        order = Order.get_by_id(order_id)
    except:
        order = None
    
    if not order:
        messages.error(request, 'Замовлення не знайдено')
        return redirect('firebase_admin:orders')
    
    context = {
        'order': order,
        'is_admin_view': True,
    }
    return render(request, 'shop/order_detail.html', context)


def firebase_users(request):
    """Керування користувачами"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    users = FirebaseUser.get_all()
    
    if request.method == 'POST':
        if 'update_user' in request.POST:
            user_id = request.POST.get('user_id')
            try:
                user = FirebaseUser.get_by_id(user_id)
                if user:
                    user.is_staff = 'is_staff' in request.POST
                    user.is_superuser = 'is_superuser' in request.POST
                    user.is_active = 'is_active' in request.POST
                    user.save()
                    messages.success(request, f'Користувач {user.username} оновлено!')
            except Exception as e:
                messages.error(request, f'Помилка оновлення користувача: {str(e)}')
        
        elif 'delete' in request.POST:
            user_id = request.POST.get('user_id')
            try:
                user = FirebaseUser.get_by_id(user_id)
                if user:
                    user.delete()
                    messages.success(request, f'Користувач {user.username} видалено!')
            except Exception as e:
                messages.error(request, f'Помилка видалення користувача: {str(e)}')
        
        return redirect('firebase_admin:users')
    
    context = {
        'users': users,
    }
    return render(request, 'admin/firebase_users.html', context)


def firebase_comments(request):
    """Керування коментарями"""
    if not is_admin(request):
        messages.error(request, 'У вас немає доступу до адмін-панелі')
        return redirect('shop:home')
    
    from datetime import datetime
    # Отримуємо всі коментарі
    all_comments = Comment.get_all()
    # Сортуємо за датою створення (від новіших до старіших)
    all_comments.sort(key=lambda x: getattr(x, 'created_at', datetime.min), reverse=True)
    
    # Фільтр за статусом
    filter_status = request.GET.get('status', 'all')
    if filter_status == 'approved':
        comments = [c for c in all_comments if getattr(c, 'is_approved', False)]
    elif filter_status == 'pending':
        comments = [c for c in all_comments if not getattr(c, 'is_approved', False)]
    else:
        comments = all_comments
    
    # Обробка дій
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        action = request.POST.get('action')
        
        if comment_id and action:
            comment = Comment.get_by_id(comment_id)
            if comment:
                if action == 'approve':
                    comment.is_approved = True
                    comment.save()
                    messages.success(request, 'Коментар схвалено')
                elif action == 'reject':
                    comment.is_approved = False
                    comment.save()
                    messages.success(request, 'Коментар відхилено')
                elif action == 'delete':
                    comment.delete()
                    messages.success(request, 'Коментар видалено')
                return redirect('firebase_admin:comments')
    
    # Отримуємо товари для відображення назв та додаємо їх до коментарів
    comments_with_products = []
    for comment in comments:
        product = None
        if comment.product_id:
            product = Product.get_by_id(comment.product_id)
        comments_with_products.append({
            'comment': comment,
            'product': product,
        })
    
    context = {
        'comments_with_products': comments_with_products,
        'filter_status': filter_status,
        'pending_count': len([c for c in all_comments if not getattr(c, 'is_approved', False)]),
        'approved_count': len([c for c in all_comments if getattr(c, 'is_approved', False)]),
    }
    return render(request, 'admin/firebase_comments.html', context)


# URL patterns для адмін-панелі Firebase
firebase_admin_urlpatterns = [
    path('firebase-admin/', firebase_admin_home, name='home'),
    path('firebase-admin/categories/', firebase_categories, name='categories'),
    path('firebase-admin/products/', firebase_products, name='products'),
    path('firebase-admin/products/add/', firebase_product_add, name='product_add'),
    path('firebase-admin/products/edit/<str:product_id>/', firebase_product_edit, name='product_edit'),
    path('firebase-admin/products/delete/<str:product_id>/', firebase_product_delete, name='product_delete'),
    path('firebase-admin/orders/', firebase_orders, name='orders'),
    path('firebase-admin/orders/<str:order_id>/', firebase_order_detail, name='order_detail'),
    path('firebase-admin/users/', firebase_users, name='users'),
    path('firebase-admin/comments/', firebase_comments, name='comments'),
]

