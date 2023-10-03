from django.db import models


class MetodologiaResult(models.Model):
    datos_clasifi = models.JSONField(default=list, null=True)
    mean_class = models.JSONField(default=list, null=True)
    infoZC = models.JSONField(default=list, null=True)
    gadso = models.JSONField(default=list, null=True)
    representativo = models.JSONField(default=list, null=True)
    dispersion = models.JSONField(default=list, null=True)
    frecuencia = models.JSONField(default=list, null=True)

    def __str__(self):
        return f"Metodologia Result - ID: {self.pk} - {self.representativo}"


class GuardadoClusterResult(models.Model):
    data = models.JSONField()
