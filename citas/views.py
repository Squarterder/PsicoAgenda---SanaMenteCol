import json
import calendar
from datetime import date, time, timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods

from .forms import (
    FormularioCrearUsuario,
    FormularioEditarUsuario,
    FormularioLogin,
    FormularioRegistro,
    FormularioReservarCita,
    FormularioSeguimiento,
)
from .models import Cita, HorarioDisponible, SeguimientoClinico, Usuario


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def requiere_rol(*roles):
    def decorador(vista):
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.rol not in roles:
                messages.error(request, 'No tienes permiso para acceder a esa pagina.')
                return redirect('dashboard')
            return vista(request, *args, **kwargs)
        return wrapper
    return decorador


MESES_ES = {
    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
    'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
    'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
    'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre',
}


def meses_calendario(n_meses=2):
    hoy = date.today()
    resultado = []
    anio, mes = hoy.year, hoy.month
    for _ in range(n_meses):
        resultado.append((anio, mes))
        mes += 1
        if mes > 12:
            mes = 1
            anio += 1
    return resultado


def dias_del_mes(anio, mes):
    hoy = date.today()
    _, total_dias = calendar.monthrange(anio, mes)
    primer_dia = date(anio, mes, 1).weekday()
    dias = []
    for _ in range(primer_dia):
        dias.append(None)
    for d in range(1, total_dias + 1):
        fecha = date(anio, mes, d)
        dias.append({
            'fecha': fecha,
            'pasado': fecha < hoy,
            'hoy': fecha == hoy,
        })
    return dias


def construir_calendarios():
    calendarios = []
    for anio, mes in meses_calendario(2):
        nombre_mes = MESES_ES.get(calendar.month_name[mes], calendar.month_name[mes])
        calendarios.append({
            'anio': anio,
            'mes': mes,
            'nombre_mes': nombre_mes,
            'dias': dias_del_mes(anio, mes),
        })
    return calendarios


# ---------------------------------------------------------------------------
# Correos electronicos
# ---------------------------------------------------------------------------

def enviar_correo_nueva_cita(cita):
    """Avisa al psicologo que un paciente reservo una cita."""
    asunto = f'Nueva solicitud de cita — {cita.paciente.nombre_completo()}'
    mensaje = (
        f'Hola {cita.psicologo.nombre},\n\n'
        f'El paciente {cita.paciente.nombre_completo()} ha solicitado una cita contigo.\n\n'
        f'Detalles de la cita:\n'
        f'  Fecha:   {cita.fecha.strftime("%d/%m/%Y")}\n'
        f'  Horario: {cita.hora_inicio_str()} - {cita.hora_fin_str()}\n'
        f'  Estado:  Pendiente de tu confirmacion\n'
    )
    if cita.motivo:
        mensaje += f'  Motivo:  {cita.motivo}\n'
    mensaje += (
        f'\nIngresa al sistema para confirmar o cancelar la cita:\n'
        f'http://127.0.0.1:8000/psicologo/\n\n'
        f'— PsicoAgenda / SanaMenteCol'
    )
    try:
        send_mail(
            asunto, mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [cita.psicologo.correo],
            fail_silently=True,
        )
    except Exception:
        pass


def enviar_correo_cita_confirmada(cita):
    """Avisa al paciente que su cita fue confirmada."""
    asunto = 'Tu cita ha sido confirmada — PsicoAgenda'
    mensaje = (
        f'Hola {cita.paciente.nombre},\n\n'
        f'Tu cita con la psicologa {cita.psicologo.nombre_completo()} ha sido CONFIRMADA.\n\n'
        f'Detalles:\n'
        f'  Fecha:   {cita.fecha.strftime("%d/%m/%Y")}\n'
        f'  Horario: {cita.hora_inicio_str()} - {cita.hora_fin_str()}\n\n'
        f'Recuerda llegar unos minutos antes de tu cita. Si necesitas cancelar, '
        f'hazlo con anticipacion desde el sistema:\n'
        f'http://127.0.0.1:8000/paciente/\n\n'
        f'— PsicoAgenda / SanaMenteCol'
    )
    try:
        send_mail(
            asunto, mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [cita.paciente.correo],
            fail_silently=True,
        )
    except Exception:
        pass


