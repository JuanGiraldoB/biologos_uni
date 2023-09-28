from django.db import models

# Create your models here.


class Progreso(models.Model):
    archivos_completados = models.IntegerField(default=0)
    cantidad_archivos = models.IntegerField(default=0, null=True)
    uno_porciento = models.IntegerField(default=0)
