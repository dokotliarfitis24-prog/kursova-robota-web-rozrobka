#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Простий скрипт для завантаження logo.png та favicon.png на Cloudinary
Запустіть: python run_upload_assets.py
"""
import os
import sys

# Додаємо поточну директорію до шляху
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weapons_shop.settings')

import django
django.setup()

from shop.cloudinary_utils import upload_image

def main():
    logo_url = None
    favicon_url = None
    
    # Завантаження logo
    logo_path = os.path.join(BASE_DIR, 'logo.png')
    if os.path.exists(logo_path):
        print("📤 Завантаження logo.png на Cloudinary...")
        try:
            with open(logo_path, 'rb') as f:
                result = upload_image(f, folder='assets', public_id='logo')
                if result:
                    logo_url = result.get('secure_url')
                    print(f"✅ Logo завантажено успішно!")
                    print(f"   URL: {logo_url}")
                    print(f"   Public ID: {result.get('public_id')}")
                else:
                    print("❌ Помилка завантаження logo")
        except Exception as e:
            print(f"❌ Помилка: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Файл logo.png не знайдено в {logo_path}")
    
    # Завантаження favicon
    favicon_path = os.path.join(BASE_DIR, 'favicon.png')
    if os.path.exists(favicon_path):
        print("\n📤 Завантаження favicon.png на Cloudinary...")
        try:
            with open(favicon_path, 'rb') as f:
                result = upload_image(f, folder='assets', public_id='favicon')
                if result:
                    favicon_url = result.get('secure_url')
                    print(f"✅ Favicon завантажено успішно!")
                    print(f"   URL: {favicon_url}")
                    print(f"   Public ID: {result.get('public_id')}")
                else:
                    print("❌ Помилка завантаження favicon")
        except Exception as e:
            print(f"❌ Помилка: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Файл favicon.png не знайдено в {favicon_path}")
    
    if logo_url and favicon_url:
        print("\n" + "="*60)
        print("📋 URL для використання в шаблонах:")
        print("="*60)
        print(f"Logo URL: {logo_url}")
        print(f"Favicon URL: {favicon_url}")
        print("="*60)
        print("\n💡 Збережіть ці URL - вони будуть використані в шаблонах!")
    elif logo_url:
        print(f"\n⚠️  Тільки logo завантажено: {logo_url}")
    elif favicon_url:
        print(f"\n⚠️  Тільки favicon завантажено: {favicon_url}")

if __name__ == '__main__':
    main()

