from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from donaciones import views

urlpatterns = [
    path('', views.DonacionList.as_view()),
    path('categoria/', views.CategoriasList.as_view()),
]
