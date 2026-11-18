from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, ProtectedError
from django.utils import timezone
from functools import wraps
from .models import Categoria, Producto, Pedido, DetallePedido
from .forms import CategoriaForm, ProductoForm, ConfirmarPedidoForm


def solo_encargado(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def solo_cliente(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'cafeteria/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def inicio(request):
    if request.user.is_staff:
        return redirect('producto_lista')
    return redirect('catalogo')


@solo_cliente
def catalogo(request):
    categorias = Categoria.objects.filter(activa=True).order_by('nombre')
    productos = Producto.objects.filter(disponible=True, categoria__activa=True).select_related('categoria').order_by('nombre')

    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()

    if q:
        productos = productos.filter(nombre__icontains=q)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    context = {
        'categorias': categorias,
        'productos': productos,
        'q': q,
        'categoria_seleccionada': categoria_id,
    }
    return render(request, 'cafeteria/catalogo.html', context)


@solo_encargado
def panel_encargado(request):
    return redirect('producto_lista')


@solo_encargado
def categoria_lista(request):
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'cafeteria/categoria_lista.html', {'categorias': categorias})


@solo_encargado
def categoria_detalle(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    productos = categoria.productos.all().order_by('codigo')
    return render(request, 'cafeteria/categoria_detalle.html', {'categoria': categoria, 'productos': productos})


@solo_encargado
def categoria_crear(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('categoria_lista')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = CategoriaForm()
    return render(request, 'cafeteria/categoria_form.html', {'form': form, 'titulo': 'Nueva Categoría'})


@solo_encargado
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('categoria_lista')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'cafeteria/categoria_form.html', {'form': form, 'titulo': 'Editar Categoría'})


@solo_encargado
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, 'Categoría eliminada correctamente.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar la categoría porque tiene productos asociados.')
        return redirect('categoria_lista')
    return render(request, 'cafeteria/categoria_confirmar_eliminar.html', {'categoria': categoria})


@solo_encargado
def producto_lista(request):
    categorias = Categoria.objects.all().order_by('nombre')
    productos = Producto.objects.select_related('categoria').all().order_by('codigo')

    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    disponible = request.GET.get('disponible', '').strip()

    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if disponible == '1':
        productos = productos.filter(disponible=True)
    elif disponible == '0':
        productos = productos.filter(disponible=False)

    context = {
        'productos': productos,
        'categorias': categorias,
        'q': q,
        'categoria_seleccionada': categoria_id,
        'disponible_seleccionado': disponible,
    }
    return render(request, 'cafeteria/producto_lista.html', context)


@solo_encargado
def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'cafeteria/producto_detalle.html', {'producto': producto})


@solo_encargado
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('producto_lista')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = ProductoForm()
    return render(request, 'cafeteria/producto_form.html', {'form': form, 'titulo': 'Nuevo Producto'})


@solo_encargado
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('producto_lista')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'cafeteria/producto_form.html', {'form': form, 'titulo': 'Editar Producto'})


@solo_encargado
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        try:
            producto.delete()
            messages.success(request, 'Producto eliminado correctamente.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar el producto porque figura en algún pedido.')
        return redirect('producto_lista')
    return render(request, 'cafeteria/producto_confirmar_eliminar.html', {'producto': producto})


def _construir_items_carrito(carrito):
    items = []
    total = 0
    ids = [int(k) for k in carrito.keys()]
    productos = Producto.objects.filter(id__in=ids)
    mapa_productos = {p.id: p for p in productos}

    for prod_id_str, cantidad in carrito.items():
        prod = mapa_productos.get(int(prod_id_str))
        if prod:
            subtotal = prod.precio * cantidad
            total += subtotal
            items.append({
                'producto': prod,
                'cantidad': cantidad,
                'subtotal': subtotal,
            })
    return items, total


@solo_cliente
def carrito_ver(request):
    carrito = request.session.get('carrito', {})
    items, total = _construir_items_carrito(carrito)
    form = ConfirmarPedidoForm()
    return render(request, 'cafeteria/carrito.html', {
        'items': items,
        'total': total,
        'form': form,
    })


