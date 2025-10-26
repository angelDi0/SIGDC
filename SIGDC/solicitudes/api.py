from rest_framework import viewsets, permissions, filters
from .models import Solicitud
from .serializers import SolicitudSerializer

class SolicitudViewSet(viewsets.ModelViewSet):
    """
    API REST para el modelo Solicitud.
    Permite CRUD (leer para todos, mutaciones solo para usuarios autenticados).
    """
    queryset = Solicitud.objects.select_related('solicitante', 'donacion').all()
    serializer_class = SolicitudSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'detalle', 'mensaje', 'tipo']

    def perform_create(self, serializer):
        perfil = getattr(self.request.user, 'perfil', None)
        serializer.save(solicitante=perfil)