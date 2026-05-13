from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cita, HorarioDisponible, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'nombre', 'apellidos', 'correo', 'rol', 'habilitado')
    list_filter = ('rol', 'habilitado')
    search_fields = ('nombre', 'apellidos', 'correo', 'username')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {'fields': ('nombre', 'apellidos', 'correo', 'celular', 'rol', 'habilitado')}),
    )


@admin.register(HorarioDisponible)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    list_display = ('psicologo', 'fecha', 'hora_inicio', 'hora_fin')
    list_filter = ('psicologo', 'fecha')


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('psicologo', 'paciente', 'fecha', 'hora_inicio', 'estado')
    list_filter = ('estado', 'psicologo', 'fecha')
    search_fields = ('paciente__nombre', 'paciente__apellidos')
