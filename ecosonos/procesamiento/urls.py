from django.urls import path
from . import views


urlpatterns = [
    path('', views.lluvia, name='preproceso'),
    path('barra_progreso', views.barra_progreso, name='barra_progreso'),
]
