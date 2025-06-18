from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
import openpyxl
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest
import json


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
        onepiece_prods = onepieceprods.objects.all().order_by('id')
        onepiececards = OnepieceCards.objects.all().order_by('id')
        productos_unificadosop = list(onepiececards) + list(onepiece_prods)

        context = {'productosop': productos_unificadosop, 'current_page': 1}
        return render(request, 'productos_views.html', context)

    elif page_number == '2':
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 60))

        pokemoncards = PokemonCard.objects.all().order_by('id')
        pokemon_prods = pokemonprods.objects.all().order_by('id')
        total = pokemoncards.count() + pokemon_prods.count()

        all_data = []

        for carta in pokemoncards[offset:offset+limit]:
            data = getattr(carta, 'data', {})
            all_data.append({
                'id': carta.id,
                'nombre': data.get('name', 'N/A'),
                'rareza': data.get('rarity', 'N/A'),
                'set': data.get('set', {}).get('name', 'N/A'),
                'imagen': data.get('images', {}).get('large', ''),
                'precio': data.get('precio_local', 'N/A'),
                'stock': data.get('stock_local', 'N/A'),
                'tipo_origen': 'pokemoncard',
            })

        restantes = limit - len(all_data)
        if restantes > 0:
            prod_offset = max(0, offset - pokemoncards.count())
            for prod in pokemon_prods[prod_offset:prod_offset+restantes]:
                all_data.append({
                    'id': prod.id,
                    'nombre': prod.nombre,
                    'rareza': prod.rareza,
                    'set': prod.set,
                    'imagen': prod.imagen.url if prod.imagen else '',
                    'precio': prod.precio if prod.precio is not None else 'N/A',
                    'stock': prod.stock,
                    'tipo_origen': 'pokemonprod',
                })

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'results': all_data,
                'has_more': (offset + limit) < total
            })

        context = {
            'pokemon_pagina': all_data,
            'current_page': 2,
            'total': total,
        }
        return render(request, 'productos_views.html', context)

    return redirect('/productos/?page=1')


@login_required
@user_passes_test(es_admin)
def agregar_producto(request, id):
    if request.method == 'POST':
        print("✅ POST recibido")
        categoria = request.POST.get('categoria')

        if categoria == 'pokemon':
            nombrepk = request.POST.get('nombrepk', '').strip()
            set_nombre = request.POST.get('set', '').strip()
            rareza = request.POST.get('rareza', '').strip()
            precio = request.POST.get('precio_local_pk', '').strip()
            stock = request.POST.get('stock_local_pk', '').strip()
            imagen_archivo = request.FILES.get('imagen')
            
            print("Nombre:", nombrepk)
            print("set:", set_nombre)
            print("rareza:", rareza)

            if not (nombrepk and set_nombre and rareza):
                messages.error(request, 'Debes completar nombre, set y rareza.')
                return redirect('Productos:agregar_producto')

            pokemonprods.objects.create(
                nombre=nombrepk,
                set=set_nombre,
                rareza=rareza,
                precio=int(precio) if precio else None,
                stock=int(stock) if stock else 0,
                imagen=imagen_archivo
            )
            messages.success(request, 'Producto Pokémon guardado correctamente.')


        elif categoria == 'onepiece':
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            tipo = request.POST.get('tipo', '').strip()
            precio = request.POST.get('precio_local_op', '').strip()
            stock = request.POST.get('stock_op', '').strip()
            imagen_archivo = request.FILES.get('imagen')

            if not (nombre and descripcion and tipo):
                messages.error(request, 'Debes completar nombre, descripción y tipo.')
                return redirect('Productos:agregar_producto')

            onepieceprods.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                tipo=tipo,
                precio=int(precio) if precio else None,
                stock=int(stock) if stock else 0,
                imagen=imagen_archivo
            )
            messages.success(request, 'Producto One Piece guardado correctamente.')

        else:
            messages.error(request, 'Categoría no válida.')

        return redirect('Productos:agregar_producto')

    # Parte GET: mostrar datos existentes para los selects
    onepiececards = OnepieceCards.objects.all().order_by('id')
    pokemoncards = PokemonCard.objects.all().order_by('id')

    sets_pokemon = sorted(set(
        getattr(card, 'data', {}).get('set', {}).get('name', 'N/A')
        for card in pokemoncards if getattr(card, 'data', {}).get('set')
    ))

    rareza_set = set()
    for carta in pokemoncards:
        data = getattr(carta, 'data', {})
        rareza = data.get('rarity')
        if rareza:
            rareza_set.add(rareza)
    rareza_lista = sorted(list(rareza_set))

    descripcion_onepiece = sorted(set(
        card.descripcion for card in onepiececards if card.descripcion
    ))

    tipos_onepiece = sorted(set(
        card.tipo for card in onepiececards if card.tipo
    ))

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

    context = {
        'pokemoncards': pokemon_pagina,
        'onepiececards': onepiececards,
        'sets_pokemon': sets_pokemon,
        'tipos_onepiece': tipos_onepiece,
        'rareza_pokemon': rareza_lista,
        'descripcion_onepiece': descripcion_onepiece,
    }

    return render(request, 'add_prod.html', context)

