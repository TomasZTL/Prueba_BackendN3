import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from cafeteria.models import Categoria, Producto

encargado, created = User.objects.get_or_create(
    username='encargado',
    defaults={'first_name': 'Carlos', 'email': 'carlos@inacap.cl', 'is_staff': True, 'is_superuser': True}
)
if created:
    encargado.set_password('inacap123')
    encargado.save()

clientes_data = [
    ('cliente1', 'Ana', 'ana@inacapmail.cl'),
    ('cliente2', 'Diego', 'diego@inacapmail.cl'),
]

for username, nombre, email in clientes_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'first_name': nombre, 'email': email, 'is_staff': False}
    )
    if created:
        user.set_password('inacap123')
        user.save()

categorias_data = [
    ('Cafetería', 'Cafés calientes, té e infusiones', True),
    ('Sándwiches', 'Sándwiches preparados y prensados', True),
    ('Pastelería', 'Dulces, queques y pasteles', True),
    ('Bebidas Frías', 'Jugos naturales, aguas y gaseosas', True),
    ('Temporada Invierno', 'Productos estacionales fuera de carta', False),
]

categorias = {}
for nombre, desc, activa in categorias_data:
    cat, _ = Categoria.objects.get_or_create(
        nombre=nombre,
        defaults={'descripcion': desc, 'activa': activa}
    )
    categorias[nombre] = cat

productos_data = [
    ('CAF-001', 'Espresso', 'Cafetería', 1500, 30, True),
    ('CAF-002', 'Americano', 'Cafetería', 1700, 25, True),
    ('CAF-003', 'Cappuccino', 'Cafetería', 2200, 20, True),
    ('CAF-004', 'Latte Vainilla', 'Cafetería', 2500, 15, True),
    ('CAF-005', 'Té Ceylán', 'Cafetería', 1200, 40, True),
    ('CAF-006', 'Ave Palta', 'Sándwiches', 3200, 12, True),
    ('CAF-007', 'Barros Jarpa', 'Sándwiches', 2800, 10, True),
    ('CAF-008', 'Aliado Jamón Queso', 'Sándwiches', 2000, 18, True),
    ('CAF-009', 'Churrasco Italiano', 'Sándwiches', 3800, 0, True),
    ('CAF-010', 'Vegetariano Quesillo', 'Sándwiches', 2900, 8, False),
    ('CAF-011', 'Muffin de Arándano', 'Pastelería', 1600, 14, True),
    ('CAF-012', 'Brownie con Nueces', 'Pastelería', 1800, 10, True),
    ('CAF-013', 'Media Luna', 'Pastelería', 1100, 25, True),
    ('CAF-014', 'Kuchen de Manzana', 'Pastelería', 2400, 0, True),
    ('CAF-015', 'Galleta Choco Chips', 'Pastelería', 1200, 20, True),
    ('CAF-016', 'Jugo Natural Naranja', 'Bebidas Frías', 2300, 15, True),
    ('CAF-017', 'Agua Mineral sin Gas', 'Bebidas Frías', 1300, 30, True),
    ('CAF-018', 'Limonada Menta Jengibre', 'Bebidas Frías', 2500, 10, True),
    ('CAF-019', 'Bebida Lata 350ml', 'Bebidas Frías', 1500, 25, True),
    ('CAF-020', 'Té Helado Durazno', 'Bebidas Frías', 1700, 12, False),
    ('CAF-021', 'Chocolate Caliente', 'Temporada Invierno', 2200, 10, True),
]

for codigo, nombre, cat_nombre, precio, stock, disp in productos_data:
    Producto.objects.get_or_create(
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'categoria': categorias[cat_nombre],
            'precio': precio,
            'stock': stock,
            'disponible': disp,
        }
    )
