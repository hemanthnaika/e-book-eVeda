# context_processors.py
from .models import Cart

def cart_context(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_items = cart.get_total_items()
            return {'cart_item_count': total_items}
        except Cart.DoesNotExist:
            return {'cart_item_count': 0}
    return {'cart_item_count': 0}
