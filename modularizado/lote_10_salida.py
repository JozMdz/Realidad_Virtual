"""Lote 9: ordena las columnas, guarda los csv finales e imprime el resumen."""

from modularizado import config
from modularizado.utilidades import cargar_intermedio, titulo


def ordenar_columnas(datos):
    """Deja la columna objetivo al final."""
    orden = [columna for columna in datos.columns if columna != config.OBJETIVO] + [config.OBJETIVO]
    return datos[orden]


def guardar_finales(entrenamiento, prueba):
    """Escribe support2_train.csv y support2_test.csv."""
    entrenamiento.to_csv(config.RUTA_TRAIN, index=False)
    prueba.to_csv(config.RUTA_TEST, index=False)


def resumen(entrenamiento, prueba):
    """Imprime el estado final de ambos conjuntos."""
    print("Resumen del preprocesamiento")
    print("-" * 40)
    print(f"Columna objetivo: {config.OBJETIVO}")
    print(f"Columnas excluidas por fuga o redundancia: {list(config.motivos_exclusion())}")
    print()
    print(f"Entrenamiento: {entrenamiento.shape[0]} filas, {entrenamiento.shape[1]} columnas, "
          f"{entrenamiento.isna().sum().sum()} faltantes")
    print(f"Prueba:        {prueba.shape[0]} filas, {prueba.shape[1]} columnas, "
          f"{prueba.isna().sum().sum()} faltantes")
    print()
    print("Proporcion de la clase positiva (hospdead=1):")
    print(f"  Entrenamiento: {entrenamiento[config.OBJETIVO].mean():.3f}")
    print(f"  Prueba:        {prueba[config.OBJETIVO].mean():.3f}")
    print()
    print(f"Archivo de entrenamiento: {config.RUTA_TRAIN}")
    print(f"Archivo de prueba:        {config.RUTA_TEST}")


def ejecutar():
    """Genera los dos archivos listos para entrenar y evaluar."""
    titulo("Lote 10: resultado final")

    entrenamiento = ordenar_columnas(cargar_intermedio("09_entrenamiento"))
    prueba = ordenar_columnas(cargar_intermedio("09_prueba"))

    guardar_finales(entrenamiento, prueba)
    resumen(entrenamiento, prueba)
    return entrenamiento, prueba


if __name__ == "__main__":
    ejecutar()
