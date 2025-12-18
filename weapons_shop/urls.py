"""
URL configuration for weapons_shop project.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop.firebase_admin import firebase_admin_urlpatterns

urlpatterns = [
    # path('admin/', admin.site.urls),  # Видалено - використовуємо Firebase адмінку
    path('', include('shop.urls')),
    path('', include((firebase_admin_urlpatterns, 'firebase_admin'), namespace='firebase_admin')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



