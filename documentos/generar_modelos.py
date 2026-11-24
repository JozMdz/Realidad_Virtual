"""Genera las figuras y tablas del documento de modelos de clasificacion."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree

from modularizado import config

RAIZ = Path(__file__).resolve().parent
FIGURAS = RAIZ / "figuras"
TABLAS = RAIZ / "tablas"

PROFUNDIDAD = 5
VECINOS = 25
VALORES_K = (5, 15, 25, 51, 101, 201)


def escapar(texto):
    """Escapa los caracteres que LaTeX interpreta de forma especial."""
    return str(texto).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def cargar():
    """Lee los conjuntos de entrenamiento y prueba y separa el objetivo."""
    entrenamiento = pd.read_csv(config.RUTA_TRAIN)
    prueba = pd.read_csv(config.RUTA_TEST)
    return (entrenamiento.drop(columns=config.OBJETIVO), entrenamiento[config.OBJETIVO],
            prueba.drop(columns=config.OBJETIVO), prueba[config.OBJETIVO])


def figura_coeficientes(X, y, cantidad=12):
    """Grafica los coeficientes de mayor magnitud de la regresion logistica."""
    escalador = StandardScaler().fit(X)
    modelo = LogisticRegression(max_iter=3000, random_state=config.SEMILLA)
    modelo.fit(escalador.transform(X), y)
    pesos = pd.Series(modelo.coef_[0], index=X.columns)
    pesos = pesos.reindex(pesos.abs().sort_values(ascending=False).index)[:cantidad][::-1]

    figura, eje = plt.subplots(figsize=(6.2, 4.0))
    colores = ["#C00000" if v > 0 else "#1F4E79" for v in pesos.values]
    eje.barh([n.replace("_", " ") for n in pesos.index], pesos.values, color=colores)
    eje.axvline(0, color="black", linewidth=0.8)
    eje.set_xlabel("Coeficiente sobre variables estandarizadas")
    eje.spines[["top", "right"]].set_visible(False)
    figura.tight_layout()
    figura.savefig(FIGURAS / "coeficientes.png", dpi=200)
    plt.close(figura)
    return pesos


def figura_arbol(X, y, niveles=2):
    """Dibuja los primeros niveles del arbol de decision."""
    modelo = DecisionTreeClassifier(max_depth=PROFUNDIDAD, random_state=config.SEMILLA).fit(X, y)
    figura, eje = plt.subplots(figsize=(9.5, 5.0))
    plot_tree(modelo, max_depth=niveles, feature_names=[c.replace("_", " ") for c in X.columns],
              class_names=["sobrevive", "muere"], filled=True, rounded=True,
              impurity=False, proportion=True, fontsize=7, ax=eje)
    figura.tight_layout()
    figura.savefig(FIGURAS / "arbol.png", dpi=200)
    plt.close(figura)
    return modelo.get_depth(), modelo.get_n_leaves()


def figura_vecinos(X, y):
    """Grafica el AUC por validacion cruzada en funcion del numero de vecinos."""
    particiones = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.SEMILLA)
    marcas = []
    for k in VALORES_K:
        tubo = Pipeline([("escalado", StandardScaler()),
                         ("modelo", KNeighborsClassifier(n_neighbors=k))])
        marcas.append(cross_val_score(tubo, X, y, cv=particiones, scoring="roc_auc").mean())

    figura, eje = plt.subplots(figsize=(5.6, 3.2))
    eje.plot(VALORES_K, marcas, marker="o", color="#1F4E79")
    eje.axvline(VECINOS, color="#C00000", linestyle="--", linewidth=1)
    eje.annotate(f"k = {VECINOS}", xy=(VECINOS, min(marcas)), xytext=(VECINOS + 12, min(marcas)),
                 color="#C00000", fontsize=9)
    eje.set_xlabel("Número de vecinos (k)")
    eje.set_ylabel("AUC en validación cruzada")
    eje.spines[["top", "right"]].set_visible(False)
    figura.tight_layout()
    figura.savefig(FIGURAS / "vecinos.png", dpi=200)
    plt.close(figura)
    return list(zip(VALORES_K, marcas))


def modelos():
    """Devuelve los tres clasificadores y la referencia, con su configuracion."""
    return {
        "Regresión logística": Pipeline([
            ("escalado", StandardScaler()),
            ("modelo", LogisticRegression(max_iter=3000, random_state=config.SEMILLA))]),
        "Árbol de decisión": DecisionTreeClassifier(max_depth=PROFUNDIDAD,
                                                    random_state=config.SEMILLA),
        "Vecinos más cercanos": Pipeline([
            ("escalado", StandardScaler()),
            ("modelo", KNeighborsClassifier(n_neighbors=VECINOS))]),
        "Referencia trivial": DummyClassifier(strategy="prior"),
    }


def tabla_configuracion():
    """Tabla con los hiperparametros y el escalado de cada modelo."""
    filas = [
        ("Regresión logística", "Penalización L2, hasta 3000 iteraciones", "Sí"),
        ("Árbol de decisión", f"Profundidad máxima {PROFUNDIDAD}, criterio Gini", "No"),
        ("Vecinos más cercanos", f"{VECINOS} vecinos, distancia euclidiana", "Sí"),
        ("Referencia trivial", "Predice siempre la clase mayoritaria", "No"),
    ]
    cuerpo = "\n".join(f"{a} & {b} & {c} \\\\" for a, b, c in filas)
    (TABLAS / "configuracion.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Configuración de los modelos evaluados}\n"
        "\\label{tab:configuracion}\n\\small\n"
        "\\begin{tabular}{p{3.6cm} p{5.4cm} p{1.6cm}}\n\\toprule\n"
        "\\textbf{Modelo} & \\textbf{Parámetros} & \\textbf{Escalado} \\\\\n\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")


def tabla_resultados(X, y, Xp, yp):
    """Tabla resumida de desempeno de los cuatro modelos sobre prueba."""
    filas = []
    for nombre, modelo in modelos().items():
        modelo.fit(X, y)
        prediccion = modelo.predict(Xp)
        probabilidad = modelo.predict_proba(Xp)[:, 1]
        filas.append((nombre,
                      f"{roc_auc_score(yp, probabilidad):.3f}",
                      f"{(prediccion == yp).mean():.3f}",
                      f"{precision_score(yp, prediccion, zero_division=0):.3f}",
                      f"{recall_score(yp, prediccion, zero_division=0):.3f}"))

    cuerpo = "\n".join(f"{a} & {b} & {c} & {d} & {e} \\\\" for a, b, c, d, e in filas)
    (TABLAS / "resultados.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Desempeño de los modelos sobre el conjunto de prueba}\n"
        "\\label{tab:resultados}\n\\small\n"
        "\\begin{tabular}{p{3.8cm} r r r r}\n\\toprule\n"
        "\\textbf{Modelo} & \\textbf{AUC} & \\textbf{Exactitud} & \\textbf{Precisión} & "
        "\\textbf{Recall} \\\\\n\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")
    return filas


def main():
    """Genera todo el material del documento de modelos."""
    FIGURAS.mkdir(exist_ok=True)
    TABLAS.mkdir(exist_ok=True)
    X, y, Xp, yp = cargar()

    pesos = figura_coeficientes(X, y)
    profundidad, hojas = figura_arbol(X, y)
    curva = figura_vecinos(X, y)
    tabla_configuracion()
    resultados = tabla_resultados(X, y, Xp, yp)

    print(f"Variables de entrada: {X.shape[1]}")
    print("Coeficientes de mayor magnitud:")
    print(pesos[::-1].head(5).round(3).to_string())
    print(f"Árbol: profundidad {profundidad}, {hojas} hojas")
    print("AUC por número de vecinos:")
    for k, auc in curva:
        print(f"  k={k:>3}  {auc:.3f}")
    print("Desempeño sobre prueba:")
    for fila in resultados:
        print(f"  {fila[0]}: AUC={fila[1]} exactitud={fila[2]} "
              f"precisión={fila[3]} recall={fila[4]}")


if __name__ == "__main__":
    main()
