from django.urls import path
from . import views

urlpatterns = [

    path('', views.pagina_inicio, name='inicio'),
    path('login/', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),
    path('registro/', views.vista_registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('admin-panel/', views.panel_admin, name='panel_admin'),
    path('admin-panel/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('admin-panel/usuarios/<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('admin-panel/usuarios/<int:usuario_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('admin-panel/usuarios/<int:usuario_id>/toggle/', views.toggle_usuario, name='toggle_usuario'),

    path('psicologo/', views.dashboard_psicologo, name='dashboard_psicologo'),
    path('psicologo/horarios/semanal/guardar/', views.guardar_horario_semanal, name='guardar_horario_semanal'),
    path('psicologo/horarios/<str:fecha_str>/', views.horarios_dia, name='horarios_dia'),
    path('psicologo/horarios/<str:fecha_str>/guardar/', views.guardar_horario, name='guardar_horario'),
    path('psicologo/citas/<int:cita_id>/actualizar/', views.actualizar_cita, name='actualizar_cita'),
    path('psicologo/pacientes/', views.lista_pacientes_psicologo, name='lista_pacientes_psicologo'),
    path('psicologo/pacientes/<int:paciente_id>/', views.seguimiento_paciente, name='seguimiento_paciente'),

    path('paciente/', views.dashboard_paciente, name='dashboard_paciente'),
    path('paciente/disponibilidad/<int:psicologo_id>/<int:anio>/<int:mes>/', views.disponibilidad_psicologo, name='disponibilidad_psicologo'),
    path('paciente/reservar/', views.reservar_cita, name='reservar_cita'),
    path('paciente/citas/<int:cita_id>/cancelar/', views.cancelar_cita_paciente, name='cancelar_cita_paciente'),
]
