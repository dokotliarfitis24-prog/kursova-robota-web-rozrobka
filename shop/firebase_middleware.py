"""
Middleware для Firebase аутентифікації
"""
from .firebase_auth import get_current_user


class FirebaseAuthMiddleware:
    """Middleware для додавання Firebase користувача в request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Додаємо user в request (для сумісності з Django)
        request.user = FirebaseUserWrapper(request)
        request.firebase_user = get_current_user(request)
        
        response = self.get_response(request)
        return response


class FirebaseUserWrapper:
    """Обгортка для сумісності з Django request.user"""
    
    def __init__(self, request):
        self.request = request
        self._user = None
    
    @property
    def user(self):
        """Отримати Firebase користувача"""
        if self._user is None:
            from .firebase_auth import get_current_user
            self._user = get_current_user(self.request)
        return self._user
    
    @property
    def is_authenticated(self):
        """Перевірка авторизації"""
        return self.user is not None
    
    @property
    def is_anonymous(self):
        """Перевірка, чи користувач анонімний"""
        return not self.is_authenticated
    
    @property
    def id(self):
        """ID користувача"""
        return self.user.id if self.user else None
    
    @property
    def username(self):
        """Username користувача"""
        return self.user.username if self.user else None
    
    @property
    def email(self):
        """Email користувача"""
        return self.user.email if self.user else None
    
    @property
    def first_name(self):
        """Ім'я користувача"""
        return self.user.first_name if self.user else ''
    
    @property
    def last_name(self):
        """Прізвище користувача"""
        return self.user.last_name if self.user else ''
    
    @property
    def is_staff(self):
        """Перевірка, чи користувач адміністратор"""
        return self.user.is_staff if self.user else False
    
    @property
    def is_superuser(self):
        """Перевірка, чи користувач суперкористувач"""
        return self.user.is_superuser if self.user else False
    
    def __str__(self):
        return self.username or self.email or 'AnonymousUser'

