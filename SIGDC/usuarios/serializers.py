from .models import Perfil
from rest_framework import serializers

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ['id', 'usuario', 'email', 'telefono', 'direccion', 'ciudad', 'pais', 'activo']

