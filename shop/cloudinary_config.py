"""
Cloudinary configuration - читає ключі з .env файлу
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# Завантаження .env файлу
load_dotenv('.env')
load_dotenv('.env.local')  # Також перевіряємо .env.local

def init_cloudinary():
    """Ініціалізація Cloudinary"""
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not cloud_name or not api_key or not api_secret:
        print("⚠️  Cloudinary не налаштовано!")
        print("Додайте в .env.local:")
        print("CLOUDINARY_CLOUD_NAME=your_cloud_name")
        print("CLOUDINARY_API_KEY=your_api_key")
        print("CLOUDINARY_API_SECRET=your_api_secret")
        print("\nОтримайте ключі на https://cloudinary.com/users/register_free")
        return False
    
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True  # Використовуємо HTTPS
    )
    
    print("✅ Cloudinary успішно налаштовано!")
    return True

# Автоматична ініціалізація при імпорті (тільки один раз)
_initialized = False
if not _initialized:
    try:
        _initialized = init_cloudinary()
    except:
        pass  # Якщо помилка, просто пропускаємо

