from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import random
import json
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from functools import wraps

User = get_user_model()



def reload_favor_products(request):
    favor_prod = FavorProd.objects.all()
    html = render_to_string('partials/favor_products.html', {'favor_prod': favor_prod})
    return JsonResponse({'html': html})

@csrf_exempt
def add_to_favorites(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            FavorProd.objects.create(
                title=product.title,
                description=product.description,
                price=product.price,
                image_url=product.image_url
            )
            return JsonResponse({'status': 'ok'})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        try:
            if user:
                cart_item = CartItem.objects.get(cart__user=user, product_id=product_id)
            else:
                cart_item = CartItem.objects.get(cart__session_key=session_key, product_id=product_id)

            cart_item.delete()
            return JsonResponse({'status': 'ok'})
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



@csrf_exempt
def update_cart_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if not product_id or not quantity:
            return JsonResponse({'status': 'error', 'message': 'Missing data'})

        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(cart__user=request.user, product_id=product_id).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                return JsonResponse({'status': 'error', 'message': 'No session'})
            cart_item = CartItem.objects.filter(cart__session_key=session_key, product_id=product_id).first()

        if cart_item:
            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error', 'message': 'Item not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

def hed_home(request):
  new_arrivals = Product.objects.filter(is_new=True).order_by('-created_at')[:8]
  best_sellers = Product.objects.filter(is_best_seller=True)[:8]

  categories = [
    {"key": "new", "title": "New",
     "img": "https://images.pexels.com/photos/1183266/pexels-photo-1183266.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"},
    {"key": "womens", "title": "Women's Clothing",
     "img": "https://images.pexels.com/photos/1536619/pexels-photo-1536619.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"},
    {"key": "mens", "title": "Men's Clothing",
     "img": "https://images.pexels.com/photos/1148960/pexels-photo-1148960.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"},
    {"key": "accessories", "title": "Accessories",
     "img": "https://images.pexels.com/photos/1158905/pexels-photo-1158905.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"},
    {"key": "discounts", "title": "Discounts",
     "img": "https://images.pexels.com/photos/1488463/pexels-photo-1488463.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"},
  ]

  context = {
    'new_arrivals': new_arrivals,
    'best_sellers': best_sellers,
    'categories': categories
  }

  return render(request, 'hed.html', context)


@property
def get_image(self):
    if self.image:
        return self.image.url
    elif self.image_url:
        return self.image_url
    return ""


def get_cart_for_user_or_session(request):
  if request.user.is_authenticated:
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
      cart = Cart.objects.create(user=request.user)
  else:
    session_key = request.session.session_key
    if not session_key:
      request.session.create()
      session_key = request.session.session_key
    cart = Cart.objects.filter(session_key=session_key).first()
    if not cart:
      cart = Cart.objects.create(session_key=session_key)
  return cart


@csrf_exempt
def update_cart_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        # логіка пошуку CartItem і оновлення кількості
        cart = get_cart_for_user_or_session(request)  # твоя логіка отримання корзини
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.quantity = quantity
        cart_item.save()

        # підрахунок subtotal
        cart_items = CartItem.objects.filter(cart=cart)
        subtotal = sum(item.product.price * item.quantity for item in cart_items)

        return JsonResponse({'status': 'ok', 'subtotal': float(subtotal)})


def cart(request):
  sizes = ["XS", "S", "M", "L", "XL", "XXL"]

  if request.user.is_authenticated:
    cart = Cart.objects.filter(user=request.user).first()
  else:
    session_key = request.session.session_key
    if not session_key:
      request.session.create()
      session_key = request.session.session_key
    cart = Cart.objects.filter(session_key=session_key).first()

  cart_items = CartItem.objects.filter(cart=cart) if cart else []

  for item in cart_items:
    item.random_size = random.choice(sizes)

  favor_prod = FavorProd.objects.all()

  # Підрахунок підсумкової вартості (subtotal)
  subtotal = sum(item.product.price * item.quantity for item in cart_items)

  return render(request, 'cart.html', {
    'cart_items': cart_items,
    'favor_prod': favor_prod,
    'subtotal': subtotal,
  })


def get_cart_count(request):
  if request.user.is_authenticated:
    cart = Cart.objects.filter(user=request.user).first()
  else:
    session_key = request.session.session_key
    if not session_key:
      request.session.create()
      session_key = request.session.session_key
    cart = Cart.objects.filter(session_key=session_key).first()

  count = CartItem.objects.filter(cart=cart).count() if cart else 0
  return JsonResponse({'count': count})


def redirect_if_not_authenticated(view_func):
  @wraps(view_func)
  def wrapper(request, *args, **kwargs):
    if not request.user.is_authenticated:
      return redirect('noprof')  # або '/noprof/' якщо не використовуєш ім'я URL
    return view_func(request, *args, **kwargs)

  return wrapper

@redirect_if_not_authenticated
def prof(request):
  profile = Profile.objects.get(user=request.user)
  if request.method == 'POST':
    user = request.user
    user.first_name = request.POST.get('first_name', user.first_name)
    user.last_name = request.POST.get('last_name', user.last_name)
    user.email = request.POST.get('email', user.email)
    new_password = request.POST.get('new_password')
    if new_password and new_password != '********':
      user.set_password(new_password)
      update_session_auth_hash(request, user)
    user.save()
    profile.phone_number = request.POST.get('phone_number', profile.phone_number)
    profile.save()
    return redirect('prof')

  return render(request, 'prof.html', {"profile": profile})



def noprof_view(request):
  return render(request, 'noprof.html')


@redirect_if_not_authenticated
def favor(request):
  favor_prod = FavorProd.objects.all()
  new_arrivals = Product.objects.filter(is_new=True).order_by('-created_at')[:8]

  context = {
    'favor_prod': favor_prod,
    'new_arrivals': new_arrivals,
  }
  return render(request, 'favor.html', context)

@require_POST
@csrf_exempt
def delete_favor_product(request, id):
  product = get_object_or_404(FavorProd, id=id)
  if request.method == 'POST':
    product.delete()
    return JsonResponse({'status': 'success', 'message': 'Product removed from favorites'})

  return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def order(request):
  new_arrivals = Product.objects.filter(is_new=True).order_by('-created_at')[:8]
  orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
  return render(request, 'order.html', {
    'new_arrivals': new_arrivals,
    'orders': orders
  })

def product_detail(request, pk):
  product = get_object_or_404(Product, pk=pk)
  de_prod = ProductImage.objects.all()
  new_arrivals = Product.objects.filter(is_new=True).order_by('-created_at')[:8]
  return render(request, 'prod-detail.html', {
    'product': product,
    'de_prod': de_prod,
    'new_arrivals': new_arrivals
  })

def prod(request):
  favor_prod = FavorProd.objects.all()
  return render(request, 'prod-detail.html', {
    "favor_prod": favor_prod
  })


def register(request):
  if request.method == "POST":
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      request.session['user_id'] = user.id
      # код буде введено пізніше, тому логін після verify_phone
      return redirect("enter_phone")
  else:
    form = CustomUserCreationForm()
  return render(request, "blog/register.html", {"form": form})


def enter_phone(request):
  if request.method == "POST":
    phone_number = request.POST.get('phone_number')
    user_id = request.session.get('user_id')
    if user_id:
      user = User.objects.get(id=user_id)
      profile, created = Profile.objects.get_or_create(user=user)
      profile.phone_number = phone_number
      profile.phone_verified = False
      profile.save()

      # Генеруємо код і кладемо у сесію
      verification_code = str(random.randint(100000, 999999))
      request.session['verification_code'] = verification_code

      return redirect('verify_phone')
  return render(request, "blog/enter_phone.html")


def verify_phone(request):
  if request.method == "POST":
    entered_code = request.POST.get('code')
    real_code = request.session.get('verification_code')

    if entered_code == real_code:
      user_id = request.session.get('user_id')
      if user_id:
        user = User.objects.get(id=user_id)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.phone_verified = True
        profile.save()

      # Видаляємо код тільки якщо він існує
      if 'verification_code' in request.session:
        del request.session['verification_code']

      # Логінимо користувача після верифікації
      login(request, user)

      return redirect('home')
    else:
      return render(request, 'blog/verify_phone.html', {
        'error': 'Invalid code. Please try again.',
        'verification_code': real_code
      })

  return render(request, 'blog/verify_phone.html', {
    'verification_code': request.session.get('verification_code')
  })


def resend_code(request):
  # Генеруємо новий код
  new_code = str(random.randint(100000, 999999))
  request.session['verification_code'] = new_code

  # Можна додати повідомлення, що код надіслано знову
  return render(request, 'blog/verify_phone.html', {
    'message': 'Verification code resent. Please check.'
  })


def add_to_cart(request, product_id):
  product = get_object_or_404(Product, pk=product_id)

  # Якщо користувач залогінений — прив'язуємо до user
  if request.user.is_authenticated:
    cart, created = Cart.objects.get_or_create(user=request.user)
  else:
    # Якщо не залогінений — використовуємо session_key
    session_key = request.session.session_key
    if not session_key:
      request.session.create()
      session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)

  # Додати товар до корзини
  item, created = CartItem.objects.get_or_create(cart=cart, product=product)
  if not created:
    item.quantity += 1
    item.save()

  return JsonResponse({'message': '✅ Додано до кошика'})



@login_required
def checkout_view(request):
    cart = get_cart_for_user_or_session(request)
    cart_items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            # Створюємо OrderItem для кожного товару в корзині
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_title=item.product.title,
                    product_price=item.product.price,
                    product_image_url=item.product.get_image()
                )

            # Очищуємо корзину
            cart_items.delete()

            return redirect('home')  # або сторінка успішного оформлення
    else:
        form = OrderForm()

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
    })