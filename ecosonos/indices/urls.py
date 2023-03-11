from django.urls import path
from . import views


urlpatterns = [
    path('', views.indices, name='indices'),
    path('folder', views.folder_view, name='folder_view'),
    path('procesar', views.procesar, name='procesar_view'),
]
