from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q, ProtectedError
from functools import wraps
from .models import Categoria, Producto
from .forms import CategoriaForm, ProductoForm


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
