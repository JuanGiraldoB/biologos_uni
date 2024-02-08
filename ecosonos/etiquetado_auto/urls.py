from django.urls import path
from .views import (
    etiquetado_auto_view,
    sonotipo_view,
    reconocer_view,
    temporal_view,
    barra_progreso,
    plots_view,
)

urlpatterns = [
    path('', etiquetado_auto_view, name='etiquetado-auto'),
    path('sonotipo', sonotipo_view, name='sonotipo'),
    path('reconocer', reconocer_view, name='reconocer'),
    path('temporal', temporal_view, name='temporal'),
    path('plots', plots_view, name='plots'),
    path('barra_progreso', barra_progreso, name='barra_progreso'),
]
