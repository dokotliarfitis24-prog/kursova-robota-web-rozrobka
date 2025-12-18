"""
Скрипт для завантаження logo.png та favicon.png на Cloudinary
"""
import os
import sys
import django

# Налаштування Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weapons_shop.settings')
django.setup()

from shop.cloudinary_utils import upload_image

def upload_logo_and_favicon():
    """Завантажити logo та favicon на Cloudinary"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Завантаження logo
    logo_path = os.path.join(base_dir, 'logo.png')
    if os.path.exists(logo_path):
        print("📤 Завантаження logo.png на Cloudinary...")
        with open(logo_path, 'rb') as f:
            result = upload_image(f, folder='assets', public_id='logo')
            if result:
                print(f"✅ Logo завантажено успішно!")
                print(f"   URL: {result.get('secure_url')}")
                print(f"   Public ID: {result.get('public_id')}")
                return result.get('secure_url')
            else:
                print("❌ Помилка завантаження logo")
    else:
        print("❌ Файл logo.png не знайдено")
    
    # Завантаження favicon
    favicon_path = os.path.join(base_dir, 'favicon.png')
    if os.path.exists(favicon_path):
        print("\n📤 Завантаження favicon.png на Cloudinary...")
        with open(favicon_path, 'rb') as f:
            result = upload_image(f, folder='assets', public_id='favicon')
            if result:
                print(f"✅ Favicon завантажено успішно!")
                print(f"   URL: {result.get('secure_url')}")
                print(f"   Public ID: {result.get('public_id')}")
                return result.get('secure_url')
            else:
                print("❌ Помилка завантаження favicon")
    else:
        print("❌ Файл favicon.png не знайдено")

if __name__ == '__main__':
    upload_logo_and_favicon()

