from django.urls import path
from . import views


urlpatterns = [
    path('', views.lluvia, name='preproceso'),
    path('escoger_carpeta', views.escoger_carpeta, name='escoger_carpeta'),
    path('lista_carpeta', views.lista_carpetas, name='lista_carpeta'),
]
