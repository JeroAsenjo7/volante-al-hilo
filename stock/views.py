from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import Stock
from turnos.models import Turno
import datetime
from django.db.models import Sum, Count
from collections import defaultdict
from .models import HistorialColocacion

class StockView(View):
    def get(self, request):
    # --- STOCK ---
        rojo = Stock.objects.get(tipo='rojo')
        negro = Stock.objects.get(tipo='negro')
        total_stock = rojo.cantidad + negro.cantidad

    # --- FECHAS ---
        hoy = datetime.date.today()

    # Semana (lunes a sábado)
        inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + datetime.timedelta(days=5)

    # --- DASHBOARD DÍA ---
        turnos_hoy = Turno.objects.filter(fecha=hoy)
        total_turnos_hoy = turnos_hoy.count()
        atendidos_hoy = turnos_hoy.filter(atendido=True).count()
        recaudacion_hoy = turnos_hoy.filter(atendido=True).aggregate(
            total=Sum('precio')
        )['total'] or 0

    # --- DASHBOARD SEMANA ---
        turnos_semana = Turno.objects.filter(
            fecha__gte=inicio_semana,
            fecha__lte=fin_semana
        )
        total_turnos_semana = turnos_semana.count()
        atendidos_semana = turnos_semana.filter(atendido=True).count()
        recaudacion_semana = turnos_semana.filter(atendido=True).aggregate(
            total=Sum('precio')
        )['total'] or 0

    # --- DASHBOARD MES ---
        turnos_mes = Turno.objects.filter(
            fecha__year=hoy.year,
            fecha__month=hoy.month
        )
        total_turnos_mes = turnos_mes.count()
        atendidos_mes = turnos_mes.filter(atendido=True).count()
        recaudacion_mes = turnos_mes.filter(atendido=True).aggregate(
            total=Sum('precio')
        )['total'] or 0

        return render(request, 'stock/stock.html', {
            'rojo': rojo,
            'negro': negro,
            'total_stock': total_stock,
            'hoy': hoy,

            # Día
            'total_turnos_hoy': total_turnos_hoy,
            'atendidos_hoy': atendidos_hoy,
            'recaudacion_hoy': recaudacion_hoy,

            # Semana
            'total_turnos_semana': total_turnos_semana,
            'atendidos_semana': atendidos_semana,
            'recaudacion_semana': recaudacion_semana,

            # Mes
            'total_turnos_mes': total_turnos_mes,
            'atendidos_mes': atendidos_mes,
            'recaudacion_mes': recaudacion_mes,
        })

    def post(self, request):
        tipo = request.POST.get('tipo')
        accion = request.POST.get('accion')
        try:
            cantidad = int(request.POST.get('cantidad', 0))
        except ValueError:
            messages.error(request, 'Ingresá un número válido.')
            return redirect('stock')

        if cantidad <= 0:
            messages.error(request, 'La cantidad tiene que ser mayor a 0.')
            return redirect('stock')

        try:
            stock = Stock.objects.get(tipo=tipo)
        except Stock.DoesNotExist:
            messages.error(request, 'Tipo de hilo no válido.')
            return redirect('stock')

        if accion == 'ingresar':
            stock.cantidad += cantidad
            stock.save()
            messages.success(request, f'Se ingresaron {cantidad} unidades de hilo {tipo}.')
        elif accion == 'restar':
            if cantidad > stock.cantidad:
                messages.error(request, f'No hay suficiente stock de hilo {tipo}.')
            else:
                stock.cantidad -= cantidad
                stock.save()
                messages.success(request, f'Se restaron {cantidad} unidades de hilo {tipo}.')

        return redirect('stock')
    
class HistorialView(View):
    def get(self, request):
        from .models import HistorialColocacion

        meses_es = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre',
        }

        registros = HistorialColocacion.objects.all()

        por_mes = {}
        for r in registros:
            clave = (r.fecha.year, r.fecha.month)
            if clave not in por_mes:
                por_mes[clave] = {
                    'titulo': f"{meses_es[r.fecha.month]} {r.fecha.year}",
                    'registros': []
                }
            por_mes[clave]['registros'].append(r)

        por_mes_ordenado = dict(sorted(por_mes.items(), reverse=True))

        return render(request, 'stock/historial.html', {
            'por_mes': por_mes_ordenado,
        })
    
class EliminarHistorialRangoView(View):
    def get(self, request):
        return render(request, 'stock/eliminar_historial_rango.html')

    def post(self, request):
        desde = request.POST.get('desde')
        hasta = request.POST.get('hasta')

        if not desde or not hasta:
            messages.error(request, 'Tenés que completar ambas fechas.')
            return render(request, 'stock/eliminar_historial_rango.html')

        try:
            desde = datetime.date.fromisoformat(desde)
            hasta = datetime.date.fromisoformat(hasta)
        except ValueError:
            messages.error(request, 'Las fechas no son válidas.')
            return render(request, 'stock/eliminar_historial_rango.html')

        if desde > hasta:
            messages.error(request, 'La fecha de inicio no puede ser mayor a la de fin.')
            return render(request, 'stock/eliminar_historial_rango.html')

        cantidad = HistorialColocacion.objects.filter(fecha__gte=desde, fecha__lte=hasta).count()
        HistorialColocacion.objects.filter(fecha__gte=desde, fecha__lte=hasta).delete()

        messages.success(request, f'Se eliminaron {cantidad} registro(s) entre el {desde} y el {hasta}.')
        return redirect('historial')