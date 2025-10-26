from rest_framework import serializers
from .models import Solicitud, Transaccion

class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = '__all__'

class SolicitudSerializer(serializers.ModelSerializer):
    transaccion = TransaccionSerializer(read_only=True)
    solicitante = serializers.PrimaryKeyRelatedField(read_only=True)
    donacion = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Solicitud
        fields = '__all__'