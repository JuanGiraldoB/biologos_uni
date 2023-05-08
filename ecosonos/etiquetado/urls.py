from django.urls import path
from . import views


urlpatterns = [
    path('', views.etiquetado, name='etiquetado'),
    path('espectrograma/<str:ruta>', views.espectrograma, name='espectrograma'),
    path('espectrograma/reproducir/<str:ruta>',
         views.reproducir_sonido_archivo, name='reproducir'),
]
