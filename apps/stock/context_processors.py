from .models import Cart


def cart_context(request):
    cart_count = 0
    cart_total = 0
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            cart_count = cart.total_items
            cart_total = cart.total_price
        except Cart.DoesNotExist:
            pass
    return {
        "cart_count": cart_count,
        "cart_total": cart_total,
    }
