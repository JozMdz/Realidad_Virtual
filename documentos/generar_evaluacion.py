"""Genera las figuras y tablas del documento de evaluacion."""

import sys
from itertools import combinations
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import binomtest, friedmanchisquare, wilcoxon
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from modularizado import config
from documentos.generar_modelos import cargar, modelos

RAIZ = Path(__file__).resolve().parent
FIGURAS = RAIZ / "figuras"
TABLAS = RAIZ / "tablas"
PARTICIONES = 10
COLORES = {"Regresión logística": "#1F4E79", "Árbol de decisión": "#C00000",
           "Vecinos más cercanos": "#7F7F7F"}


def escribir_tabla(archivo, caption, etiqueta, columnas, cabecera, filas, extra=""):
    """Escribe una tabla LaTeX con el formato comun de los documentos."""
    cuerpo = "\n".join(" & ".join(str(c) for c in fila) + r" \\" for fila in filas)
    contenido = (
        "\\begin{table}[H]\n\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{etiqueta}}}\n\\small\n"
        f"\\begin{{tabular}}{{{columnas}}}\n"
        "\\toprule\n"
        + " & ".join(f"\\textbf{{{c}}}" for c in cabecera) + " \\\\\n"
        "\\midrule\n"
        + cuerpo + "\n"
        + extra
        + "\\bottomrule\n\\end{tabular}\n\\end{table}\n")
    (TABLAS / archivo).write_text(contenido, encoding="utf-8")


def entrenados(X, y):
    """Entrena los modelos y los devuelve ajustados."""
    ajustados = {}
    for nombre, modelo in modelos().items():
        modelo.fit(X, y)
        ajustados[nombre] = modelo
    return ajustados


def tabla_metricas(ajustados, Xp, yp):
    """Tabla completa de metricas sobre el conjunto de prueba."""
    filas = []
    for nombre, modelo in ajustados.items():
        pred = modelo.predict(Xp)
        prob = modelo.predict_proba(Xp)[:, 1]
        filas.append((nombre, f"{roc_auc_score(yp, prob):.3f}", f"{(pred == yp).mean():.3f}",
                      f"{precision_score(yp, pred, zero_division=0):.3f}",
                      f"{recall_score(yp, pred, zero_division=0):.3f}",
                      f"{f1_score(yp, pred, zero_division=0):.3f}"))
    escribir_tabla("metricas.tex",
                   "Métricas sobre el conjunto de prueba. Precisión, recall y F1 corresponden a "
                   "la clase \\textit{fallece}.",
                   "tab:metricas", "p{3.6cm} r r r r r",
                   ["Modelo", "AUC", "Exactitud", "Precisión", "Recall", "F1"], filas)
    return filas


def tabla_confusion(ajustados, Xp, yp):
    """Matrices de confusion de los tres clasificadores."""
    filas = []
    for nombre, modelo in ajustados.items():
        if nombre == "Referencia trivial":
            continue
        vn, fp, fn, vp = confusion_matrix(yp, modelo.predict(Xp)).ravel()
        filas.append((nombre, vn, fp, fn, vp))
    escribir_tabla("confusion.tex",
                   "Matrices de confusión sobre el conjunto de prueba. VN y VP son los aciertos; "
                   "FP las falsas alarmas y FN los fallecimientos no detectados.",
                   "tab:confusion", "p{3.6cm} r r r r",
                   ["Modelo", "VN", "FP", "FN", "VP"], filas)
    return filas


def figura_roc(ajustados, Xp, yp):
    """Curvas ROC de los tres clasificadores."""
    figura, eje = plt.subplots(figsize=(5.4, 4.4))
    for nombre, modelo in ajustados.items():
        if nombre == "Referencia trivial":
            continue
        prob = modelo.predict_proba(Xp)[:, 1]
        fpr, tpr, _ = roc_curve(yp, prob)
        eje.plot(fpr, tpr, color=COLORES[nombre],
                 label=f"{nombre} ({roc_auc_score(yp, prob):.3f})")
    eje.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="Azar (0.500)")
    eje.set_xlabel("Tasa de falsos positivos")
    eje.set_ylabel("Tasa de verdaderos positivos")
    eje.legend(loc="lower right", fontsize=8)
    eje.spines[["top", "right"]].set_visible(False)
    figura.tight_layout()
    figura.savefig(FIGURAS / "roc.png", dpi=200)
    plt.close(figura)


def auc_por_particion(X, y):
    """AUC de cada modelo en cada particion de validacion cruzada."""
    kfold = StratifiedKFold(n_splits=PARTICIONES, shuffle=True, random_state=config.SEMILLA)
    return pd.DataFrame({n: cross_val_score(m, X, y, cv=kfold, scoring="roc_auc")
                         for n, m in modelos().items() if n != "Referencia trivial"})


