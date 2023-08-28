from django.urls import path, include
from .views import etiquetado_auto, barra_progreso, files_list_view

urlpatterns = [
    path('', etiquetado_auto, name='etiquetado-auto'),
    path('lista_audios', files_list_view, name='lista_audios'),
    path('barra_progreso', barra_progreso, name='barra_progreso'),
]
