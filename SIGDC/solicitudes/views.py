from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Solicitud
from django.shortcuts import get_object_or_404, render, redirect

def crear_solicitud(request):
    tipo = request.GET.get('tipo')
    if request.method == 'POST':
        # ajustar según campos reales de tu modelo Solicitud
        titulo = request.POST.get('titulo', '').strip()
        detalle = request.POST.get('detalle', '').strip()
        cantidad = request.POST.get('cantidad', '').strip()
        s = Solicitud.objects.create(
            tipo = request.POST.get('tipo') or tipo,
            titulo = titulo,
            detalle = detalle,
            cantidad = cantidad or None
        )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'id': s.id})
        return redirect('usuarios:menu')
    return render(request, 'solicitudes/crear_solicitud.html', {'tipo': tipo})

def detalle(request, pk):
    s = get_object_or_404(Solicitud, pk=pk)
    return render(request, 'solicitudes/detalle.html', {'s': s})