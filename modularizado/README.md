# modularizado

Version en lotes `.py` del preprocesamiento que en el repositorio esta en `support/notebook.ipynb`.
Cada lote es un modulo ejecutable por separado: lee el archivo intermedio que dejo el lote
anterior en `intermedios/` y escribe el suyo.

- [PRESENTACION.md](PRESENTACION.md): version breve, para exponer o leer de corrido.
- [PIPELINE.md](PIPELINE.md): narracion completa, auditoria y correcciones respecto al notebook.

## Ejecucion

Desde la raiz del repositorio:

```bash
pip install -r modularizado/requirements.txt

python -m modularizado.pipeline             # todos los lotes en orden
python -m modularizado.lote_07_atipicos     # un lote suelto
python -m modularizado.modelado_base        # modelos base, version modular
python -m modularizado.modelado_secuencial  # los mismos modelos, de corrido
```

El pipeline solo necesita `pandas`. `scikit-learn` es para el modelado y `ucimlrepo`
solo si se quiere volver a descargar el csv desde UCI: sin conexion el lote 1 reutiliza
`support/support2.csv`.

## Lotes

| Lote | Archivo | Que hace |
|---|---|---|
| 1 | `lote_01_descarga.py` | Descarga el dataset de UCI o reutiliza el csv local |
| 2 | `lote_02_auditoria.py` | Estandariza nombres, audita nulos y guarda estadisticas descriptivas |
| 3 | `lote_03_seleccion.py` | Excluye columnas con fuga de informacion, redundantes y posteriores al ingreso |
| 4 | `lote_04_duplicados.py` | Elimina filas repetidas |
| 5 | `lote_05_particion.py` | Divide 80/20 estratificado por `hospdead` |
| 6 | `lote_06_nulos.py` | Descarta columnas con mas de 50% de nulos |
| 7 | `lote_07_atipicos.py` | Acota atipicos con el RIC del entrenamiento |
| 8 | `lote_08_imputacion.py` | Rellena con mediana y moda del entrenamiento |
| 9 | `lote_09_codificacion.py` | Convierte categorias en columnas 0/1 |
| 10 | `lote_10_salida.py` | Ordena columnas y guarda `support2_train.csv` y `support2_test.csv` |
| 11 | `lote_11_validacion.py` | Comprueba que la salida este lista para modelar |

`config.py` concentra rutas y parametros (objetivo, semilla, limites, columnas excluidas).
`utilidades.py` maneja los archivos intermedios y la separacion numericas/categoricas.

El orden importa: se acota **antes** de rellenar, porque calcular el RIC sobre datos ya
imputados aplasta las columnas con muchos nulos. Todo lo que se calcula (mediana, moda, limites,
categorias) sale unicamente del conjunto de entrenamiento y se aplica igual al de prueba.

## Salida del pipeline

`support/support2_train.csv` (7284 x 41) y `support/support2_test.csv` (1821 x 41): todo
numerico, sin faltantes, con `hospdead` como ultima columna.

Para volver a incluir las columnas posteriores al ingreso (`dnr`, `dnrday`, `charges`, `totcst`,
`totmcst`, `avtisst`) y comparar, poner `INCLUIR_POSTERIORES = True` en `config.py`.

---

# Modelado

Dos archivos, el mismo trabajo, los mismos resultados. Cambia como se leen.

| | `modelado_base.py` | `modelado_secuencial.py` |
|---|---|---|
| Estructura | funciones reutilizables | un flujo de arriba a abajo |
| Para que sirve | correrlo y extenderlo | leerlo y explicarlo |

`modelado_base.py` parte el trabajo en funciones (`definir_modelos`, `evaluar`, `comparar`) y
toma las rutas de `config.py`. Suma una referencia tonta con `DummyClassifier`.

`modelado_secuencial.py` hace lo mismo en siete pasos numerados, sin definir ninguna funcion y
declarando sus rutas y parametros arriba del archivo. Se lee de corrido, sin saltar a otro lado.

## Que hace el secuencial, paso por paso

### El problema

Predecir `hospdead`: si el paciente muere durante esa hospitalizacion. Es un si o no, o sea un
problema de **clasificacion binaria**. De cada 100 pacientes, 26 mueren y 74 sobreviven.

### Paso 1 — Particion 80/20

Carga los dos csv que dejo el lote 10: 7,284 pacientes para entrenar y 1,821 para probar.

La idea de partir es simple: si al modelo se le mide con los mismos pacientes que uso para
aprender, va a parecer mejor de lo que es, igual que un examen con las respuestas a la vista. El
80% es para aprender y el 20% se guarda cerrado hasta el final.

La particion es **estratificada**: los dos grupos tienen la misma proporcion de fallecidos
(0.259), para que ninguno quede con una mezcla distinta por azar.

El paso no vuelve a partir, solo carga. Las medianas y los limites del lote 7 se calcularon con
ese 80%, asi que una particion nueva mandaria a prueba filas que ya influyeron en esos numeros.

### Paso 2 — Entradas y objetivo

