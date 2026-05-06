from django import forms
from .models import Turno
import datetime

CLIENTES = [
    ('', '— Seleccionar —'),
    ('Bauza', 'Bauza'),
    ('Cayla', 'Cayla'),
    ('Tomi', 'Tomi'),
]

class TurnoForm(forms.ModelForm):

    class Meta:
        model = Turno
        fields = ['fecha', 'hora', 'auto', 'cliente_de', 'precio', 'hilo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'precio': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['fecha'].input_formats = ['%Y-%m-%d']

        horarios = []
        hora_actual = datetime.time(9, 0)
        fin = datetime.time(19, 30)

        while hora_actual <= fin:
            horarios.append((hora_actual.strftime("%H:%M:%S"), hora_actual.strftime("%H:%M")))
            dt = datetime.datetime.combine(datetime.date.today(), hora_actual)
            dt += datetime.timedelta(minutes=15)
            hora_actual = dt.time()

        self.fields['hora'] = forms.TypedChoiceField(
            choices=horarios,
            coerce=lambda v: datetime.time.fromisoformat(v),
            label="Hora",
        )

        self.fields['cliente_de'] = forms.ChoiceField(
            choices=CLIENTES,
            required=False,
            label="Cliente de",
        )