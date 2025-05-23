from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, ItemCarrito, OrdenCompra, DetalleOrden, Categoria, Categoria_producto, OnepieceCards, PokemonCard
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
import openpyxl
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType


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
            producto = detalle.producto
            nombre_producto = getattr(producto, 'nombre', str(producto))  # Usa 'nombre' o el string del objeto
            subtotal = detalle.cantidad * detalle.precio_unitario

            ws.append([
                orden.id,
                orden.fecha.strftime('%d/%m/%Y %H:%M'),
                nombre_producto,
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
        productos = Producto.objects.filter(id__isnull=False).select_related('categoria', 'CategoriaProd').order_by('id')
        productos_data = []
        for carta in productos:
            productos_data.append({
                'id': carta.id,
                'nombre': carta.nombre,
                'descripcion': carta.descripcion,
                'imagen': carta.imagen,
                'precio': carta.precio,
                'stock': carta.stock,
            })
        context = {'productos': productos_data, 'current_page': 1}
    
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

        return redirect('Productos:productos_views')

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
        return redirect('Productos:editar_producto', id=producto_id)

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
        return redirect('Productos:productos_views')

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
    return redirect('Productos:productos_views')

@login_required
@user_passes_test(es_admin)
def historial_ordenes(request):
    ordenes = OrdenCompra.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'historial_ordenes.html', {'ordenes': ordenes})

@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    productos_carrito = carrito.items.all()
    
    carrito_total = 0
    for item in productos_carrito:
        carrito_total += item.subtotal

    context = {
        'carrito': carrito,
        'productos_carrito': productos_carrito,
        'carrito_total': carrito_total,
    }
    return render(request, 'carrito/ver_carrito.html', context)

@login_required
def agregar_al_carrito(request, tipo_producto, producto_id):
    modelos = {
        'producto': Producto,
        'onepiececard': OnepieceCards,
        'pokemoncard': PokemonCard,
    }

    modelo = modelos.get(tipo_producto.lower())
    if not modelo:
        messages.error(request, "Tipo de producto inválido.")
        return redirect('Productos:productos_views')

    producto = get_object_or_404(modelo, id=producto_id)

    if hasattr(producto, 'stock') and producto.stock <= 0:
        messages.error(request, f'El producto "{producto}" está agotado.')
        return redirect('Productos:productos_views')

    try:
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
    except ValueError:
        cantidad = 1

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    content_type = ContentType.objects.get_for_model(modelo)
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        content_type=content_type,
        object_id=producto.id
    )

    if not creado:
        item.cantidad += cantidad
    else:
        item.cantidad = cantidad

    item.save()

    messages.success(request, f'Se agregó {cantidad} unidad(es) de {producto} al carrito.')
    return redirect('Productos:ver_carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    messages.info(request, 'Producto eliminado del carrito.')
    return redirect('Productos:ver_carrito')

@login_required
def vaciar_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    carrito.items.all().delete()
    messages.info(request, 'Carrito vaciado.')
    return redirect('Productos:ver_carrito')

@login_required
def confirmar_compra(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.all()

    for item in items:
        if item.cantidad > item.producto.stock:
            messages.error(request, f'Stock insuficiente para {item.producto.nombre}.')
            return redirect('Productos:ver_carrito')

    orden = OrdenCompra.objects.create(usuario=request.user, total=0)
    total_compra = 0

    for item in items:
        producto = item.producto
        producto.stock -= item.cantidad
        producto.save()

        if hasattr(producto, 'precio_local') and producto.precio_local:
            precio_unitario = producto.precio_local
        else:
            precio_unitario = producto.precio

        DetalleOrden.objects.create(
            orden=orden,
            producto=producto,
            cantidad=item.cantidad,
            precio_unitario=precio_unitario
        )

        total_compra += item.cantidad * precio_unitario

    orden.total = total_compra
    orden.save()

    items.delete()

    return redirect('Productos:compra_exitosa')



def compra_exitosa(request):
    return render(request, 'carrito/compra_exitosa.html')