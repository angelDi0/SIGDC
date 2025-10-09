from django.contrib import admin

from .models import Donacion, Categoria

# Register your models here.

admin.site.register(Donacion)
admin.site.register(Categoria)