@solo_cliente
def carrito_agregar(request, pk):
    if request.method != 'POST':
        return redirect('catalogo')

    producto = get_object_or_404(Producto, pk=pk, disponible=True, categoria__activa=True)
    if producto.stock <= 0:
        messages.error(request, f'El producto "{producto.nombre}" está agotado.')
        return redirect('catalogo')

    carrito = request.session.get('carrito', {})
    prod_key = str(producto.id)
    cantidad_actual = carrito.get(prod_key, 0)
    total_unidades = sum(carrito.values())

    if total_unidades + 1 > 10:
        messages.error(request, 'Un pedido no puede tener más de 10 unidades en total.')
        return redirect('catalogo')

    if cantidad_actual + 1 > producto.stock:
        messages.error(request, f'No puedes agregar más unidades de "{producto.nombre}". Stock disponible: {producto.stock}.')
        return redirect('catalogo')

    carrito[prod_key] = cantidad_actual + 1
    request.session['carrito'] = carrito
    messages.success(request, f'Se agregó "{producto.nombre}" al carrito.')
    return redirect('catalogo')


@solo_cliente
def carrito_actualizar(request, pk):
    if request.method != 'POST':
        return redirect('carrito_ver')

    carrito = request.session.get('carrito', {})
    prod_key = str(pk)
    if prod_key not in carrito:
        return redirect('carrito_ver')

    producto = get_object_or_404(Producto, pk=pk)
    try:
        nueva_cantidad = int(request.POST.get('cantidad', 1))
    except ValueError:
        messages.error(request, 'Cantidad inválida.')
        return redirect('carrito_ver')

    if nueva_cantidad <= 0:
        del carrito[prod_key]
        request.session['carrito'] = carrito
        messages.success(request, f'Se quitó "{producto.nombre}" del carrito.')
        return redirect('carrito_ver')

    if nueva_cantidad > producto.stock:
        messages.error(request, f'La cantidad de "{producto.nombre}" supera su stock disponible ({producto.stock}).')
        return redirect('carrito_ver')

    otras_unidades = sum(cant for k, cant in carrito.items() if k != prod_key)
    if otras_unidades + nueva_cantidad > 10:
        messages.error(request, 'Un pedido no puede superar las 10 unidades en total.')
        return redirect('carrito_ver')

    carrito[prod_key] = nueva_cantidad
    request.session['carrito'] = carrito
    messages.success(request, f'Cantidad de "{producto.nombre}" actualizada.')
    return redirect('carrito_ver')


@solo_cliente
def carrito_quitar(request, pk):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        prod_key = str(pk)
        if prod_key in carrito:
            del carrito[prod_key]
            request.session['carrito'] = carrito
            messages.success(request, 'Producto quitado del carrito.')
    return redirect('carrito_ver')


@solo_cliente
def carrito_vaciar(request):
    if request.method == 'POST':
        request.session['carrito'] = {}
        messages.success(request, 'Se vació el carrito.')
    return redirect('carrito_ver')


@solo_cliente
def carrito_confirmar(request):
    if request.method != 'POST':
        return redirect('carrito_ver')

    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'El carrito está vacío.')
        return redirect('carrito_ver')

    total_unidades = sum(carrito.values())
    if total_unidades > 10:
        messages.error(request, 'El pedido no puede tener más de 10 unidades en total.')
        return redirect('carrito_ver')

    form = ConfirmarPedidoForm(request.POST)
    if not form.is_valid():
        items, total = _construir_items_carrito(carrito)
        messages.error(request, 'Revisa la hora de retiro ingresada.')
        return render(request, 'cafeteria/carrito.html', {
            'items': items,
            'total': total,
            'form': form,
        })

    with transaction.atomic():
        ids = [int(k) for k in carrito.keys()]
        productos_db = Producto.objects.select_for_update().filter(id__in=ids)
        mapa_productos = {p.id: p for p in productos_db}

        sin_stock = []
        for prod_id_str, cantidad in carrito.items():
            prod = mapa_productos.get(int(prod_id_str))
            if not prod or not prod.disponible or not prod.categoria.activa or prod.stock < cantidad:
                nombre_prod = prod.nombre if prod else f'ID {prod_id_str}'
                stock_disp = prod.stock if prod else 0
                sin_stock.append(f'{nombre_prod} (solicitado: {cantidad}, disponible: {stock_disp})')

        if sin_stock:
            detalle_fallo = ', '.join(sin_stock)
            messages.error(request, f'No se pudo confirmar el pedido por falta de stock en: {detalle_fallo}.')
            return redirect('carrito_ver')

        pedido = Pedido.objects.create(
            cliente=request.user,
            hora_retiro=form.cleaned_data['hora_retiro'],
            estado='Pendiente',
            total=0,
            observacion=form.cleaned_data.get('observacion', ''),
        )

        total_pedido = 0
        for prod_id_str, cantidad in carrito.items():
            prod = mapa_productos[int(prod_id_str)]
            subtotal = prod.precio * cantidad
            total_pedido += subtotal

            DetallePedido.objects.create(
                pedido=pedido,
                producto=prod,
                cantidad=cantidad,
                precio_unitario=prod.precio,
                subtotal=subtotal,
            )

            prod.stock -= cantidad
            prod.save()

        pedido.total = total_pedido
        pedido.save()

    request.session['carrito'] = {}
    messages.success(request, f'Pedido #{pedido.id} confirmado con éxito en estado Pendiente.')
    return redirect('mis_pedidos')


