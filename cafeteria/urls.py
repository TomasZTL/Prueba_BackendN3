from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('carrito/', views.carrito_ver, name='carrito_ver'),
    path('carrito/agregar/<int:pk>/', views.carrito_agregar, name='carrito_agregar'),
    path('carrito/actualizar/<int:pk>/', views.carrito_actualizar, name='carrito_actualizar'),
    path('carrito/quitar/<int:pk>/', views.carrito_quitar, name='carrito_quitar'),
    path('carrito/vaciar/', views.carrito_vaciar, name='carrito_vaciar'),
    path('carrito/confirmar/', views.carrito_confirmar, name='carrito_confirmar'),
    path('gestion/', views.panel_encargado, name='panel_encargado'),
    path('gestion/categorias/', views.categoria_lista, name='categoria_lista'),
    path('gestion/categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('gestion/categorias/<int:pk>/', views.categoria_detalle, name='categoria_detalle'),
    path('gestion/categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('gestion/categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
    path('gestion/productos/', views.producto_lista, name='producto_lista'),
    path('gestion/productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('gestion/productos/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('gestion/productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('gestion/productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
]
