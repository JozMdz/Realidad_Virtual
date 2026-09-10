"""Lote 7: acota valores atipicos con el rango intercuartilico del entrenamiento."""

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
    """Devuelve los limites inferior y superior segun Q1, Q3 y el RIC."""
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    ric = q3 - q1
    return q1 - factor * ric, q3 + factor * ric


def acotar(entrenamiento, prueba, columnas):
    """Recorta los valores fuera de rango en ambos conjuntos y resume lo acotado."""
    resumen = []

    for columna in columnas:
        inferior, superior = limites_ric(entrenamiento[columna])
        fuera_train = ((entrenamiento[columna] < inferior) | (entrenamiento[columna] > superior)).sum()
        fuera_test = ((prueba[columna] < inferior) | (prueba[columna] > superior)).sum()

        if fuera_train or fuera_test:
            resumen.append((columna, fuera_train, fuera_test, round(inferior, 2), round(superior, 2)))

        entrenamiento[columna] = entrenamiento[columna].clip(lower=inferior, upper=superior)
        prueba[columna] = prueba[columna].clip(lower=inferior, upper=superior)

    tabla = pd.DataFrame(
        resumen,
        columns=["columna", "atipicos_entrenamiento", "atipicos_prueba", "limite_inferior", "limite_superior"],
    ).sort_values("atipicos_entrenamiento", ascending=False)

    return entrenamiento, prueba, tabla


def ejecutar():
    """Entrega ambos conjuntos con los valores extremos acotados."""
    titulo("Lote 7: valores atipicos")

    entrenamiento = cargar_intermedio("06_entrenamiento")
    prueba = cargar_intermedio("06_prueba")

    numericas, _ = columnas_por_tipo(entrenamiento)
    binarias, revisables = separar_binarias(entrenamiento, numericas)
    print(f"Columnas binarias excluidas de la regla: {binarias}")

    entrenamiento, prueba, tabla = acotar(entrenamiento, prueba, revisables)
    print("\nColumnas con valores atipicos acotados (limites fijados con entrenamiento):")
    print(tabla.to_string(index=False))

    guardar_intermedio(entrenamiento, "07_entrenamiento")
    guardar_intermedio(prueba, "07_prueba")
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
