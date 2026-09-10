"""Lote 2: carga el csv crudo, estandariza nombres y audita el estado inicial."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from modularizado import config
from modularizado.utilidades import guardar_intermedio, titulo


def cargar_datos(ruta=None):
    """Lee el csv crudo reconociendo los marcadores de dato faltante."""
    ruta = ruta or config.RUTA_CSV
    return pd.read_csv(ruta, na_values=config.VALORES_NULOS)


def estandarizar_columnas(datos):
    """Pasa los nombres a minusculas con guion bajo y descarta filas vacias."""
    datos = datos.copy()
    datos.columns = [
        columna.strip().lower().replace(" ", "_").replace(".", "_")
        for columna in datos.columns
    ]
    return datos.dropna(how="all").copy()


def resumen_columnas(datos):
    """Arma la tabla de tipo, nulos y valores unicos por columna."""
    resumen = pd.DataFrame({
        "columna": datos.columns,
        "tipo": [str(datos[columna].dtype) for columna in datos.columns],
        "nulos": [datos[columna].isna().sum() for columna in datos.columns],
        "porcentaje_nulos": [round(datos[columna].isna().mean() * 100, 1) for columna in datos.columns],
        "unicos": [datos[columna].nunique(dropna=True) for columna in datos.columns],
    })
    return resumen.sort_values("porcentaje_nulos", ascending=False)


def guardar_estadisticas(datos):
    """Guarda las estadisticas descriptivas de todas las columnas."""
    descripcion = datos.describe(include="all").transpose()
    descripcion.to_csv(config.RUTA_ESTADISTICAS)
    return descripcion


def ejecutar():
    """Genera el dataset estandarizado y el reporte de auditoria."""
    titulo("Lote 2: auditoria estadistica inicial")

    datos = estandarizar_columnas(cargar_datos())
    print(f"Filas: {datos.shape[0]}")
    print(f"Columnas: {datos.shape[1]}")
    print("Nombres de columnas:")
    print(list(datos.columns))

    print()
    print("Diagnostico de valores faltantes por columna:")
    print(resumen_columnas(datos).to_string(index=False))

    print()
    print(guardar_estadisticas(datos))
    print(f"\nEstadisticas descriptivas guardadas en: {config.RUTA_ESTADISTICAS}")

    guardar_intermedio(datos, "02_estandarizado")
    return datos


if __name__ == "__main__":
    ejecutar()
