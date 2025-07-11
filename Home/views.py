import openpyxl
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from Productos.models import *
from django.db.models import Avg, Sum
from django.contrib.auth.decorators import user_passes_test, login_required
import json, requests
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import UserCreationForm

def es_admin(user):
    return user.is_staff

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  
            return redirect('Home:inicio')  
        else:
            messages.error(request, "Usuario o contraseña incorrectos") 

        return redirect('Home:login')

    return render(request, 'login.html')

def obtener_clima_y_pronostico(ciudad="Santiago"):
    api_key = "df1da491904f147826ff50b7ae790e62"
    url_actual = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"
    url_pronostico = f"http://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={api_key}&units=metric&lang=es"

    try:
        response_actual = requests.get(url_actual)
        data_actual = response_actual.json()
    except Exception as e:
        return {'error': f'Error al obtener clima actual: {e}'}

    try:
        response_pronostico = requests.get(url_pronostico)
        data_pronostico = response_pronostico.json()
    except Exception as e:
        return {'error': f'Error al obtener pronóstico: {e}'}

    if response_actual.status_code != 200 or "main" not in data_actual:
        return {'error': 'No se pudo obtener el clima actual'}

    if response_pronostico.status_code != 200 or "list" not in data_pronostico:
        return {'error': 'No se pudo obtener el pronóstico'}

    # Clima actual
    clima_actual = {
        'ciudad': ciudad,
        'temperatura': data_actual['main']['temp'],
        'sensacion_termica': data_actual['main']['feels_like'],
        'descripcion': data_actual['weather'][0]['description'],
        'icono': data_actual['weather'][0]['icon'],
        'humedad': data_actual['main']['humidity'],
        'presion': data_actual['main']['pressure'],
        'velocidad_viento': round(data_actual['wind']['speed'] * 3.6, 1),  # m/s a km/h
        'unidad_viento': 'Km/h',
    }

    from datetime import datetime
    pronostico_dias = {}

    for item in data_pronostico['list']:
        fecha = item['dt_txt'].split(' ')[0]

        temp_min = item['main']['temp_min']
        temp_max = item['main']['temp_max']
        descripcion = item['weather'][0]['description']
        icono = item['weather'][0]['icon']

        if fecha not in pronostico_dias:
            pronostico_dias[fecha] = {
                'temp_min': temp_min,
                'temp_max': temp_max,
                'descripcion': descripcion,
                'icono': icono,
                'contador': 1,
            }
        else:
            pronostico_dias[fecha]['temp_min'] = min(pronostico_dias[fecha]['temp_min'], temp_min)
            pronostico_dias[fecha]['temp_max'] = max(pronostico_dias[fecha]['temp_max'], temp_max)
            pronostico_dias[fecha]['descripcion'] = descripcion
            pronostico_dias[fecha]['icono'] = icono
            pronostico_dias[fecha]['contador'] += 1

        dias_semana = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
    dia_ingles = fecha_obj.strftime('%A')
    dia_semana = dias_semana.get(dia_ingles, dia_ingles)

    pronostico_lista = []
    for fecha, valores in pronostico_dias.items():
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        dia_ingles = fecha_obj.strftime('%A')
        dia_semana = dias_semana.get(dia_ingles, dia_ingles)

        pronostico_lista.append({
            'fecha': fecha,
            'dia_semana': dia_semana,
            'temp_min': round(valores['temp_min']),
            'temp_max': round(valores['temp_max']),
            'descripcion': valores['descripcion'].capitalize(),
            'icono': valores['icono'],
        })

    if pronostico_lista:
        pronostico_lista.pop(0)

    return {
        'clima_actual': clima_actual,
        'pronostico': pronostico_lista,
        'error': None,
    }

@login_required
def inicio(request):
    datos_clima = obtener_clima_y_pronostico()

    if datos_clima.get('error'):
        contexto = {'error_clima': datos_clima['error']}
    else:
        contexto = datos_clima

    if request.user.is_staff:
        return render(request, 'inicio.html', contexto)
    else:
        return redirect('InicioClientes:inicio')

