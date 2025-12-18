"""
Утиліти для роботи з Cloudinary
"""
import cloudinary.uploader
import cloudinary.api
from .cloudinary_config import init_cloudinary

def upload_image(file, folder='products', public_id=None):
    """
    Завантажити зображення в Cloudinary
    
    Args:
        file: Django UploadedFile або файловий об'єкт
        folder: Папка в Cloudinary (за замовчуванням 'products')
        public_id: Унікальний ID для зображення (опціонально)
    
    Returns:
        dict: {'url': str, 'public_id': str, 'secure_url': str} або None при помилці
    """
    if not init_cloudinary():
        return None
    
    try:
        # Завантаження зображення
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            public_id=public_id,
            resource_type='image',
            transformation=[
                {'quality': 'auto:good'},  # Автоматична оптимізація якості
                {'fetch_format': 'auto'},  # Автоматичний формат (WebP, якщо підтримується)
            ]
        )
        
        return {
            'url': result.get('url'),
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'width': result.get('width'),
            'height': result.get('height'),
            'format': result.get('format'),
            'bytes': result.get('bytes'),
        }
    except Exception as e:
        print(f"❌ Помилка завантаження зображення: {e}")
        return None


def upload_image_from_url(image_url, folder='products', public_id=None):
    """
    Завантажити зображення з URL в Cloudinary
    
    Args:
        image_url: URL зображення
        folder: Папка в Cloudinary
        public_id: Унікальний ID для зображення (опціонально)
    
    Returns:
        dict: {'url': str, 'public_id': str, 'secure_url': str} або None при помилці
    """
    if not init_cloudinary():
        return None
    
    try:
        result = cloudinary.uploader.upload(
            image_url,
            folder=folder,
            public_id=public_id,
            resource_type='image',
            transformation=[
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'},
            ]
        )
        
        return {
            'url': result.get('url'),
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'width': result.get('width'),
            'height': result.get('height'),
            'format': result.get('format'),
            'bytes': result.get('bytes'),
        }
    except Exception as e:
        print(f"❌ Помилка завантаження зображення з URL: {e}")
        return None


def delete_image(public_id):
    """
    Видалити зображення з Cloudinary
    
    Args:
        public_id: Public ID зображення в Cloudinary
    
    Returns:
        bool: True якщо успішно видалено
    """
    if not init_cloudinary():
        return False
    
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"❌ Помилка видалення зображення: {e}")
        return False


def get_image_url(public_id, transformation=None):
    """
    Отримати URL зображення з Cloudinary з трансформаціями
    
    Args:
        public_id: Public ID зображення
        transformation: Словник з параметрами трансформації
            Приклад: {'width': 500, 'height': 500, 'crop': 'fill', 'quality': 'auto'}
    
    Returns:
        str: URL зображення
    """
    if not init_cloudinary():
        return None
    
    try:
        if transformation:
            url = cloudinary.CloudinaryImage(public_id).build_url(**transformation)
        else:
            url = cloudinary.CloudinaryImage(public_id).build_url()
        return url
    except Exception as e:
        print(f"❌ Помилка отримання URL: {e}")
        return None


def get_optimized_url(image_url, width=None, height=None, crop='fill', quality='auto'):
    """
    Отримати оптимізований URL зображення (якщо воно вже в Cloudinary)
    або повернути оригінальний URL
    
    Args:
        image_url: URL зображення
        width: Ширина
        height: Висота
        crop: Метод обрізання ('fill', 'fit', 'scale', 'thumb')
        quality: Якість ('auto', 'auto:good', 'auto:best', або число 1-100)
    
    Returns:
        str: Оптимізований URL
    """
    # Якщо URL вже з Cloudinary, можна додати трансформації
    if 'cloudinary.com' in image_url:
        # Додаємо трансформації до URL
        parts = image_url.split('/upload/')
        if len(parts) == 2:
            base = parts[0] + '/upload/'
            path = parts[1]
            
            transformations = []
            if width or height:
                if width:
                    transformations.append(f'w_{width}')
                if height:
                    transformations.append(f'h_{height}')
                if crop:
                    transformations.append(f'c_{crop}')
            if quality:
                transformations.append(f'q_{quality}')
            
            if transformations:
                transform_str = ','.join(transformations)
                return f"{base}{transform_str}/{path}"
    
    return image_url

