"""
Команда для створення суперкористувача в Firebase
"""
from django.core.management.base import BaseCommand
from shop.firebase_auth import create_user
from shop.firebase_models import FirebaseUser


class Command(BaseCommand):
    help = 'Створити суперкористувача в Firebase'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Ім\'я користувача')
        parser.add_argument('--email', type=str, help='Email')
        parser.add_argument('--password', type=str, help='Пароль')

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')

        if not username:
            username = input('Ім\'я користувача: ')
        if not email:
            email = input('Email: ')
        if not password:
            from getpass import getpass
            password = getpass('Пароль: ')

        try:
            # Створюємо користувача
            user = create_user(username, email, password)
            
            # Робимо його суперкористувачем
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Суперкористувач {username} успішно створено!')
            )
        except ValueError as e:
            self.stdout.write(
                self.style.ERROR(f'Помилка: {str(e)}')
            )

