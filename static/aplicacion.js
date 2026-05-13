// PsicoAgenda — lógica de interacción general

// token CSRF para fetch() — viene del meta tag inyectado por base.html
const CSRF = document.querySelector('meta[name="csrf-token"]')?.content || '';


// sombra en la navegación al hacer scroll
const navegacion = document.querySelector('.navegacion');
if (navegacion) {
  window.addEventListener('scroll', () => {
    navegacion.classList.toggle('con-sombra', window.scrollY > 20);
  });
}


// animaciones de revelado con IntersectionObserver
const elementosAnimados = document.querySelectorAll('.revelar, .revelar-izquierda, .revelar-derecha');
if (elementosAnimados.length > 0) {
  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach((entrada, indice) => {
      if (entrada.isIntersecting) {
        setTimeout(() => entrada.target.classList.add('visible'), indice * 90);
        observador.unobserve(entrada.target);
      }
    });
  }, { threshold: 0.12 });
  elementosAnimados.forEach(el => observador.observe(el));
}


// toggle contraseña — login
const campoLogin = document.getElementById('id_contrasena');
const botonLogin = document.getElementById('alternar-contrasena');
const iconoLogin = document.getElementById('icono-ojo');
if (campoLogin && botonLogin && iconoLogin) {
  const ojoAbierto = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  const ojoCerrado = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>';
  botonLogin.addEventListener('click', () => {
    const oculta = campoLogin.type === 'password';
    campoLogin.type = oculta ? 'text' : 'password';
    iconoLogin.innerHTML = oculta ? ojoCerrado : ojoAbierto;
  });
}


// toggle contraseña — registro (dos campos: contraseña y confirmar)
function togglePass(campoId, iconoId) {
  const campo = document.getElementById(campoId);
  const icono = document.getElementById(iconoId);
  if (!campo || !icono) return;
  const ojoAbierto = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  const ojoCerrado = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>';
  const oculta = campo.type === 'password';
  campo.type = oculta ? 'text' : 'password';
  icono.innerHTML = oculta ? ojoCerrado : ojoAbierto;
}
document.getElementById('btn-ver-pass')?.addEventListener('click', () => togglePass('id_contrasena', 'ico-pass'));
document.getElementById('btn-ver-confirm')?.addEventListener('click', () => togglePass('id_confirmar', 'ico-confirm'));


// dashboard psicólogo

// modal de horarios
let fechaActual = '';

async function abrirModalHorarios(fecha, fechaDisplay) {
  fechaActual = fecha;
  document.getElementById('modal-horarios-titulo').textContent = 'Horarios — ' + fechaDisplay;
  document.getElementById('modal-horarios').classList.add('abierto');
  ocultarMsgHorarios();
  await cargarHorarios();
}

function cerrarModalHorarios() {
  document.getElementById('modal-horarios').classList.remove('abierto');
  fechaActual = '';
}

async function cargarHorarios() {
  const lista = document.getElementById('lista-horarios');
  lista.innerHTML = '<p style="text-align:center;color:var(--texto-medio);font-size:.85rem;padding:.5rem;">Cargando...</p>';
  try {
    const r = await fetch('/psicologo/horarios/' + fechaActual + '/');
    const d = await r.json();
    renderHorarios(d.horarios || []);
    actualizarPuntoCal(fechaActual, (d.horarios || []).length > 0);
  } catch (e) {
    lista.innerHTML = '<p style="color:var(--vino);font-size:.85rem;padding:.5rem;">Error al cargar.</p>';
  }
}

function renderHorarios(horarios) {
  const lista = document.getElementById('lista-horarios');
  if (!horarios.length) {
    lista.innerHTML = '<p style="text-align:center;color:var(--texto-medio);font-size:.85rem;padding:.5rem;">Sin horarios. Agrega uno abajo.</p>';
    return;
  }
  lista.innerHTML = horarios.map(h => `
    <div class="horario-item" id="hi-${h.id}">
      <span class="hora">${h.hora_inicio} &mdash; ${h.hora_fin}</span>
      ${h.estado_cita
        ? `<span class="estado-cita">Cita: ${h.estado_cita}</span>`
        : `<button class="btn-eliminar-hora" onclick="eliminarHorario(${h.id},'${h.hora_inicio}')" title="Eliminar">
            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
              <path d="M10 11v6"/><path d="M14 11v6"/>
            </svg>
           </button>`
      }
    </div>
  `).join('');
}

async function agregarHorario() {
  const inicio = document.getElementById('inp-inicio').value;
  const fin    = document.getElementById('inp-fin').value;
  if (!inicio || !fin) { mostrarMsgHorarios('Ingresa la hora de inicio y fin.', 'err'); return; }
  if (fin <= inicio)   { mostrarMsgHorarios('La hora de fin debe ser mayor que la de inicio.', 'err'); return; }
  try {
    const r = await fetch('/psicologo/horarios/' + fechaActual + '/guardar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
      body: JSON.stringify({ accion: 'agregar', hora_inicio: inicio + ':00', hora_fin: fin + ':00' }),
    });
    const d = await r.json();
    if (d.ok) { mostrarMsgHorarios('Horario agregado.', 'ok'); await cargarHorarios(); }
    else       mostrarMsgHorarios(d.error || 'Error.', 'err');
  } catch (e) { mostrarMsgHorarios('Error de conexion.', 'err'); }
}

async function eliminarHorario(id, hi) {
  if (!confirm('Eliminar el horario de las ' + hi + '?')) return;
  try {
    const r = await fetch('/psicologo/horarios/' + fechaActual + '/guardar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
      body: JSON.stringify({ accion: 'eliminar', horario_id: id, hora_inicio: hi + ':00', hora_fin: '00:00:00' }),
    });
    const d = await r.json();
    if (d.ok) { mostrarMsgHorarios('Horario eliminado.', 'ok'); await cargarHorarios(); }
    else       mostrarMsgHorarios(d.error || 'Error.', 'err');
  } catch (e) { mostrarMsgHorarios('Error de conexion.', 'err'); }
}

function mostrarMsgHorarios(txt, tipo) {
  const el = document.getElementById('msg-horarios');
  if (!el) return;
  el.textContent = txt;
  el.className = 'msg-modal ' + (tipo === 'ok' ? 'msg-ok' : 'msg-err');
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 3500);
}

function ocultarMsgHorarios() {
  const el = document.getElementById('msg-horarios');
  if (el) el.style.display = 'none';
}

function actualizarPuntoCal(fecha, tiene) {
  const id    = fecha.replace(/-/g, '');
  const punto = document.getElementById('punto-' + id);
  const dia   = document.getElementById('dia-' + id);
  if (punto) punto.style.display = tiene ? 'block' : 'none';
  if (dia)   dia.classList.toggle('disponible', tiene);
}

// marca disponibilidad al cargar el dashboard del psicólogo
async function marcarDisponibilidadInicial() {
  const dias = document.querySelectorAll('.cal-dia.futuro[data-fecha]');
  for (const dia of dias) {
    try {
      const r = await fetch('/psicologo/horarios/' + dia.dataset.fecha + '/');
      const d = await r.json();
      if (d.horarios && d.horarios.length > 0) actualizarPuntoCal(dia.dataset.fecha, true);
    } catch (e) {}
  }
}

// modal cancelar cita (psicólogo)
let citaIdACancelar = null;

function abrirModalCancelar(citaId, nombrePaciente, fecha, hora) {
  citaIdACancelar = citaId;
  document.getElementById('cancel-titulo').textContent = 'Cancelar cita';
  document.getElementById('cancel-info').textContent =
    'Vas a cancelar la cita de ' + nombrePaciente + ' el ' + fecha + ' a las ' + hora + '. ' +
    'El paciente recibira un correo con el motivo que escribas a continuacion.';
  document.getElementById('cancel-motivo').value = '';
  document.getElementById('cancel-error').style.display = 'none';
  document.getElementById('modal-cancelar').classList.add('abierto');
}

function cerrarModalCancelar() {
  document.getElementById('modal-cancelar').classList.remove('abierto');
  citaIdACancelar = null;
}

function enviarCancelacion() {
  const motivo  = document.getElementById('cancel-motivo').value.trim();
  const errorEl = document.getElementById('cancel-error');
  if (motivo.length < 10) {
    errorEl.textContent = 'Por favor escribe un motivo mas detallado (minimo 10 caracteres).';
    errorEl.style.display = 'block';
    return;
  }
  errorEl.style.display = 'none';
  document.getElementById('hidden-motivo').value = motivo;
  const form = document.getElementById('form-cancelar');
  form.action = '/psicologo/citas/' + citaIdACancelar + '/actualizar/';
  form.submit();
}

// inicialización del dashboard psicólogo
if (document.getElementById('modal-horarios')) {
  document.getElementById('modal-horarios').addEventListener('click', function (e) {
    if (e.target === this) cerrarModalHorarios();
  });
  document.getElementById('modal-cancelar').addEventListener('click', function (e) {
    if (e.target === this) cerrarModalCancelar();
  });
  document.addEventListener('DOMContentLoaded', marcarDisponibilidadInicial);
}


// dashboard paciente
// datos del servidor inyectados en el template como JSON island:
// <script type="application/json" id="datos-paciente">...</script>

const _datosPaciente = JSON.parse(document.getElementById('datos-paciente')?.textContent || '{}');
const PSICOLOGO_ID   = _datosPaciente.psicologoId || '';
const _calendarios   = _datosPaciente.calendarios || [];
let slotSeleccionado = null;

// carga disponibilidad de un mes y marca los días con horarios
async function cargarDisponibilidad(anio, mes) {
  try {
    const resp  = await fetch('/paciente/disponibilidad/' + PSICOLOGO_ID + '/' + anio + '/' + mes + '/');
    const datos = await resp.json();
    Object.entries(datos.disponibilidad || {}).forEach(([fecha, slots]) => {
      if (!slots.length) return;
      const el    = document.getElementById('pdia-'   + fecha.replace(/-/g, ''));
      const punto = document.getElementById('ppunto-' + fecha.replace(/-/g, ''));
      if (el && !el.classList.contains('pasado')) {
        el.classList.add('con-disponibilidad');
        el.style.cursor = 'pointer';
        el.onclick = () => abrirModal(fecha, el.dataset.display, slots);
        if (punto) punto.style.display = 'block';
      }
    });
  } catch (e) {}
}

// abre el modal de reserva con los slots de una fecha
function abrirModal(fecha, fechaDisplay, slots) {
  slotSeleccionado = null;
  document.getElementById('btn-confirmar-reserva').disabled = true;
  document.getElementById('modal-titulo').textContent    = 'Reservar cita';
  document.getElementById('modal-subtitulo').textContent = 'Fecha: ' + fechaDisplay + ' — Selecciona un horario';
  document.getElementById('msg-modal').style.display     = 'none';
  document.getElementById('motivo-input').value          = '';

  const lista = document.getElementById('slots-lista');
  lista.innerHTML = slots.length
    ? slots.map(s => `
        <div class="slot-item" onclick="seleccionarSlot(this, ${s.horario_id})"
             data-id="${s.horario_id}" data-inicio="${s.hora_inicio}" data-fin="${s.hora_fin}">
          <span class="slot-hora">${s.hora_inicio} - ${s.hora_fin}</span>
          <span style="font-size:.75rem;color:var(--texto-medio);">Disponible</span>
        </div>
      `).join('')
    : '<p style="text-align:center;color:var(--texto-medio);font-size:.85rem;padding:.5rem;">No hay horarios disponibles para este dia.</p>';

  document.getElementById('modal-overlay').classList.add('abierto');
}

function seleccionarSlot(el, id) {
  document.querySelectorAll('.slot-item').forEach(s => s.classList.remove('seleccionado'));
  el.classList.add('seleccionado');
  slotSeleccionado = id;
  document.getElementById('btn-confirmar-reserva').disabled = false;
}

async function confirmarReserva() {
  if (!slotSeleccionado) return;
  const motivo = document.getElementById('motivo-input').value.trim();
  const btn    = document.getElementById('btn-confirmar-reserva');
  btn.disabled = true;
  btn.textContent = 'Reservando...';

  try {
    const resp  = await fetch('/paciente/reservar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
      body: JSON.stringify({ horario_id: slotSeleccionado, motivo }),
    });
    const datos = await resp.json();
    const msg   = document.getElementById('msg-modal');
    if (datos.ok) {
      msg.textContent = datos.mensaje;
      msg.className   = 'msg-modal msg-ok';
      msg.style.display = 'block';
      setTimeout(() => { cerrarModal(); location.reload(); }, 2200);
    } else {
      msg.textContent = datos.error || 'Error al reservar.';
      msg.className   = 'msg-modal msg-err';
      msg.style.display = 'block';
      btn.disabled    = false;
      btn.textContent = 'Reservar';
    }
  } catch (e) {
    const msg = document.getElementById('msg-modal');
    msg.textContent = 'Error de conexion.';
    msg.className   = 'msg-modal msg-err';
    msg.style.display = 'block';
    btn.disabled    = false;
    btn.textContent = 'Reservar';
  }
}

function cerrarModal() {
  document.getElementById('modal-overlay')?.classList.remove('abierto');
  slotSeleccionado = null;
}

// inicialización del dashboard paciente
if (document.getElementById('modal-overlay')) {
  document.getElementById('modal-overlay').addEventListener('click', function (e) {
    if (e.target === this) cerrarModal();
  });
  if (PSICOLOGO_ID) {
    document.addEventListener('DOMContentLoaded', () => {
      _calendarios.forEach(c => cargarDisponibilidad(c.anio, c.mes));
    });
  }
}


// modal horario semanal (psicólogo)

function abrirModalSemanal() {
  const msg = document.getElementById('msg-semanal');
  if (msg) { msg.style.display = 'none'; msg.textContent = ''; }
  document.getElementById('modal-semanal').classList.add('abierto');
}

function cerrarModalSemanal() {
  document.getElementById('modal-semanal').classList.remove('abierto');
}

async function aplicarHorarioSemanal() {
  const inicio = document.getElementById('sem-inicio').value;
  const fin    = document.getElementById('sem-fin').value;
  const mes    = document.querySelector('input[name="mes-semanal"]:checked')?.value || 'actual';
  const dias   = [...document.querySelectorAll('.dia-check:checked')].map(el => parseInt(el.value));

  const msg = document.getElementById('msg-semanal');

  function mostrar(txt, tipo) {
    msg.textContent = txt;
    msg.className = 'msg-modal ' + (tipo === 'ok' ? 'msg-ok' : 'msg-err');
    msg.style.display = 'block';
  }

  if (!inicio || !fin)    { mostrar('Ingresa la hora de inicio y fin.', 'err'); return; }
  if (fin <= inicio)      { mostrar('La hora de fin debe ser mayor que la de inicio.', 'err'); return; }
  if (dias.length === 0)  { mostrar('Selecciona al menos un día de la semana.', 'err'); return; }

  const btn = document.querySelector('.btn-aplicar-semanal');
  btn.disabled = true;
  btn.textContent = 'Aplicando...';

  try {
    const r = await fetch('/psicologo/horarios/semanal/guardar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
      body: JSON.stringify({ hora_inicio: inicio + ':00', hora_fin: fin + ':00', dias, mes }),
    });
    const d = await r.json();
    if (d.ok) {
      mostrar(d.mensaje, 'ok');
      // refrescar los puntos del calendario después de un momento
      setTimeout(() => { cerrarModalSemanal(); marcarDisponibilidadInicial(); }, 1800);
    } else {
      mostrar(d.error || 'Error al aplicar.', 'err');
    }
  } catch (e) {
    mostrar('Error de conexión.', 'err');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Aplicar al mes';
  }
}

// cierra modal semanal al hacer clic fuera
if (document.getElementById('modal-semanal')) {
  document.getElementById('modal-semanal').addEventListener('click', function (e) {
    if (e.target === this) cerrarModalSemanal();
  });
}
