"""
Views для роботи з Firebase
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from decimal import Decimal
from datetime import datetime

from .firebase_auth import login_user, logout_user, is_authenticated, is_staff, is_superuser, get_current_user
from .firebase_forms import (
    FirebaseUserRegistrationForm, 
    FirebaseUserLoginForm, 
    FirebaseUserUpdateForm, 
    UserProfileForm as FirebaseUserProfileForm,
    OrderForm
)
from .firebase_models import Category, Product, Order, OrderItem, UserProfile, FirebaseUser, Comment


def home(request):
    """Головна сторінка"""
    categories = Category.get_all(limit=4)
    popular_products = Product.get_all(
        filters=[('is_active', '==', True), ('is_popular', '==', True)],
        limit=8
    )
    context = {
        'categories': categories,
        'popular_products': popular_products,
    }
    return render(request, 'shop/home.html', context)


def catalog(request):
    """Каталог товарів"""
    filters = [('is_active', '==', True)]
    
    # Фільтри
    category_slug = request.GET.get('category')
    manufacturer = request.GET.get('manufacturer')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')
    popular = request.GET.get('popular')
    search_query = request.GET.get('search')
    
    if category_slug:
        category = Category.get_one(filters=[('slug', '==', category_slug)])
        if category:
            filters.append(('category_id', '==', category.id))
    
    if manufacturer:
        filters.append(('manufacturer', '==', manufacturer))
    
    if in_stock == 'true':
        filters.append(('stock', '>', 0))
    
    if popular == 'true':
        filters.append(('is_popular', '==', True))
    
    # Отримання всіх товарів
    products = Product.get_all(filters=filters)
    
    # Фільтрація за ціною та пошуком (в пам'яті, оскільки Firestore має обмеження)
    if min_price:
        try:
            min_price_decimal = Decimal(min_price)
            products = [p for p in products if p.price and p.price >= min_price_decimal]
        except:
            pass
    
    if max_price:
        try:
            max_price_decimal = Decimal(max_price)
            products = [p for p in products if p.price and p.price <= max_price_decimal]
        except:
            pass
    
    if search_query:
        search_lower = search_query.lower()
        products = [p for p in products if 
                    (p.name and search_lower in p.name.lower()) or
                    (p.description and search_lower in p.description.lower()) or
                    (p.manufacturer and search_lower in p.manufacturer.lower())]
    
    # Сортування
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = sorted(products, key=lambda x: x.price or 0)
    elif sort_by == 'price_desc':
        products = sorted(products, key=lambda x: x.price or 0, reverse=True)
    elif sort_by == 'popular':
        products = sorted(products, key=lambda x: (x.is_popular, x.created_at if hasattr(x, 'created_at') else None), reverse=True)
    else:
        products = sorted(products, key=lambda x: x.created_at if hasattr(x, 'created_at') else None, reverse=True)
    
    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.get_all()
    all_products = Product.get_all(filters=[('is_active', '==', True)])
    manufacturers = sorted(set([p.manufacturer for p in all_products if p.manufacturer]))
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'manufacturers': manufacturers,
        'current_category': category_slug,
        'current_manufacturer': manufacturer,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_in_stock': in_stock,
        'current_popular': popular,
        'current_sort': sort_by,
        'search_query': search_query,
    }
    return render(request, 'shop/catalog.html', context)


def category_detail(request, category_slug):
    """Сторінка категорії"""
    category = Category.get_one(filters=[('slug', '==', category_slug)])
    if not category:
        messages.error(request, 'Категорію не знайдено')
        return redirect('shop:catalog')
    
    filters = [('category_id', '==', category.id), ('is_active', '==', True)]
    
    # Фільтри
    manufacturer = request.GET.get('manufacturer')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')
    popular = request.GET.get('popular')
    sort_by = request.GET.get('sort', 'newest')
    if manufacturer:
        filters.append(('manufacturer', '==', manufacturer))
    if in_stock == 'true':
        filters.append(('stock', '>', 0))
    if popular == 'true':
        filters.append(('is_popular', '==', True))
    
    products = Product.get_all(filters=filters)
    
    # Фільтрація за ціною
    if min_price:
        try:
            min_price_decimal = Decimal(min_price)
            products = [p for p in products if p.price and p.price >= min_price_decimal]
        except:
            pass
    
    if max_price:
        try:
            max_price_decimal = Decimal(max_price)
            products = [p for p in products if p.price and p.price <= max_price_decimal]
        except:
            pass
    
    # Сортування
    if sort_by == 'price_asc':
        products = sorted(products, key=lambda x: x.price or 0)
    elif sort_by == 'price_desc':
        products = sorted(products, key=lambda x: x.price or 0, reverse=True)
    elif sort_by == 'popular':
        products = sorted(products, key=lambda x: (x.is_popular, x.created_at if hasattr(x, 'created_at') else None), reverse=True)
    else:
        products = sorted(products, key=lambda x: x.created_at if hasattr(x, 'created_at') else None, reverse=True)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    manufacturers = sorted(set([p.manufacturer for p in products if p.manufacturer]))
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'manufacturers': manufacturers,
        'current_manufacturer': manufacturer,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_in_stock': in_stock,
        'current_popular': popular,
        'current_sort': sort_by,
    }
    return render(request, 'shop/category_detail.html', context)


def product_detail(request, product_slug):
    """Сторінка товару"""
    product = Product.get_one(filters=[('slug', '==', product_slug), ('is_active', '==', True)])
    if not product:
        messages.error(request, 'Товар не знайдено')
        return redirect('shop:catalog')
    
    # Отримуємо категорію товару
    category = None
    if product.category_id:
        category = Category.get_by_id(product.category_id)
    
    # Схожі товари
    related_products = []
    if product.category_id:
        related_products = Product.get_all(
            filters=[('category_id', '==', product.category_id), ('is_active', '==', True)],
            limit=5
        )
        related_products = [p for p in related_products if p.id != product.id][:4]
    
    # Отримуємо коментарі для товару (тільки схвалені)
    from shop.firebase_models import Comment
    # Отримуємо всі коментарі для товару, потім фільтруємо та сортуємо в Python
    # Це уникне необхідності створювати складний індекс в Firestore
    all_comments = Comment.get_all(
        filters=[('product_id', '==', product.id)]
    )
    # Фільтруємо тільки схвалені та сортуємо за датою створення (від новіших до старіших)
    comments = [c for c in all_comments if getattr(c, 'is_approved', False)]
    comments.sort(key=lambda x: getattr(x, 'created_at', datetime.min), reverse=True)
    
    context = {
        'product': product,
        'category': category,
        'related_products': related_products,
        'comments': comments,
    }
    return render(request, 'shop/product_detail.html', context)


def add_to_cart(request, product_id):
    """Додати товар до кошика"""
    product = Product.get_by_id(product_id)
    if not product or not product.is_active:
        messages.error(request, 'Товар не знайдено')
        return redirect('shop:catalog')
    
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} додано до кошика')
    return redirect('shop:product_detail', product_slug=product.slug)


def remove_from_cart(request, product_id):
    """Видалити товар з кошика"""
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, 'Товар видалено з кошика')
    
    return redirect('shop:cart')


def update_cart(request, product_id):
    """Оновити кількість товару в кошику"""
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart[product_id] = quantity
    else:
        if product_id in cart:
            del cart[product_id]
    
    request.session['cart'] = cart
    return redirect('shop:cart')


def cart_view(request):
    """Сторінка кошика"""
    return render(request, 'shop/cart.html')


def checkout(request):
    """Оформлення замовлення"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Ваш кошик порожній')
        return redirect('shop:cart')
    
    # Перевірка наявності товарів
    cart_items = []
    total_price = Decimal('0.00')
    
    for product_id, quantity in cart.items():
        try:
            product = Product.get_by_id(product_id)
            if not product or not product.is_active:
                # Видаляємо неіснуючий товар з кошика
                del cart[product_id]
                continue
            
            if product.stock < quantity:
                messages.error(request, f'Недостатньо товару {product.name} на складі')
                return redirect('shop:cart')
            
            item_total = Decimal(str(product.price)) * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total,
            })
            total_price += item_total
        except:
            # Якщо товар не знайдено, пропускаємо
            continue
    
    # Оновлюємо кошик (видаляємо неіснуючі товари)
    if len(cart_items) != len(cart):
        request.session['cart'] = {item['product'].id: item['quantity'] for item in cart_items}
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            user = request.firebase_user if is_authenticated(request) else None
            order = Order(
                user_id=user.id if user else None,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data.get('postal_code', ''),
                payment_method=form.cleaned_data['payment_method'],
                total_price=float(total_price),
            )
            order.save()
            
            # Створення елементів замовлення
            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=str(item['product'].id),
                    quantity=item['quantity'],
                    price=float(item['product'].price),
                )
                order_item.save()
                
                # Оновлення наявності
                item['product'].stock -= item['quantity']
                item['product'].save()
            
            # Очищення кошика
            request.session['cart'] = {}
            
            # Відправка email
            try:
                send_mail(
                    f'Замовлення #{order.id} прийнято',
                    f'Ваше замовлення #{order.id} на суму {order.total_price} грн прийнято до обробки.',
                    settings.EMAIL_HOST_USER or 'noreply@weaponshop.com',
                    [order.email],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Замовлення успішно оформлено!')
            return redirect('shop:order_success', order_id=order.id)
    else:
        # Заповнення форми даними з профілю
        initial_data = {}
        if is_authenticated(request):
            user = request.firebase_user
            initial_data['email'] = user.email
            initial_data['first_name'] = user.first_name
            initial_data['last_name'] = user.last_name
            try:
                profile = UserProfile.get_by_user_id(user.id)
                if profile:
                    initial_data['phone'] = profile.phone
                    initial_data['address'] = profile.address
                    initial_data['city'] = profile.city
                    initial_data['postal_code'] = profile.postal_code
            except:
                pass
        form = OrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'shop/checkout.html', context)


