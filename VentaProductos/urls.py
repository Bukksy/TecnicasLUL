from django.urls import path
from . import views

app_name = 'VentasProductos'

urlpatterns = [
    path('onepiece', views.onepiece, name='onepiece'),
    path('pokemon', views.pokemon, name='pokemon'),
    path('todo', views.todo, name='todo'),
    path('cartas_pokemon', views.cartas_pokemon, name='cartas_pokemon'),
    path('cargar-mas-cartas/', views.cargar_mas_cartas, name='cargar_mas_cartas'),
]