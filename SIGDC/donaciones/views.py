from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Donacion, Categoria
from .serializers import DonacionSerializer, CategoriaSerializer
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Donacion
from django.shortcuts import get_object_or_404, render

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

def crear_donacion(request):
    tipo = request.GET.get('tipo')
    if request.method == 'POST':
        # ajustar según campos reales de tu modelo Donacion
        origen = request.POST.get('origen', '').strip()
        monto = request.POST.get('monto', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        # crea registro (cambia los campos según tu modelo)
        d = Donacion.objects.create(
            tipo= request.POST.get('tipo') or request.GET.get('tipo'),
            origen=origen,
            monto = monto or None,
            descripcion = descripcion
        )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'id': d.id})
        return redirect('usuarios:menu')
    # GET → devolver el fragmento de formulario para el modal
    return render(request, 'donaciones/crear_donacion.html', {'tipo': tipo})

def detalle(request, pk):
    """Vista que devuelve el fragmento HTML con todos los datos de una donación."""
    d = get_object_or_404(Donacion, pk=pk)
    return render(request, 'donaciones/detalle.html', {'d': d})