def order_success(request, order_id):
    """Сторінка підтвердження замовлення"""
    try:
        order = Order.get_by_id(order_id)
    except:
        order = None
    
    if not order:
        messages.error(request, 'Замовлення не знайдено')
        return redirect('shop:home')
    
    user = request.firebase_user if is_authenticated(request) else None
    if user and order.user_id and order.user_id != user.id:
        messages.error(request, 'У вас немає доступу до цього замовлення')
        return redirect('shop:home')
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_success.html', context)


def register(request):
    """Реєстрація"""
    if request.method == 'POST':
        form = FirebaseUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login_user(request, user)
                messages.success(request, 'Реєстрація успішна!')
                return redirect('shop:home')
            except forms.ValidationError as e:
                messages.error(request, str(e))
    else:
        form = FirebaseUserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})


def user_login(request):
    """Авторизація"""
    if request.method == 'POST':
        form = FirebaseUserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login_user(request, user)
                messages.success(request, f'Вітаємо, {user.username}!')
                return redirect('shop:home')
            else:
                messages.error(request, 'Невірний email/ім\'я користувача або пароль')
        # Якщо форма невалідна, помилки вже додані до форми і будуть відображені в шаблоні
    else:
        form = FirebaseUserLoginForm()
    return render(request, 'shop/login.html', {'form': form})


