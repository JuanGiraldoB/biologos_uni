from django.urls import path
from .views import sonotipo_view, reconocer_view, barra_progreso, spectrogram_view, spectrogram_view

urlpatterns = [
    path('', sonotipo_view, name='etiquetado-auto'),
    path('reconocer', reconocer_view, name='reconocer'),
    path('espectrograma', spectrogram_view, name='espectrograma'),
    # path('espectrograma/<str:path>', spectrogram_view, name='espectrograma'),
    path('barra_progreso', barra_progreso, name='barra_progreso'),
]
