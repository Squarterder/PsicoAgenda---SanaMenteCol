from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('psicologo', 'Psicologo'),
        ('paciente', 'Paciente'),
    ]

    nombre = models.CharField(max_length=80, verbose_name='Nombre')
    apellidos = models.CharField(max_length=80, verbose_name='Apellidos')
    correo = models.EmailField(unique=True, verbose_name='Correo electronico')
    celular = models.CharField(max_length=20, blank=True, verbose_name='Celular')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, verbose_name='Rol')
    habilitado = models.BooleanField(default=True, verbose_name='Habilitado')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.nombre} {self.apellidos} ({self.get_rol_display()})'

    def nombre_completo(self):
        return f'{self.nombre} {self.apellidos}'


class HorarioDisponible(models.Model):
    psicologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='horarios',
        limit_choices_to={'rol': 'psicologo'},
    )
    fecha = models.DateField(verbose_name='Fecha')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')

    class Meta:
        verbose_name = 'Horario disponible'
        verbose_name_plural = 'Horarios disponibles'
        unique_together = ['psicologo', 'fecha', 'hora_inicio']
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f'{self.psicologo.nombre_completo()} - {self.fecha} {self.hora_inicio}-{self.hora_fin}'

    def hora_inicio_str(self):
        return self.hora_inicio.strftime('%H:%M')

    def hora_fin_str(self):
        return self.hora_fin.strftime('%H:%M')


class Cita(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    psicologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='citas_psicologo',
        limit_choices_to={'rol': 'psicologo'},
    )
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='citas_paciente',
        limit_choices_to={'rol': 'paciente'},
    )
    fecha = models.DateField(verbose_name='Fecha')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado'
    )
    motivo = models.TextField(blank=True, verbose_name='Motivo de consulta')
    motivo_cancelacion = models.TextField(blank=True, verbose_name='Motivo de cancelacion')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        unique_together = ['psicologo', 'fecha', 'hora_inicio']
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return (
            f'Cita {self.fecha} {self.hora_inicio} - '
            f'{self.paciente.nombre_completo()} con {self.psicologo.nombre_completo()}'
        )

    def hora_inicio_str(self):
        return self.hora_inicio.strftime('%H:%M')

    def hora_fin_str(self):
        return self.hora_fin.strftime('%H:%M')


class SeguimientoClinico(models.Model):
    psicologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='seguimientos_realizados',
        limit_choices_to={'rol': 'psicologo'},
    )
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='seguimientos_recibidos',
        limit_choices_to={'rol': 'paciente'},
    )
    notas = models.TextField(verbose_name='Notas clinicas', blank=True)
    diagnostico_preliminar = models.CharField(
        max_length=255, blank=True, verbose_name='Diagnostico preliminar'
    )
    proxima_accion = models.CharField(
        max_length=255, blank=True, verbose_name='Proxima accion recomendada'
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Seguimiento clinico'
        verbose_name_plural = 'Seguimientos clinicos'
        unique_together = ['psicologo', 'paciente']
        ordering = ['-fecha_actualizacion']

    def __str__(self):
        return f'Seguimiento: {self.psicologo.nombre_completo()} -> {self.paciente.nombre_completo()}'
