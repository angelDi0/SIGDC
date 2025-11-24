from django.urls import path, include
from rest_framework import routers
from .api import DonacionViewSet
from . import views

app_name = 'donaciones'  

router = routers.DefaultRouter()
router.register(r'api/donaciones', DonacionViewSet, basename='api-donacion')

urlpatterns = [
    path('', include(router.urls)),
    path('crear/', views.crear_donacion, name='crear'),
    path('<int:pk>/detalle/', views.detalle, name='detalle'),
    path('ver-solicitudes/', views.lista_solicitudes_para_donaciones, name='solicitudes_para_donaciones'),
    path('ver-solicitud/<int:pk>/', views.ver_solicitud_desde_donaciones, name='ver_solicitud_desde_donaciones'),
]