import os
import django
import random
import time
from openpyxl import Workbook

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventariado.settings') 
django.setup()

from Productos.models import PokemonCard

tipos_precio = [
    {"rareza": "Common",                        "min": 1000,   "max": 2000},
    {"rareza": "Uncommon",                      "min": 2100,   "max": 4000},
    {"rareza": "Rare",                          "min": 4100,   "max": 8000},
    {"rareza": "Rare Holo",                     "min": 8100,   "max": 16000},
    {"rareza": "Rare Holo GX",                  "min": 32100,  "max": 64000},
    {"rareza": "Rare Holo EX",                  "min": 30000,  "max": 60000},
    {"rareza": "Rare Holo LV.X",                "min": 32000,  "max": 65000},
    {"rareza": "Rare Holo Star",                "min": 35000,  "max": 70000},
    {"rareza": "Rare Holo V",                   "min": 33000,  "max": 66000},
    {"rareza": "Rare Holo VMAX",                "min": 34000,  "max": 67000},
    {"rareza": "Rare Holo VSTAR",               "min": 35000,  "max": 68000},
    {"rareza": "Rare BREAK",                    "min": 28000,  "max": 56000},
    {"rareza": "Rare Ultra",                    "min": 36000,  "max": 70000},
    {"rareza": "Rare Shiny",                    "min": 40000,  "max": 80000},
    {"rareza": "Rare Shiny GX",                 "min": 42000,  "max": 82000},
    {"rareza": "Rare Rainbow",                  "min": 45000,  "max": 90000},
    {"rareza": "Rare Secret",                   "min": 46000,  "max": 92000},
    {"rareza": "Rare Prime",                    "min": 37000,  "max": 74000},
    {"rareza": "Rare Prism Star",               "min": 33000,  "max": 66000},
    {"rareza": "Rare ACE",                      "min": 48000,  "max": 96000},
    {"rareza": "Ultra Rare",                    "min": 50000,  "max": 100000},
    {"rareza": "Hyper Rare",                    "min": 52000,  "max": 104000},
    {"rareza": "Shiny Rare",                    "min": 43000,  "max": 86000},
    {"rareza": "Shiny Ultra Rare",              "min": 54000,  "max": 108000},
    {"rareza": "Illustration Rare",             "min": 56000,  "max": 112000},
    {"rareza": "Special Illustration Rare",     "min": 60000,  "max": 120000},
    {"rareza": "Trainer Gallery Rare Holo",     "min": 30000,  "max": 60000},
    {"rareza": "Amazing Rare",                  "min": 35000,  "max": 70000},
    {"rareza": "Radiant Rare",                  "min": 32000,  "max": 64000},
    {"rareza": "Promo",                         "min": 1500,   "max": 3500},
    {"rareza": "Classic Collection",            "min": 20000,  "max": 40000},
    {"rareza": "LEGEND",                        "min": 42000,  "max": 84000},
    {"rareza": "Double Rare",                   "min": 38000,  "max": 76000},
    {"rareza": "ACE SPEC Rare",                 "min": 50000,  "max": 100000},
    {"rareza": "Desconocida",                   "min": 1000,   "max": 2000},
]

def rango_precio(rareza):
    rareza = (rareza or '').strip().lower()
    for entry in tipos_precio:
        if entry["rareza"].lower() == rareza:
            return entry["min"], entry["max"]
    return 1000, 2000

def main():
    cartas = PokemonCard.objects.all()
    total = cartas.count()
    print(f"Procesando {total} cartas...")

    # Configurar Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Cartas Inventario"
    ws.append(["ID", "Nombre", "Rareza", "Precio CLP", "Stock"])

    for carta in cartas:
        data = carta.data or {}
        rareza = data.get('rarity', '').strip() if data else ''

        precio_mercado = data.get('cardmarket', {}).get('prices', {}).get('averageSellPrice')
        if precio_mercado:
            precio = int(float(precio_mercado) * 1000)
        else:
            minimo, maximo = rango_precio(rareza)
            precio = random.randint(minimo, maximo)

        stock = data.get('stock_local', 0)  # ya asignado previamente

        data['precio_local'] = precio
        carta.data = data
        carta.save()

        ws.append([carta.id, data.get('name', 'N/A'), rareza or 'Sin rareza', precio, stock])

        print(f"[OK] ID {carta.id}: Precio {precio} CLP, Stock {stock}")
        time.sleep(0.1)

    archivo = "inventario_pokemon.xlsx"
    wb.save(archivo)
    print(f"Archivo guardado: {archivo}")

if __name__ == '__main__':
    main()