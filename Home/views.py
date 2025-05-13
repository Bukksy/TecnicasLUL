import openpyxl
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Productos.models import Producto, DetalleOrden
from django.db.models import Avg, Sum
from django.contrib.auth.decorators import user_passes_test
import json

def es_admin(user):
    return user.is_staff

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  
            return redirect('inicio')  
        else:
            messages.error(request, "Usuario o contraseña incorrectos") 

        return redirect('login')

    return render(request, 'login.html')

@login_required
def inicio(request):
    if request.user.is_staff:
        return render(request, 'inicio.html')
    else:
        return redirect('InicioPagina:inicio')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(es_admin)
def resumenInventario(request):
    productos = Producto.objects.all()

    total_productos = productos.count()
    stock_total = productos.aggregate(Sum('stock'))['stock__sum'] or 0
    precio_promedio = productos.aggregate(Avg('precio'))['precio__avg'] or 0

    labels = json.dumps([p.nombre for p in productos])
    datos_stock = json.dumps([p.stock for p in productos])
    productos_mas_vendidos = (
        DetalleOrden.objects
        .values('producto__nombre')
        .annotate(total_vendidos=Sum('cantidad'))
        .order_by('-total_vendidos')[:5]
    )


    context = {
        'productos': productos,
        'total_productos': total_productos,
        'stock_total': stock_total,
        'precio_promedio': round(precio_promedio, 2),
        'labels': labels,
        'datos_stock': datos_stock,
        'productos_mas_vendidos': productos_mas_vendidos
    }

    return render(request, 'resumenInventario.html', context)

@login_required
@user_passes_test(es_admin)
def exportar_excel(request):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = 'Productos'

    headers = ['ID', 'Nombre', 'Descripción', 'Precio', 'Stock']
    sheet.append(headers)


    productos = Producto.objects.all()
    for producto in productos:
        sheet.append([producto.id, producto.nombre, producto.descripcion, producto.precio, producto.stock])


    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=productos.xlsx'

    wb.save(response)
    return response
