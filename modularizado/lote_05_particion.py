"""Lote 5: separa entrenamiento y prueba de forma estratificada."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from modularizado import config
from modularizado.utilidades import cargar_intermedio, guardar_intermedio, titulo


def dividir(datos):
    """Reparte las filas en 80/20 manteniendo la proporcion del objetivo."""
    entrenamiento = datos.groupby(config.OBJETIVO, group_keys=False).sample(
        frac=config.FRACCION_ENTRENAMIENTO, random_state=config.SEMILLA
    )
    prueba = datos.drop(entrenamiento.index)
    return entrenamiento.reset_index(drop=True), prueba.reset_index(drop=True)


def proporciones(datos, entrenamiento, prueba):
    """Compara la tasa de la clase positiva en los tres conjuntos."""
    return {
        "total": datos[config.OBJETIVO].mean(),
        "entrenamiento": entrenamiento[config.OBJETIVO].mean(),
        "prueba": prueba[config.OBJETIVO].mean(),
    }


def ejecutar():
    """Genera los conjuntos de entrenamiento y prueba."""
    titulo("Lote 5: particion entrenamiento / prueba")

    datos = cargar_intermedio("04_sin_duplicados")
    entrenamiento, prueba = dividir(datos)

    print(f"Filas de entrenamiento: {entrenamiento.shape[0]}")
    print(f"Filas de prueba: {prueba.shape[0]}")
    print()
    print(f"Proporcion de hospdead=1 (semilla {config.SEMILLA}):")
    for nombre, valor in proporciones(datos, entrenamiento, prueba).items():
        print(f"  {nombre}: {valor:.3f}")

    guardar_intermedio(entrenamiento, "05_entrenamiento")
    guardar_intermedio(prueba, "05_prueba")
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
