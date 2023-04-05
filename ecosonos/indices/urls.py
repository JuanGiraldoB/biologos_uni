from django.urls import path
from . import views


urlpatterns = [
    path('', views.app, name='indices'),
    path('barra_progreso', views.barra_progreso, name='barra_progreso'),
]
