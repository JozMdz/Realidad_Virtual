"""Lote 3: elige el objetivo y quita columnas con fuga de informacion o redundantes."""

import pandas as pd

from modularizado import config
from modularizado.utilidades import cargar_intermedio, guardar_intermedio, titulo


def evidencia_estimaciones(datos):
    """Muestra que surv2m, surv6m, prg2m y prg6m ya responden la pregunta objetivo."""
    columnas = ["surv2m", "surv6m", "prg2m", "prg6m"]
    if config.RUTA_DICCIONARIO.exists():
        diccionario = pd.read_csv(config.RUTA_DICCIONARIO)
        print("Lo que dice la ficha oficial sobre estas columnas:")
        print(diccionario[diccionario["name"].isin(columnas)].to_string(index=False))
        print()
    print("Promedio de estas columnas segun si el paciente murio en el hospital o no:")
    print(datos.groupby(config.OBJETIVO)[columnas].mean())
    print()
    print("Correlacion entre ellas (1.0 = identicas):")
    print(datos[columnas].corr().round(2))


def evidencia_dzclass(datos):
    """Cruza dzgroup con dzclass para mostrar que dzclass es derivada."""
    print("dzgroup (filas) contra dzclass (columnas):")
    print(pd.crosstab(datos["dzgroup"], datos["dzclass"]))
    print("Cada categoria de dzgroup cae siempre en una sola de dzclass: se conserva dzgroup.")


def evidencia_adls(datos):
    """Compara adls con adlsc para justificar conservar solo adlsc."""
    con_adls = datos["adls"].notna()
    coinciden = (datos.loc[con_adls, "adls"] == datos.loc[con_adls, "adlsc"]).sum()
    print(f"Filas donde adls tiene dato: {con_adls.sum()}")
    print(f"De esas, adlsc tiene exactamente el mismo valor en: {coinciden}")
    print(f"Valores faltantes en adlsc: {datos['adlsc'].isna().sum()}")
    print("adlsc es la version calibrada e imputada de adls: se conserva adlsc.")


def evidencia_severidad(datos):
    """Revisa si sps y aps son copias entre si."""
    print("Correlacion entre sps y aps:")
    print(datos[["sps", "aps"]].corr().round(2))
    print("No son identicas, se conservan ambas.")


def evidencia_posteriores(datos):
    """Muestra que dnr, los costos y avtisst reflejan lo ocurrido durante la estancia."""
    columnas = [c for c in config.COLUMNAS_POSTERIORES if c != "dnr"]
    print("Promedio segun si el paciente murio en el hospital:")
    print(datos.groupby(config.OBJETIVO)[columnas].mean().round(1))
    print()
    print("Distribucion de dnr por hospdead (% de cada columna):")
    print((pd.crosstab(datos["dnr"], datos[config.OBJETIVO], normalize="columns") * 100).round(1))


def tabla_exclusion():
    """Devuelve la lista de columnas excluidas con su motivo."""
    motivos = config.motivos_exclusion()
    return pd.DataFrame({"columna": list(motivos), "motivo": list(motivos.values())})


def aplicar_exclusion(datos):
    """Elimina las columnas excluidas del dataset."""
    return datos.drop(columns=list(config.motivos_exclusion()))


def ejecutar():
    """Deja solo las columnas utilizables para predecir hospdead."""
    titulo("Lote 3: seleccion de variables")

    datos = cargar_intermedio("02_estandarizado")

    evidencia_estimaciones(datos)
    print()
    evidencia_dzclass(datos)
    print()
    evidencia_adls(datos)
    print()
    evidencia_severidad(datos)
    print()
    evidencia_posteriores(datos)

    print()
    print(tabla_exclusion().to_string(index=False))

    columnas_antes = datos.shape[1]
    datos = aplicar_exclusion(datos)
    print(f"\nColumnas antes: {columnas_antes}")
    print(f"Columnas despues: {datos.shape[1]}")

    guardar_intermedio(datos, "03_seleccionado")
    return datos


if __name__ == "__main__":
    ejecutar()
