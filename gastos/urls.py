from django.urls import path
from .views import GastosView, EliminarGastoView, ExportarGastosExcelView

urlpatterns = [
    path('', GastosView.as_view(), name='gastos'),
    path('eliminar/<int:pk>/', EliminarGastoView.as_view(), name='eliminar_gasto'),
    path('exportar/', ExportarGastosExcelView.as_view(), name='exportar_gastos'),
]