from django.urls import path
from . import views

app_name='Productos'

urlpatterns = [
    path('', views.productos_view, name="productos_views"),
    path('agregar/', views.agregar, name='agregar'),
    path('editar/', views.editar, name='editar'),
    path('editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('historial/', views.historial_ordenes, name='historial_ordenes'),
    path('exportar_historial_excel/', views.exportar_historial_excel, name='exportar_historial_excel'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<str:tipo_producto>/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/confirmar/', views.confirmar_compra, name='confirmar_compra'),
    path('carrito/compra-exitosa/', views.compra_exitosa, name='compra_exitosa'),
]