from django.db import models

# Create your models here.

from django.db import models
from django.core.exceptions import ValidationError
import datetime
from django.core.validators import MinValueValidator


class Turno(models.Model):

    HILO_CHOICES = [
        ('negro', 'Negro'),
        ('rojo', 'Rojo'),
    ]

    fecha = models.DateField()
    hora = models.TimeField()
    auto = models.CharField(max_length=100)
    cliente_de = models.CharField(max_length=100, blank=True, null=True)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    hilo = models.CharField(max_length=10, choices=HILO_CHOICES)
    atendido = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha', 'hora']

    def clean(self):

    # Si no hay fecha u hora, no validar todavía
        if not self.fecha or not self.hora:
            return

    # No domingos
        if self.fecha.weekday() == 6:
            raise ValidationError("No se permiten turnos los domingos.")

    # Rango horario
        if not (datetime.time(9, 0) <= self.hora <= datetime.time(19, 30)):
            raise ValidationError("Horario fuera de rango (9:00 a 19:30).")

    # Solo cada 30 minutos
        if self.hora.minute not in [0, 15, 30, 45]:
            raise ValidationError("Los turnos deben ser cada 15 minutos.")
    
    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        if Turno.objects.filter(
        fecha=self.fecha,
        hora=self.hora
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Ya existe un turno para esa fecha y hora.")