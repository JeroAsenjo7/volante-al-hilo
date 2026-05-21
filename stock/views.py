from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import Stock
from turnos.models import Turno
import datetime
from django.db.models import Sum, Count
from collections import defaultdict
from .models import HistorialColocacion

# Tabla de pagos: pago_a → {agendado_por → monto}
PAGOS = {
    'Cayla': {'Cayla': 6000, 'Bauza': 6000, 'Tomi': 6000},
    'Tomi':  {'Cayla': 5000, 'Bauza': 5000, 'Tomi': 10000},
    'Bauza': {'Cayla': 29000, 'Tomi': 15000, 'Bauza': 35000},
}

def calcular_colocaciones(turnos_qs):
    resultados = {
        'Cayla': {'nombre': 'Cayla', 'turnos': 0, 'total': 0},
        'Tomi':  {'nombre': 'Tomi',  'turnos': 0, 'total': 0},
        'Bauza': {'nombre': 'Bauza', 'turnos': 0, 'total': 0},
    }

    for turno in turnos_qs.values('cliente_de'):
        agendado_por = turno['cliente_de']
        if not agendado_por:
            continue

        if agendado_por in resultados:
            resultados[agendado_por]['turnos'] += 1

        # Cayla: solo cobra si el turno es de Cayla
        if agendado_por == 'Cayla':
            resultados['Cayla']['total'] += 6000

        # Tomi: cobra 10000 si es de Tomi, 5000 si es de cualquier otro
        if agendado_por == 'Tomi':
            resultados['Tomi']['total'] += 10000
        else:
            resultados['Tomi']['total'] += 5000

        # Bauza: cobra según quién agendó
        pagos_bauza = {'Cayla': 29000, 'Tomi': 15000, 'Bauza': 35000}
        resultados['Bauza']['total'] += pagos_bauza.get(agendado_por, 0)

    lista = list(resultados.values())
    total = sum(c['total'] for c in lista)
    return lista, total


class StockView(View):
    def get(self, request):
        # --- STOCK ---
        rojo, _ = Stock.objects.get_or_create(tipo='rojo', defaults={'cantidad': 0})
        negro, _ = Stock.objects.get_or_create(tipo='negro', defaults={'cantidad': 0})
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

        # --- CLIENTES DÍA ---
        turnos_hoy_atendidos = Turno.objects.filter(fecha=hoy, atendido=True)
        clientes_hoy, total_clientes_hoy = calcular_colocaciones(turnos_hoy_atendidos)

        # --- CLIENTES SEMANA ---
        turnos_semana_atendidos = Turno.objects.filter(fecha__gte=inicio_semana, fecha__lte=fin_semana, atendido=True)
        clientes_semana, total_clientes_semana = calcular_colocaciones(turnos_semana_atendidos)

        # --- CLIENTES MES ---
        turnos_mes_atendidos = Turno.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month, atendido=True)
        clientes_mes, total_clientes_mes = calcular_colocaciones(turnos_mes_atendidos)

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

            # Clientes
            'clientes_hoy': clientes_hoy,
            'total_clientes_hoy': total_clientes_hoy,
            'clientes_semana': clientes_semana,
            'total_clientes_semana': total_clientes_semana,
            'clientes_mes': clientes_mes,
            'total_clientes_mes': total_clientes_mes,
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