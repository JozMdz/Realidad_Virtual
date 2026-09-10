"""Lote 8: convierte las columnas de categoria en columnas numericas 0/1."""

import pandas as pd

from modularizado.utilidades import (
    cargar_intermedio,
    columnas_por_tipo,
    guardar_intermedio,
    titulo,
)


def fijar_categorias(entrenamiento, categoricas):
    """Toma de entrenamiento la lista de categorias validas de cada columna."""
    return {
        columna: sorted(entrenamiento[columna].dropna().unique().tolist())
        for columna in categoricas
    }


def aplicar_categorias(entrenamiento, prueba, categorias_fijas):
    """Impone las mismas categorias en ambos conjuntos y avisa de valores nuevos."""
    for columna, categorias in categorias_fijas.items():
        desconocidas = ~prueba[columna].isin(categorias)
        if desconocidas.any():
            print(f"Atencion: {desconocidas.sum()} filas de prueba con categoria nueva en '{columna}'.")
        entrenamiento[columna] = pd.Categorical(entrenamiento[columna], categories=categorias)
        prueba[columna] = pd.Categorical(prueba[columna], categories=categorias)
    return entrenamiento, prueba


def codificar(entrenamiento, prueba, categoricas):
    """Genera las columnas dummy y alinea prueba con las columnas de entrenamiento."""
    entrenamiento = pd.get_dummies(entrenamiento, columns=categoricas, drop_first=True)
    prueba = pd.get_dummies(prueba, columns=categoricas, drop_first=True)
    prueba = prueba.reindex(columns=entrenamiento.columns, fill_value=0)

    booleanas = [columna for columna in entrenamiento.columns if entrenamiento[columna].dtype == bool]
    entrenamiento[booleanas] = entrenamiento[booleanas].astype(int)
    prueba[booleanas] = prueba[booleanas].astype(int)

    return entrenamiento, prueba


def ejecutar():
    """Entrega ambos conjuntos completamente numericos y con las mismas columnas."""
    titulo("Lote 8: codificacion de categorias")

    entrenamiento = cargar_intermedio("07_entrenamiento")
    prueba = cargar_intermedio("07_prueba")

    _, categoricas = columnas_por_tipo(entrenamiento)
    categorias_fijas = fijar_categorias(entrenamiento, categoricas)

    print("Categorias fijadas a partir de entrenamiento:")
    for columna, categorias in categorias_fijas.items():
        print(f"  {columna}: {categorias}")
    print()

    entrenamiento, prueba = aplicar_categorias(entrenamiento, prueba, categorias_fijas)

    columnas_antes = entrenamiento.shape[1]
    entrenamiento, prueba = codificar(entrenamiento, prueba, categoricas)

    print(f"Columnas antes de codificar: {columnas_antes}")
    print(f"Columnas despues de codificar: {entrenamiento.shape[1]}")
    print(f"Mismas columnas y mismo orden en ambos conjuntos: {list(entrenamiento.columns) == list(prueba.columns)}")

    guardar_intermedio(entrenamiento, "08_entrenamiento")
    guardar_intermedio(prueba, "08_prueba")
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
