from django.urls import path
from .views import (
    lluvia,
    progress_bar,
    csv_cargado
)


urlpatterns = [
    path('', lluvia, name='preproceso'),
    path('barra_progreso', progress_bar, name='barra_progreso'),
    path('csv_cargado', csv_cargado, name='csv_cargado'),
]
