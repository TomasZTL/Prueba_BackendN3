def carrito_total_unidades(request):
    carrito = request.session.get('carrito', {})
    total_unidades = sum(carrito.values())
    return {'carrito_unidades': total_unidades}
