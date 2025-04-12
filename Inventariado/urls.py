from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('Productos', include('Productos.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
