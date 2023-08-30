from django.urls import path, include
from .views import etiquetado_auto_view, barra_progreso, spectrogram_view, spectrogram_view

urlpatterns = [
    path('', etiquetado_auto_view, name='etiquetado-auto'),
    path('espectrograma', spectrogram_view, name='espectrograma'),
    # path('espectrograma/<str:path>', spectrogram_view, name='espectrograma'),
    path('barra_progreso', barra_progreso, name='barra_progreso'),
]
