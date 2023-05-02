from django.urls import path
from . import views


urlpatterns = [
    path('', views.etiquetado, name='etiquetado'),
    path('espectrograma/<str:ruta>', views.espectrograma, name='espectrograma'),
]
