from django.contrib import admin
from .models import Cuenta, Transaccion

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'saldo')
    search_fields = ('usuario__username',)

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('cuenta', 'tipo', 'monto', 'fecha', 'nota')
    list_filter = ('tipo', 'fecha')
    search_fields = ('cuenta__usuario__username', 'nota')
    date_hierarchy = 'fecha'