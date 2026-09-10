"""Lote 11: comprueba que los archivos finales esten listos para modelar."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from modularizado import config
from modularizado.utilidades import titulo


def cargar_finales():
    """Lee los dos csv de salida."""
    return pd.read_csv(config.RUTA_TRAIN), pd.read_csv(config.RUTA_TEST)


def revisar_estructura(entrenamiento, prueba):
    """Verifica columnas, tipos, nulos y posicion del objetivo."""
    problemas = []

    if list(entrenamiento.columns) != list(prueba.columns):
        problemas.append("entrenamiento y prueba no tienen las mismas columnas en el mismo orden")
    if entrenamiento.columns[-1] != config.OBJETIVO:
        problemas.append(f"la ultima columna no es {config.OBJETIVO}")

    for nombre, datos in [("entrenamiento", entrenamiento), ("prueba", prueba)]:
        nulos = int(datos.isna().sum().sum())
        if nulos:
            problemas.append(f"{nombre} tiene {nulos} valores faltantes")
        no_numericas = datos.select_dtypes(exclude="number").columns.tolist()
        if no_numericas:
            problemas.append(f"{nombre} tiene columnas no numericas: {no_numericas}")
        valores = set(datos[config.OBJETIVO].unique())
        if not valores <= {0, 1}:
            problemas.append(f"{nombre} tiene un objetivo que no es 0/1: {sorted(valores)}")

    return problemas


def revisar_columnas_inutiles(entrenamiento):
    """Busca columnas constantes o repetidas, que no aportan al modelo."""
    constantes = [c for c in entrenamiento.columns if entrenamiento[c].nunique() <= 1]
    repetidas = []
    columnas = list(entrenamiento.columns)
    for i, a in enumerate(columnas):
        for b in columnas[i + 1:]:
            if entrenamiento[a].equals(entrenamiento[b]):
                repetidas.append((a, b))
    return constantes, repetidas


def revisar_separacion(entrenamiento, prueba):
    """Cuenta filas de prueba que aparecen identicas en entrenamiento."""
    marca_train = set(map(tuple, entrenamiento.to_numpy()))
    return sum(1 for fila in map(tuple, prueba.to_numpy()) if fila in marca_train)


def revisar_desbalance(entrenamiento, prueba):
    """Compara la proporcion de la clase positiva en ambos conjuntos."""
    return entrenamiento[config.OBJETIVO].mean(), prueba[config.OBJETIVO].mean()


def ejecutar():
    """Corre todas las revisiones e informa si los datos estan listos."""
    titulo("Lote 11: validacion final")

    entrenamiento, prueba = cargar_finales()
    print(f"Entrenamiento: {entrenamiento.shape[0]} filas x {entrenamiento.shape[1]} columnas")
    print(f"Prueba:        {prueba.shape[0]} filas x {prueba.shape[1]} columnas")

    problemas = revisar_estructura(entrenamiento, prueba)

    constantes, repetidas = revisar_columnas_inutiles(entrenamiento)
    print(f"\nColumnas constantes: {constantes or 'ninguna'}")
    print(f"Columnas repetidas: {repetidas or 'ninguna'}")

    compartidas = revisar_separacion(entrenamiento, prueba)
    print(f"Filas de prueba que tambien estan en entrenamiento: {compartidas}")
    if compartidas:
        problemas.append(f"{compartidas} filas se repiten entre entrenamiento y prueba")

    tasa_train, tasa_test = revisar_desbalance(entrenamiento, prueba)
    print(f"Proporcion de hospdead=1 -> entrenamiento {tasa_train:.3f} / prueba {tasa_test:.3f}")
    if abs(tasa_train - tasa_test) > 0.02:
        problemas.append("la proporcion de la clase positiva difiere entre los dos conjuntos")

    print()
    if problemas:
        for problema in problemas:
            print(f"PROBLEMA: {problema}")
        raise AssertionError(f"{len(problemas)} revision(es) fallaron")

    print("Todas las revisiones pasaron: los archivos estan listos para modelar.")
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
