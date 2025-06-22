from .models import Cart, CartItem

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()

    count = CartItem.objects.filter(cart=cart).count() if cart else 0
    return {'cart_count': count}
