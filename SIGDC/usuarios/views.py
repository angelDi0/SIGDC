from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Perfil
from .serializers import PerfilSerializer
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from donaciones.models import Donacion
from solicitudes.models import Solicitud

# ...existing code...

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
    """
    Renderiza la página de inicio / login (usuarios/index.html).
    Si se envía POST intenta autenticar al usuario usando email o username.
    """
    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = None
        # Intentar autenticar directamente con el valor enviado como username
        if email_or_username:
            user = authenticate(request, username=email_or_username, password=password)

        # Si falla, buscar por email y autenticar con su username
        if not user and email_or_username:
            try:
                u = User.objects.get(email=email_or_username)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            messages.success(request, 'Has iniciado sesión correctamente.')
            return redirect('usuarios:menu')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'usuarios/index.html')


def registro(request):
    """
    Registro usando UserCreationForm. Guarda first_name, last_name y email del POST.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        # traducir etiquetas y añadir attrs a widgets 
        form.fields['username'].label = 'Nombre de usuario'
        form.fields['password1'].label = 'Contraseña'
        form.fields['password2'].label = 'Confirmar contraseña'
        form.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        form.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        form.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})

        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.save()
            messages.success(request, 'Cuenta creada correctamente. Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
        else:
            return render(request, 'usuarios/registro.html', {'form': form})
    else:
        form = UserCreationForm()
        form.fields['username'].label = 'Nombre de usuario'
        form.fields['password1'].label = 'Contraseña'
        form.fields['password2'].label = 'Confirmar contraseña'
        form.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        form.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        form.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})

    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def menu(request):
    donaciones = Donacion.objects.order_by('-id')[:10]   # ajustar orden/cantidad
    solicitudes = Solicitud.objects.order_by('-id')[:10]
    return render(request, 'SIGDC/menu.html', {'donaciones': donaciones, 'solicitudes': solicitudes})


@login_required
def salir(request):
    """Logout y redirección al login."""
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('usuarios:login')

@staff_member_required
def admin_users(request):
    """
    Lista usuarios y procesa eliminación vía POST (solo staff).
    URL: /usuarios/admin-users/
    """
    if request.method == 'POST':
        delete_id = request.POST.get('delete_user_id')
        if delete_id:
            # evitar que un admin se elimine a sí mismo
            if str(request.user.id) == str(delete_id):
                messages.error(request, 'No puedes eliminarte a ti mismo.')
            else:
                target = get_object_or_404(User, pk=delete_id)
                username = target.username
                target.delete()
                messages.success(request, f'Usuario "{username}" eliminado.')
        return redirect('usuarios:admin_users')

    users = User.objects.order_by('-date_joined').all()
    return render(request, 'usuarios/admin.html', {'users': users})

@staff_member_required
def admin_edit_user(request, user_id):
    """
    Editar datos de un usuario (solo si no es staff).
    Solo staff (administradores) pueden acceder a esta vista.
    """
    target = get_object_or_404(User, pk=user_id)

    # No permitir editar usuarios staff
    if target.is_staff:
        messages.error(request, 'No se pueden editar usuarios con privilegios de administrador.')
        return redirect('usuarios:admin_users')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        is_active = True if request.POST.get('is_active') == 'on' else False

        # Validaciones básicas
        if not username:
            messages.error(request, 'El nombre de usuario no puede estar vacío.')
            return render(request, 'usuarios/admin_edit.html', {'u': target})

        if User.objects.filter(username=username).exclude(pk=target.pk).exists():
            messages.error(request, 'El nombre de usuario ya está en uso por otro usuario.')
            return render(request, 'usuarios/admin_edit.html', {'u': target})

        if email and User.objects.filter(email=email).exclude(pk=target.pk).exists():
            messages.error(request, 'El correo ya está en uso por otro usuario.')
            return render(request, 'usuarios/admin_edit.html', {'u': target})

        # Guardar cambios
        target.username = username
        target.first_name = first_name
        target.last_name = last_name
        target.email = email
        target.is_active = is_active
        target.save()

        messages.success(request, f'Usuario "{target.username}" actualizado correctamente.')
        return redirect('usuarios:admin_users')

    # GET: mostrar formulario con datos actuales
    return render(request, 'usuarios/admin_edit.html', {'u': target})