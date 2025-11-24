from django.urls import path, include
from rest_framework import routers
from .api import SolicitudViewSet
from . import views
from .views import SolicitudEditCBV, SolicitudDeleteCBV

app_name = 'solicitudes'

router = routers.DefaultRouter()
router.register(r'api/solicitudes', SolicitudViewSet, basename='api-solicitud')

urlpatterns = [
    path('', include(router.urls)),

    # FBV (vistas originales)
    path('crear/', views.crear_solicitud, name='crear'),
    path('<int:pk>/detalle/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar_solicitud, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_solicitud, name='eliminar'),

    # CBV (vistas con mixins)
    path('<int:pk>/editar-cbv/', SolicitudEditCBV.as_view(), name='editar_cbv'),
    path('<int:pk>/eliminar-cbv/', SolicitudDeleteCBV.as_view(), name='eliminar_cbv'),
]
