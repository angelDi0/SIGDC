from django.urls import path
from usuarios import views

urlpatterns = [
    path('', views.PerfilList.as_view(), name='perfil-list'),
]
