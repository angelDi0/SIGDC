from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

from .models import Solicitud
from .serializers import SolicitudSerializer
from usuarios.models import Perfil


class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
                    usuario=user,
                    defaults={'email': email}
                )
            except IntegrityError:
                # intentar recuperar cualquier perfil existente como fallback
                perfil = Perfil.objects.filter(usuario=user).first()
                if perfil is None:
                    raise ValidationError({
                        'solicitante': (
                            'Perfil no disponible y no se pudo crear automáticamente. '
                            'Crea el perfil desde el admin o contacta al administrador.'
                        )
                    })

        serializer.save(solicitante=perfil)