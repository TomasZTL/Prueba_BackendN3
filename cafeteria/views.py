from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps


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
        return redirect('panel_encargado')
    return redirect('catalogo')


@solo_cliente
def catalogo(request):
    return render(request, 'cafeteria/catalogo.html')


@solo_encargado
def panel_encargado(request):
    return render(request, 'cafeteria/panel_encargado.html')
