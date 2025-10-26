from django.urls import path, include
from rest_framework import routers
from .api import SolicitudViewSet
from . import views

app_name = 'solicitudes'

router = routers.DefaultRouter()
router.register(r'api/solicitudes', SolicitudViewSet, basename='api-solicitud')

urlpatterns = [
    path('', include(router.urls)),
    path('crear/', views.crear_solicitud, name='crear'),
    path('<int:pk>/detalle/', views.detalle, name='detalle'),
]