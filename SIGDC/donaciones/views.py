from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Donacion, Categoria
from .serializers import DonacionSerializer, CategoriaSerializer

class DonacionList(APIView):
    
    def get(self, request, format=None):
        donaciones = Donacion.objects.all()
        serilizer = DonacionSerializer(donaciones, many=True)
        return Response(serilizer.data)

    def post(self, request, format=None):
        serializer = DonacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class CategoriasList(APIView):
    def get(self, request, format=None):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = CategoriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)