from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    ROLES = [
        ('DONANTE', 'Donante'),
        ('SOLICITANTE', 'Solicitante'),
        ('AMBOS', 'Ambos'),
        ('ADMIN', 'Administrador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=15, choices=ROLES, default='DONANTE')
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

    @property
    def es_admin(self):
        return self.rol == 'ADMIN'
