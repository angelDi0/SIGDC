"""
URL configuration for SIGDC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as drf_authtoken_views

"registra las rutas de la API y el endpoint de autenticación por token"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # login/logout browsable
    path('api-token-auth/', drf_authtoken_views.obtain_auth_token, name='api-token-auth'),
    path('usuarios/', include('usuarios.urls')),
    path('donaciones/', include('donaciones.urls')),
    path('solicitudes/', include('solicitudes.urls')),
    path('', include('usuarios.urls')),  
]