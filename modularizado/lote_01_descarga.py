"""Lote 1: obtiene support2.csv desde el repositorio UCI o reutiliza el archivo local."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from modularizado import config
from modularizado.utilidades import titulo


def descargar_desde_uci():
    """Descarga el dataset 880 de UCI y devuelve datos y diccionario de variables."""
    from ucimlrepo import fetch_ucirepo

    support2 = fetch_ucirepo(id=config.ID_REPOSITORIO_UCI)
    datos = support2.data.features.join(support2.data.targets)
    diccionario = support2.variables[["name", "role", "description"]]
    diccionario = diccionario[diccionario["name"] != "id"]
    return datos, diccionario


def guardar_datos(datos):
    """Escribe el csv crudo."""
    config.DIR_DATOS.mkdir(parents=True, exist_ok=True)
    datos.to_csv(config.RUTA_CSV, index=False)


def guardar_diccionario(diccionario):
    """Escribe la ficha de variables que publica UCI."""
    config.DIR_DATOS.mkdir(parents=True, exist_ok=True)
    diccionario.to_csv(config.RUTA_DICCIONARIO, index=False)


def comparar_con_local(datos):
    """Compara la descarga con el csv ya guardado."""
    local = pd.read_csv(config.RUTA_CSV)
    return local.shape == datos.shape, local.columns.equals(datos.columns)


def ejecutar():
    """Deja support2.csv disponible para el resto del pipeline."""
    titulo("Lote 1: descarga de datos")

    try:
        datos, diccionario = descargar_desde_uci()
    except Exception as error:
        if not config.RUTA_CSV.exists():
            raise FileNotFoundError(
                f"No hay conexion con UCI ({error}) y tampoco existe {config.RUTA_CSV}."
            ) from error
        print(f"Sin descarga ({type(error).__name__}); se usa el archivo local {config.RUTA_CSV.name}.")
        return config.RUTA_CSV

    print(f"Pacientes: {datos.shape[0]}")
    print(f"Columnas descargadas: {datos.shape[1]}")

    if config.RUTA_CSV.exists():
        misma_forma, mismas_columnas = comparar_con_local(datos)
        print(f"Misma forma que el archivo ya guardado: {misma_forma}")
        print(f"Mismas columnas: {mismas_columnas}")
    else:
        print("No habia un archivo previo; se guarda por primera vez.")
        guardar_datos(datos)

    guardar_diccionario(diccionario)
    print(f"Diccionario de variables guardado en: {config.RUTA_DICCIONARIO}")

    return config.RUTA_CSV


if __name__ == "__main__":
    ejecutar()
