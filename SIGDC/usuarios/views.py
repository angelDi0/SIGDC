from django.shortcuts import render
from rest_framework import status
from django.http import HttpResponse
from rest_framework.response import Response
from .models import Perfil
from .serializers import PerfilSerializer
from rest_framework.views import APIView

# Create your views here.
class PerfilList(APIView):
    def get(self, request):
        perfiles = Perfil.objects.all()
        serializer = PerfilSerializer(perfiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PerfilSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    return render(request, 'usuarios/index.html')

