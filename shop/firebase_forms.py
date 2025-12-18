"""
Форми для Firebase аутентифікації
"""
from django import forms
from .firebase_auth import create_user, authenticate_user
from .firebase_models import UserProfile


class FirebaseUserRegistrationForm(forms.Form):
    """Форма реєстрації"""
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Ім\'я користувача',
        help_text='Обов\'язкове поле. До 150 символів. Тільки літери, цифри та @/./+/-/_'
    )
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=30, required=False, label='Ім\'я')
    last_name = forms.CharField(max_length=30, required=False, label='Прізвище')
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label='Пароль',
        min_length=8,
        help_text='Мінімум 8 символів'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label='Підтвердження пароля'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Перевірка на дозволені символи
            import re
            if not re.match(r'^[\w.@+-]+$', username):
                raise forms.ValidationError('Ім\'я користувача містить недозволені символи')
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Паролі не співпадають')
        if password1 and len(password1) < 8:
            raise forms.ValidationError('Пароль має бути мінімум 8 символів')
        return password2
    
    def save(self):
        """Зберегти користувача в Firebase"""
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        first_name = self.cleaned_data.get('first_name', '')
        last_name = self.cleaned_data.get('last_name', '')
        
        try:
            user = create_user(username, email, password, first_name, last_name)
            return user
        except ValueError as e:
            raise forms.ValidationError(str(e))


class FirebaseUserLoginForm(forms.Form):
    """Форма входу"""
    username = forms.CharField(
        required=True,
        label='Email або ім\'я користувача'
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label='Пароль'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            user = authenticate_user(username, password)
            if not user:
                # Додаємо помилку як non-field error (загальна помилка форми)
                raise forms.ValidationError('Невірний email/ім\'я користувача або пароль')
            cleaned_data['user'] = user
        
        return cleaned_data
    
    def get_user(self):
        """Отримати користувача"""
        return self.cleaned_data.get('user')


class FirebaseUserUpdateForm(forms.Form):
    """Форма оновлення користувача"""
    first_name = forms.CharField(max_length=30, required=False, label='Ім\'я')
    last_name = forms.CharField(max_length=30, required=False, label='Прізвище')
    email = forms.EmailField(required=True, label='Email')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            # Перевірка, чи email не зайнятий іншим користувачем
            from .firebase_models import FirebaseUser
            existing = FirebaseUser.get_by_email(email)
            if existing and existing.id != self.user.id:
                raise forms.ValidationError('Цей email вже використовується')
        return email
    
    def save(self):
        """Оновити користувача"""
        if not self.user:
            return None
        
        self.user.first_name = self.cleaned_data.get('first_name', '')
        self.user.last_name = self.cleaned_data.get('last_name', '')
        self.user.email = self.cleaned_data['email']
        self.user.save()
        return self.user


class OrderForm(forms.Form):
    """Форма замовлення"""
    first_name = forms.CharField(max_length=100, required=True, label='Ім\'я')
    last_name = forms.CharField(max_length=100, required=True, label='Прізвище')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        label='Адреса доставки'
    )
    city = forms.CharField(max_length=100, required=True, label='Місто')
    postal_code = forms.CharField(max_length=20, required=False, label='Поштовий індекс')
    payment_method = forms.ChoiceField(
        choices=[
            ('cash_on_delivery', 'Накладений платіж'),
            ('card', 'Банківська карта'),
            ('bank_transfer', 'Банківський переказ'),
        ],
        required=True,
        label='Спосіб оплати',
        initial='cash_on_delivery'
    )


class UserProfileForm(forms.Form):
    """Форма профілю користувача"""
    phone = forms.CharField(max_length=20, required=False, label='Телефон')
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Адреса'
    )
    city = forms.CharField(max_length=100, required=False, label='Місто')
    postal_code = forms.CharField(max_length=20, required=False, label='Поштовий індекс')

