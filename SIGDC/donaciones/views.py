from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Donacion, Categoria
from .serializers import DonacionSerializer, CategoriaSerializer
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404

# Comunicación segura con solicitudes
from solicitudes.models import Solicitud
from solicitudes.utils import user_can_access_solicitud


class DonacionList(APIView):
    def get(self, request, format=None):
        donaciones = Donacion.objects.all()
        serializer = DonacionSerializer(donaciones, many=True)
        return Response(serializer.data)

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
        origen = request.POST.get('origen', '').strip()
        monto = request.POST.get('monto', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        d = Donacion.objects.create(
            tipo=request.POST.get('tipo') or tipo,
            origen=origen,
            monto=monto or None,
            descripcion=descripcion
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'id': d.id})

        return redirect('usuarios:menu')

    return render(request, 'donaciones/crear_donacion.html', {'tipo': tipo})


def detalle(request, pk):
    d = get_object_or_404(Donacion, pk=pk)
    return render(request, 'donaciones/detalle.html', {'d': d})

# Comunicación segura entre apps
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def lista_solicitudes_para_donaciones(request):
    """La app Donaciones accede a Solicitudes solo si el usuario es staff."""
    solicitudes = Solicitud.objects.all().order_by('-id')
    return render(request, "donaciones/solicitudes_para_donaciones.html", {
        "solicitudes": solicitudes
    })


@login_required
def ver_solicitud_desde_donaciones(request, pk):
    """Acceso seguro: superuser o dueño."""
    solicitud = get_object_or_404(Solicitud, pk=pk)

    if not user_can_access_solicitud(request.user, solicitud):
        return HttpResponseForbidden("No tienes permiso para ver esta solicitud.")

    return render(request, "donaciones/detalle_solicitud.html", {
        "solicitud": solicitud
    })
