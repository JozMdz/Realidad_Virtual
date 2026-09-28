"""Prueba rapida de PCA: revisa si se pueden reducir las variables sin perder rendimiento."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from modularizado import config
from modularizado.utilidades import titulo

UMBRALES = [0.80, 0.90, 0.95, 0.99]
CANTIDADES = [5, 10, 15, 20, 30, 40]


def cargar():
    """Lee los csv del pipeline y separa entradas del objetivo."""
    entrenamiento = pd.read_csv(config.RUTA_TRAIN)
    prueba = pd.read_csv(config.RUTA_TEST)
    return (
        entrenamiento.drop(columns=config.OBJETIVO),
        entrenamiento[config.OBJETIVO],
        prueba.drop(columns=config.OBJETIVO),
        prueba[config.OBJETIVO],
    )


def ajustar_pca(X):
    """Escala y ajusta PCA sobre entrenamiento, devolviendo el pipeline y el PCA."""
    modelo = Pipeline([("escalado", StandardScaler()), ("pca", PCA(random_state=config.SEMILLA))])
    modelo.fit(X)
    return modelo, modelo.named_steps["pca"]


def componentes_necesarios(pca, umbrales=UMBRALES):
    """Cuenta cuantos componentes hacen falta para cada porcentaje de varianza."""
    acumulada = pca.explained_variance_ratio_.cumsum()
    filas = [(f"{int(u * 100)}%", int((acumulada < u).sum() + 1)) for u in umbrales]
    return pd.DataFrame(filas, columns=["varianza_explicada", "componentes"])


def varianza_primeros(pca, cantidad=10):
    """Muestra cuanta varianza aporta cada uno de los primeros componentes."""
    proporcion = pca.explained_variance_ratio_[:cantidad]
    return pd.DataFrame({
        "componente": [f"PC{i + 1}" for i in range(len(proporcion))],
        "varianza": proporcion.round(3),
        "acumulada": proporcion.cumsum().round(3),
    })


def variables_pesadas(pca, nombres, componente=0, cantidad=6):
    """Lista las variables con mas peso en un componente."""
    pesos = pd.Series(pca.components_[componente], index=nombres).abs().sort_values(ascending=False)
    return pesos.head(cantidad).round(3)


def auc_logistica(X, y, X_prueba, y_prueba, reductor=None):
    """Entrena una logistica, opcionalmente sobre variables reducidas, y devuelve el AUC."""
    pasos = [("escalado", StandardScaler())]
    if reductor is not None:
        pasos.append(("reductor", reductor))
    pasos.append(("modelo", LogisticRegression(max_iter=3000, random_state=config.SEMILLA)))
    modelo = Pipeline(pasos).fit(X, y)
    return round(roc_auc_score(y_prueba, modelo.predict_proba(X_prueba)[:, 1]), 4)


def comparar(X, y, X_prueba, y_prueba, cantidades=CANTIDADES):
    """Compara el AUC usando todas las variables, PCA y seleccion directa."""
    completo = auc_logistica(X, y, X_prueba, y_prueba)
    filas = [{"variables": X.shape[1], "metodo": "todas", "auc": completo, "diferencia": 0.0}]

    for cantidad in cantidades:
        if cantidad >= X.shape[1]:
            continue
        for nombre, reductor in [
            ("pca", PCA(n_components=cantidad, random_state=config.SEMILLA)),
            ("mejores k", SelectKBest(f_classif, k=cantidad)),
        ]:
            auc = auc_logistica(X, y, X_prueba, y_prueba, reductor)
            filas.append({
                "variables": cantidad,
                "metodo": nombre,
                "auc": auc,
                "diferencia": round(auc - completo, 4),
            })

    return pd.DataFrame(filas)


def ejecutar():
    """Corre la prueba de reduccion de variables e informa los resultados."""
    titulo("Prueba de PCA")

    X, y, X_prueba, y_prueba = cargar()
    print(f"Variables de entrada: {X.shape[1]}")

    _, pca = ajustar_pca(X)

    print("\nVarianza de los primeros componentes:")
    print(varianza_primeros(pca).to_string(index=False))

    print("\nComponentes necesarios por nivel de varianza:")
    print(componentes_necesarios(pca).to_string(index=False))

    print("\nVariables con mas peso en PC1:")
    print(variables_pesadas(pca, X.columns).to_string())

    print("\nAUC de una logistica segun cuantas variables se usen:")
    print(comparar(X, y, X_prueba, y_prueba).to_string(index=False))

    print("\nPCA mezcla columnas continuas con columnas 0/1 (dummies y banderas),")
    print("donde la varianza no significa lo mismo: leer el resultado con esa reserva.")
    return pca


if __name__ == "__main__":
    ejecutar()
