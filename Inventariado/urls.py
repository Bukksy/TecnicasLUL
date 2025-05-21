from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('inicio/', include('InicioPagina.urls')),
    path('productos/', include('Productos.urls')),
    path('venta/', include('VentaProductos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)