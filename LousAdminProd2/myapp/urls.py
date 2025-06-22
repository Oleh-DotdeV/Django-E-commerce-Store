from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
  path('', views.hed_home, name='home'),
  path('cart/', views.cart, name='cart-page'),
  path('prof-page/', views.prof, name='prof'),
  path('favor-me/', views.favor, name='favor'),
  path('orders/', views.order, name='order'),
  path('prod-details/', views.prod, name='prod'),
  path('product/<int:pk>/', views.product_detail, name='product_detail'),
  path('delete_favor_product/<int:id>/', views.delete_favor_product, name='delete_favor_product'),
  path('reload_favor_products/', views.reload_favor_products, name='reload_favor_products'),
  path('register/', views.register, name='register'),
  path('login/', LoginView.as_view(template_name='blog/login.html', next_page='prof'), name='login'),
  path('verify_phone/', views.verify_phone, name='verify_phone'),
  path('enter_phone/', views.enter_phone, name='enter_phone'),
  path('resend-code/', views.resend_code, name='resend_code'),
  path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
  path('noprof-page/', views.noprof_view, name='noprof'),
  path('add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
  path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
  path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
  path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
  path('checkout/', views.checkout_view, name='checkout'),
  path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
]

urlpatterns += staticfiles_urlpatterns()
