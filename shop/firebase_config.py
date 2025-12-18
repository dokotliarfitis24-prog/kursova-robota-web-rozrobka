"""
Firebase Firestore configuration - читає ключі з .env файлу
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Завантаження .env файлу
load_dotenv('.env')
load_dotenv('.env.local')  # Також перевіряємо .env.local

# Глобальний клієнт Firestore
_db = None

def get_db():
    """Отримати клієнт Firestore"""
    global _db
    
    if _db is not None:
        return _db
    
    # Перевірка, чи вже ініціалізовано
    if firebase_admin._apps:
        _db = firestore.client()
        return _db
    
    # Спочатку перевіряємо JSON файл (найпростіше)
    json_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if json_path and os.path.exists(json_path):
        cred = credentials.Certificate(json_path)
    else:
        # Шукаємо JSON файли з ключами
        import glob
        import os as os_module
        
        # Список можливих назв файлів
        possible_names = [
            'localproject1-e35dd-firebase-adminsdk-fbsvc-747cc464e0.json',
            '*firebase*adminsdk*.json',
            '*firebase*.json',
            '*service*account*.json',
            '*adminsdk*.json',
        ]
        
        json_file = None
        for pattern in possible_names:
            files = glob.glob(pattern)
            if files and os_module.path.exists(files[0]):
                json_file = files[0]
                break
        
        if json_file:
            cred = credentials.Certificate(json_file)
        else:
            # Читаємо ключі з .env файлу
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
            client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
            
            if project_id and private_key and client_email:
                # Використовуємо ключі з .env
                firebase_credentials = {
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                    "private_key": private_key,
                    "client_email": client_email,
                    "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                    "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                    "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL', ''),
                }
                cred = credentials.Certificate(firebase_credentials)
            else:
                raise ValueError(
                    "Не знайдено ключі Firebase!\n"
                    "Варіант 1: Завантажте Service Account JSON з Firebase Console і помістіть в корінь проекту\n"
                    "Варіант 2: Додайте в .env:\n"
                    "FIREBASE_PROJECT_ID=localproject1-e35dd\n"
                    "FIREBASE_PRIVATE_KEY=\"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n\"\n"
                    "FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@localproject1-e35dd.iam.gserviceaccount.com\n"
                    "\nДив. GET_SERVICE_ACCOUNT.md для інструкцій"
                )
    
    # Ініціалізація Firebase
    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    
    return _db

