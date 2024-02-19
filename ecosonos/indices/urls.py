from django.urls import path
from .views import (
    indices_vista,
    barra_progreso_vista,
    csv_cargado
)


urlpatterns = [
    path('', indices_vista, name='indices'),
    path('barra_progreso', barra_progreso_vista, name='barra_progreso'),
    path('csv_cargado', csv_cargado, name='csv_cargado'),
]
