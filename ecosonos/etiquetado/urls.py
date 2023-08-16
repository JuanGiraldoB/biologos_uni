from django.urls import path
from . import views


urlpatterns = [
    path('', views.label_view, name='etiquetado'),
    path('espectrograma/<str:path>', views.spectrogram_view, name='espectrograma'),
    path('espectrograma/reproducir/<str:path>',
         views.play_segment_view, name='reproducir'),
]