@solo_cliente
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).prefetch_related('detalles__producto').order_by('-fecha')
    return render(request, 'cafeteria/mis_pedidos.html', {'pedidos': pedidos})


@solo_cliente
def pedido_detalle_cliente(request, pk):
    pedido = get_object_or_404(Pedido.objects.prefetch_related('detalles__producto'), pk=pk)
    if pedido.cliente != request.user:
        raise PermissionDenied
    return render(request, 'cafeteria/pedido_detalle_cliente.html', {'pedido': pedido})


@solo_cliente
def pedido_cancelar(request, pk):
    pedido = get_object_or_404(Pedido.objects.prefetch_related('detalles__producto'), pk=pk)
    if pedido.cliente != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        with transaction.atomic():
            pedido_bloqueado = Pedido.objects.select_for_update().get(pk=pedido.pk)
            if pedido_bloqueado.estado != 'Pendiente':
                messages.error(request, 'Solo se pueden cancelar pedidos en estado Pendiente.')
                return redirect('mis_pedidos')

            for detalle in pedido_bloqueado.detalles.select_related('producto'):
                producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)
                producto.stock += detalle.cantidad
                producto.save()

            pedido_bloqueado.estado = 'Cancelado'
            pedido_bloqueado.save()

        messages.success(request, f'Pedido #{pedido.id} cancelado. Se ha repuesto el stock de los productos.')
    return redirect('mis_pedidos')


TRANSICIONES_ESTADO = {
    'Pendiente': 'En preparación',
    'En preparación': 'Listo',
    'Listo': 'Entregado',
}


@solo_encargado
def gestion_pedidos(request):
    hoy = timezone.localdate()
    pedidos = Pedido.objects.filter(fecha__date=hoy).select_related('cliente').prefetch_related('detalles__producto').order_by('hora_retiro', 'fecha')

    estado = request.GET.get('estado', '').strip()
    estados_filtro = ['Pendiente', 'En preparación', 'Listo', 'Entregado', 'Cancelado']
    if estado in estados_filtro:
        pedidos = pedidos.filter(estado=estado)

    for p in pedidos:
        p.siguiente_estado = TRANSICIONES_ESTADO.get(p.estado)

    return render(request, 'cafeteria/gestion_pedidos.html', {
        'pedidos': pedidos,
        'hoy': hoy,
        'estado_seleccionado': estado,
        'estados_filtro': estados_filtro,
    })


@solo_encargado
def pedido_avanzar_estado(request, pk):
    if request.method != 'POST':
        return redirect('gestion_pedidos')

    pedido = get_object_or_404(Pedido, pk=pk)
    siguiente = TRANSICIONES_ESTADO.get(pedido.estado)

    if not siguiente:
        messages.error(request, f'El pedido #{pedido.id} está en estado "{pedido.estado}" y no puede avanzar más.')
        return redirect('gestion_pedidos')

    estado_solicitado = request.POST.get('nuevo_estado')
    if estado_solicitado and estado_solicitado != siguiente:
        messages.error(request, f'Transición inválida. El pedido debe pasar de "{pedido.estado}" a "{siguiente}".')
        return redirect('gestion_pedidos')

    pedido.estado = siguiente
    pedido.save()
    messages.success(request, f'Pedido #{pedido.id} avanzó al estado "{siguiente}".')
    return redirect('gestion_pedidos')
