"""Lote 4: elimina filas duplicadas antes de dividir entrenamiento y prueba."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from modularizado.utilidades import cargar_intermedio, guardar_intermedio, titulo


def contar_duplicados(datos):
    """Cuenta las filas repetidas por completo."""
    return int(datos.duplicated().sum())


def quitar_duplicados(datos):
    """Devuelve el dataset sin filas repetidas y con indice reiniciado."""
    return datos.drop_duplicates().reset_index(drop=True)


def ejecutar():
    """Deja el dataset sin filas repetidas."""
    titulo("Lote 4: filas repetidas")

    datos = cargar_intermedio("03_seleccionado")
    filas_antes = datos.shape[0]

    print(f"Filas duplicadas encontradas: {contar_duplicados(datos)}")
    datos = quitar_duplicados(datos)

    print(f"Filas antes: {filas_antes}")
    print(f"Filas despues de quitar duplicados: {datos.shape[0]}")

    guardar_intermedio(datos, "04_sin_duplicados")
    return datos


if __name__ == "__main__":
    ejecutar()
