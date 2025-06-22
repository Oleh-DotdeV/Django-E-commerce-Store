from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import random


class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  phone_number = models.CharField(max_length=15, blank=True, null=True)
  phone_verified = models.BooleanField(default=False)
  profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

  def __str__(self):
    return self.user.username


class FavorProd(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_products', null=True, blank=True)
  my_field = models.CharField(max_length=100, default="default_value")
  title = models.CharField(max_length=255, verbose_name="Title")
  description = models.TextField(verbose_name="Description")
  price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
  image = models.ImageField(upload_to='products/', blank=True, verbose_name="Product image")
  image_url = models.URLField(blank=True, null=True, help_text="Посилання на зображення (альтернатива завантаженню)")
  created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation")

  def __str__(self):
    return f"{self.user.username} - {self.title}"

  def get_image(self):
    """Повертає пріоритетне зображення"""
    if self.image:
      return self.image.url
    elif self.image_url:
      return self.image_url
    return ""

class Product(models.Model):
  title = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  price = models.DecimalField(max_digits=10, decimal_places=2)

  # Головне зображення: або файл, або URL
  image_file = models.ImageField(upload_to='products/main/', blank=True, null=True)
  image_url = models.URLField(blank=True, null=True,
                              help_text="Посилання на головне зображення (альтернатива завантаженню файлу)")

  is_new = models.BooleanField(default=False, help_text="Показувати як новинку")
  is_best_seller = models.BooleanField(default=False, help_text="Показувати як хіт продажу")
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title

  def clean(self):
    # Перевірка: або файл, або URL, або одне з двох
    if not self.image_file and not self.image_url:
      raise ValidationError("Вкажи або файл, або посилання на головне зображення.")
    if self.image_file and self.image_url:
      raise ValidationError("Можна вказати або файл, або посилання — не обидва.")

  def get_image(self):
    """Повертає головне зображення"""
    if self.image_file:
      return self.image_file.url
    elif self.image_url:
      return self.image_url
    return ""

  def get_additional_images(self):
    """Повертає список другорядних зображень"""
    return [img.get_image() for img in self.productimage_set.all()]


class ProductImage(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  image_file = models.ImageField(upload_to='products/additional/', blank=True, null=True)
  image_url = models.URLField(blank=True, null=True,
                              help_text="Посилання на зображення (альтернатива завантаженню файлу)")

  def clean(self):
    # Перевірка: або файл, або URL, або одне з двох
    if not self.image_file and not self.image_url:
      raise ValidationError("Необхідно вказати або файл, або посилання на зображення.")
    if self.image_file and self.image_url:
      raise ValidationError("Можна вказати або файл, або посилання — не обидва.")

    # Обмеження: максимум 5 зображень на продукт
    if self.product and self.product.productimage_set.count() >= 5 and not self.pk:
      raise ValidationError("Можна додати максимум 5 другорядних зображень до одного продукту.")

  def get_image(self):
    if self.image_file:
      return self.image_file.url
    elif self.image_url:
      return self.image_url
    return ""

  def __str__(self):
    return f"Додаткове зображення для {self.product.title}"



class Cart(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
  session_key = models.CharField(max_length=40, null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Cart (User: {self.user})" if self.user else f"Cart (Session: {self.session_key})"


class CartItem(models.Model):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)

  def __str__(self):
    return f"{self.quantity} x {self.product.title}"




def generate_order_number():
  return str(random.randint(10 ** 11, 10 ** 12 - 1))

class Order(models.Model):
  STATUS_CHOICES = [
    ('waiting', 'Waiting for'),
    ('published', 'Published'),
  ]

  DELIVERY_CHOICES = [
    ('courier', 'Courier'),
    ('post', 'Post'),
  ]

  user = models.ForeignKey(User, on_delete=models.CASCADE)
  order_number = models.CharField(max_length=12, unique=True, default=generate_order_number)
  delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Order #{self.order_number} by {self.user.username}"


class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
  product_title = models.CharField(max_length=255)
  product_price = models.DecimalField(max_digits=10, decimal_places=2)
  product_image_url = models.URLField(blank=True, null=True)

  def __str__(self):
    return self.product_title