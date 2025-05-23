from django.urls import path
from . import views

app_name = 'Home'

urlpatterns = [
    path('login', views.login, name="login"),
    path('inicio', views.inicio, name="inicio"),
    path('logout/', views.logout_view, name='logout'),
    path('resumeninventario/', views.resumenInventario, name='resumenInventario'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
    path('registro/', views.register_view, name='register_view'),
]   