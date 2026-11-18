from django.contrib import admin
from .models import Categoria, Producto, Pedido, DetallePedido


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activa')
    search_fields = ('nombre',)
    list_filter = ('activa',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio', 'stock', 'disponible')
    search_fields = ('codigo', 'nombre')
    list_filter = ('categoria', 'disponible')
    readonly_fields = ('creado',)


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'hora_retiro', 'estado', 'total')
    search_fields = ('cliente__username', 'cliente__first_name')
    list_filter = ('estado', 'fecha')
    readonly_fields = ('fecha',)
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('producto__nombre', 'pedido__id')
    list_filter = ('producto__categoria',)