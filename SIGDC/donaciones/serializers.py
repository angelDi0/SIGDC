from rest_framework import serializers
from .models import Donacion, Categoria

class DonacionSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return Donacion.objects.create(**validated_data)
    
    class Meta:
        model = Donacion
        fields = ['id', 'monto', 'fecha', 'donante']
        
class CategoriaSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        return Categoria.objects.create(**validated_data)
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']
    