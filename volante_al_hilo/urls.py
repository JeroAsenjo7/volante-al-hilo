from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('turnos.urls')),
    path('stock/', include('stock.urls')),
    path('gastos/', include('gastos.urls')),
]




