from django.shortcuts import render, redirect, get_object_or_404, redirect
from Productos.models import *
from django.contrib.auth.decorators import login_required
from django.db import transaction, models
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
import requests
from django.shortcuts import render


def onepiece(request):
    categoria = get_object_or_404(Categoria, nombre='One Piece')
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'OnePiece.html', {'productos': productos})

def pokemon(request):
    categoria = get_object_or_404(Categoria, nombre='Pokemon')
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'Pokemon.html', {'productos': productos})

def todo(request):
    productos = Producto.objects.all()
    return render(request, 'Todo.html', {'productos': productos})

def cartas_pokemon(request):
    return render(request, "cartas.html")  # Solo carga la base y el contenedor

def cargar_mas_cartas(request):
    page = int(request.GET.get("page", 1))
    url = f"https://api.pokemontcg.io/v2/cards?page={page}&pageSize=50"
    headers = {
        "X-Api-Key": "3ba7564d-df35-4de4-8de5-9a2ab43ff7f3"
    }
    response = requests.get(url, headers=headers)
    cartas = response.json().get("data", [])

    # Extraer solo los datos necesarios para la UI y filtros
    cartas_data = []
    for carta in cartas:
        cartas_data.append({
            "id": carta.get("id"),
            "nombre": carta.get("name"),
            "imagen": carta.get("images", {}).get("small", ""),
            "rareza": carta.get("rarity", "Desconocida"),
            "set": carta.get("set", {}).get("name", "Desconocido")
        })

    return JsonResponse({"cartas": cartas_data})

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
    item.cantidad = cantidad
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
