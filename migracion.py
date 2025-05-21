import os
import django
import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventariado.settings')
django.setup()

from Productos.models import OnepieceCards
from django.conf import settings

def importar_cartas():
    base_url = 'https://apitcg.com/api/one-piece/cards'
    headers = {'x-api-key': settings.TCG_ONEPIECE_API_KEY}
    page = 1
    total_importadas = 0

    while True:
        params = {'page': page, 'limit': 100}
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json().get('data', [])

            if not data:
                print("No hay más cartas que importar.")
                break

            for carta in data:
                imagen_url = carta.get('images', {}).get('large')
                obj, created = OnepieceCards.objects.update_or_create(
                    nombre=carta.get('name'),
                    defaults={
                        'descripcion': f"{carta.get('family', '')} | Set: {carta.get('set', {}).get('name', '')}",
                        'tipo': carta.get('rarity'),
                        'ataque': carta.get('power') or None,
                        'defensa': None,
                        'velocidad': None,
                        'habilidad': carta.get('ability'),
                    }
                )
                if imagen_url and not obj.imagen:
                    img_response = requests.get(imagen_url)
                    if img_response.status_code == 200:
                        nombre_archivo = os.path.basename(urlparse(imagen_url).path)
                        obj.imagen.save(nombre_archivo, ContentFile(img_response.content), save=False)
                        obj.save()  # Guarda el modelo con la imagen asociada
                        print(f"Imagen guardada para {obj.nombre} en: {obj.imagen.url}")
                    else:
                        print(f"No se pudo descargar la imagen para {obj.nombre}")

                total_importadas += 1

            print(f"Página {page} procesada. Total importadas hasta ahora: {total_importadas}")
            page += 1

        except Exception as e:
            print(f"Error en la página {page}: {e}")
            break

    print(f"\nImportación completada. Total de cartas importadas: {total_importadas}")

if __name__ == '__main__':
    importar_cartas()
