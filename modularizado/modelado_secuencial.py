"""Mismo modelado que modelado_base.py, pero secuencial y sin funciones.

Pensado para leerse o explicarse de corrido, de arriba a abajo. Las rutas y los
parametros se repiten aqui a proposito, para no tener que abrir config.py.
"""

from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
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

DIR_DATOS = Path(__file__).resolve().parent.parent / "support"
OBJETIVO = "hospdead"
SEMILLA = 42
PROFUNDIDAD_ARBOL = 5
VECINOS = 25

resultados = []


# 1. Particion 80/20
# El pipeline ya la dejo hecha, estratificada por hospdead y con semilla 42.
entrenamiento = pd.read_csv(DIR_DATOS / "support2_train.csv")
prueba = pd.read_csv(DIR_DATOS / "support2_test.csv")

print("1. PARTICION 80/20")
print(f"   Entrenamiento: {entrenamiento.shape[0]} filas x {entrenamiento.shape[1]} columnas")
print(f"   Prueba:        {prueba.shape[0]} filas x {prueba.shape[1]} columnas")
print(f"   {OBJETIVO}=1 en entrenamiento: {entrenamiento[OBJETIVO].mean():.3f}")
print(f"   {OBJETIVO}=1 en prueba:        {prueba[OBJETIVO].mean():.3f}")


# 2. Separar entradas y objetivo
X_entrenamiento = entrenamiento.drop(columns=OBJETIVO)
y_entrenamiento = entrenamiento[OBJETIVO]
X_prueba = prueba.drop(columns=OBJETIVO)
y_prueba = prueba[OBJETIVO]

print("\n2. ENTRADAS Y OBJETIVO")
print(f"   Variables de entrada: {X_entrenamiento.shape[1]}")
print(f"   Objetivo: {OBJETIVO}")


# 3. Escalado
# Se ajusta SOLO con entrenamiento y se aplica a los dos, para no filtrar informacion de prueba.
escalador = StandardScaler()
X_entrenamiento_escalado = escalador.fit_transform(X_entrenamiento)
X_prueba_escalado = escalador.transform(X_prueba)

print("\n3. ESCALADO")
print(f"   Media de las variables escaladas: {X_entrenamiento_escalado.mean():.3f}")
print(f"   Desviacion de las variables escaladas: {X_entrenamiento_escalado.std():.3f}")


# 4. Regresion logistica (usa los datos escalados)
logistica = LogisticRegression(max_iter=3000, random_state=SEMILLA)
logistica.fit(X_entrenamiento_escalado, y_entrenamiento)

prediccion = logistica.predict(X_prueba_escalado)
probabilidad = logistica.predict_proba(X_prueba_escalado)[:, 1]

print("\n4. REGRESION LOGISTICA")
print(f"   AUC:       {roc_auc_score(y_prueba, probabilidad):.3f}")
print(f"   Exactitud: {(prediccion == y_prueba).mean():.3f}")
print(classification_report(y_prueba, prediccion, target_names=["sobrevive", "muere"], digits=3))

resultados.append({
    "modelo": "logistica",
    "auc": round(roc_auc_score(y_prueba, probabilidad), 3),
    "exactitud": round((prediccion == y_prueba).mean(), 3),
    "precision_muere": round(precision_score(y_prueba, prediccion), 3),
    "recall_muere": round(recall_score(y_prueba, prediccion), 3),
    "f1_muere": round(f1_score(y_prueba, prediccion), 3),
})


# 5. Arbol de decision (usa los datos SIN escalar: parte por umbrales)
arbol = DecisionTreeClassifier(max_depth=PROFUNDIDAD_ARBOL, random_state=SEMILLA)
arbol.fit(X_entrenamiento, y_entrenamiento)

prediccion = arbol.predict(X_prueba)
probabilidad = arbol.predict_proba(X_prueba)[:, 1]

print("\n5. ARBOL DE DECISION")
print(f"   AUC:       {roc_auc_score(y_prueba, probabilidad):.3f}")
print(f"   Exactitud: {(prediccion == y_prueba).mean():.3f}")
print(classification_report(y_prueba, prediccion, target_names=["sobrevive", "muere"], digits=3))

resultados.append({
    "modelo": "arbol",
    "auc": round(roc_auc_score(y_prueba, probabilidad), 3),
    "exactitud": round((prediccion == y_prueba).mean(), 3),
    "precision_muere": round(precision_score(y_prueba, prediccion), 3),
    "recall_muere": round(recall_score(y_prueba, prediccion), 3),
    "f1_muere": round(f1_score(y_prueba, prediccion), 3),
})


# 6. Vecinos mas cercanos (usa los datos escalados: mide distancias)
# El k se elige con validacion cruzada SOBRE ENTRENAMIENTO, nunca mirando prueba.
# Va en un Pipeline para que el escalador se reajuste en cada particion.
print("\n6. VECINOS MAS CERCANOS")
print("   Busqueda de k (validacion cruzada sobre entrenamiento):")
particiones = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
for k in (5, 15, 25, 51, 101, 201):
    tubo = Pipeline([("escalado", StandardScaler()), ("modelo", KNeighborsClassifier(n_neighbors=k))])
    auc_k = cross_val_score(tubo, X_entrenamiento, y_entrenamiento,
                            cv=particiones, scoring="roc_auc").mean()
    print(f"     k={k:>3}  AUC={auc_k:.3f}")

vecinos = KNeighborsClassifier(n_neighbors=VECINOS)
vecinos.fit(X_entrenamiento_escalado, y_entrenamiento)

prediccion = vecinos.predict(X_prueba_escalado)
probabilidad = vecinos.predict_proba(X_prueba_escalado)[:, 1]

print(f"\n   Con k={VECINOS}:")
print(f"   AUC:       {roc_auc_score(y_prueba, probabilidad):.3f}")
print(f"   Exactitud: {(prediccion == y_prueba).mean():.3f}")
print(classification_report(y_prueba, prediccion, target_names=["sobrevive", "muere"], digits=3))

resultados.append({
    "modelo": "vecinos",
    "auc": round(roc_auc_score(y_prueba, probabilidad), 3),
    "exactitud": round((prediccion == y_prueba).mean(), 3),
    "precision_muere": round(precision_score(y_prueba, prediccion), 3),
    "recall_muere": round(recall_score(y_prueba, prediccion), 3),
    "f1_muere": round(f1_score(y_prueba, prediccion), 3),
})


# 7. Comparacion de los tres
comparacion = pd.DataFrame(resultados).sort_values("auc", ascending=False)

print("\n7. COMPARACION")
print(comparacion.to_string(index=False))
print(f"\n   Mejor por AUC: {comparacion.iloc[0]['modelo']}")
print(f"   Referencia: contestar siempre 'sobrevive' acierta {1 - y_prueba.mean():.3f}")
