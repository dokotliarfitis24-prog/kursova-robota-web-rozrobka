#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# Налаштування Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weapons_shop.settings')
django.setup()

from shop.cloudinary_utils import upload_image

# Завантаження logo
logo_path = os.path.join(BASE_DIR, 'logo.png')
if os.path.exists(logo_path):
    print("📤 Завантаження logo.png на Cloudinary...")
    with open(logo_path, 'rb') as f:
        result = upload_image(f, folder='assets', public_id='logo')
        if result:
            logo_url = result.get('secure_url')
            print(f"✅ Logo завантажено!")
            print(f"URL: {logo_url}")
        else:
            print("❌ Помилка завантаження logo")
else:
    print("❌ Файл logo.png не знайдено")
    logo_url = None

# Завантаження favicon
favicon_path = os.path.join(BASE_DIR, 'favicon.png')
if os.path.exists(favicon_path):
    print("\n📤 Завантаження favicon.png на Cloudinary...")
    with open(favicon_path, 'rb') as f:
        result = upload_image(f, folder='assets', public_id='favicon')
        if result:
            favicon_url = result.get('secure_url')
            print(f"✅ Favicon завантажено!")
            print(f"URL: {favicon_url}")
        else:
            print("❌ Помилка завантаження favicon")
else:
    print("❌ Файл favicon.png не знайдено")
    favicon_url = None

if logo_url and favicon_url:
    print("\n" + "="*60)
    print("📋 URL для використання:")
    print("="*60)
    print(f"Logo: {logo_url}")
    print(f"Favicon: {favicon_url}")
    print("="*60)

