from django.urls import path
from .views import StockView, HistorialView, EliminarHistorialRangoView

urlpatterns = [
    path('', StockView.as_view(), name='stock'),
    path('historial/', HistorialView.as_view(), name='historial'),
    path('historial/eliminar-rango/', EliminarHistorialRangoView.as_view(), name='eliminar_historial_rango'),
]