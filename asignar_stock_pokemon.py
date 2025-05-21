import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventariado.settings')
django.setup()

from Productos.models import PokemonCard

stock_por_rareza = [
    {"rareza": "Common",                        "stock_min": 20, "stock_max": 60},
    {"rareza": "Uncommon",                      "stock_min": 15, "stock_max": 40},
    {"rareza": "Rare",                          "stock_min": 10, "stock_max": 30},
    {"rareza": "Rare Holo",                     "stock_min": 6,  "stock_max": 20},
    {"rareza": "Rare Holo GX",                  "stock_min": 4,  "stock_max": 12},
    {"rareza": "Rare Holo EX",                  "stock_min": 3,  "stock_max": 10},
    {"rareza": "Rare Holo LV.X",                "stock_min": 2,  "stock_max": 8},
    {"rareza": "Rare Holo Star",                "stock_min": 1,  "stock_max": 6},
    {"rareza": "Rare Holo V",                   "stock_min": 3,  "stock_max": 10},
    {"rareza": "Rare Holo VMAX",                "stock_min": 3,  "stock_max": 10},
    {"rareza": "Rare Holo VSTAR",               "stock_min": 3,  "stock_max": 10},
    {"rareza": "Rare BREAK",                    "stock_min": 2,  "stock_max": 6},
    {"rareza": "Rare Ultra",                    "stock_min": 1,  "stock_max": 4},
    {"rareza": "Rare Shiny",                    "stock_min": 1,  "stock_max": 4},
    {"rareza": "Rare Shiny GX",                 "stock_min": 1,  "stock_max": 4},
    {"rareza": "Rare Rainbow",                  "stock_min": 1,  "stock_max": 3},
    {"rareza": "Rare Secret",                   "stock_min": 1,  "stock_max": 3},
    {"rareza": "Rare Prime",                    "stock_min": 1,  "stock_max": 5},
    {"rareza": "Rare Prism Star",               "stock_min": 2,  "stock_max": 6},
    {"rareza": "Rare ACE",                      "stock_min": 1,  "stock_max": 3},
    {"rareza": "Ultra Rare",                    "stock_min": 1,  "stock_max": 3},
    {"rareza": "Hyper Rare",                    "stock_min": 1,  "stock_max": 2},
    {"rareza": "Shiny Rare",                    "stock_min": 1,  "stock_max": 4},
    {"rareza": "Shiny Ultra Rare",              "stock_min": 1,  "stock_max": 3},
    {"rareza": "Illustration Rare",             "stock_min": 1,  "stock_max": 2},
    {"rareza": "Special Illustration Rare",     "stock_min": 1,  "stock_max": 2},
    {"rareza": "Trainer Gallery Rare Holo",     "stock_min": 2,  "stock_max": 6},
    {"rareza": "Amazing Rare",                  "stock_min": 2,  "stock_max": 6},
    {"rareza": "Radiant Rare",                  "stock_min": 2,  "stock_max": 5},
    {"rareza": "Promo",                         "stock_min": 10, "stock_max": 25},
    {"rareza": "Classic Collection",            "stock_min": 2,  "stock_max": 6},
    {"rareza": "LEGEND",                        "stock_min": 1,  "stock_max": 3},
    {"rareza": "Double Rare",                   "stock_min": 4,  "stock_max": 8},
    {"rareza": "ACE SPEC Rare",                 "stock_min": 1,  "stock_max": 2},
    {"rareza": "Desconocida",                   "stock_min": 5,  "stock_max": 15},
]

def obtener_rango_stock(rareza):
    if rareza:
        rareza = rareza.strip()
    else:
        rareza = ""
    for r in stock_por_rareza:
        if r["rareza"].lower() == rareza.lower():
            return r["stock_min"], r["stock_max"]
    # Stock por defecto si no encuentra rareza o está vacía
    return 5, 15

def main():
    cartas = PokemonCard.objects.all()
    total = cartas.count()
    print(f"Total cartas a procesar: {total}")

    for carta in cartas:
        try:
            data = carta.data or {}  # Asegúrate que no sea None
            rareza = data.get('rarity', '') if data else ''
            stock_min, stock_max = obtener_rango_stock(rareza)
            stock = random.randint(stock_min, stock_max)

            data['stock_local'] = stock
            carta.data = data
            carta.save()
            print(f"[OK] Carta ID {carta.id} ({rareza}) - Stock asignado: {stock}")

        except Exception as e:
            print(f"[ERROR] Carta ID {carta.id}: {e}")

if __name__ == '__main__':
    main()