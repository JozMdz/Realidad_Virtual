"""Lote 7: acota valores atipicos con el RIC y marca con una bandera las filas recortadas."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from modularizado import config
from modularizado.utilidades import (
    cargar_intermedio,
    columnas_por_tipo,
    guardar_intermedio,
    titulo,
)


def separar_binarias(entrenamiento, numericas):
    """Aparta las columnas de 0/1, donde la regla del RIC no aplica."""
    binarias = [columna for columna in numericas if entrenamiento[columna].nunique() <= 2]
    revisables = [columna for columna in numericas if columna not in binarias]
    return binarias, revisables


def limites_ric(serie, factor=config.FACTOR_RIC):
    """Devuelve los limites inferior y superior segun Q1, Q3 y el RIC, ignorando nulos."""
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    ric = q3 - q1
    return q1 - factor * ric, q3 + factor * ric


def bandera_atipicos(serie, inferior, superior):
    """Marca con 1 las filas cuyo valor cae fuera de los limites, antes de recortarlo."""
    return ((serie < inferior) | (serie > superior)).astype(int)


def acotar(entrenamiento, prueba, columnas, minimo=config.MINIMO_BANDERA_ATIPICOS):
    """Recorta los valores fuera de rango y agrega una bandera por columna que si corto."""
    resumen = []
    banderas_entrenamiento = {}
    banderas_prueba = {}
    piso = max(1, round(minimo * len(entrenamiento)))

    for columna in columnas:
        inferior, superior = limites_ric(entrenamiento[columna])
        marca_entrenamiento = bandera_atipicos(entrenamiento[columna], inferior, superior)
        marca_prueba = bandera_atipicos(prueba[columna], inferior, superior)
        fuera_train = int(marca_entrenamiento.sum())
        fuera_test = int(marca_prueba.sum())

        lleva_bandera = fuera_train >= piso
        if lleva_bandera:
            nombre = f"{columna}{config.SUFIJO_BANDERA}"
            banderas_entrenamiento[nombre] = marca_entrenamiento
            banderas_prueba[nombre] = marca_prueba

        if fuera_train or fuera_test:
            resumen.append((
                columna,
                fuera_train,
                fuera_test,
                round(fuera_train / len(entrenamiento) * 100, 1),
                round(inferior, 2),
                round(superior, 2),
                "si" if lleva_bandera else "no",
            ))

        entrenamiento[columna] = entrenamiento[columna].clip(lower=inferior, upper=superior)
        prueba[columna] = prueba[columna].clip(lower=inferior, upper=superior)

    if banderas_entrenamiento:
        entrenamiento = pd.concat(
            [entrenamiento, pd.DataFrame(banderas_entrenamiento, index=entrenamiento.index)], axis=1
        )
        prueba = pd.concat(
            [prueba, pd.DataFrame(banderas_prueba, index=prueba.index)], axis=1
        )

    tabla = pd.DataFrame(
        resumen,
        columns=[
            "columna",
            "atipicos_entrenamiento",
            "atipicos_prueba",
            "porcentaje_train",
            "limite_inferior",
            "limite_superior",
            "bandera",
        ],
    ).sort_values("atipicos_entrenamiento", ascending=False)

    return entrenamiento, prueba, tabla, list(banderas_entrenamiento)


def ejecutar():
    """Entrega ambos conjuntos con los valores extremos acotados."""
    titulo("Lote 7: valores atipicos")

    entrenamiento = cargar_intermedio("06_entrenamiento")
    prueba = cargar_intermedio("06_prueba")

    numericas, _ = columnas_por_tipo(entrenamiento)
    binarias, revisables = separar_binarias(entrenamiento, numericas)
    print(f"Columnas binarias excluidas de la regla: {binarias}")

    entrenamiento, prueba, tabla, banderas = acotar(entrenamiento, prueba, revisables)
    print("\nColumnas con valores atipicos acotados (limites fijados con entrenamiento):")
    print(tabla.to_string(index=False))

    print(f"\nBanderas agregadas ({len(banderas)}): {banderas}")
    print(f"Columnas totales: {entrenamiento.shape[1]}")

    guardar_intermedio(entrenamiento, "07_entrenamiento")
    guardar_intermedio(prueba, "07_prueba")
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
