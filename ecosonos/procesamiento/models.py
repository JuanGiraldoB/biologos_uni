from django.db import models

# Create your models here.


class Progreso(models.Model):
    archivos_completados = models.IntegerField(default=0)
    cantidad_archivos = models.IntegerField(default=100, null=True)
