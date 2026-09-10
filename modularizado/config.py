"""Rutas y parametros compartidos por todos los lotes."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DIR_DATOS = RAIZ.parent / "support"
DIR_INTERMEDIOS = RAIZ / "intermedios"

RUTA_CSV = DIR_DATOS / "support2.csv"
RUTA_DICCIONARIO = DIR_DATOS / "diccionario_variables.csv"
RUTA_ESTADISTICAS = DIR_DATOS / "estadisticas_descriptivas.csv"
RUTA_TRAIN = DIR_DATOS / "support2_train.csv"
RUTA_TEST = DIR_DATOS / "support2_test.csv"

ID_REPOSITORIO_UCI = 880
VALORES_NULOS = ["?", "NA", "N/A", "", "null"]

OBJETIVO = "hospdead"

COLUMNAS_EXCLUIDAS = {
    "death": "otra variable de muerte, casi la misma pregunta que hospdead",
    "sfdm2": "otra variable objetivo, medida despues del alta",
    "surv2m": "estimacion de supervivencia calculada por el modelo SUPPORT",
    "surv6m": "estimacion de supervivencia calculada por el modelo SUPPORT",
    "prg2m": "estimacion de supervivencia del medico tratante",
    "prg6m": "estimacion de supervivencia del medico tratante",
    "dzclass": "redundante: es un resumen derivado de dzgroup",
    "adls": "redundante: adlsc ya contiene la misma informacion, sin huecos",
}

COLUMNAS_POSTERIORES = {
    "dnr": "la orden de no reanimar suele firmarse cuando el paciente ya esta empeorando",
    "dnrday": "dia de la orden de no reanimar: misma razon que dnr",
    "charges": "cobro total de la hospitalizacion, se conoce recien al dar de alta",
    "totcst": "costo total de la hospitalizacion, se conoce recien al dar de alta",
    "totmcst": "costo total detallado, se conoce recien al dar de alta",
    "avtisst": "promedio de intervenciones de los dias 3 al 25, cubre toda la estancia",
}

INCLUIR_POSTERIORES = False

SEMILLA = 42
FRACCION_ENTRENAMIENTO = 0.8
LIMITE_FALTANTES = 50.0
FACTOR_RIC = 1.5


def motivos_exclusion():
    """Devuelve el diccionario de columnas excluidas segun la configuracion vigente."""
    motivos = dict(COLUMNAS_EXCLUIDAS)
    if not INCLUIR_POSTERIORES:
        motivos.update(COLUMNAS_POSTERIORES)
    return motivos
