from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
    
class Categoria_producto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    CategoriaProd = models.ForeignKey(Categoria_producto, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre
    

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Carrito de {self.usuario}"
    
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    producto = GenericForeignKey('content_type', 'object_id')
    cantidad = models.PositiveBigIntegerField(default=1)

    @property
    def subtotal(self):
        return self.cantidad * self.get_precio()

    def get_precio(self):
        if hasattr(self.producto, 'precio') and self.producto.precio is not None:
            return self.producto.precio
        elif hasattr(self.producto, 'precio_local') and self.producto.precio_local is not None:
            return self.producto.precio_local
        return 0

    def __str__(self):
        return f"{self.cantidad} x {str(self.producto)}"

class OrdenCompra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ], default='pendiente')

    def __str__(self):
        return f"Orden #{self.id} de {self.usuario.username}"

class DetalleOrden(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    producto = GenericForeignKey('content_type', 'object_id')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=100, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario
    


class OnepieceCards(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='onepiececards/', blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    ataque = models.IntegerField(blank=True, null=True)
    defensa = models.IntegerField(blank=True, null=True)
    velocidad = models.IntegerField(blank=True, null=True)
    habilidad = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    precio_local = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    @property
    def precio(self):
        precio_obj = self.precios.first()  
        return precio_obj.precio if precio_obj else None
    
class PrecioCartaOP(models.Model):
    id_carta = models.ForeignKey(OnepieceCards, on_delete=models.CASCADE, related_name='precios')
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.id_carta.nombre} - {self.precio}"
    
class PokemonCard(models.Model):
    card_id = models.CharField(max_length=100, unique=True)
    data = models.JSONField() 

    def __str__(self):
        return self.data.get('name', 'Sin nombre')
    
class DetalleOrdenOnepiece(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles_onepiece')
    carta = models.ForeignKey(OnepieceCards, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

class DetalleOrdenPokemon(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles_pokemon')
    carta = models.ForeignKey(PokemonCard, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
