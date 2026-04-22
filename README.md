# Volante al Hilo 🧵

Sistema de gestión de turnos y stock para taller de cubre volantes.

## ¿Qué es?

Aplicación web desarrollada con Django pensada para uso móvil. Permite gestionar la agenda de turnos del taller, controlar el stock de hilo y llevar un historial de trabajos realizados.

## Funcionalidades

### Agenda de turnos
- Creación, edición y eliminación de turnos
- Turnos cada 15 minutos en el rango de 9:00 a 19:30
- Sin turnos los domingos
- Horarios ocupados se ocultan automáticamente al agendar
- Agrupación por semanas del mes
- Marcar turno como atendido directamente desde la lista
- Eliminación de turnos por rango de fechas
- Búsqueda por fecha
- Total recaudado por día y por semana

### Stock
- Control de stock de hilo rojo y negro
- Ingreso y descuento manual de stock
- Descuento automático al marcar un turno como atendido
- Devolución automática al desmarcar
- Resumen del día, semana y mes: turnos, atendidos y recaudación

### Historial
- Registro permanente de cada cubre volante colocado
- Guarda fecha, hora, color de hilo y cliente
- No se borra al eliminar turnos de la agenda
- Agrupado por mes
- Eliminación por rango de fechas

## Tecnologías

- Python 3.12
- Django 6.x
- PostgreSQL
- HTML / CSS / JavaScript vanilla
- Whitenoise para archivos estáticos
- Gunicorn como servidor de producción

## Instalación local

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/volante-al-hilo.git
cd volante-al-hilo/volante_al_hilo

# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Crear archivo .env con los datos de tu base de datos (ver .env.example)

# Correr migraciones
python manage.py migrate

# Crear registros iniciales de stock
python manage.py shell
>>> from stock.models import Stock
>>> Stock.objects.create(tipo='rojo', cantidad=0)
>>> Stock.objects.create(tipo='negro', cantidad=0)
>>> exit()

# Iniciar servidor
python manage.py runserver
```

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:
