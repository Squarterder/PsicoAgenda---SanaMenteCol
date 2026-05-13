#!/usr/bin/env python
"""Utilidad de linea de comandos de Django para tareas administrativas."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psicoagenda.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Asegurate de tenerlo instalado "
            "y de que la variable DJANGO_SETTINGS_MODULE este configurada."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
