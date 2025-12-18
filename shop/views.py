from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal

from .models import Category, Product, Order, OrderItem, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, OrderForm, UserProfileForm, UserUpdateForm


def home(request):
    """Головна сторінка"""
    categories = Category.objects.all()[:4]
    popular_products = Product.objects.filter(is_active=True, is_popular=True)[:8]
    context = {
        'categories': categories,
        'popular_products': popular_products,
    }
    return render(request, 'shop/home.html', context)


def catalog(request):
    """Каталог товарів"""
    products = Product.objects.filter(is_active=True)
    
    # Фільтри
    category_slug = request.GET.get('category')
    weapon_type = request.GET.get('weapon_type')
    manufacturer = request.GET.get('manufacturer')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')
    search_query = request.GET.get('search')
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if weapon_type:
        products = products.filter(weapon_type=weapon_type)
    
    if manufacturer:
        products = products.filter(manufacturer__icontains=manufacturer)
    
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except:
            pass
    
    if in_stock == 'true':
        products = products.filter(stock__gt=0)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(manufacturer__icontains=search_query)
        )
    
    # Сортування
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-is_popular', '-created_at')
    else:
        products = products.order_by('-created_at')
    
    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    manufacturers = Product.objects.filter(is_active=True).values_list('manufacturer', flat=True).distinct()
    manufacturers = [m for m in manufacturers if m]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'manufacturers': sorted(manufacturers),
        'current_category': category_slug,
        'current_weapon_type': weapon_type,
        'current_manufacturer': manufacturer,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_in_stock': in_stock,
        'current_sort': sort_by,
        'search_query': search_query,
    }
    return render(request, 'shop/catalog.html', context)


def category_detail(request, category_slug):
    """Сторінка категорії"""
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Фільтри та сортування (аналогічно catalog)
    weapon_type = request.GET.get('weapon_type')
    manufacturer = request.GET.get('manufacturer')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')
    sort_by = request.GET.get('sort', 'newest')
    
    if weapon_type:
        products = products.filter(weapon_type=weapon_type)
    if manufacturer:
        products = products.filter(manufacturer__icontains=manufacturer)
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except:
            pass
    if in_stock == 'true':
        products = products.filter(stock__gt=0)
    
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-is_popular', '-created_at')
    else:
        products = products.order_by('-created_at')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    manufacturers = products.values_list('manufacturer', flat=True).distinct()
    manufacturers = [m for m in manufacturers if m]
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'manufacturers': sorted(manufacturers),
        'current_weapon_type': weapon_type,
        'current_manufacturer': manufacturer,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_in_stock': in_stock,
        'current_sort': sort_by,
    }
    return render(request, 'shop/category_detail.html', context)


def product_detail(request, product_slug):
    """Сторінка товару"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)


def add_to_cart(request, product_id):
    """Додати товар до кошика"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = request.session.get('cart', {})
    
    product_id_str = str(product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} додано до кошика')
    return redirect('shop:product_detail', product_slug=product.slug)


def remove_from_cart(request, product_id):
    """Видалити товар з кошика"""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        messages.success(request, 'Товар видалено з кошика')
    
    return redirect('shop:cart')


def update_cart(request, product_id):
    """Оновити кількість товару в кошику"""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart[product_id_str] = quantity
    else:
        if product_id_str in cart:
            del cart[product_id_str]
    
    request.session['cart'] = cart
    return redirect('shop:cart')


def cart_view(request):
    """Сторінка кошика"""
    return render(request, 'shop/cart.html')


@login_required
def checkout(request):
    """Оформлення замовлення"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Ваш кошик порожній')
        return redirect('shop:cart')
    
    # Перевірка наявності товарів
    from .models import Product
    cart_items = []
    total_price = Decimal('0.00')
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            if product.stock < quantity:
                messages.error(request, f'Недостатньо товару {product.name} на складі')
                return redirect('shop:cart')
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total,
            })
            total_price += item_total
        except Product.DoesNotExist:
            messages.error(request, 'Один з товарів більше не доступний')
            return redirect('shop:cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price
            order.save()
            
            # Створення елементів замовлення
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price,
                )
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
        if request.user.is_authenticated:
            initial_data['email'] = request.user.email
            initial_data['first_name'] = request.user.first_name
            initial_data['last_name'] = request.user.last_name
            try:
                profile = request.user.profile
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
    order = get_object_or_404(Order, id=order_id)
    if request.user.is_authenticated and order.user != request.user:
        messages.error(request, 'У вас немає доступу до цього замовлення')
        return redirect('shop:home')
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_success.html', context)


def register(request):
    """Реєстрація"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація успішна!')
            return redirect('shop:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})


def user_login(request):
    """Авторизація"""
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Вітаємо, {user.username}!')
            return redirect('shop:home')
    else:
        form = UserLoginForm()
    return render(request, 'shop/login.html', {'form': form})


def user_logout(request):
    """Вихід"""
    logout(request)
    messages.success(request, 'Ви вийшли з акаунту')
    return redirect('shop:home')


@login_required
def dashboard(request):
    """Особистий кабінет"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'shop/dashboard.html', context)


@login_required
def order_detail(request, order_id):
    """Деталі замовлення"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)


@login_required
def profile_edit(request):
    """Редагування профілю"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('shop:dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
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

