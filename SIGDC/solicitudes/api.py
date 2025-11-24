from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS
from django.db import IntegrityError

from .models import Solicitud
from .serializers import SolicitudSerializer
from usuarios.models import Perfil


def _user_is_owner_of_solicitud(user, solicitud):
    """Helper local para comprobar propietario (tolerante con formato de campo)."""
    solicitante = getattr(solicitud, 'solicitante', None)
    if not solicitante:
        return False
    s_field = getattr(solicitante, 'usuario', None)
    try:
        if s_field and str(s_field) == str(getattr(user, 'username', '')):
            return True
        if hasattr(solicitante, 'email') and getattr(solicitante, 'email', None) and getattr(user, 'email', None):
            if str(getattr(solicitante, 'email')) == str(getattr(user, 'email')):
                return True
        if s_field and str(s_field).isdigit() and int(str(s_field)) == int(getattr(user, 'pk', -1)):
            return True
    except Exception:
        return False
    return False


class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer
    # Permiso personalizado: lectura pública, creación autenticada, edición/eliminación
    # sólo por el creador (solicitante) o por staff/superuser.

    class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
        def has_permission(self, request, view):
            # permitir GET/HEAD/OPTIONS a todo el mundo
            if request.method in SAFE_METHODS:
                return True
            # para creación, el usuario debe estar autenticado
            if view.action == 'create' and (not request.user or not request.user.is_authenticated):
                return False
            return True

        def has_object_permission(self, request, view, obj):
            # Safe methods already permit
            if request.method in SAFE_METHODS:
                return True
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                return False
            # staff o superuser pueden hacer cualquier cambio
            if user.is_staff or user.is_superuser:
                return True
            # permitir si es el propietario (comparación tolerante)
            return _user_is_owner_of_solicitud(user, obj)

    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def perform_create(self, serializer):
        # obtener usuario autenticado
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            raise ValidationError({'solicitante': 'Usuario no autenticado. Inicia sesión para crear una solicitud.'})

        # intentar obtener perfil asociado; si no existe, intentamos crearlo
        perfil = getattr(user, 'perfil', None)
        if perfil is None:
            email = getattr(user, 'email', None) or f'{user.username}@noemail.local'
            try:
                perfil, created = Perfil.objects.get_or_create(
                    usuario=getattr(user, 'username', str(user)),
                    defaults={'email': email}
                )
            except IntegrityError:
                # intentar recuperar cualquier perfil existente como fallback
                perfil = Perfil.objects.filter(usuario=getattr(user, 'username', str(user))).first()
                if perfil is None:
                    raise ValidationError({
                        'solicitante': (
                            'Perfil no disponible y no se pudo crear automáticamente. '
                            'Crea el perfil desde el admin o contacta al administrador.'
                        )
                    })

        serializer.save(solicitante=perfil)