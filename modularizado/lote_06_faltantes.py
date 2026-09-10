"""Lote 6: elimina columnas con exceso de nulos y rellena los faltantes restantes."""

from modularizado import config
from modularizado.utilidades import (
    cargar_intermedio,
    columnas_por_tipo,
    guardar_intermedio,
    titulo,
)


def porcentaje_faltante(entrenamiento):
    """Calcula el porcentaje de nulos por columna usando solo entrenamiento."""
    return (entrenamiento.isna().mean() * 100).round(1).sort_values(ascending=False)


def columnas_sobre_limite(faltantes, limite=config.LIMITE_FALTANTES):
    """Lista las columnas que superan el limite permitido de nulos."""
    return faltantes[faltantes > limite].index.tolist()


def eliminar_columnas(entrenamiento, prueba, columnas):
    """Quita las mismas columnas de ambos conjuntos."""
    return entrenamiento.drop(columns=columnas), prueba.drop(columns=columnas)


def imputar(entrenamiento, prueba):
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
    titulo("Lote 6: valores faltantes")

    entrenamiento = cargar_intermedio("05_entrenamiento")
    prueba = cargar_intermedio("05_prueba")

    faltantes = porcentaje_faltante(entrenamiento)
    print("Porcentaje de nulos por columna (calculado en entrenamiento):")
    print(faltantes.to_string())

    eliminadas = columnas_sobre_limite(faltantes)
    print(f"\nColumnas con mas de {config.LIMITE_FALTANTES}% de nulos: {eliminadas}")
    entrenamiento, prueba = eliminar_columnas(entrenamiento, prueba, eliminadas)
    print(f"Columnas despues de eliminar: {entrenamiento.shape[1]}")

    nulos_antes = entrenamiento.isna().sum().sum() + prueba.isna().sum().sum()
    entrenamiento, prueba = imputar(entrenamiento, prueba)
    nulos_despues = entrenamiento.isna().sum().sum() + prueba.isna().sum().sum()

    print(f"\nFaltantes antes de rellenar (train + test): {nulos_antes}")
    print(f"Faltantes despues de rellenar (train + test): {nulos_despues}")

    guardar_intermedio(entrenamiento, "06_entrenamiento")
    guardar_intermedio(prueba, "06_prueba")
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
