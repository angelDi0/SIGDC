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
    Registro simple usando UserCreationForm.
    Guarda first_name, last_name y email si se proporcionan en el POST.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = request.POST.get('first_name', '') or user.first_name
            user.last_name = request.POST.get('last_name', '') or user.last_name
            user.email = request.POST.get('email', '') or user.email
            user.save()
            messages.success(request, 'Cuenta creada correctamente. Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = UserCreationForm()

    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def menu(request):
    """Vista del menú principal. Requiere autenticación."""
    return render(request, 'SIGDC/menu.html')


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