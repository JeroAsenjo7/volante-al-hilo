from django.urls import path
from .views import (
    TurnoListView,
    TurnoCreateView,
    TurnoUpdateView,
    TurnoDeleteView,
    TurnoToggleAtendidoView,
    EliminarRangoView
)

urlpatterns = [
    path('', TurnoListView.as_view(), name='lista_turnos'),
    path('crear/', TurnoCreateView.as_view(), name='crear_turno'),
    path('editar/<int:pk>/', TurnoUpdateView.as_view(), name='editar_turno'),
    path('eliminar/<int:pk>/', TurnoDeleteView.as_view(), name='eliminar_turno'),
    path('toggle/<int:pk>/', TurnoToggleAtendidoView.as_view(), name='toggle_atendido'),
    path('eliminar-rango/', EliminarRangoView.as_view(), name='eliminar_rango'),
]