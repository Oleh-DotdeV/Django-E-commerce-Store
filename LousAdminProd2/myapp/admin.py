from django.contrib import admin
from .models import *


@admin.register(FavorProd, Profile, Product, ProductImage, Cart, CartItem, Order, OrderItem)
class MyModelAdmin(admin.ModelAdmin):
  list_per_page = 20
  list_select_related = True
