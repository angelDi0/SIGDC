from django.db import models
from usuarios.models import Perfil
from donaciones.models import Donacion

class Solicitud(models.Model):
    solicitante = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='solicitudes')
    donacion = models.ForeignKey(Donacion, on_delete=models.CASCADE, related_name='solicitudes')
    mensaje = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False)

    def __str__(self):
        return f"Solicitud de {self.solicitante.user.username} por {self.donacion.titulo}"


class Transaccion(models.Model):
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    confirmacion_donante = models.BooleanField(default=False)
    confirmacion_solicitante = models.BooleanField(default=False)

    def __str__(self):
        return f"Transacción #{self.id} - {self.solicitud.donacion.titulo}"
