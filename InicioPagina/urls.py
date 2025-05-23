from django.urls import path
from . import views

app_name='InicioClientes'

urlpatterns = [
    path('', views.inicio, name='inicio'),
]