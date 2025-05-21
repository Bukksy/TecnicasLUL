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
from django.core.paginator import Paginator
from django.template.loader import render_to_string

def cargar_mas_cartas_onepiece(request):
    page = int(request.GET.get("page", 1))
    nombre = request.GET.get('nombre', '')  
    tipo = request.GET.get('tipo', '')

    cartas_op = OnepieceCards.objects.all().order_by('id')
    if nombre:
        cartas_op = cartas_op.filter(nombre__icontains=nombre)
    if tipo:
        cartas_op = cartas_op.filter(tipo__icontains=tipo)

    paginator = Paginator(cartas_op, 50)  # 50 cartas por página
    cartas_pagina = paginator.get_page(page)

    html = render_to_string("carta_op.html", {"cartas_op": cartas_pagina})
    return JsonResponse({
        "cartas_html": html,
        "has_next": cartas_pagina.has_next()
    })

def cartas_onepiece(request):
    tipos = OnepieceCards.objects.values_list('tipo', flat=True).distinct().exclude(tipo__isnull=True).exclude(tipo__exact='')
    cartas = OnepieceCards.objects.all()[:50] 
    return render(request, 'cartas_onepiece.html', {
        'cartas_op': cartas,
        'tipos': tipos,
    })

def filtrar_cartas_onepiece(request):
    tipo = request.GET.get('tipo')
    cartas = OnepieceCards.objects.all()

    if tipo:
        cartas = cartas.filter(tipo=tipo)

    cartas_html = render_to_string('carta_op.html', {'cartas_op': cartas})
    return JsonResponse({
        'cartas_html': cartas_html,
        'cantidad': cartas.count(),
    })

def onepiece(request):
    categoria = get_object_or_404(Categoria, nombre='One Piece')
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'onepiece.html', {'productos': productos})

def pokemon(request):
    categoria = get_object_or_404(Categoria, nombre='Pokemon')
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'Pokemon.html', {'productos': productos})

def todo(request):
    productos = Producto.objects.all()
    return render(request, 'Todo.html', {'productos': productos})

def cartas_pokemon(request):
    cartas = PokemonCard.objects.all().order_by('id')

    rarezas = set()
    sets = set()

    for carta in cartas:
        data = carta.data
        rareza = data.get('rarity')
        set_name = data.get('set', {}).get('name')

        if rareza:
            rarezas.add(rareza)
        if set_name:
            sets.add(set_name)

    paginator = Paginator(cartas, 50)
    primeras_cartas = paginator.get_page(1)

    cartas_pagina = []
    for carta in primeras_cartas:
        data = carta.data
        cartas_pagina.append({
            'id': carta.id,
            'nombre': data.get('name', 'N/A'),
            'rareza': data.get('rarity', 'N/A'),
            'set': data.get('set', {}).get('name', 'N/A'),
            'imagen': data.get('images', {}).get('small', ''),
            'precio': data.get('precio_local', 'N/A'),
            'stock': data.get('stock_local', 'N/A'),
        })

    return render(request, 'cartas.html', {
        'rarezas': sorted(rarezas),
        'sets': sorted(sets),
        'cartas_pagina': cartas_pagina,
    })


def cargar_mas_cartas(request):
    page_number = int(request.GET.get('page', 1))
    texto_filtro = request.GET.get('nombre', '').strip().lower()
    filtro_rareza = request.GET.get('rareza', '').strip().lower()
    filtro_set = request.GET.get('set', '').strip().lower()

    todas_cartas = PokemonCard.objects.all().order_by('id')

    cartas_filtradas = []
    for carta in todas_cartas:
        data = carta.data
        nombre = data.get('name', '').lower()
        rareza = (data.get('rarity') or '').lower()
        set_name = (data.get('set', {}).get('name') or '').lower()

        if texto_filtro and texto_filtro not in nombre:
            continue
        if filtro_rareza and filtro_rareza != rareza:
            continue
        if filtro_set and filtro_set != set_name:
            continue

        cartas_filtradas.append({
            'id': carta.id,
            'nombre': data.get('name', 'N/A'),
            'rareza': data.get('rarity', 'N/A'),
            'set': data.get('set', {}).get('name', 'N/A'),
            'imagen': data.get('images', {}).get('small', ''),
            'precio': data.get('precio_local', 'N/A'),
            'stock': data.get('stock_local', 'N/A'),
        })

    paginator = Paginator(cartas_filtradas, 50)  # <-- Aquí defines cuántas cartas por página
    page_obj = paginator.get_page(page_number)
    print(f"[DEBUG] Página {page_number} con {len(page_obj.object_list)} cartas filtradas")


    return JsonResponse({
        'cartas': page_obj.object_list,
        'has_next': page_obj.has_next()
    })
