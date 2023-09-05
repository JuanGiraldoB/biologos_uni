from django.db import models


class MetodologiaResult(models.Model):
    datos_clasifi = models.JSONField(null=True)
    mean_class = models.JSONField(null=True)
    infoZC = models.JSONField(null=True)
    gadso = models.JSONField(null=True)
    representativo = models.JSONField(null=True)
    dispersion = models.JSONField(null=True)
    frecuencia = models.JSONField(null=True)

    def __str__(self):
        return f"Metodologia Result - ID: {self.pk}"
