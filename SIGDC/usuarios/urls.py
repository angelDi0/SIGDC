from django.urls import path
from . import views

# ...existing code...

app_name = 'usuarios'

urlpatterns = [
    # API existente (se mantiene en la raíz de la app)
    path('', views.PerfilList.as_view(), name='perfil-list'),

    # vistas de frontend
    path('index/', views.index, name='index'),
    path('login/', views.index, name='login'),

    # registro
    path('registro/', views.registro, name='registro'),

    # menú y logout
    path('menu/', views.menu, name='menu'),
    path('logout/', views.salir, name='logout'),

    # opción: exponer la API en una ruta dedicada además de la raíz si se desea
    path('api/perfiles/', views.PerfilList.as_view(), name='api-perfil-list'),
]