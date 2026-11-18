from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('gestion/', views.panel_encargado, name='panel_encargado'),
]
