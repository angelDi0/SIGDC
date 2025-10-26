from django.db import models

class Solicitud(models.Model):
    solicitante = models.ForeignKey('usuarios.Perfil', on_delete=models.CASCADE, related_name='solicitudes')
    donacion = models.ForeignKey('donaciones.Donacion', on_delete=models.CASCADE, related_name='solicitudes', null=True, blank=True)
    titulo = models.CharField(max_length=200, blank=True)
    detalle = models.TextField(blank=True)
    mensaje = models.TextField(blank=True)
    tipo = models.CharField(max_length=50, blank=True)            # añadido
    cantidad = models.PositiveIntegerField(null=True, blank=True) # añadido
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False)

    def __str__(self):
        return f"Solicitud #{self.pk} - {self.titulo or self.tipo or 'sin título'}"

class Transaccion(models.Model):
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE, related_name='transaccion')
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    confirmacion_donante = models.BooleanField(default=False)
    confirmacion_solicitante = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaccion #{self.pk} (solicitud #{self.solicitud_id})"