def modificar_producto(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')

    try:
        data = json.loads(request.body)

        tipo_origen = data.get('tipo_origen')
        id = data.get('id')
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '')
        precio = data.get('precio')
        stock = data.get('stock')
        rareza = data.get('rareza', '')
        set_ = data.get('set', '')

        # Validaciones básicas
        if not id or not nombre or precio is None or stock is None:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        if tipo_origen == 'pokemonprod':
            producto = pokemonprods.objects.filter(id=id).first()
            if not producto:
                return JsonResponse({'error': 'Producto no encontrado'}, status=404)

            producto.nombre = nombre
            producto.rareza = rareza.strip()
            producto.set = set_.strip()
            producto.precio = int(precio)
            producto.stock = int(stock)
            producto.save()

        elif tipo_origen == 'onepieceprod':
            producto = onepieceprods.objects.filter(id=id).first()
            if not producto:
                return JsonResponse({'error': 'Producto no encontrado'}, status=404)

            producto.nombre = nombre
            producto.descripcion = descripcion.strip()
            producto.precio = int(precio)
            producto.stock = int(stock)
            producto.save()

        elif tipo_origen == 'pokemoncard':
            producto = PokemonCard.objects.filter(id=id).first()
            if not producto:
                return JsonResponse({'error': 'Producto no encontrado'}, status=404)

            producto.nombre = nombre
            producto.rareza = rareza.strip()
            producto.set = set_.strip()
            producto.save()

        elif tipo_origen == 'onepiececard':
            producto = OnepieceCards.objects.filter(id=id).first()
            if not producto:
                return JsonResponse({'error': 'Producto no encontrado'}, status=404)

            producto.nombre = nombre
            producto.descripcion = descripcion.strip()
            producto.save()

        else:
            return JsonResponse({'error': 'Tipo de origen no válido'}, status=400)

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(es_admin)
def eliminar_producto(request, id, categoria):
    if categoria == 'pokemon':
        modelo = pokemonprods
    elif categoria == 'onepiece':
        modelo = onepieceprods
    else:
        messages.error(request, "Categoría inválida.")
        return redirect('Productos:productos_views')

    try:
        producto = modelo.objects.get(id=id)
        producto.delete()
        messages.success(request, f"Producto {categoria.capitalize()} eliminado correctamente.")
    except modelo.DoesNotExist:
        messages.error(request, f"Producto {categoria.capitalize()} no encontrado.")

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
        producto = item.producto
        clase_producto = producto.__class__.__name__

        if clase_producto == 'PokemonCard':
            item.nombre = producto.data.get('name', 'Sin nombre')
            precios = producto.data.get('prices', {})
            item.precio_local = producto.data.get('precio_local') or precios.get('holofoil') or precios.get('normal') or 0
            item.precio = item.precio_local
            item.stock_local = producto.data.get('stock_local', 0)
            item.stock = item.stock_local

        elif clase_producto == 'OnepieceCards':
            item.nombre = producto.nombre
            item.precio_local = producto.precio_local or producto.precio or 0
            item.precio = item.precio_local
            item.stock_local = producto.stock
            item.stock = producto.stock

        elif clase_producto == 'Producto':
            item.nombre = producto.nombre
            item.precio_local = producto.precio
            item.precio = producto.precio
            item.stock_local = producto.stock
            item.stock = producto.stock

        else:
            item.nombre = 'Producto desconocido'
            item.precio_local = 0
            item.precio = 0
            item.stock_local = 0
            item.stock = 0

        carrito_total += item.subtotal

    context = {
        'productos_carrito': productos_carrito,
        'carrito_total': carrito_total,
    }
    return render(request, 'carrito/ver_carrito.html', context)


