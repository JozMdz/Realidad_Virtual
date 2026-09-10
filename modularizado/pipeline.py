"""Ejecuta los lotes del preprocesamiento en orden."""

from modularizado import (
    lote_01_descarga,
    lote_02_auditoria,
    lote_03_seleccion,
    lote_04_duplicados,
    lote_05_particion,
    lote_06_nulos,
    lote_07_atipicos,
    lote_08_imputacion,
    lote_09_codificacion,
    lote_10_salida,
    lote_11_validacion,
)

LOTES = [
    lote_01_descarga,
    lote_02_auditoria,
    lote_03_seleccion,
    lote_04_duplicados,
    lote_05_particion,
    lote_06_nulos,
    lote_07_atipicos,
    lote_08_imputacion,
    lote_09_codificacion,
    lote_10_salida,
    lote_11_validacion,
]


def ejecutar():
    """Corre todos los lotes, cada uno leyendo la salida del anterior."""
    for lote in LOTES:
        lote.ejecutar()


if __name__ == "__main__":
    ejecutar()
