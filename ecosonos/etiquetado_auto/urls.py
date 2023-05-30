from django.urls import path, include
from .views import etiquetado_auto

urlpatterns = [
    path('', etiquetado_auto, name='etiquetado-auto'),
]
