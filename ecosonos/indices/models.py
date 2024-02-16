from django.db import models

# Create your models here.


class Indices(models.Model):
    grabaciones = models.JSONField()
    indices_seleccionados = models.JSONField()
    valores = models.JSONField()
    csv_path = models.CharField(max_length=1000)

    def __str__(self):
        return f'grabaciones: {self.grabaciones} \n\
                    indices seleccionados: {self.indices_seleccionados} \n\
                    valores: {self.valores} \n\
                    csv_path: {self.csv_path}'
