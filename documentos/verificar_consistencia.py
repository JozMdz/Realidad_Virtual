"""Comprueba que las tablas de los documentos coincidan con la salida del codigo del proyecto.

Las pruebas estadisticas se calculan en dos lugares: modelado_secuencial.py, que es el
codigo del proyecto, y generar_evaluacion.py, que produce las tablas. Este script ejecuta
el primero y contrasta su salida contra las tablas generadas, de modo que una divergencia
entre ambas implementaciones se detecte en lugar de pasar al documento.
"""

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
TABLAS = RAIZ / "tablas"


def salida_del_proyecto():
    """Ejecuta el modelado secuencial y devuelve su salida."""
    resultado = subprocess.run(
        [sys.executable, "-m", "modularizado.modelado_secuencial"],
        cwd=RAIZ.parent, capture_output=True, text=True, check=True)
    return resultado.stdout


def valores(texto, patron):
    """Extrae los grupos de todas las coincidencias de un patron."""
    return re.findall(patron, texto)


def comprobar(nombre, esperado, obtenido, fallos):
    """Registra el resultado de una comprobacion.

    Una extraccion vacia se trata como fallo: comparar dos listas vacias daria por buena
    una comprobacion que en realidad no comparo nada.
    """
    if not esperado or not obtenido:
        print(f"  FALLA  {nombre}: no se pudo extraer el valor "
              f"(codigo: {len(esperado)}, tabla: {len(obtenido)})")
        fallos.append(nombre)
        return
    if esperado == obtenido:
        print(f"  OK     {nombre}: {obtenido}")
    else:
        print(f"  FALLA  {nombre}: el codigo dice {esperado}, la tabla dice {obtenido}")
        fallos.append(nombre)


def main():
    """Contrasta las tablas generadas contra la salida del modelado secuencial."""
    salida = salida_del_proyecto()
    pruebas = (TABLAS / "pruebas.tex").read_text(encoding="utf-8")
    metricas = (TABLAS / "metricas.tex").read_text(encoding="utf-8")
    fallos = []

    print("Comparando las tablas con la salida de modelado_secuencial.py\n")

    # Wilcoxon: tres valores p en el mismo orden en ambas fuentes
    p_codigo = valores(salida, r"vs\s+\w+\s+p=([\d.]+)")
    p_tabla = valores(pruebas, r"&\s*([\d.]+)\*?\s*&\s*\d+\s*/")
    comprobar("Wilcoxon (p corregidos)", p_codigo, p_tabla, fallos)

    # McNemar: conteos de aciertos exclusivos y sus valores p
    mc_codigo = valores(salida, r"solo \w+ acierta=\s*(\d+)\s+solo \w+ acierta=\s*(\d+)\s+p=([\d.]+)")
    mc_tabla = [(a, b, p) for a, b, p in
                valores(pruebas, r"&\s*(\d+)\s*/\s*(\d+)\s*&\s*([\d.]+)\*?\s*\\\\")]
    comprobar("McNemar (conteos y p)", mc_codigo, mc_tabla, fallos)

    # AUC sobre prueba de los tres modelos
    auc_codigo = re.findall(r"^\s*(?:logistica|arbol|vecinos)\s+(0\.\d{3})", salida, re.M)
    # Una fila por linea: se toma solo la primera columna numerica, que es el AUC.
    auc_tabla = [m.group(1) for linea in metricas.splitlines()
                 if (m := re.match(r"^[^&]+&\s*(0\.\d{3})\s*&", linea))
                 and "Referencia" not in linea]
    comprobar("AUC sobre prueba", auc_codigo, auc_tabla, fallos)

    print()
    if fallos:
        print(f"{len(fallos)} comprobacion(es) fallaron: las tablas no reflejan el codigo.")
        sys.exit(1)
    print("Las tablas coinciden con la salida del codigo del proyecto.")


if __name__ == "__main__":
    main()
