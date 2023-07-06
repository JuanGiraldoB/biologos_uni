from django.urls import path, include
from .views import etiquetado_auto, barra_progreso

urlpatterns = [
    path('', etiquetado_auto, name='etiquetado-auto'),
    path('barra_progreso', barra_progreso, name='barra_progreso'),
]
