from decimal import Decimal


def cart(request):
    """Контекстний процесор для кошика"""
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = Decimal('0.00')
    total_items = 0

    from .firebase_models import Product

    for product_id, quantity in cart.items():
        try:
            product = Product.get_by_id(product_id)
            if product and product.is_active:
                item_total = Decimal(str(product.price)) * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total,
                })
                total_price += item_total
                total_items += quantity
        except:
            continue

    return {
        'cart_items': cart_items,
        'cart_total': total_price,
        'cart_items_count': total_items,
    }

