from django.shortcuts import render
from .forms import TurnoForm
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
import datetime
# Create your views here.

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Turno
from collections import defaultdict

from stock.models import Stock, HistorialColocacion

class TurnoToggleAtendidoView(View):
    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)

        if not turno.atendido:
            # Descontar stock
            try:
                stock = Stock.objects.get(tipo=turno.hilo)
                if stock.cantidad > 0:
                    stock.cantidad -= 1
                    stock.save()
            except Stock.DoesNotExist:
                pass

            # Guardar en historial
            HistorialColocacion.objects.create(
                fecha=turno.fecha,
                hora=turno.hora,
                hilo=turno.hilo,
                cliente_de=turno.cliente_de,
            )

        else:
            # Devolver stock
            try:
                stock = Stock.objects.get(tipo=turno.hilo)
                stock.cantidad += 1
                stock.save()
            except Stock.DoesNotExist:
                pass

        turno.atendido = not turno.atendido
        turno.save()
        return redirect('lista_turnos')

class TurnoListView(ListView):
    model = Turno
    template_name = 'turnos/turno_list.html'
    context_object_name = 'turnos'

    def get_queryset(self):
        qs = super().get_queryset()
        fecha = self.request.GET.get('fecha')
        if fecha:
            try:
                fecha_parsed = datetime.date.fromisoformat(fecha)
                qs = qs.filter(fecha=fecha_parsed)
            except ValueError:
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fecha_busqueda'] = self.request.GET.get('fecha', '')
        
        dias_es = {
            0: "Lunes", 1: "Martes", 2: "Miércoles",
            3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo",
        }

        meses_es = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
        }

        semanas = {}

        for turno in context['turnos']:
            año = turno.fecha.year
            mes = turno.fecha.month
            semana_del_mes = (turno.fecha.day - 1) // 7 + 1
            clave_semana = (año, mes, semana_del_mes)

            if clave_semana not in semanas:
                semanas[clave_semana] = {
                    'titulo': f"Semana {semana_del_mes} — {meses_es[mes]} {año}",
                    'dias': {},
                    'total': 0,  # ← agregar
                }

            dia_num = turno.fecha.weekday()
            if dia_num not in semanas[clave_semana]['dias']:
                semanas[clave_semana]['dias'][dia_num] = {
                    'nombre': dias_es[dia_num],
                    'fecha': turno.fecha,
                    'turnos': [],
                    'total': 0,  # ← agregar
                }
            semanas[clave_semana]['dias'][dia_num]['turnos'].append(turno)

    # Sumar precio si existe
            if turno.precio:
                semanas[clave_semana]['dias'][dia_num]['total'] += turno.precio
                semanas[clave_semana]['total'] += turno.precio

    # Ordenar semanas y días dentro de cada semana
        semanas_ordenadas = {}
        for clave in sorted(semanas):
            semanas_ordenadas[clave] = semanas[clave]
            semanas_ordenadas[clave]['dias'] = dict(sorted(semanas[clave]['dias'].items()))

        context['semanas'] = semanas_ordenadas
        return context

class TurnoCreateView(CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/formulario.html'
    success_url = reverse_lazy('lista_turnos')

class TurnoUpdateView(UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/formulario.html'
    success_url = reverse_lazy('lista_turnos')

class TurnoDeleteView(DeleteView):
    model = Turno
    template_name = 'turnos/eliminar.html'
    success_url = reverse_lazy('lista_turnos')

# vista de formulario para eliminar turnos
class EliminarRangoView(View):
    def get(self, request):
        return render(request, 'turnos/eliminar_rango.html')

    def post(self, request):
        desde = request.POST.get('desde')
        hasta = request.POST.get('hasta')

        if not desde or not hasta:
            messages.error(request, 'Tenés que completar ambas fechas.')
            return render(request, 'turnos/eliminar_rango.html')

        try:
            desde = datetime.date.fromisoformat(desde)
            hasta = datetime.date.fromisoformat(hasta)
        except ValueError:
            messages.error(request, 'Las fechas no son válidas.')
            return render(request, 'turnos/eliminar_rango.html')

        if desde > hasta:
            messages.error(request, 'La fecha de inicio no puede ser mayor a la de fin.')
            return render(request, 'turnos/eliminar_rango.html')

        cantidad = Turno.objects.filter(fecha__gte=desde, fecha__lte=hasta).count()
        Turno.objects.filter(fecha__gte=desde, fecha__lte=hasta).delete()

        messages.success(request, f'Se eliminaron {cantidad} turno(s) entre el {desde} y el {hasta}.')
        return redirect('lista_turnos')