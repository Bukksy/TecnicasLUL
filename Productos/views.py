from django.shortcuts import render, redirect, get_object_or_404, redirect
from .models import Producto, Carrito, ItemCarrito, OrdenCompra, DetalleOrden
from django.contrib.auth.decorators import login_required
from django.db import transaction, models
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

# Create your views here.
@login_required
def productos_view(request):
    productos = Producto.objects.all()
    return render(request, 'productos_views.html', {'productos': productos})

@login_required
def agregar(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        stock = request.POST['stock']
        imagen = request.FILES.get('imagen', None)
        
        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen
        )
        
        return redirect('productos_views') 

    return render(request, 'add_prod.html')

@login_required
def editar(request):
    productos = Producto.objects.all()
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        return redirect('editar_producto', id=producto_id)
    return render(request, 'mod_prod.html', {'productos': productos})

@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.precio = request.POST['precio']
        producto.stock = request.POST['stock']
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES['imagen']
        producto.save()
        return redirect('productos_views')

    return render(request, 'edit_prod_form.html', {'producto': producto})

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('productos_views')


@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('producto')
    total = sum(item.subtotal() for item in items)
    return render(request, 'carrito_view.html', {'items': items, 'total': total})



@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    if cantidad <= 0:
        return JsonResponse({'error': 'La cantidad debe ser al menos 1'}, status=400)
    
    if cantidad > producto.stock:
        return JsonResponse({'error': f'No hay suficiente stock de {producto.nombre}'}, status=400)

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    
    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    item.cantidad += cantidad
    item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'mensaje': f'{producto.nombre} agregado al carrito', 'cantidad': item.cantidad})

    return redirect('ver_carrito')


@login_required
def quitar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('ver_carrito')

@login_required
def finalizar_compra(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.select_related('producto')

    if not items.exists():
        return redirect('ver_carrito')

    total = sum(item.subtotal() for item in items)

    # Crear la orden
    orden = OrdenCompra.objects.create(usuario=request.user, total=total)

    # Crear los detalles
    for item in items:
        DetalleOrden.objects.create(
            orden=orden,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio
        )
        item.producto.stock -= item.cantidad
        item.producto.save()

    # Vaciar el carrito
    items.delete()

    return render(request, 'orden_exitosa.html', {'total': total})

@login_required
def historial_ordenes(request):
    ordenes = OrdenCompra.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'historial_ordenes.html', {'ordenes': ordenes})


@staff_member_required
def limpiar_historial_compras(request):
    DetalleOrden.objects.all().delete()
    OrdenCompra.objects.all().delete()
    return redirect('productos_views')