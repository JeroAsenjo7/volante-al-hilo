from django.db import models

# Create your models here.

class Stock(models.Model):
    TIPO_CHOICES = [
        ('rojo', 'Rojo'),
        ('negro', 'Negro'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, unique=True)
    cantidad = models.IntegerField(default=0)

    def __str__(self):
        return f"Hilo {self.tipo}: {self.cantidad}"

class HistorialColocacion(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    hilo = models.CharField(max_length=10)
    cliente_de = models.CharField(max_length=100, blank=True, null=True)
    fecha_colocacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"{self.fecha} {self.hora} — {self.hilo} — {self.cliente_de or 'Sin cliente'}"