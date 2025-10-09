from django.db import models
from usuarios.models import Perfil

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Donacion(models.Model):
    ESTADO_DONACION = [
        ('DISPONIBLE', 'Disponible'),
        ('RESERVADO', 'Reservado'),
        ('ENTREGADO', 'Entregado'),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    donante = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='donaciones')
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_DONACION, default='DISPONIBLE')
    imagen = models.ImageField(upload_to='donaciones/', blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} - {self.estado}"
