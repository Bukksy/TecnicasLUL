from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('inicio', views.inicio, name="inicio"),
    path('logout/', views.logout_view, name='logout'),
]