def tabla_particiones(marcas):
    """Tabla del AUC por particion con promedio y desviacion."""
    filas = [[i + 1] + [f"{marcas[c].iloc[i]:.3f}" for c in marcas] for i in range(len(marcas))]
    rangos = marcas.rank(axis=1, ascending=False).mean()
    extra = ("\\midrule\n"
             + "Promedio & " + " & ".join(f"\\textbf{{{marcas[c].mean():.3f}}}" for c in marcas)
             + " \\\\\n"
             + "Desviación & " + " & ".join(f"{marcas[c].std():.3f}" for c in marcas) + " \\\\\n"
             + "Rango promedio & " + " & ".join(f"{rangos[c]:.1f}" for c in marcas) + " \\\\\n")
    escribir_tabla("particiones.tex",
                   "AUC obtenido por cada modelo en las diez particiones de validación cruzada",
                   "tab:particiones", "l r r r",
                   ["Partición"] + list(marcas.columns), filas, extra)


def tabla_pruebas(marcas, ajustados, Xp, yp):
    """Resultados de Wilcoxon y McNemar por pares."""
    chi2, p_friedman = friedmanchisquare(*[marcas[c] for c in marcas])
    aciertos = {n: m.predict(Xp) == yp for n, m in ajustados.items() if n != "Referencia trivial"}

    filas = []
    for a, b in combinations(marcas.columns, 2):
        _, p_w = wilcoxon(marcas[a], marcas[b])
        p_w = min(p_w * 3, 1.0)
        solo_a = int((aciertos[a] & ~aciertos[b]).sum())
        solo_b = int((~aciertos[a] & aciertos[b]).sum())
        p_m = min(binomtest(solo_a, solo_a + solo_b, 0.5).pvalue * 3, 1.0)
        filas.append((f"{a} vs. {b}", f"{p_w:.4f}" + ("*" if p_w < 0.05 else ""),
                      f"{solo_a} / {solo_b}", f"{p_m:.4f}" + ("*" if p_m < 0.05 else "")))

    (TABLAS / "friedman.tex").write_text(
        f"$\\chi^2 = {chi2:.3f}$ con $p = {p_friedman:.4f}$", encoding="utf-8")

    escribir_tabla("pruebas.tex",
                   "Comparación por pares. Los valores $p$ incluyen corrección de Bonferroni "
                   "para tres comparaciones; el asterisco indica significancia al 5\\%.",
                   "tab:pruebas", "p{5.2cm} r c r",
                   ["Comparación", "Wilcoxon", "Aciertos exclusivos", "McNemar"], filas)
    return chi2, p_friedman, marcas.rank(axis=1, ascending=False).mean()


def tabla_balanceo(X, y, Xp, yp):
    """Compara la logistica con y sin ponderacion de clases."""
    filas = []
    for etiqueta, peso in [("Sin ponderación", None), ("Con ponderación balanceada", "balanced")]:
        modelo = Pipeline([("escalado", StandardScaler()),
                           ("modelo", LogisticRegression(max_iter=3000, class_weight=peso,
                                                         random_state=config.SEMILLA))]).fit(X, y)
        pred = modelo.predict(Xp)
        prob = modelo.predict_proba(Xp)[:, 1]
        filas.append((etiqueta, f"{roc_auc_score(yp, prob):.3f}", f"{(pred == yp).mean():.3f}",
                      f"{precision_score(yp, pred):.3f}", f"{recall_score(yp, pred):.3f}"))
    escribir_tabla("balanceo.tex",
                   "Efecto de la ponderación de clases sobre la regresión logística",
                   "tab:balanceo", "p{5cm} r r r r",
                   ["Configuración", "AUC", "Exactitud", "Precisión", "Recall"], filas)
    return filas


def main():
    """Genera todo el material del documento de evaluacion."""
    FIGURAS.mkdir(exist_ok=True)
    TABLAS.mkdir(exist_ok=True)
    X, y, Xp, yp = cargar()
    ajustados = entrenados(X, y)

    metricas = tabla_metricas(ajustados, Xp, yp)
    confusion = tabla_confusion(ajustados, Xp, yp)
    figura_roc(ajustados, Xp, yp)
    marcas = auc_por_particion(X, y)
    tabla_particiones(marcas)
    chi2, p_friedman, rangos = tabla_pruebas(marcas, ajustados, Xp, yp)
    balanceo = tabla_balanceo(X, y, Xp, yp)

    print("Métricas sobre prueba:")
    for f in metricas:
        print(f"  {f[0]}: AUC={f[1]} exact={f[2]} prec={f[3]} recall={f[4]} F1={f[5]}")
    print("Matrices de confusión (VN, FP, FN, VP):")
    for f in confusion:
        print(f"  {f[0]}: {f[1]}, {f[2]}, {f[3]}, {f[4]}")
    print(f"\nFriedman: chi2={chi2:.3f} p={p_friedman:.4f}")
    print("Rango promedio:")
    print(rangos.round(2).to_string())
    print("\nPonderación de clases:")
    for f in balanceo:
        print(f"  {f[0]}: AUC={f[1]} exact={f[2]} prec={f[3]} recall={f[4]}")


if __name__ == "__main__":
    main()
