"""
Django management command для завантаження logo та favicon на Cloudinary
"""
from django.core.management.base import BaseCommand
import os
from shop.cloudinary_utils import upload_image


class Command(BaseCommand):
    help = 'Завантажити logo.png та favicon.png на Cloudinary'

    def handle(self, *args, **options):
        from django.conf import settings
        base_dir = settings.BASE_DIR
        
        logo_url = None
        favicon_url = None
        
        # Завантаження logo
        logo_path = os.path.join(base_dir, 'logo.png')
        if os.path.exists(logo_path):
            self.stdout.write('📤 Завантаження logo.png на Cloudinary...')
            try:
                with open(logo_path, 'rb') as f:
                    result = upload_image(f, folder='assets', public_id='logo')
                    if result:
                        logo_url = result.get('secure_url')
                        self.stdout.write(self.style.SUCCESS(f'✅ Logo завантажено успішно!'))
                        self.stdout.write(f'   URL: {logo_url}')
                        self.stdout.write(f'   Public ID: {result.get("public_id")}')
                    else:
                        self.stdout.write(self.style.ERROR('❌ Помилка завантаження logo'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Помилка: {e}'))
        else:
            self.stdout.write(self.style.ERROR('❌ Файл logo.png не знайдено'))
        
        # Завантаження favicon
        favicon_path = os.path.join(base_dir, 'favicon.png')
        if os.path.exists(favicon_path):
            self.stdout.write('\n📤 Завантаження favicon.png на Cloudinary...')
            try:
                with open(favicon_path, 'rb') as f:
                    result = upload_image(f, folder='assets', public_id='favicon')
                    if result:
                        favicon_url = result.get('secure_url')
                        self.stdout.write(self.style.SUCCESS(f'✅ Favicon завантажено успішно!'))
                        self.stdout.write(f'   URL: {favicon_url}')
                        self.stdout.write(f'   Public ID: {result.get("public_id")}')
                    else:
                        self.stdout.write(self.style.ERROR('❌ Помилка завантаження favicon'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Помилка: {e}'))
        else:
            self.stdout.write(self.style.ERROR('❌ Файл favicon.png не знайдено'))
        
        if logo_url and favicon_url:
            self.stdout.write('\n' + '='*60)
            self.stdout.write('📋 URL для використання в шаблонах:')
            self.stdout.write('='*60)
            self.stdout.write(f'Logo URL: {logo_url}')
            self.stdout.write(f'Favicon URL: {favicon_url}')
            self.stdout.write('='*60)

