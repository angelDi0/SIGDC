from django.contrib import admin

from .models import Solicitud, Transaccion

# Register your models here.

admin.site.register(Solicitud)
admin.site.register(Transaccion)
