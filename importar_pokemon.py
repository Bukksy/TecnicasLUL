import os
import time
import django
import requests
from django.db import transaction
from requests.exceptions import RequestException

# --- Configuración Django ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventariado.settings')  # Ajusta si es necesario
django.setup()

from Productos.models import PokemonCard  # Después de django.setup()

# --- Función de importación con reintentos y backoff ---
def importar_todas_cartas_pokemon():
    API_KEY = "3ba7564d-df35-4de4-8de5-9a2ab43ff7f3"
    BASE_URL = "https://api.pokemontcg.io/v2/cards"
    page = 1
    page_size = 250  # máximo permitido
    max_retries = 5

    while True:
        backoff = 1  # segundos iniciales de backoff
        for intento in range(1, max_retries + 1):
            try:
                response = requests.get(
                    BASE_URL,
                    headers={"X-Api-Key": API_KEY},
                    params={"page": page, "pageSize": page_size},
                    timeout=10
                )
                response.raise_for_status()
                break  # si todo bien, salimos del bucle de reintentos
            except RequestException as e:
                print(f"[Página {page}] Error (intento {intento}/{max_retries}): {e}")
                if intento == max_retries:
                    print("Máximo de reintentos alcanzado. Abortando importación.")
                    return
                print(f"Reintentando en {backoff} segundos…")
                time.sleep(backoff)
                backoff *= 2  # backoff exponencial

        data = response.json()
        cartas = data.get("data", [])
        if not cartas:
            print("No quedan más cartas por descargar.")
            break

        print(f"Descargando página {page}: {len(cartas)} cartas…")

        # Guardado atómico para evitar medias actualizaciones
        with transaction.atomic():
            for carta in cartas:
                PokemonCard.objects.update_or_create(
                    card_id=carta["id"],
                    defaults={"data": carta}
                )

        page += 1
        time.sleep(1)  # espera corta para no sobrecargar la API

    print("Importación finalizada.")

# --- Ejecución cuando se llame el script directamente ---
if __name__ == '__main__':
    importar_todas_cartas_pokemon()