def enviar_correo_cita_cancelada(cita, motivo_cancelacion):
    """Avisa al paciente que su cita fue cancelada e indica el motivo."""
    asunto = 'Tu cita ha sido cancelada — PsicoAgenda'
    mensaje = (
        f'Hola {cita.paciente.nombre},\n\n'
        f'Lamentamos informarte que tu cita con {cita.psicologo.nombre_completo()} '
        f'programada para el {cita.fecha.strftime("%d/%m/%Y")} a las '
        f'{cita.hora_inicio_str()} ha sido CANCELADA.\n\n'
        f'Motivo indicado por el psicologo:\n'
        f'  "{motivo_cancelacion}"\n\n'
        f'Puedes ingresar al sistema para reservar una nueva cita en otro '
        f'horario disponible:\n'
        f'http://127.0.0.1:8000/paciente/\n\n'
        f'Disculpa los inconvenientes.\n\n'
        f'— PsicoAgenda / SanaMenteCol'
    )
    try:
        send_mail(
            asunto, mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [cita.paciente.correo],
            fail_silently=True,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Pagina de inicio
# ---------------------------------------------------------------------------

def pagina_inicio(request):
    return render(request, 'index.html')


# ---------------------------------------------------------------------------
# Autenticacion
# ---------------------------------------------------------------------------

def vista_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    formulario = FormularioLogin()
    if request.method == 'POST':
        formulario = FormularioLogin(request.POST)
        if formulario.is_valid():
            usuario = formulario.cleaned_data['usuario_obj']
            login(request, usuario)
            return redirect('dashboard')
    return render(request, 'login.html', {'formulario': formulario})


def vista_logout(request):
    logout(request)
    return redirect('inicio')


def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    formulario = FormularioRegistro()
    if request.method == 'POST':
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            messages.success(
                request,
                f'Cuenta creada exitosamente. Tu usuario es: {usuario.username}. Ya puedes iniciar sesion.'
            )
            return redirect('login')
    return render(request, 'registro.html', {'formulario': formulario})


@login_required
def dashboard(request):
    rol = request.user.rol
    if rol == 'admin':
        return redirect('panel_admin')
    elif rol == 'psicologo':
        return redirect('dashboard_psicologo')
    else:
        return redirect('dashboard_paciente')


# ---------------------------------------------------------------------------
# Panel de Administrador
# ---------------------------------------------------------------------------

@requiere_rol('admin')
def panel_admin(request):
    filtro_rol = request.GET.get('rol', '')
    filtro_busqueda = request.GET.get('q', '')
    usuarios = Usuario.objects.exclude(pk=request.user.pk)
    if filtro_rol:
        usuarios = usuarios.filter(rol=filtro_rol)
    if filtro_busqueda:
        usuarios = (
            usuarios.filter(nombre__icontains=filtro_busqueda)
            | usuarios.filter(apellidos__icontains=filtro_busqueda)
            | usuarios.filter(correo__icontains=filtro_busqueda)
        )
    usuarios = usuarios.order_by('rol', 'apellidos')
    contexto = {
        'usuarios': usuarios,
        'filtro_rol': filtro_rol,
        'filtro_busqueda': filtro_busqueda,
        'total_admin': Usuario.objects.filter(rol='admin').count(),
        'total_psicologo': Usuario.objects.filter(rol='psicologo').count(),
        'total_paciente': Usuario.objects.filter(rol='paciente').count(),
        'migas': [
            {'label': 'Inicio', 'url': '/'},
            {'label': 'Panel Admin', 'url': ''},
        ],
    }
    return render(request, 'dashboard_admin.html', contexto)


@requiere_rol('admin')
def crear_usuario(request):
    formulario = FormularioCrearUsuario()
    if request.method == 'POST':
        formulario = FormularioCrearUsuario(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            messages.success(
                request,
                f'Usuario {usuario.nombre_completo()} creado. Nombre de usuario: {usuario.username}'
            )
            return redirect('panel_admin')
    return render(request, 'admin_crear_usuario.html', {
        'formulario': formulario,
        'accion': 'Crear',
        'migas': [
            {'label': 'Inicio', 'url': '/'},
            {'label': 'Panel Admin', 'url': '/admin-panel/'},
            {'label': 'Crear Usuario', 'url': ''},
        ],
    })


@requiere_rol('admin')
def editar_usuario(request, usuario_id):
    usuario_obj = get_object_or_404(Usuario, pk=usuario_id)
    formulario = FormularioEditarUsuario(instance=usuario_obj)
    if request.method == 'POST':
        formulario = FormularioEditarUsuario(request.POST, instance=usuario_obj)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('panel_admin')
    return render(request, 'admin_crear_usuario.html', {
        'formulario': formulario,
        'accion': 'Editar',
        'usuario_editado': usuario_obj,
        'migas': [
            {'label': 'Inicio', 'url': '/'},
            {'label': 'Panel Admin', 'url': '/admin-panel/'},
            {'label': f'Editar: {usuario_obj.nombre}', 'url': ''},
        ],
    })


@requiere_rol('admin')
@require_POST
def eliminar_usuario(request, usuario_id):
    usuario_obj = get_object_or_404(Usuario, pk=usuario_id)
    if usuario_obj.pk == request.user.pk:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
        return redirect('panel_admin')
    nombre = usuario_obj.nombre_completo()
    usuario_obj.delete()
    messages.success(request, f'Usuario {nombre} eliminado.')
    return redirect('panel_admin')


@requiere_rol('admin')
@require_POST
def toggle_usuario(request, usuario_id):
    usuario_obj = get_object_or_404(Usuario, pk=usuario_id)
    if usuario_obj.pk == request.user.pk:
        messages.error(request, 'No puedes deshabilitarte a ti mismo.')
        return redirect('panel_admin')
    usuario_obj.habilitado = not usuario_obj.habilitado
    usuario_obj.save()
    estado = 'habilitado' if usuario_obj.habilitado else 'deshabilitado'
    messages.success(request, f'Usuario {usuario_obj.nombre_completo()} {estado}.')
    return redirect('panel_admin')


# ---------------------------------------------------------------------------
# Dashboard Psicologo
# ---------------------------------------------------------------------------

@requiere_rol('psicologo')
def dashboard_psicologo(request):
    hoy = date.today()
    citas_pendientes = Cita.objects.filter(
        psicologo=request.user,
        estado='pendiente',
        fecha__gte=hoy,
    ).select_related('paciente').order_by('fecha', 'hora_inicio')

    citas_confirmadas = Cita.objects.filter(
        psicologo=request.user,
        estado='confirmada',
        fecha__gte=hoy,
    ).select_related('paciente').order_by('fecha', 'hora_inicio')

    total_pacientes = (
        Cita.objects.filter(psicologo=request.user)
        .values('paciente').distinct().count()
    )

    contexto = {
        'calendarios': construir_calendarios(),
        'citas_pendientes': citas_pendientes,
        'citas_confirmadas': citas_confirmadas,
        'dias_semana': ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'],
        'total_pacientes': total_pacientes,
    }
    return render(request, 'dashboard_psicologo.html', contexto)


@login_required
@require_http_methods(['GET'])
def horarios_dia(request, fecha_str):
    if request.user.rol != 'psicologo':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        return JsonResponse({'error': 'Fecha invalida'}, status=400)

    horarios = HorarioDisponible.objects.filter(
        psicologo=request.user, fecha=fecha
    ).values('id', 'hora_inicio', 'hora_fin')

    citas_del_dia = Cita.objects.filter(
        psicologo=request.user, fecha=fecha
    ).values('hora_inicio', 'estado')
    horas_ocupadas = {str(c['hora_inicio'])[:5]: c['estado'] for c in citas_del_dia}

    datos = []
    for h in horarios:
        hi = str(h['hora_inicio'])[:5]
        hf = str(h['hora_fin'])[:5]
        datos.append({
            'id': h['id'],
            'hora_inicio': hi,
            'hora_fin': hf,
            'estado_cita': horas_ocupadas.get(hi, None),
        })
    return JsonResponse({'horarios': datos, 'fecha': fecha_str})


@login_required
@require_POST
def guardar_horario(request, fecha_str):
    if request.user.rol != 'psicologo':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        return JsonResponse({'error': 'Fecha invalida'}, status=400)
    if fecha < date.today():
        return JsonResponse({'error': 'No puedes modificar fechas pasadas'}, status=400)
    try:
        datos = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalido'}, status=400)

    accion = datos.get('accion')
    hora_inicio_str = datos.get('hora_inicio')
    hora_fin_str = datos.get('hora_fin')
    if not hora_inicio_str:
        return JsonResponse({'error': 'Hora de inicio requerida'}, status=400)
    try:
        hora_inicio = time.fromisoformat(hora_inicio_str)
        hora_fin = time.fromisoformat(hora_fin_str) if hora_fin_str else None
    except ValueError:
        return JsonResponse({'error': 'Formato de hora invalido'}, status=400)

    if accion == 'agregar':
        if not hora_fin:
            return JsonResponse({'error': 'Hora de fin requerida'}, status=400)
        if hora_fin <= hora_inicio:
            return JsonResponse({'error': 'La hora de fin debe ser mayor que la de inicio'}, status=400)
        horario, creado = HorarioDisponible.objects.get_or_create(
            psicologo=request.user,
            fecha=fecha,
            hora_inicio=hora_inicio,
            defaults={'hora_fin': hora_fin},
        )
        if not creado:
            return JsonResponse({'error': 'Ya existe ese horario'}, status=400)
        return JsonResponse({'ok': True, 'id': horario.id, 'mensaje': 'Horario agregado'})

    elif accion == 'eliminar':
        horario_id = datos.get('horario_id')
        try:
            horario = HorarioDisponible.objects.get(
                pk=horario_id, psicologo=request.user, fecha=fecha
            )
        except HorarioDisponible.DoesNotExist:
            return JsonResponse({'error': 'Horario no encontrado'}, status=404)
        tiene_cita = Cita.objects.filter(
            psicologo=request.user,
            fecha=fecha,
            hora_inicio=hora_inicio,
            estado__in=['pendiente', 'confirmada'],
        ).exists()
        if tiene_cita:
            return JsonResponse(
                {'error': 'No puedes eliminar un horario con una cita activa'}, status=400
            )
        horario.delete()
        return JsonResponse({'ok': True, 'mensaje': 'Horario eliminado'})

    return JsonResponse({'error': 'Accion desconocida'}, status=400)


@login_required
@require_POST
def guardar_horario_semanal(request):
    """Crea horarios para todos los días de una semana del mes indicado."""
    if request.user.rol != 'psicologo':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        datos = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalido'}, status=400)

    hora_inicio_str = datos.get('hora_inicio')
    hora_fin_str    = datos.get('hora_fin')
    dias_semana     = datos.get('dias', [])   # lista de ints 0-6 (lun-dom)
    mes_str         = datos.get('mes')         # "actual" | "siguiente"

    if not hora_inicio_str or not hora_fin_str:
        return JsonResponse({'error': 'Horas requeridas'}, status=400)
    if not dias_semana:
        return JsonResponse({'error': 'Selecciona al menos un dia'}, status=400)

    try:
        hora_inicio = time.fromisoformat(hora_inicio_str)
        hora_fin    = time.fromisoformat(hora_fin_str)
    except ValueError:
        return JsonResponse({'error': 'Formato de hora invalido'}, status=400)

    if hora_fin <= hora_inicio:
        return JsonResponse({'error': 'La hora de fin debe ser mayor que la de inicio'}, status=400)

    hoy = date.today()
    if mes_str == 'siguiente':
        if hoy.month == 12:
            primer_dia = date(hoy.year + 1, 1, 1)
        else:
            primer_dia = date(hoy.year, hoy.month + 1, 1)
    else:
        primer_dia = date(hoy.year, hoy.month, 1)

    ultimo_dia = date(
        primer_dia.year,
        primer_dia.month,
        calendar.monthrange(primer_dia.year, primer_dia.month)[1]
    )

    creados   = 0
    omitidos  = 0
    dia_actual = primer_dia
    while dia_actual <= ultimo_dia:
        # weekday(): 0=lunes … 6=domingo
        if dia_actual >= hoy and dia_actual.weekday() in dias_semana:
            _, fue_creado = HorarioDisponible.objects.get_or_create(
                psicologo   = request.user,
                fecha       = dia_actual,
                hora_inicio = hora_inicio,
                defaults    = {'hora_fin': hora_fin},
            )
            if fue_creado:
                creados += 1
            else:
                omitidos += 1
        dia_actual += timedelta(days=1)

    return JsonResponse({
        'ok': True,
        'creados':  creados,
        'omitidos': omitidos,
        'mensaje':  f'{creados} horarios creados, {omitidos} ya existian.',
    })


@requiere_rol('psicologo')
@require_POST
def actualizar_cita(request, cita_id):
    """El psicologo confirma, cancela o completa una cita.
    Al confirmar: envia correo al paciente.
    Al cancelar: requiere motivo y envia correo al paciente explicando la razon.
    """
    cita = get_object_or_404(Cita, pk=cita_id, psicologo=request.user)
    nuevo_estado = request.POST.get('estado')

    if nuevo_estado not in ('confirmada', 'cancelada', 'completada'):
        messages.error(request, 'Estado no valido.')
        return redirect('dashboard_psicologo')

    if nuevo_estado == 'cancelada':
        motivo_cancelacion = request.POST.get('motivo_cancelacion', '').strip()
        if not motivo_cancelacion:
            messages.error(
                request,
                'Debes indicar un motivo para cancelar la cita. El paciente recibira esa explicacion.'
            )
            return redirect('dashboard_psicologo')
        cita.estado = 'cancelada'
        cita.motivo_cancelacion = motivo_cancelacion
        cita.save()
        enviar_correo_cita_cancelada(cita, motivo_cancelacion)
        messages.success(
            request,
            f'Cita cancelada. Se notifico a {cita.paciente.nombre_completo()} por correo con el motivo.'
        )

    elif nuevo_estado == 'confirmada':
        cita.estado = 'confirmada'
        cita.save()
        enviar_correo_cita_confirmada(cita)
        messages.success(
            request,
            f'Cita confirmada. Se notifico a {cita.paciente.nombre_completo()} por correo.'
        )

    else:
        cita.estado = 'completada'
        cita.save()
        messages.success(request, 'Cita marcada como completada.')

    return redirect('dashboard_psicologo')


# ---------------------------------------------------------------------------
# Seguimiento clinico (Psicologo)
# ---------------------------------------------------------------------------

@requiere_rol('psicologo')
def lista_pacientes_psicologo(request):
    """Lista todos los pacientes que tienen o tuvieron citas con este psicologo."""
    busqueda = request.GET.get('q', '').strip()

    ids_pacientes = (
        Cita.objects.filter(psicologo=request.user)
        .values_list('paciente_id', flat=True)
        .distinct()
    )
    pacientes_qs = Usuario.objects.filter(pk__in=ids_pacientes, rol='paciente')

    if busqueda:
        pacientes_qs = pacientes_qs.filter(
            nombre__icontains=busqueda
        ) | pacientes_qs.filter(
            apellidos__icontains=busqueda
        )

    pacientes_qs = pacientes_qs.order_by('apellidos', 'nombre')

    pacientes_data = []
    for p in pacientes_qs:
        citas_p = Cita.objects.filter(psicologo=request.user, paciente=p)
        try:
            seguimiento = SeguimientoClinico.objects.get(psicologo=request.user, paciente=p)
        except SeguimientoClinico.DoesNotExist:
            seguimiento = None

        ultima = citas_p.order_by('-fecha').first()
        pacientes_data.append({
            'paciente': p,
            'total_citas': citas_p.count(),
            'completadas': citas_p.filter(estado='completada').count(),
            'ultima_cita': ultima,
            'tiene_notas': seguimiento is not None and bool(
                seguimiento.notas or seguimiento.diagnostico_preliminar
            ),
        })

    contexto = {
        'pacientes_data': pacientes_data,
        'busqueda': busqueda,
        'total': len(pacientes_data),
        'migas': [
            {'label': 'Inicio', 'url': '/'},
            {'label': 'Mi Agenda', 'url': '/psicologo/'},
            {'label': 'Mis Pacientes', 'url': ''},
        ],
    }
    return render(request, 'lista_pacientes.html', contexto)


@requiere_rol('psicologo')
def seguimiento_paciente(request, paciente_id):
    """Ficha clinica de un paciente: historial de citas + notas del psicologo."""
    paciente = get_object_or_404(Usuario, pk=paciente_id, rol='paciente')

    tiene_citas = Cita.objects.filter(
        psicologo=request.user, paciente=paciente
    ).exists()
    if not tiene_citas:
        messages.error(request, 'Este paciente no tiene citas contigo.')
        return redirect('lista_pacientes_psicologo')

    seguimiento, _ = SeguimientoClinico.objects.get_or_create(
        psicologo=request.user, paciente=paciente
    )

    formulario = FormularioSeguimiento(instance=seguimiento)
    if request.method == 'POST':
        formulario = FormularioSeguimiento(request.POST, instance=seguimiento)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Ficha clinica guardada correctamente.')
            return redirect('seguimiento_paciente', paciente_id=paciente_id)

    citas = Cita.objects.filter(
        psicologo=request.user, paciente=paciente
    ).order_by('-fecha', '-hora_inicio')

    contexto = {
        'paciente': paciente,
        'formulario': formulario,
        'seguimiento': seguimiento,
        'citas': citas,
        'resumen': {
            'total': citas.count(),
            'completadas': citas.filter(estado='completada').count(),
            'pendientes': citas.filter(estado='pendiente').count(),
            'confirmadas': citas.filter(estado='confirmada').count(),
            'canceladas': citas.filter(estado='cancelada').count(),
        },
        'migas': [
            {'label': 'Inicio', 'url': '/'},
            {'label': 'Mi Agenda', 'url': '/psicologo/'},
            {'label': 'Mis Pacientes', 'url': '/psicologo/pacientes/'},
            {'label': f'{paciente.nombre} {paciente.apellidos}', 'url': ''},
        ],
    }
    return render(request, 'seguimiento_paciente.html', contexto)


# ---------------------------------------------------------------------------
# Dashboard Paciente
# ---------------------------------------------------------------------------

@requiere_rol('paciente')
def dashboard_paciente(request):
    psicologos = Usuario.objects.filter(rol='psicologo', habilitado=True).order_by('apellidos')
    psicologo_sel_id = request.GET.get('psicologo', '')
    psicologo_sel = None

    if psicologo_sel_id:
        try:
            psicologo_sel = Usuario.objects.get(pk=psicologo_sel_id, rol='psicologo', habilitado=True)
        except Usuario.DoesNotExist:
            psicologo_sel = None

    mis_citas = Cita.objects.filter(
        paciente=request.user
    ).select_related('psicologo').order_by('-fecha', '-hora_inicio')

    contexto = {
        'psicologos': psicologos,
        'psicologo_sel': psicologo_sel,
        'psicologo_sel_id': psicologo_sel_id,
        'calendarios': construir_calendarios(),
        'mis_citas': mis_citas,
        'dias_semana': ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'],
    }
    return render(request, 'dashboard_paciente.html', contexto)


@login_required
@require_http_methods(['GET'])
def disponibilidad_psicologo(request, psicologo_id, anio, mes):
    try:
        psicologo = Usuario.objects.get(pk=psicologo_id, rol='psicologo', habilitado=True)
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Psicologo no encontrado'}, status=404)

    hoy = date.today()
    _, total_dias = calendar.monthrange(anio, mes)
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, total_dias)

    horarios = HorarioDisponible.objects.filter(
        psicologo=psicologo,
        fecha__gte=max(fecha_inicio, hoy),
        fecha__lte=fecha_fin,
    ).values('id', 'fecha', 'hora_inicio', 'hora_fin')

    citas_ocupadas = Cita.objects.filter(
        psicologo=psicologo,
        fecha__gte=max(fecha_inicio, hoy),
        fecha__lte=fecha_fin,
        estado__in=['pendiente', 'confirmada'],
    ).values('fecha', 'hora_inicio')

    horas_ocupadas = set()
    for c in citas_ocupadas:
        horas_ocupadas.add((str(c['fecha']), str(c['hora_inicio'])[:5]))

    por_fecha = {}
    for h in horarios:
        fecha_str = str(h['fecha'])
        hi = str(h['hora_inicio'])[:5]
        hf = str(h['hora_fin'])[:5]
        if (fecha_str, hi) not in horas_ocupadas:
            por_fecha.setdefault(fecha_str, []).append({
                'horario_id': h['id'],
                'fecha': fecha_str,
                'hora_inicio': hi,
                'hora_fin': hf,
            })

    return JsonResponse({'disponibilidad': por_fecha})


@login_required
@require_POST
def reservar_cita(request):
    if request.user.rol != 'paciente':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        datos = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalido'}, status=400)

    horario_id = datos.get('horario_id')
    motivo = datos.get('motivo', '')

    try:
        horario = HorarioDisponible.objects.select_related('psicologo').get(pk=horario_id)
    except HorarioDisponible.DoesNotExist:
        return JsonResponse({'error': 'Horario no encontrado'}, status=404)

    if horario.fecha < date.today():
        return JsonResponse({'error': 'No puedes reservar en fechas pasadas'}, status=400)

    ya_ocupado = Cita.objects.filter(
        psicologo=horario.psicologo,
        fecha=horario.fecha,
        hora_inicio=horario.hora_inicio,
        estado__in=['pendiente', 'confirmada'],
    ).exists()
    if ya_ocupado:
        return JsonResponse({'error': 'Ese horario ya no esta disponible'}, status=400)

    conflicto = Cita.objects.filter(
        paciente=request.user,
        fecha=horario.fecha,
        hora_inicio=horario.hora_inicio,
        estado__in=['pendiente', 'confirmada'],
    ).exists()
    if conflicto:
        return JsonResponse({'error': 'Ya tienes una cita en ese horario'}, status=400)

    cita = Cita.objects.create(
        psicologo=horario.psicologo,
        paciente=request.user,
        fecha=horario.fecha,
        hora_inicio=horario.hora_inicio,
        hora_fin=horario.hora_fin,
        estado='pendiente',
        motivo=motivo,
    )

    # Notificar al psicologo por correo electronico
    enviar_correo_nueva_cita(cita)

    return JsonResponse({
        'ok': True,
        'mensaje': (
            'Cita reservada exitosamente. '
            'Se notifico al psicologo por correo. '
            'Estado: Pendiente de confirmacion.'
        ),
        'cita_id': cita.id,
    })


@login_required
@require_POST
def cancelar_cita_paciente(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id, paciente=request.user)
    if cita.estado in ('pendiente', 'confirmada'):
        cita.estado = 'cancelada'
        cita.save()
        messages.success(request, 'Cita cancelada correctamente.')
    else:
        messages.error(request, 'No se puede cancelar esta cita.')
    return redirect('dashboard_paciente')