def user_logout(request):
    """Вихід"""
    logout_user(request)
    messages.success(request, 'Ви вийшли з акаунту')
    return redirect('shop:home')


def dashboard(request):
    """Особистий кабінет"""
    if not is_authenticated(request):
        messages.error(request, 'Будь ласка, увійдіть в систему')
        return redirect('shop:login')
    
    user = request.firebase_user
    orders = Order.get_all(filters=[('user_id', '==', user.id)])
    # Сортування за датою
    orders = sorted(orders, key=lambda x: x.created_at if hasattr(x, 'created_at') else None, reverse=True)
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/dashboard.html', context)


def order_detail(request, order_id):
    """Деталі замовлення"""
    if not is_authenticated(request):
        messages.error(request, 'Будь ласка, увійдіть в систему')
        return redirect('shop:login')
    
    user = request.firebase_user
    try:
        order = Order.get_by_id(order_id)
    except:
        order = None
    
    if not order or (order.user_id and order.user_id != user.id):
        messages.error(request, 'Замовлення не знайдено')
        return redirect('shop:dashboard')
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)


def profile_edit(request):
    """Редагування профілю"""
    if not is_authenticated(request):
        messages.error(request, 'Будь ласка, увійдіть в систему')
        return redirect('shop:login')
    
    user = request.firebase_user
    profile = UserProfile.get_by_user_id(user.id)
    if not profile:
        profile = UserProfile(user_id=user.id)
    
    if request.method == 'POST':
        user_form = FirebaseUserUpdateForm(request.POST, user=user)
        profile_form = FirebaseUserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile.phone = profile_form.cleaned_data.get('phone', '')
            profile.address = profile_form.cleaned_data.get('address', '')
            profile.city = profile_form.cleaned_data.get('city', '')
            profile.postal_code = profile_form.cleaned_data.get('postal_code', '')
            profile.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('shop:dashboard')
    else:
        user_form = FirebaseUserUpdateForm(user=user)
        profile_form = FirebaseUserProfileForm(initial={
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
            'city': profile.city if profile else '',
            'postal_code': profile.postal_code if profile else '',
        })
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'shop/profile_edit.html', context)


