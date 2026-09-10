"""Modelos base sobre la salida del pipeline: punto de partida del modelado."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from modularizado import config
from modularizado.utilidades import titulo


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
    """Envuelve un modelo que necesita variables en la misma escala."""
    return Pipeline([("escalado", StandardScaler()), ("modelo", modelo)])


def definir_modelos():
    """Devuelve los modelos base a comparar."""
    return {
        "referencia": DummyClassifier(strategy="prior"),
        "logistica": escalado(LogisticRegression(max_iter=3000, random_state=config.SEMILLA)),
        "logistica balanceada": escalado(
            LogisticRegression(max_iter=3000, class_weight="balanced", random_state=config.SEMILLA)
        ),
        "arbol": DecisionTreeClassifier(max_depth=5, random_state=config.SEMILLA),
        "bosque": RandomForestClassifier(n_estimators=300, random_state=config.SEMILLA),
        "boosting": HistGradientBoostingClassifier(random_state=config.SEMILLA),
    }


def validacion_cruzada(modelos, X, y, particiones=5):
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


def detalle(modelo, X_prueba, y_prueba, nombre):
    """Imprime matriz de confusion y reporte por clase de un modelo ya entrenado."""
    prediccion = modelo.predict(X_prueba)
    matriz = pd.DataFrame(
        confusion_matrix(y_prueba, prediccion),
        index=["real: sobrevive", "real: muere"],
        columns=["predijo: sobrevive", "predijo: muere"],
    )
    print(f"Matriz de confusion de '{nombre}':")
    print(matriz.to_string())
    print()
    print(classification_report(y_prueba, prediccion, target_names=["sobrevive", "muere"], digits=3))


def ejecutar():
    """Entrena los modelos base y compara sus resultados."""
    titulo("Modelos base")

    X, y, X_prueba, y_prueba = cargar()
    print(f"Entrenamiento: {X.shape[0]} filas x {X.shape[1]} variables")
    print(f"Prueba:        {X_prueba.shape[0]} filas")
    print(f"Clase positiva (hospdead=1): {y.mean():.3f} en entrenamiento")

    modelos = definir_modelos()

    print("\nValidacion cruzada sobre entrenamiento (AUC, 5 particiones):")
    print(validacion_cruzada(modelos, X, y).to_string(index=False))

    resultados = comparar(modelos, X, y, X_prueba, y_prueba)
    print("\nResultados sobre prueba:")
    print(resultados.to_string(index=False))

    mejor = resultados.iloc[0]["modelo"]
    print()
    detalle(modelos[mejor], X_prueba, y_prueba, mejor)

    print("Siguiente paso: ajustar el umbral de decision y probar pesos de clase")
    print("para subir el recall de 'muere', que es la clase que interesa detectar.")
    return resultados


if __name__ == "__main__":
    ejecutar()
