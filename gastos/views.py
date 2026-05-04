from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Sum
from django.contrib import messages
from turnos.models import Turno
from .models import Gasto
from .forms import GastoForm
import datetime

from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import datetime

class GastosView(View):
    def get(self, request):
        hoy = datetime.date.today()
        fecha_str = request.GET.get('fecha')
        
        try:
            fecha_filtro = datetime.date.fromisoformat(fecha_str) if fecha_str else hoy
        except ValueError:
            fecha_filtro = hoy

        form = GastoForm()

        recaudacion = Turno.objects.filter(
            fecha=fecha_filtro, atendido=True
        ).aggregate(total=Sum('precio'))['total'] or 0

        gastos = Gasto.objects.filter(fecha=fecha_filtro)
        total_gastos = gastos.aggregate(total=Sum('monto'))['total'] or 0
        neto = recaudacion - total_gastos

        return render(request, 'gastos/gastos.html', {
            'form': form,
            'recaudacion_hoy': recaudacion,
            'gastos_hoy': gastos,
            'total_gastos': total_gastos,
            'neto': neto,
            'hoy': hoy,
            'fecha_filtro': fecha_filtro,
        })

    def post(self, request):
        hoy = datetime.date.today()
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.fecha = hoy
            gasto.save()
            messages.success(request, 'Gasto registrado.')
        else:
            messages.error(request, 'Completá todos los campos correctamente.')
        return redirect('gastos')


class EliminarGastoView(View):
    def post(self, request, pk):
        gasto = get_object_or_404(Gasto, pk=pk)
        gasto.delete()
        messages.success(request, 'Gasto eliminado.')
        return redirect('gastos')

class ExportarGastosExcelView(View):
    def get(self, request):
        hoy = datetime.date.today()
        inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + datetime.timedelta(days=5)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Gastos Semana"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="5E0C0E")
        subheader_fill = PatternFill("solid", fgColor="F3F3F3")
        center = Alignment(horizontal="center")

        # Título
        ws.merge_cells("A1:E1")
        ws["A1"] = f"Resumen semanal: {inicio_semana.strftime('%d/%m/%Y')} — {fin_semana.strftime('%d/%m/%Y')}"
        ws["A1"].font = Font(bold=True, color="FFFFFF", size=12)
        ws["A1"].fill = header_fill
        ws["A1"].alignment = center

        # Encabezados
        headers = ["Fecha", "Descripción", "Monto gasto", "Recaudado del día", "Neto del día"]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col, value=h)
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="F5E6E6")
            cell.alignment = center

        # Datos por día
        row = 3
        total_semana_recaudado = 0
        total_semana_gastos = 0

        fecha_actual = inicio_semana
        while fecha_actual <= fin_semana:
            gastos_dia = Gasto.objects.filter(fecha=fecha_actual)
            recaudado_dia = Turno.objects.filter(
                fecha=fecha_actual, atendido=True
            ).aggregate(total=Sum('precio'))['total'] or 0
            total_gastos_dia = gastos_dia.aggregate(total=Sum('monto'))['total'] or 0
            neto_dia = recaudado_dia - total_gastos_dia

            total_semana_recaudado += recaudado_dia
            total_semana_gastos += total_gastos_dia

            if gastos_dia.exists():
                first = True
                for gasto in gastos_dia:
                    ws.cell(row=row, column=1, value=fecha_actual.strftime('%d/%m/%Y') if first else "")
                    ws.cell(row=row, column=2, value=gasto.descripcion)
                    ws.cell(row=row, column=3, value=float(gasto.monto))
                    ws.cell(row=row, column=4, value=float(recaudado_dia) if first else "")
                    ws.cell(row=row, column=5, value=float(neto_dia) if first else "")
                    row += 1
                    first = False
            else:
                ws.cell(row=row, column=1, value=fecha_actual.strftime('%d/%m/%Y'))
                ws.cell(row=row, column=2, value="Sin gastos")
                ws.cell(row=row, column=3, value=0)
                ws.cell(row=row, column=4, value=float(recaudado_dia))
                ws.cell(row=row, column=5, value=float(neto_dia))
                row += 1

            fecha_actual += datetime.timedelta(days=1)

        # Totales semana
        ws.cell(row=row, column=1, value="TOTAL SEMANA").font = Font(bold=True)
        ws.cell(row=row, column=3, value=float(total_semana_gastos)).font = Font(bold=True)
        ws.cell(row=row, column=4, value=float(total_semana_recaudado)).font = Font(bold=True)
        ws.cell(row=row, column=5, value=float(total_semana_recaudado - total_semana_gastos)).font = Font(bold=True)
        for col in range(1, 6):
            ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor="F5E6E6")

        # Ancho de columnas
        ws.column_dimensions['A'].width = 16
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 16
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 16

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="gastos_semana_{hoy}.xlsx"'
        wb.save(response)
        return response