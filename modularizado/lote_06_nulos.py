"""Lote 6: elimina las columnas con demasiados valores faltantes."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from modularizado import config
from modularizado.utilidades import cargar_intermedio, guardar_intermedio, titulo


def porcentaje_faltante(entrenamiento):
    """Calcula el porcentaje de nulos por columna usando solo entrenamiento."""
    return (entrenamiento.isna().mean() * 100).round(1).sort_values(ascending=False)


def columnas_sobre_limite(faltantes, limite=config.LIMITE_FALTANTES):
    """Lista las columnas que superan el limite permitido de nulos."""
    return faltantes[faltantes > limite].index.tolist()


def eliminar_columnas(entrenamiento, prueba, columnas):
    """Quita las mismas columnas de ambos conjuntos."""
    return entrenamiento.drop(columns=columnas), prueba.drop(columns=columnas)


def ejecutar():
    """Deja fuera las columnas con mas nulos que el limite configurado."""
    titulo("Lote 6: columnas con exceso de nulos")

    entrenamiento = cargar_intermedio("05_entrenamiento")
    prueba = cargar_intermedio("05_prueba")

    faltantes = porcentaje_faltante(entrenamiento)
    print("Porcentaje de nulos por columna (calculado en entrenamiento):")
    print(faltantes.to_string())

    eliminadas = columnas_sobre_limite(faltantes)
    print(f"\nColumnas con mas de {config.LIMITE_FALTANTES}% de nulos: {eliminadas}")
    entrenamiento, prueba = eliminar_columnas(entrenamiento, prueba, eliminadas)
    print(f"Columnas restantes: {entrenamiento.shape[1]}")

    guardar_intermedio(entrenamiento, "06_entrenamiento")
    guardar_intermedio(prueba, "06_prueba")
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
