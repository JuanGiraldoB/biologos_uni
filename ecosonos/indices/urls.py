from django.urls import path
from . import views


urlpatterns = [
    path('', views.indices_vista, name='indices'),
    path('barra_progreso', views.barra_progreso_vista, name='barra_progreso'),
]
