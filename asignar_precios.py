import os
import django
import random
import time
from openpyxl import Workbook

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventariado.settings')
django.setup()

from Productos.models import OnepieceCards

# Rango de precios según tipo de carta
precios_por_tipo = [
    {"tipo": "C", "precio_min": 1000, "precio_max": 2000},
    {"tipo": "UC", "precio_min": 2100, "precio_max": 4000},
    {"tipo": "R", "precio_min": 4100, "precio_max": 8000},
    {"tipo": "SR", "precio_min": 8100, "precio_max": 16000},
    {"tipo": "L", "precio_min": 16100, "precio_max": 32000},
    {"tipo": "P", "precio_min": 32100, "precio_max": 64000},
    {"tipo": "SEC", "precio_min": 25000, "precio_max": 50000},
    {"tipo": "SP CARD", "precio_min": 40000, "precio_max": 80000},
]

def obtener_rango_precio(tipo):
    tipo = tipo.strip().upper()
    for t in precios_por_tipo:
        if t["tipo"] == tipo:
            return t["precio_min"], t["precio_max"]
    print(f"[WARNING] Tipo '{tipo}' no encontrado, se usará rango por defecto.")
    return 1000, 2000

def main():
    cartas = OnepieceCards.objects.all()
    total = cartas.count()
    print(f"Procesando {total} cartas...")

    wb = Workbook()
    ws = wb.active
    ws.title = "Cartas Inventario"
    ws.append(["ID", "Nombre", "Tipo", "Precio CLP", "Stock"])

    for carta in cartas:
        tipo = carta.tipo.strip() if carta.tipo else ''
        nombre = carta.nombre or 'N/A'
        stock = carta.stock if hasattr(carta, 'stock') else 0

        minimo, maximo = obtener_rango_precio(tipo)
        precio = random.randint(minimo, maximo)

        # Si quieres guardar el precio asignado en un campo, deberías tener un campo llamado "precio_local" o similar
        if hasattr(carta, 'precio_local'):
            carta.precio_local = precio
            carta.save()

        ws.append([carta.id, nombre, tipo or 'Sin tipo', precio, stock])
        print(f"[OK] ID {carta.id}: Precio {precio} CLP, Stock {stock}")
        time.sleep(0.05)

    archivo = "inventario_onepiece.xlsx"
    wb.save(archivo)
    print(f"Archivo guardado: {archivo}")

if __name__ == '__main__':
    main()