def agregar_al_carrito(request, tipo_producto, producto_id):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'redirect': reverse('Home:login'),
                'message': 'Debes iniciar sesión para agregar productos al carrito.'
            }, status=401)
        else:
            messages.error(request, 'Debes iniciar sesión para agregar productos al carrito.')
            return redirect('Home:login') 

    modelos = {
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
    if request.method != 'POST':
        messages.error(request, 'Método no permitido para esta operación.')
        return redirect('Productos:ver_carrito')

    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.all()

    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío. No hay nada que comprar.')
        return redirect('Productos:ver_carrito')

    for item in items:
        producto = item.producto

        stock_disponible = 0
        if hasattr(producto, 'stock_local') and producto.stock_local is not None:
            stock_disponible = producto.stock_local
        elif hasattr(producto, 'stock') and producto.stock is not None:
            stock_disponible = producto.stock
        elif isinstance(producto, PokemonCard):
            stock_disponible = producto.data.get('stock_local', 0)

        if item.cantidad > stock_disponible:
            messages.error(request, f'Stock insuficiente para {item.nombre if hasattr(item, "nombre") else str(producto)}.')
            return redirect('Productos:ver_carrito')

    try:
        orden = OrdenCompra.objects.create(usuario=request.user, total=0)
        total_compra = 0

        for item in items:
            producto = item.producto

            if hasattr(producto, 'stock_local') and producto.stock_local is not None:
                producto.stock_local -= item.cantidad
                producto.save(update_fields=['stock_local'])
            elif hasattr(producto, 'stock') and producto.stock is not None:
                producto.stock -= item.cantidad
                producto.save(update_fields=['stock'])
            elif isinstance(producto, PokemonCard):
                stock_actual = producto.data.get('stock_local', 0)
                nuevo_stock = max(stock_actual - item.cantidad, 0)
                producto.data['stock_local'] = nuevo_stock
                producto.save(update_fields=['data'])

            precio_unitario = 0
            if hasattr(producto, 'precio_local') and producto.precio_local is not None:
                precio_unitario = producto.precio_local
            elif hasattr(producto, 'precio') and producto.precio is not None:
                precio_unitario = producto.precio
            elif isinstance(producto, PokemonCard):
                precio_unitario = producto.data.get('precio_local', 0)

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
        carrito.save()

        messages.success(request, f'¡Tu compra de ${total_compra:.2f} ha sido confirmada con éxito!')
        return redirect('Productos:compra_exitosa')
    
    except Exception as e:
        messages.error(request, f'Hubo un error inesperado al procesar tu compra: {e}. Por favor, contacta a soporte.')
        return redirect('Productos:ver_carrito')

def compra_exitosa(request):
    return render(request, 'carrito/compra_exitosa.html')