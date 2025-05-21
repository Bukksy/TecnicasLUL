from django.contrib import admin
from .models import *

admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Categoria_producto)
admin.site.register(OnepieceCards)
admin.site.register(PokemonCard)
admin.site.register(PrecioCartaOP)