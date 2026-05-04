from django.db import models

class Gasto(models.Model):
    descripcion = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()

    class Meta:
        ordering = ['-fecha', '-id']

    def __str__(self):
        return f"{self.fecha} — {self.descripcion}: ${self.monto}"