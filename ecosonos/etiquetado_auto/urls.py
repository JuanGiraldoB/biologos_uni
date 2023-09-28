from django.urls import path
from .views import sonotipo_view, reconocer_view, barra_progreso, plots_view, plots_view, temporal_view

urlpatterns = [
    path('', sonotipo_view, name='etiquetado-auto'),
    path('reconocer', reconocer_view, name='reconocer'),
    path('temporal', temporal_view, name='temporal'),
    path('plots', plots_view, name='plots'),
    # path('espectrograma/<str:path>', spectrogram_view, name='espectrograma'),
    path('barra_progreso', barra_progreso, name='barra_progreso'),
]
