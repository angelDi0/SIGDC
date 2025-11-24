from rest_framework import viewsets, permissions
from .models import Donacion
from .serializers import DonacionSerializer

class DonacionViewSet(viewsets.ModelViewSet):
    queryset = Donacion.objects.all()
    serializer_class = DonacionSerializer
    # Permiso personalizado: lectura pública, creación autenticada, edición/eliminación
    # sólo por el creador (donante) o por staff/superuser.
    class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
        def has_permission(self, request, view):
            if request.method in permissions.SAFE_METHODS:
                return True
            if view.action == 'create' and (not request.user or not request.user.is_authenticated):
                return False
            return True

        def has_object_permission(self, request, view, obj):
            if request.method in permissions.SAFE_METHODS:
                return True
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                return False
            if user.is_staff or user.is_superuser:
                return True
            donante = getattr(obj, 'donante', None)
            if donante is None:
                return False
            donante_username = getattr(donante, 'usuario', None)
            return str(donante_username) == str(getattr(user, 'username', ''))

    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs