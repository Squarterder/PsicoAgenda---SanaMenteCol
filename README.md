# PsicoAgenda — SanaMenteCol
Sistema de gestion de citas para consultorio psicologico desarrollado con Django.

---

## Instalacion y ejecucion

### Paso 1 — Abrir terminal en la carpeta del proyecto
Descomprime el ZIP. Abre una terminal dentro de la carpeta `psicoagenda/`.

### Paso 2 — Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Paso 3 — Instalar Django
```bash
pip install -r requirements.txt
```

### Paso 4 — Crear la base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 5 — Crear los 3 usuarios iniciales
```bash
python manage.py crear_datos_iniciales
```

| Rol           | Usuario    | Contraseña |
|---------------|------------|------------|
| Administrador | admin      | Admin2026  |
| Psicologa     | psicologa  | Psi2026    |
| Paciente      | paciente1  | Pac2026    |

### Paso 6 — Configurar el correo (leer seccion de abajo primero)
Abre el archivo `psicoagenda/settings.py` y reemplaza las dos lineas:
```python
EMAIL_HOST_USER     = 'AQUI_TU_CORREO@gmail.com'
EMAIL_HOST_PASSWORD = 'AQUI_TU_CONTRASEÑA_DE_APLICACION'
DEFAULT_FROM_EMAIL  = 'PsicoAgenda SanaMenteCol <AQUI_TU_CORREO@gmail.com>'
```
por tus datos reales. El procedimiento para obtenerlos esta mas abajo.

### Paso 7 — Iniciar el servidor
```bash
python manage.py runserver
```
Abre el navegador en: http://127.0.0.1:8000/

---

## Como obtener la contraseña de aplicacion de Gmail (paso a paso)

Los correos del sistema (notificaciones de citas) se envian desde una cuenta de Gmail.
Gmail no permite usar tu contraseña normal desde aplicaciones externas por seguridad.
En su lugar debes generar una "contraseña de aplicacion", que es una clave especial
de 16 caracteres que Google crea para que PsicoAgenda se conecte a tu cuenta.

### Requisito previo: tener verificacion en dos pasos activada

Google solo permite crear contraseñas de aplicacion si tienes activa la verificacion
en dos pasos (el codigo que te llega al celular cuando inicias sesion).

Si aun no la tienes:

1. Ve a https://myaccount.google.com
2. Haz clic en "Seguridad" en el menu de la izquierda.
3. Busca la seccion "Como inicias sesion en Google".
4. Haz clic en "Verificacion en dos pasos".
5. Sigue los pasos para activarla (necesitas tu celular).

### Paso 1 — Ir a la configuracion de seguridad de tu cuenta Google

Ve a esta direccion directamente:
https://myaccount.google.com/security

### Paso 2 — Buscar "Contraseñas de aplicacion"

En esa pagina, dentro de la seccion "Como inicias sesion en Google",
busca la opcion llamada "Contraseñas de aplicacion".

Si no aparece, significa que la verificacion en dos pasos no esta activa.
Activala primero y luego vuelve a buscarla.

### Paso 3 — Crear la contraseña de aplicacion

1. Haz clic en "Contraseñas de aplicacion".
2. Google te pedira confirmar tu identidad con tu contraseña normal.
3. En la pantalla que aparece veras un campo que dice "Nombre de la app".
4. Escribe cualquier nombre descriptivo, por ejemplo: PsicoAgenda
5. Haz clic en "Crear".

### Paso 4 — Copiar la contraseña generada

Google te mostrara una contraseña de 16 caracteres separados en 4 grupos,
por ejemplo: abcd efgh ijkl mnop

Copia esa contraseña exactamente como aparece, incluyendo los espacios,
o sin espacios, ambas formas funcionan.

IMPORTANTE: esa contraseña solo se muestra una vez. Si la cierras sin copiarla
tendras que generar una nueva.

### Paso 5 — Pegar los datos en settings.py

Abre el archivo `psicoagenda/settings.py` y edita estas tres lineas:

```python
EMAIL_HOST_USER     = 'tucorreo@gmail.com'
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'
DEFAULT_FROM_EMAIL  = 'PsicoAgenda SanaMenteCol <tucorreo@gmail.com>'
```

Reemplaza `tucorreo@gmail.com` con tu correo real de Gmail.
Reemplaza `abcd efgh ijkl mnop` con la contraseña de 16 caracteres que copiaste.

Guarda el archivo.

### Paso 6 — Probar que funciona

Inicia el servidor y reserva una cita con el usuario paciente1.
El psicologo deberia recibir un correo en la bandeja de entrada de la cuenta
de Gmail que configuraste.

Si el correo llega a la carpeta de spam, abrelo y marcalo como "No es spam"
para que los siguientes lleguen al inbox.

### Que pasa si no configuro el correo

El sistema funciona normalmente en todos los demas aspectos.
Simplemente los correos de notificacion no se enviaran y Django
mostrara un error silencioso en segundo plano sin afectar la aplicacion.
Las citas se pueden gestionar igual desde los paneles.

---

## Estructura del proyecto

```
psicoagenda/
|
|-- manage.py                    Comando principal de Django
|-- requirements.txt             Dependencias (solo Django)
|-- db.sqlite3                   Base de datos (se crea con migrate)
|
|-- psicoagenda/
|   |-- settings.py              Ajustes: BD, correo, rutas, idioma
|   |-- urls.py                  URLs principales
|   |-- wsgi.py                  Para despliegue en servidor
|
|-- citas/
|   |-- models.py                Modelos: Usuario, HorarioDisponible, Cita, SeguimientoClinico
|   |-- views.py                 Logica del sistema y envio de correos
|   |-- urls.py                  Rutas de la aplicacion
|   |-- forms.py                 Formularios y validaciones
|   |-- admin.py                 Panel de administracion Django
|   |-- management/
|       |-- commands/
|           |-- crear_datos_iniciales.py   Crea los 3 usuarios de prueba
|   |-- migrations/              Migraciones de la BD
|
|-- templates/                   Paginas HTML
|   |-- base.html
|   |-- index.html               Pagina de inicio
|   |-- login.html
|   |-- registro.html
|   |-- dashboard_admin.html     Panel del administrador
|   |-- admin_crear_usuario.html Crear y editar usuarios
|   |-- dashboard_psicologo.html Agenda del psicologo
|   |-- lista_pacientes.html     Lista de pacientes del psicologo
|   |-- seguimiento_paciente.html Ficha clinica individual
|   |-- dashboard_paciente.html  Vista del paciente
|
|-- static/
    |-- estilos.css
    |-- aplicacion.js
    |-- psicologa.jpg
    |-- consultorio.jpg
```

---

## Comandos utiles

```bash
# Crear migraciones tras cambiar models.py
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear los 3 usuarios de prueba
python manage.py crear_datos_iniciales

# Iniciar el servidor
python manage.py runserver
```
