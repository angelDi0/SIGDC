from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

from .models import Solicitud
from usuarios.models import Perfil


# ===========================================================
#       FUNCIÓN AUXILIAR: verificar propietario (owner)
# ===========================================================
def _user_is_owner_of_solicitud(user, solicitud):
    solicitante = getattr(solicitud, 'solicitante', None)
    if not solicitante:
        return False

    s_field = getattr(solicitante, 'usuario', None)

    try:
        # match por username
        if s_field and str(s_field) == str(user.username):
            return True

        # match por email
        if hasattr(solicitante, 'email') and solicitante.email and user.email:
            if str(solicitante.email) == str(user.email):
                return True

        # match por ID si viene como texto
        if s_field and str(s_field).isdigit() and int(s_field) == int(user.pk):
            return True

    except Exception:
        return False

    return False


# ===========================================================
#                  VISTAS FBV (TUS ORIGINALES)
# ===========================================================

@login_required
def crear_solicitud(request):
    tipo = request.GET.get('tipo')

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        detalle = request.POST.get('detalle', '').strip()
        cantidad = request.POST.get('cantidad', '').strip()

        perfil = getattr(request.user, 'perfil', None)
        if perfil is None:
            email = request.user.email or f"{request.user.username}@noemail.local"
            perfil, _ = Perfil.objects.get_or_create(usuario=request.user.username, defaults={'email': email})

        s = Solicitud.objects.create(
            tipo=request.POST.get('tipo') or tipo,
            titulo=titulo,
            detalle=detalle,
            cantidad=cantidad or None,
            solicitante=perfil
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'id': s.id})

        return redirect('usuarios:menu')

    return render(request, 'solicitudes/crear_solicitud.html', {'tipo': tipo})


def detalle(request, pk):
    s = get_object_or_404(Solicitud, pk=pk)
    return render(request, 'solicitudes/detalle.html', {'s': s})


@login_required
def editar_solicitud(request, pk):
    s = get_object_or_404(Solicitud, pk=pk)
    user = request.user

    owns = _user_is_owner_of_solicitud(user, s)

    if not (user.is_staff or user.is_superuser or owns or user.has_perm('solicitudes.change_solicitud')):
        return HttpResponseForbidden('No tienes permiso para editar esta solicitud.')

    if request.method == 'POST':
        s.titulo = request.POST.get('titulo', s.titulo)
        s.detalle = request.POST.get('detalle', s.detalle)
        s.cantidad = request.POST.get('cantidad', s.cantidad)
        s.save()

        messages.success(request, 'Solicitud actualizada correctamente.')
        return redirect('solicitudes:detalle', pk=s.pk)

    return render(request, 'solicitudes/editar.html', {'s': s})


@login_required
def eliminar_solicitud(request, pk):
    s = get_object_or_404(Solicitud, pk=pk)
    user = request.user

    owns = _user_is_owner_of_solicitud(user, s)

    if not (user.is_staff or user.is_superuser or owns or user.has_perm('solicitudes.delete_solicitud')):
        return HttpResponseForbidden('No tienes permiso para eliminar esta solicitud.')

    if request.method == 'POST':
        s.delete()
        messages.success(request, 'Solicitud eliminada.')
        return redirect('usuarios:menu')

    return render(request, 'solicitudes/confirm_delete.html', {'s': s})


# ===========================================================
#                  NUEVAS VISTAS CON MIXINS (CBV)
# ===========================================================

class SolicitudEditCBV(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vista basada en clases con mixins:
    - LoginRequiredMixin → exige autenticación
    - UserPassesTestMixin → valida que sea dueño, staff, superuser o tenga permiso
    """
    model = Solicitud
    fields = ["titulo", "detalle", "cantidad", "tipo"]
    template_name = "solicitudes/editar.html"

    def test_func(self):
        user = self.request.user
        obj = self.get_object()

        return (
            user.is_staff
            or user.is_superuser
            or user.has_perm("solicitudes.change_solicitud")
            or _user_is_owner_of_solicitud(user, obj)
        )

    def get_success_url(self):
        return reverse_lazy("solicitudes:detalle", args=[self.object.pk])


class SolicitudDeleteCBV(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Vista basada en clases con mixins:
    - LoginRequiredMixin → exige login
    - PermissionRequiredMixin → exige permiso delete_solicitud
      *pero añadimos owner-check y staff-check*
    """
    model = Solicitud
    template_name = "solicitudes/confirm_delete.html"
    permission_required = "solicitudes.delete_solicitud"
    success_url = reverse_lazy("usuarios:menu")

    def has_permission(self):
        user = self.request.user
        obj = self.get_object()

        return (
            user.is_staff
            or user.is_superuser
            or user.has_perm(self.permission_required)
            or _user_is_owner_of_solicitud(user, obj)
        )