Separa la tabla en dos partes: `X` son las 40 variables con las que el modelo trabaja (edad,
presion, creatinina, grupo de enfermedad) e `y` es la columna `hospdead`, la respuesta que tiene
que aprender a dar.

### Paso 3 — Escalado

Las variables estan en unidades muy distintas: la edad va de 21 a 102, el pH de 7.25 a 7.60, la
glucosa hasta 318. Escalar es reexpresarlas todas en la misma medida: se le resta a cada una su
promedio y se la divide por su desviacion, y quedan centradas en 0 con desviacion 1.

El escalador se ajusta con `fit_transform` sobre entrenamiento y se aplica con `transform` a
prueba. Son dos metodos distintos a proposito: el primero aprende el promedio y la desviacion, el
segundo solo los usa. Si se usara `fit_transform` en prueba, el modelo estaria viendo datos del
20% que se supone no conoce.

Va escrito a la vista, no dentro de un pipeline, justamente para que se vea de un vistazo que el
escalador solo aprende del 80%.

### Paso 4 — Regresion logistica

Le asigna un peso a cada variable, los suma y convierte el total en una probabilidad de morir
entre 0 y 1. Es la idea de "la edad suma riesgo, la presion alta suma riesgo", todo en una cuenta.

Usa los datos escalados. Sin escalar tambien funcionaria, pero `LogisticRegression` trae una
penalizacion que castiga los pesos grandes, y sin unidades comparables ese castigo cae desparejo.

### Paso 5 — Arbol de decision

Hace preguntas encadenadas: "el puntaje de gravedad es mayor a 50.5? entonces mira la edad, y
si es mayor a 70...". El resultado se puede dibujar y leer como un diagrama de reglas.

Usa los datos **sin escalar**, y esto es lo unico raro del archivo a primera vista. Escalar no
cambia el orden de los valores: quien tenia el puntaje mas alto lo sigue teniendo. Y el arbol solo
compara umbrales, de una variable a la vez. Asi que elige el mismo corte y da exactamente el mismo
resultado. Escalarlo no aporta nada y hace pensar que hace falta.

### Paso 6 — Vecinos mas cercanos

No aprende una regla: guarda a los 7,284 pacientes de entrenamiento y, para cada paciente nuevo,
busca los `k` que mas se le parecen y hace que voten.

Aqui el escalado **no es opcional**. "Parecerse" se mide sumando las diferencias de todas las
variables en un solo numero, y sin escalar una diferencia de 50 en glucosa pesaria miles de veces
mas que la diferencia completa del pH de punta a punta: el vecino mas parecido saldria decidido
casi solo por la glucosa.

El `k` no se elige a dedo. Se prueban varios con **validacion cruzada sobre entrenamiento**: se
parte el 80% en 5 pedazos, se entrena con 4 y se mide con el que quedo, cinco veces, y se
promedia. Se hace asi, y no mirando prueba, porque elegir un parametro por como rinde en prueba es
otra forma de hacer trampa: el 20% deja de ser una medida limpia.

Es el unico lugar del archivo con un `Pipeline`, y esta ahi por una razon concreta: dentro de
`cross_val_score` el escalador tiene que reajustarse en cada uno de los 5 pedazos.

### Paso 7 — Comparacion

Junta las metricas de los tres. Las cuatro que importan:

- **AUC**: que tan bien ordena a los pacientes de menos a mas riesgo. 0.5 es azar, 1.0 es perfecto.
- **Exactitud**: el porcentaje que acierta. Enganosa aca, ver abajo.
- **Precision** de "muere": de los que marco como que van a morir, cuantos murieron de verdad.
- **Recall** de "muere": de los que murieron de verdad, cuantos habia marcado.

| Modelo | AUC | Exactitud | Precision (muere) | Recall (muere) |
|---|---|---|---|---|
| Logistica | **0.879** | 0.827 | 0.736 | 0.519 |
| Arbol | 0.847 | 0.807 | 0.701 | 0.447 |
| Vecinos | 0.835 | 0.797 | 0.721 | 0.356 |
| Referencia tonta | 0.500 | 0.741 | 0.000 | 0.000 |

La ultima fila es el dato mas util de la tabla. Es un modelo que contesta siempre "sobrevive",
sin mirar nada, y acierta el **74.1%**. Por eso la exactitud sola no dice nada aca: el mejor
modelo llega a 82.7% y no hacer nada ya da 74.1%.

## Lo que queda pendiente

La logistica detecta solo el **51.9%** de los pacientes que mueren. Se le escapa casi la mitad,
y son justo los que interesa detectar.

Pasa porque las clases estan desbalanceadas: como morir es lo menos frecuente, al modelo le
conviene inclinarse hacia "sobrevive". Se corrige con `class_weight="balanced"`, que hace pesar
mas a los casos de la clase chica: el recall sube a 79%, pero la precision cae y aparecen falsas
alarmas.

Ese intercambio es la decision que viene: que es peor, avisar de mas o dejar pasar a un paciente
grave.
