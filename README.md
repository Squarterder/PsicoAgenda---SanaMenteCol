# PsicoAgenda — SanaMenteCol

Sistema web de gestión de citas para consultorio psicológico, desarrollado con Django. Permite que pacientes agenden citas con psicólogos, y que los psicólogos gestionen su disponibilidad y el seguimiento clínico de sus pacientes.

---

## Tecnologías usadas

| Capa          | Tecnología                                                            |
|---------------|-----------------------------------------------------------------------|
| Backend       | Python 3.x + Django 4.2                                               |
| Base de datos | SQLite (incluida con Django, sin instalación extra)                   |
| Frontend      | HTML5, CSS3 con variables personalizadas, JavaScript ES6+ (Fetch API) |
| Autenticación | Sistema de usuarios propio extendiendo `AbstractUser` de Django       |
| Correo        | SMTP de Gmail con contraseña de aplicación                            |

---

## Funcionalidades principales

- **3 roles de usuario:** Administrador, Psicólogo, Paciente
- Registro con username personalizado y validación en servidor
- Calendario de disponibilidad por mes (psicólogo configura horarios individuales o semanales recurrentes)
- Reserva de citas con confirmación por correo electrónico
- Seguimiento clínico con ficha por paciente
- Panel de administración para gestión de usuarios

---

## Instalación paso a paso

### 1 — Clonar o descomprimir el proyecto

```bash
git clone https://github.com/Squarterder/PsicoAgenda---SanaMenteCol.git
cd psicoagenda
```

### 2 — Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4 — Configurar variables de entorno

Copia el archivo de ejemplo y edítalo con tus datos:

Abre `psicoagenda/settings.py` y reemplaza los valores:

```
SECRET_KEY=django-insecure-psicoagenda-sanamentecol-2026-cambia-en-produccion
DEBUG=True
EMAIL_HOST_USER=tucorreo@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
```

> **Nota:** El sistema funciona igual sin configurar el correo, simplemente no se enviarán notificaciones.

### 5 — Crear la base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6 — Crear los usuarios de prueba

```bash
python manage.py crear_datos_iniciales
```

| Rol           | Usuario   | Contraseña |
|---------------|-----------|------------|
| Administrador | admin     | Admin2026  |
| Psicóloga     | psicologa | Psi2026    |
| Paciente      | paciente1 | Pac2026    |

### 7 — Iniciar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador: **http://127.0.0.1:8000/**

---

## Guía de conexión — Correo Gmail

El correo es opcional. Si no lo configuras, el sistema funciona normalmente en todo lo demás.

Para activar las notificaciones por correo necesitas una **contraseña de aplicación** de Gmail (no es tu contraseña normal):

1. Ve a https://myaccount.google.com/security
2. Activa la **Verificación en dos pasos** si no la tienes
3. Busca **Contraseñas de aplicación** y crea una nueva llamada "PsicoAgenda"
4. Copia los 16 caracteres que Google te muestra
5. Pégalos en `EMAIL_HOST_PASSWORD` dentro de `settings.py`

---

## Estructura del proyecto

```
psicoagenda/
│
├── manage.py
├── requirements.txt
├── db.sqlite3                        Base de datos (se genera con migrate)
│
├── psicoagenda/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── citas/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── management/commands/
│       └── crear_datos_iniciales.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── registro.html
│   ├── dashboard_admin.html
│   ├── admin_crear_usuario.html
│   ├── dashboard_psicologo.html
│   ├── lista_pacientes.html
│   ├── seguimiento_paciente.html
│   └── dashboard_paciente.html
│
└── static/
    ├── estilos.css
    ├── aplicacion.js
    ├── psicologa.jpg
    └── consultorio.jpg
```

---
