from django.shortcuts import render, redirect
from .models import Producto

# Create your views here.
def productos_view(request):
    productos = Producto.objects.all()
    return render(request, 'productos_views.html', {'productos': productos})

def agregar(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        stock = request.POST['stock']
        imagen = request.FILES.get('imagen', None)
        
        # Crear el producto con el siguiente ID disponible
        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen
        )
        
        return redirect('productos')  # Redirige a la lista de productos o donde desees

    return render(request, 'add_prod.html')

def editar(request):
    productos = Producto.objects.all()
    return render(request, 'mod_prod.html', {'productos': productos})