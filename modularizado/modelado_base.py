"""Modelos base sobre la salida del pipeline: tres clasificadores sencillos, comparados."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from modularizado import config
from modularizado.utilidades import titulo

PROFUNDIDAD_ARBOL = 5
VECINOS = 25
PARTICIONES = 5


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


def escalado(modelo):
    """Envuelve un modelo que compara magnitudes y necesita todo en la misma escala."""
    return Pipeline([("escalado", StandardScaler()), ("modelo", modelo)])


def definir_modelos():
    """Devuelve los tres clasificadores a comparar, mas una referencia tonta."""
    return {
        "referencia": DummyClassifier(strategy="prior"),
        "logistica": escalado(LogisticRegression(max_iter=3000, random_state=config.SEMILLA)),
        "arbol": DecisionTreeClassifier(
            max_depth=PROFUNDIDAD_ARBOL, random_state=config.SEMILLA
        ),
        "vecinos": escalado(KNeighborsClassifier(n_neighbors=VECINOS)),
    }


def describir_modelos():
    """Explica de que familia es cada clasificador y si necesita escalado."""
    return pd.DataFrame([
        ("referencia", "contesta siempre la clase mayoritaria", "no", "-"),
        ("logistica", "frontera lineal entre las dos clases", "si", "max_iter=3000"),
        ("arbol", "reglas de corte sobre una variable a la vez", "no", f"max_depth={PROFUNDIDAD_ARBOL}"),
        ("vecinos", "vota entre los pacientes mas parecidos", "si", f"n_neighbors={VECINOS}"),
    ], columns=["modelo", "como decide", "necesita escalado", "ajuste"])


def validacion_cruzada(modelos, X, y, particiones=PARTICIONES):
    """Compara los modelos por AUC con validacion cruzada sobre entrenamiento."""
    kfold = StratifiedKFold(n_splits=particiones, shuffle=True, random_state=config.SEMILLA)
    filas = []
    for nombre, modelo in modelos.items():
        marcas = cross_val_score(modelo, X, y, cv=kfold, scoring="roc_auc")
        filas.append((nombre, round(marcas.mean(), 3), round(marcas.std(), 3)))
    return pd.DataFrame(filas, columns=["modelo", "auc_promedio", "desviacion"]).sort_values(
        "auc_promedio", ascending=False
    )


def evaluar(modelo, X, y, X_prueba, y_prueba):
    """Entrena un modelo y devuelve sus metricas sobre prueba."""
    modelo.fit(X, y)
    prediccion = modelo.predict(X_prueba)
    probabilidad = modelo.predict_proba(X_prueba)[:, 1]
    return {
        "auc": round(roc_auc_score(y_prueba, probabilidad), 3),
        "exactitud": round((prediccion == y_prueba).mean(), 3),
        "precision_muere": round(precision_score(y_prueba, prediccion, zero_division=0), 3),
        "recall_muere": round(recall_score(y_prueba, prediccion, zero_division=0), 3),
        "f1_muere": round(f1_score(y_prueba, prediccion, zero_division=0), 3),
    }


def comparar(modelos, X, y, X_prueba, y_prueba):
    """Arma la tabla de metricas de prueba de todos los modelos."""
    filas = []
    for nombre, modelo in modelos.items():
        filas.append({"modelo": nombre, **evaluar(modelo, X, y, X_prueba, y_prueba)})
    return pd.DataFrame(filas).sort_values("auc", ascending=False)


def matriz(modelo, X_prueba, y_prueba):
    """Devuelve la matriz de confusion de un modelo ya entrenado."""
    return pd.DataFrame(
        confusion_matrix(y_prueba, modelo.predict(X_prueba)),
        index=["real: sobrevive", "real: muere"],
        columns=["predijo: sobrevive", "predijo: muere"],
    )


def ejecutar():
    """Entrena los tres clasificadores sencillos y compara sus resultados."""
    titulo("Modelos base: tres clasificadores")

    X, y, X_prueba, y_prueba = cargar()
    print(f"Entrenamiento: {X.shape[0]} filas x {X.shape[1]} variables")
    print(f"Prueba:        {X_prueba.shape[0]} filas")
    print(f"Clase positiva (hospdead=1): {y.mean():.3f} en entrenamiento")

    modelos = definir_modelos()

    print("\nQue hace cada uno:")
    print(describir_modelos().to_string(index=False))

    print(f"\nValidacion cruzada sobre entrenamiento (AUC, {PARTICIONES} particiones):")
    print(validacion_cruzada(modelos, X, y).to_string(index=False))

    resultados = comparar(modelos, X, y, X_prueba, y_prueba)
    print("\nResultados sobre prueba:")
    print(resultados.to_string(index=False))

    print("\nMatriz de confusion de cada clasificador:")
    for nombre in modelos:
        if nombre == "referencia":
            continue
        print(f"\n{nombre}:")
        print(matriz(modelos[nombre], X_prueba, y_prueba).to_string())

    print("\nLa referencia contesta siempre 'sobrevive' y ya acierta el "
          f"{(1 - y_prueba.mean()) * 100:.1f}%: la exactitud sola no distingue modelos.")
    print("Siguiente paso: ajustar el umbral de decision y probar pesos de clase")
    print("para subir el recall de 'muere', que es la clase que interesa detectar.")
    return resultados


if __name__ == "__main__":
    ejecutar()
