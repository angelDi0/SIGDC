from rest_framework import serializers
from .models import Solicitud, Transaccion
from django.contrib.auth import get_user_model
from donaciones.models import Donacion
from usuarios.models import Perfil

User = get_user_model()

class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = '__all__'

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'  # ajusta campos si quieres limitar lo expuesto

class DonacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donacion
        fields = '__all__'

class SolicitudSerializer(serializers.ModelSerializer):
    transaccion = TransaccionSerializer(read_only=True)
    solicitante = PerfilSerializer(read_only=True)
    donacion = DonacionSerializer(read_only=True)

    class Meta:
        model = Solicitud
        fields = '__all__'