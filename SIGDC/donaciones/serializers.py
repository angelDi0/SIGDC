from rest_framework import serializers
from django.core.exceptions import FieldError
from .models import Donacion, Categoria
from usuarios.models import Perfil
from django.db import IntegrityError

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class DonacionSerializer(serializers.ModelSerializer):
    donante = serializers.PrimaryKeyRelatedField(read_only=True)
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), required=False, allow_null=True)
    estado = serializers.CharField(read_only=True)
    imagen = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Donacion
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
            raise serializers.ValidationError({'donante': 'Usuario no autenticado. Inicie sesión.'})

        perfil = getattr(request.user, 'perfil', None)

        if perfil is None:
            email = getattr(request.user, 'email', None) or f'{request.user.username}@noemail.local'
            try:
                perfil, created = Perfil.objects.get_or_create(
                    usuario=request.user,
                    defaults={'email': email}
                )
            except IntegrityError as e:
                # Si falla por unique en email de otro perfil, intentar buscar por usuario
                perfil = Perfil.objects.filter(usuario=request.user).first()
                if perfil is None:
                    raise serializers.ValidationError({
                        'donante': (
                            'No existe un Perfil asociado y no se pudo crear automáticamente: '
                            f'{e}. Cree el perfil desde el admin o el flujo de registro.'
                        )
                    })

        validated_data['donante'] = perfil
        return super().create(validated_data)