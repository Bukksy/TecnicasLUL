from django.urls import path
from . import views

app_name = 'VentasProductos'

urlpatterns = [
    path('cartas_pokemon', views.cartas_pokemon, name='cartas_pokemon'),
    path('cargar-mas-cartas/', views.cargar_mas_cartas, name='cargar_mas_cartas'),
    path('cartas_onepiece', views.cartas_onepiece, name='cartas_onepiece'),
    path('cartas-onepiece/cargar-mas/', views.cargar_mas_cartas_onepiece, name='cargar_mas_cartas_onepiece'),
    path('cartas-onepiece/filtrar/', views.filtrar_cartas_onepiece, name='filtrar_cartas_op')
]