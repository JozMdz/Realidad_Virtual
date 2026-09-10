"""Ejecuta los lotes del preprocesamiento en orden."""

from modularizado import (
    lote_01_descarga,
    lote_02_auditoria,
    lote_03_seleccion,
    lote_04_duplicados,
    lote_05_particion,
    lote_06_faltantes,
    lote_07_atipicos,
    lote_08_codificacion,
    lote_09_salida,
)

LOTES = [
    lote_01_descarga,
    lote_02_auditoria,
    lote_03_seleccion,
    lote_04_duplicados,
    lote_05_particion,
    lote_06_faltantes,
    lote_07_atipicos,
    lote_08_codificacion,
    lote_09_salida,
]


def ejecutar():
    """Corre todos los lotes, cada uno leyendo la salida del anterior."""
    for lote in LOTES:
        lote.ejecutar()


if __name__ == "__main__":
    ejecutar()
