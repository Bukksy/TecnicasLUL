from django.urls import path
from . import views

app_name = 'InicioPagina'

urlpatterns = [
    path('', views.inicio, name='inicio'),
]