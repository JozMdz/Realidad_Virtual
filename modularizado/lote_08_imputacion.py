"""Lote 8: rellena los valores faltantes con estadisticos del entrenamiento."""

from modularizado.utilidades import (
    cargar_intermedio,
    columnas_por_tipo,
    guardar_intermedio,
    titulo,
)


def rellenar(entrenamiento, prueba):
    """Rellena numericas con la mediana y categoricas con la moda de entrenamiento."""
    numericas, categoricas = columnas_por_tipo(entrenamiento)

    for columna in numericas:
        mediana = entrenamiento[columna].median()
        entrenamiento[columna] = entrenamiento[columna].fillna(mediana)
        prueba[columna] = prueba[columna].fillna(mediana)

    for columna in categoricas:
        moda = entrenamiento[columna].mode(dropna=True)[0]
        entrenamiento[columna] = entrenamiento[columna].fillna(moda)
        prueba[columna] = prueba[columna].fillna(moda)

    return entrenamiento, prueba


def ejecutar():
    """Entrega ambos conjuntos sin valores faltantes."""
    titulo("Lote 8: relleno de valores faltantes")

    entrenamiento = cargar_intermedio("07_entrenamiento")
    prueba = cargar_intermedio("07_prueba")

    nulos_antes = entrenamiento.isna().sum().sum() + prueba.isna().sum().sum()
    entrenamiento, prueba = rellenar(entrenamiento, prueba)
    nulos_despues = entrenamiento.isna().sum().sum() + prueba.isna().sum().sum()

    print(f"Faltantes antes de rellenar (train + test): {nulos_antes}")
    print(f"Faltantes despues de rellenar (train + test): {nulos_despues}")

    guardar_intermedio(entrenamiento, "08_entrenamiento")
    guardar_intermedio(prueba, "08_prueba")
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