def logout_view(request):
    logout(request)
    return redirect('Home:login')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False 
            user.is_superuser = False
            user.save()
            auth_login(request, user)
            return redirect('InicioClientes:inicio')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def obtener_cartas_onepiece():
    cartas_op = OnepieceCards.objects.all()
    productos_con_total = []
    total_stock = 0
    valor_total = 0  # entero para pesos chilenos

    for carta in cartas_op:
        precio = getattr(carta, 'precio_local', 0) or 0
        stock = carta.stock or 0
        total = precio * stock

        productos_con_total.append({'producto': carta, 'total': total, 'es_api': True})
        total_stock += stock
        valor_total += total

    return cartas_op, productos_con_total, total_stock, valor_total

def obtener_cartas_pokemon():
    pokemon_cartas = PokemonCard.objects.all().order_by('id')
    productos_con_total = []
    total_stock = 0
    valor_total = 0
    datos_pokemon = []

    for carta in pokemon_cartas:
        data = carta.data
        nombre = data.get('name', 'Desconocido')

        precio_raw = data.get('precio_local') or data.get('cardmarket', {}).get('prices', {}).get('averageSellPrice', 1.0)
        precio = Decimal(str(precio_raw))

        stock = data.get('stock_local', 1)
        stock = int(stock)  

        total = precio * stock

        productos_con_total.append({
            'producto': {'nombre': nombre, 'precio': precio, 'stock': stock},
            'total': total,
            'es_api': True
        })
        datos_pokemon.append(data)
        total_stock += stock
        valor_total += total

    return pokemon_cartas, productos_con_total, total_stock, valor_total, datos_pokemon

@login_required
def resumenInventario(request):
    cartas_op, prod_onepiece, stock_onepiece, valor_onepiece = obtener_cartas_onepiece()
    pokemons, prod_pokemon, stock_pokemon, valor_pokemon, datos_pokemon = obtener_cartas_pokemon()
    ordenes = OrdenCompra.objects.prefetch_related('detalles__producto').all()

    productos_con_total = prod_onepiece + prod_pokemon

    total_productos = cartas_op.count() + pokemons.count()
    stock_total = stock_onepiece + stock_pokemon
    valor_total_stock = valor_onepiece + valor_pokemon

    labels = [p['producto'].nombre if not isinstance(p['producto'], dict) else p['producto']['nombre'] for p in productos_con_total]
    datos_stock = [p['producto'].stock if not isinstance(p['producto'], dict) else 1 for p in productos_con_total]

    mas_vendidos_data = (
        DetalleOrden.objects
        .values('content_type', 'object_id')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )

    mas_vendidos = []
    for item in mas_vendidos_data:
        try:
            content_type = ContentType.objects.get_for_id(item['content_type'])
            producto = content_type.get_object_for_this_type(id=item['object_id'])
            mas_vendidos.append({
                'producto': producto,
                'total_vendido': item['total_vendido']
            })
        except ContentType.DoesNotExist:
            continue 
        except content_type.model_class().DoesNotExist:
            continue

    context = {
        'productos_con_total': productos_con_total,
        'total_productos': total_productos,
        'stock_total': stock_total,
        'valor_total_stock': valor_total_stock,
        'labels': json.dumps(labels),
        'datos_stock': json.dumps(datos_stock),
        'labels_circular': json.dumps(labels),
        'datos_circular': json.dumps(datos_stock),
        'mas_vendidos': mas_vendidos,
        'datos_pokemon': datos_pokemon,
        'cartas_op': cartas_op,
        'ordenes': ordenes,
    }

    return render(request, 'resumenInventario.html', context)


@login_required
@user_passes_test(es_admin)
def exportar_excel(request):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = 'Más Vendidos'

    headers = ['ID', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Total Vendido']
    sheet.append(headers)

    mas_vendidos_data = (
        DetalleOrden.objects
        .values('content_type', 'object_id')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )

    for item in mas_vendidos_data:
        try:
            content_type = ContentType.objects.get_for_id(item['content_type'])
            producto = content_type.get_object_for_this_type(id=item['object_id'])

            sheet.append([
                producto.id,
                producto.nombre,
                producto.descripcion,
                producto.precio,
                producto.stock,
                item['total_vendido']
            ])
        except (ContentType.DoesNotExist, content_type.model_class().DoesNotExist):
            continue

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=mas_vendidos.xlsx'
    wb.save(response)
    return response


