from django.core.management.base import BaseCommand
from citas.models import Usuario


class Command(BaseCommand):
    help = 'Crea los usuarios iniciales del sistema (admin, psicologo, paciente)'

    def handle(self, *args, **options):
        self.stdout.write('Creando usuarios iniciales...')

        # --- Administrador ---
        if not Usuario.objects.filter(username='admin').exists():
            Usuario.objects.create_superuser(
                username='admin',
                email='admin@sanamente.com',
                password='Admin2026',
                nombre='Administrador',
                apellidos='Sistema',
                correo='admin@sanamente.com',
                celular='3000000000',
                rol='admin',
                habilitado=True,
            )
            self.stdout.write(self.style.SUCCESS('  Administrador creado: usuario=admin / contrasena=Admin2026'))
        else:
            self.stdout.write('  Administrador ya existe.')

        # --- Psicologa ---
        if not Usuario.objects.filter(username='psicologa').exists():
            p = Usuario(
                username='psicologa',
                email='psicologa@sanamente.com',
                nombre='Ana Maria',
                apellidos='Martinez Lopez',
                correo='psicologa@sanamente.com',
                celular='3111111111',
                rol='psicologo',
                habilitado=True,
            )
            p.set_password('Psi2026')
            p.save()
            self.stdout.write(self.style.SUCCESS('  Psicologa creada: usuario=psicologa / contrasena=Psi2026'))
        else:
            self.stdout.write('  Psicologa ya existe.')

        # --- Paciente ---
        if not Usuario.objects.filter(username='paciente1').exists():
            pac = Usuario(
                username='paciente1',
                email='paciente1@ejemplo.com',
                nombre='Juan',
                apellidos='Perez Gomez',
                correo='paciente1@ejemplo.com',
                celular='3222222222',
                rol='paciente',
                habilitado=True,
            )
            pac.set_password('Pac2026')
            pac.save()
            self.stdout.write(self.style.SUCCESS('  Paciente creado: usuario=paciente1 / contrasena=Pac2026'))
        else:
            self.stdout.write('  Paciente ya existe.')

        self.stdout.write(self.style.SUCCESS('\nUsuarios iniciales listos.'))
