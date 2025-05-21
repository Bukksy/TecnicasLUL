from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, ItemCarrito, OrdenCompra, DetalleOrden, Categoria, Categoria_producto, OnepieceCards, PokemonCard
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
import openpyxl
from django.core.paginator import Paginator

def es_admin(user):
    return user.is_staff

@login_required
@user_passes_test(es_admin)
def exportar_historial_excel(request):
    ordenes = OrdenCompra.objects.filter(usuario=request.user).order_by('-fecha')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial de Compras"

    # Encabezados
    ws.append(['ID Orden', 'Fecha', 'Producto', 'Cantidad', 'Precio Unitario', 'Subtotal', 'Total Orden'])

    for orden in ordenes:
        for detalle in orden.detalles.all():
            subtotal = detalle.cantidad * detalle.precio_unitario
            ws.append([
                orden.id,
                orden.fecha.strftime('%d/%m/%Y %H:%M'),
                detalle.producto.nombre,
                detalle.cantidad,
                detalle.precio_unitario,
                subtotal,
                orden.total,
            ])

    # Ajustar anchos de columnas
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = max_length + 2

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=historial_compras.xlsx'
    wb.save(response)
    return response

@login_required
@user_passes_test(es_admin)
def productos_view(request):
    page_number = request.GET.get('page', '1')
    
    if page_number == '1':
        productos = Producto.objects.select_related('categoria', 'CategoriaProd').all().order_by('id')
        context = {'productos': productos, 'current_page': 1}
    
    elif page_number == '2':
        onepiececards = OnepieceCards.objects.all().order_by('id')
        context = {'onepiececards': onepiececards, 'current_page': 2}
    
    elif page_number == '3':
        pokemoncards = PokemonCard.objects.all().order_by('id')
        
        pokemon_pagina = []
        for carta in pokemoncards:
            data = getattr(carta, 'data', {})
            pokemon_pagina.append({
                'id': carta.id,
                'nombre': data.get('name', 'N/A'),
                'rareza': data.get('rarity', 'N/A'),
                'set': data.get('set', {}).get('name', 'N/A'),
                'imagen': data.get('images', {}).get('small', ''),
                'precio': data.get('precio_local', 'N/A'),
                'stock': data.get('stock_local', 'N/A'),
            })
        context = {'pokemoncards': pokemon_pagina, 'current_page': 3}
    
    else:
        return redirect('/ruta/productos/?page=1')

    return render(request, 'productos_views.html', context)

@login_required
@user_passes_test(es_admin)
def agregar(request):
    categoria = Categoria.objects.all()
    categoriaprod = Categoria_producto.objects.all()
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        categoria_id = request.POST['categoria']
        categoriaprod_id = request.POST['categoriaprod']
        precio = request.POST['precio']
        stock = request.POST['stock']
        imagen = request.FILES.get('imagen')

        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            categoria_id=categoria_id,
            CategoriaProd_id=categoriaprod_id,
            precio=precio,
            stock=stock,
            imagen=imagen
        )

        return redirect('productos_views')

    return render(request, 'add_prod.html', {
        'categoria': categoria,
        'categoriaprod': categoriaprod
    })

@login_required
@user_passes_test(es_admin)
def editar(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    categorias_prod = Categoria_producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        return redirect('editar_producto', id=producto_id)

    return render(request, 'mod_prod.html', {
        'productos': productos,
        'categorias': categorias,
        'categorias_prod': categorias_prod
    })

@login_required
@user_passes_test(es_admin)
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    categorias = Categoria.objects.all()
    categorias_prod = Categoria_producto.objects.all()

    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.precio = request.POST['precio']
        producto.stock = request.POST['stock']

        categoria_id = request.POST.get('categoria')
        categoriaprod_id = request.POST.get('categoriaprod')
        
        if categoria_id:
            producto.categoria = Categoria.objects.get(id=categoria_id)
        if categoriaprod_id:
            producto.CategoriaProd = Categoria_producto.objects.get(id=categoriaprod_id)

        if request.FILES.get('imagen'):
            producto.imagen = request.FILES['imagen']
        
        producto.save()
        return redirect('productos_views')

    return render(request, 'edit_prod_form.html', {
        'producto': producto,
        'categorias': categorias,
        'categorias_prod': categorias_prod
    })

@login_required
@user_passes_test(es_admin)
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

    with transaction.atomic():
        orden = OrdenCompra.objects.create(usuario=request.user, total=total)
        for item in items:
            DetalleOrden.objects.create(
                orden=orden,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            item.producto.stock -= item.cantidad
            item.producto.save()
        items.delete()

    return render(request, 'orden_exitosa.html', {'total': total})


@login_required
@user_passes_test(es_admin)
def historial_ordenes(request):
    ordenes = OrdenCompra.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'historial_ordenes.html', {'ordenes': ordenes})


@staff_member_required
@user_passes_test(es_admin)
def limpiar_historial_compras(request):
    DetalleOrden.objects.all().delete()
    OrdenCompra.objects.all().delete()
    return redirect('productos_views')
