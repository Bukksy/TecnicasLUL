from django.urls import path
from . import views

urlpatterns = [
    path('', views.productos_view, name="productos_views"),
    path('agregar/', views.agregar, name='agregar'),
    path('editar/', views.editar, name='editar'),
    path('editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/quitar/<int:item_id>/', views.quitar_del_carrito, name='quitar_del_carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('historial/', views.historial_ordenes, name='historial_ordenes'),
    path('limpiar-historial/', views.limpiar_historial_compras, name='limpiar_historial'),
    path('exportar_historial_excel/', views.exportar_historial_excel, name='exportar_historial_excel'),


]