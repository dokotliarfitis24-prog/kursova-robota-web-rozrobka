"""
Firebase Authentication - заміна Django auth
"""
import hashlib
import secrets
from datetime import datetime
from django.contrib.sessions.models import Session
from .firebase_models import FirebaseUser
from .firebase_config import get_db


def hash_password(password: str) -> str:
    """Хешування пароля"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Перевірка пароля"""
    return hash_password(password) == hashed


def create_user(username: str, email: str, password: str, first_name: str = '', last_name: str = '') -> FirebaseUser:
    """Створити нового користувача"""
    # Перевірка, чи користувач з таким username або email вже існує
    existing_username = FirebaseUser.get_one(filters=[('username', '==', username)])
    if existing_username:
        raise ValueError('Користувач з таким ім\'ям вже існує')
    
    existing_email = FirebaseUser.get_one(filters=[('email', '==', email)])
    if existing_email:
        raise ValueError('Користувач з таким email вже існує')
    
    # Створення користувача
    user = FirebaseUser(
        username=username,
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )
    user.save()
    return user


def authenticate_user(username_or_email: str, password: str) -> FirebaseUser:
    """Аутентифікація користувача"""
    # Спробуємо знайти по username
    user = FirebaseUser.get_one(filters=[('username', '==', username_or_email)])
    
    # Якщо не знайдено, спробуємо по email
    if not user:
        user = FirebaseUser.get_one(filters=[('email', '==', username_or_email)])
    
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def login_user(request, user: FirebaseUser):
    """Увійти як користувач (зберігаємо в сесії Django)"""
    # Зберігаємо user_id в сесії Django
    request.session['firebase_user_id'] = user.id
    request.session['firebase_user_username'] = user.username
    request.session['firebase_user_email'] = user.email
    request.session['firebase_user_is_staff'] = user.is_staff
    request.session['firebase_user_is_superuser'] = user.is_superuser
    request.session.save()


def logout_user(request):
    """Вийти (очистити сесію)"""
    if 'firebase_user_id' in request.session:
        del request.session['firebase_user_id']
        del request.session['firebase_user_username']
        del request.session['firebase_user_email']
        del request.session['firebase_user_is_staff']
        del request.session['firebase_user_is_superuser']
        request.session.save()


def get_current_user(request) -> FirebaseUser:
    """Отримати поточного користувача з сесії"""
    user_id = request.session.get('firebase_user_id')
    if not user_id:
        return None
    
    try:
        user = FirebaseUser.get_by_id(user_id)
        if user and user.is_active:
            return user
    except:
        pass
    
    return None


def is_authenticated(request) -> bool:
    """Перевірка, чи користувач авторизований"""
    return get_current_user(request) is not None


def is_staff(request) -> bool:
    """Перевірка, чи користувач є адміністратором"""
    user = get_current_user(request)
    return user is not None and (user.is_staff or user.is_superuser)


def is_superuser(request) -> bool:
    """Перевірка, чи користувач є суперкористувачем"""
    user = get_current_user(request)
    return user is not None and user.is_superuser

