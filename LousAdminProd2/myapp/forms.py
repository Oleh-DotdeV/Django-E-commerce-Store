from django import forms
from django.contrib.auth.models import User
from .models import Profile, Order

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        # Генеруємо username з first_name + last_name
        first = self.cleaned_data.get("first_name", "").strip().capitalize()
        last = self.cleaned_data.get("last_name", "").strip().capitalize()
        user.username = f"{first} {last}"

        # Перевірка унікальності username (додаємо суфікс, якщо вже існує)
        original_username = user.username
        counter = 1
        while User.objects.filter(username=user.username).exists():
            user.username = f"{original_username}{counter}"
            counter += 1

        if commit:
            user.save()
            # Створити профіль із фото
            profile, created = Profile.objects.get_or_create(user=user)
            profile.profile_image = self.cleaned_data.get('profile_image')
            profile.save()
        return user





class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_method']
        widgets = {
            'delivery_method': forms.Select(choices=Order.DELIVERY_CHOICES)
        }