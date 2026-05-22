from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Cita, HorarioDisponible, SeguimientoClinico


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display  = ('username', 'nombre', 'apellidos', 'correo', 'celular', 'rol', 'habilitado', 'fecha_registro')
    list_filter   = ('rol', 'habilitado')
    search_fields = ('username', 'nombre', 'apellidos', 'correo')

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display  = ('paciente', 'psicologo', 'fecha', 'hora_inicio', 'hora_fin', 'estado', 'motivo')
    list_filter   = ('estado', 'fecha')
    search_fields = ('paciente__nombre', 'psicologo__nombre')

@admin.register(HorarioDisponible)
class HorarioAdmin(admin.ModelAdmin):
    list_display  = ('psicologo', 'fecha', 'hora_inicio', 'hora_fin')
    list_filter   = ('fecha',)
    search_fields = ('psicologo__nombre',)

@admin.register(SeguimientoClinico)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display  = ('psicologo', 'paciente', 'diagnostico_preliminar', 'proxima_accion', 'fecha_actualizacion')
    search_fields = ('paciente__nombre', 'psicologo__nombre')
