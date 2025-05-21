import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventariado.settings')
django.setup()

from Productos.models import OnepieceCards

STOCK_POR_RAREZA = {
    "C":        (50, 100),  # Común
    "UC":       (30, 70),   # Poco común
    "R":        (20, 50),   # Rara
    "SR":       (10, 25),   # Súper rara
    "SEC":      (5, 15),    # Secreta
    "L":        (3, 10),    # Leyenda
    "SP CARD":  (1, 5),     # Especial (cartas promocionales o firmadas)
    "P":        (1, 3),     # Promocional o muy limitada
}

def obtener_rango_stock(rareza):
    return STOCK_POR_RAREZA.get(rareza, (1, 10))

def main():
    cartas = OnepieceCards.objects.all()
    updates = []
    for carta in cartas:
        rareza = (carta.tipo or "").upper()
        stock_min, stock_max = obtener_rango_stock(rareza)
        stock_aleatorio = random.randint(stock_min, stock_max)
        if carta.stock != stock_aleatorio:
            carta.stock = stock_aleatorio
            updates.append(carta)

    # Guardar en batch para eficiencia
    OnepieceCards.objects.bulk_update(updates, ['stock'])

    for carta in updates:
        print(f"Actualizado stock para carta {carta.id} ({carta.tipo}): {carta.stock}")

if __name__ == '__main__':
    main()
