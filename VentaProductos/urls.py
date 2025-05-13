from django.urls import path
from . import views

app_name = 'VentasProductos'

urlpatterns = [
    path('onepiece', views.onepiece, name='onepiece'),
    path('pokemon', views.pokemon, name='pokemon'),
    path('todo', views.todo, name='todo'),
]