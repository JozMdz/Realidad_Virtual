"""Funciones de apoyo para mover datos entre lotes."""

import pandas as pd

from modularizado import config


def titulo(texto):
    """Imprime un encabezado de lote."""
    print()
    print(texto)
    print("-" * len(texto))


def guardar_intermedio(datos, nombre):
    """Guarda un DataFrame como archivo intermedio entre lotes."""
    config.DIR_INTERMEDIOS.mkdir(parents=True, exist_ok=True)
    ruta = config.DIR_INTERMEDIOS / f"{nombre}.csv"
    datos.to_csv(ruta, index=False)
    return ruta


def cargar_intermedio(nombre):
    """Lee un archivo intermedio generado por un lote anterior."""
    ruta = config.DIR_INTERMEDIOS / f"{nombre}.csv"
    if not ruta.exists():
        raise FileNotFoundError(f"Falta {ruta.name}: ejecutar antes el lote que lo genera.")
    return pd.read_csv(ruta)


def columnas_por_tipo(datos):
    """Separa los nombres de columna en numericas y categoricas."""
    numericas = datos.select_dtypes(include="number").columns.tolist()
    categoricas = [columna for columna in datos.columns if columna not in numericas]
    return numericas, categoricas
