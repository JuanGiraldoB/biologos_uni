from django.urls import path
from . import views


urlpatterns = [
    # path('', views.indices, name='indices'),
    path('', views.lluvia_carpeta, name='indices'),
    path('barra_progreso', views.barra_progreso, name='barra_progreso'),
]