def about(request):
    """Про нас"""
    return render(request, 'shop/about.html')


def contacts(request):
    """Контакти"""
    return render(request, 'shop/contacts.html')


def privacy_policy(request):
    """Політика конфіденційності"""
    return render(request, 'shop/privacy_policy.html')


def terms(request):
    """Умови використання"""
    return render(request, 'shop/terms.html')


def add_comment(request, product_slug):
    """Додати коментар до товару"""
    if not is_authenticated(request):
        messages.error(request, 'Для додавання коментарів необхідно увійти в систему')
        return redirect('shop:login')
    
    product = Product.get_one(filters=[('slug', '==', product_slug), ('is_active', '==', True)])
    if not product:
        messages.error(request, 'Товар не знайдено')
        return redirect('shop:catalog')
    
    if request.method == 'POST':
        from shop.firebase_models import Comment
        
        user = get_current_user(request)
        if not user:
            messages.error(request, 'Помилка автентифікації')
            return redirect('shop:login')
        
        text = request.POST.get('text', '').strip()
        rating = request.POST.get('rating')
        
        if not text:
            messages.error(request, 'Текст коментаря не може бути порожнім')
            return redirect('shop:product_detail', product_slug=product_slug)
        
        try:
            rating = int(rating) if rating else None
            if rating and (rating < 1 or rating > 5):
                rating = None
        except (ValueError, TypeError):
            rating = None
        
        # Створюємо коментар (за замовчуванням не схвалений, адміністратор може схвалити)
        comment = Comment(
            product_id=product.id,
            user_id=user.id,
            username=user.username or user.email,
            text=text,
            rating=rating,
            is_approved=False  # Коментарі потребують модерації
        )
        comment.save()
        
        messages.success(request, 'Ваш коментар додано і буде опубліковано після модерації')
        return redirect('shop:product_detail', product_slug=product_slug)
    
    return redirect('shop:product_detail', product_slug=product_slug)

