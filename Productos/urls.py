from django.urls import path
from . import views

urlpatterns = [
    path(' ', views.productos_view, name="productos_views"),
    path('agregar/', views.agregar, name='agregar'),
    path('editar/', views.editar, name='editar'),
     path('editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
]