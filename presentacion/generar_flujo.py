# -*- coding: utf-8 -*-
"""Genera el diagrama de las once etapas del pipeline, dispuesto en rejilla."""
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrow

ROJO = "#D7141A"
GRIS_T = "#8A8A8A"
GRIS_B = "#C9C9C9"

ETAPAS = [
    "Descarga del conjunto de datos",
    "Auditoría inicial y estandarización de nombres",
    "Selección de variables: fuga y redundancia",
    "Eliminación de registros duplicados",
    "Partición estratificada 80/20",
    "Columnas con exceso de valores ausentes",
    "Acotamiento de valores atípicos",
    "Imputación de valores faltantes",
    "Codificación de variables categóricas",
    "Ordenamiento y escritura de los archivos",
    "Validación del resultado",
]
DESTACADAS = {2: "Determina qué información es admisible",
              4: "Desde aquí todo se calcula sólo con el 80 %"}

COLS, FILAS = 4, 3
CAJA_W, CAJA_H = 3.15, 1.35
SEP_X, SEP_Y = 0.55, 1.05
MARGEN = 0.30
ANCHO = MARGEN * 2 + COLS * CAJA_W + (COLS - 1) * SEP_X
ALTO = MARGEN * 2 + FILAS * CAJA_H + (FILAS - 1) * SEP_Y

fig, ax = plt.subplots(figsize=(ANCHO / 1.6, ALTO / 1.6), dpi=260)
ax.set_xlim(0, ANCHO); ax.set_ylim(0, ALTO); ax.axis("off")


def pos(i):
    """Recorrido en serpentina: la fila par avanza a la derecha y la impar a la izquierda."""
    f, k = divmod(i, COLS)
    c = k if f % 2 == 0 else COLS - 1 - k
    x = MARGEN + c * (CAJA_W + SEP_X)
    y = ALTO - MARGEN - (f + 1) * CAJA_H - f * SEP_Y
    return x, y, f, k


for i, texto in enumerate(ETAPAS):
    x, y, f, k = pos(i)
    der = (f % 2 == 0)
    destacada = i in DESTACADAS
    ax.add_patch(FancyBboxPatch(
        (x, y), CAJA_W, CAJA_H,
        boxstyle="round,pad=0,rounding_size=0.14",
        linewidth=1.8 if destacada else 1.0,
        edgecolor=ROJO if destacada else GRIS_B,
        facecolor="#FDF2F2" if destacada else "#F7F7F7"))
    ax.text(x + 0.26, y + CAJA_H - 0.26, str(i + 1), ha="center", va="center",
            fontsize=12, fontweight="bold",
            color=ROJO if destacada else "#B0B0B0")
    ax.text(x + CAJA_W / 2, y + CAJA_H / 2 - 0.08,
            "\n".join(textwrap.wrap(texto, 21)),
            ha="center", va="center", fontsize=9.8, color="#1A1A1A",
            linespacing=1.3)
    if destacada:
        ax.text(x + CAJA_W / 2, y - 0.17,
                "\n".join(textwrap.wrap(DESTACADAS[i], 24)),
                ha="center", va="top", fontsize=9, color=ROJO, style="italic",
                linespacing=1.3)
    if i < len(ETAPAS) - 1:
        if k < COLS - 1:
            x0 = x + CAJA_W + 0.08 if der else x - 0.08
            ax.add_patch(FancyArrow(x0, y + CAJA_H / 2,
                                    (SEP_X - 0.24) * (1 if der else -1), 0,
                                    width=0.016, head_width=0.15, head_length=0.15,
                                    length_includes_head=True, color=GRIS_T))
        else:
            ax.add_patch(FancyArrow(x + CAJA_W / 2, y - 0.10, 0, -(SEP_Y - 0.28),
                                    width=0.016, head_width=0.15, head_length=0.15,
                                    length_includes_head=True, color=GRIS_T))

import os
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "documentos", "figuras", "flujo.png")
fig.savefig(SALIDA,
            dpi=260, bbox_inches="tight", pad_inches=0.06, facecolor="white")
print("flujo.png")
