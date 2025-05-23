from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Home/', include('Home.urls')),
    path('', include('InicioPagina.urls', namespace='Productos')),
    path('productos/', include('Productos.urls', namespace='InicioClientes')),
    path('venta/', include('VentaProductos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)