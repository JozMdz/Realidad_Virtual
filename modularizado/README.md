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

python -m modularizado.pipeline           # todos los lotes en orden
python -m modularizado.lote_07_atipicos   # un lote suelto
python -m modularizado.modelado_base        # modelos base, version modular
python -m modularizado.modelado_secuencial  # los mismos modelos, de corrido
python -m modularizado.prueba_pca           # prueba de reduccion de variables
```

El pipeline solo necesita `pandas`. `scikit-learn` es para `modelado_base.py` y `ucimlrepo`
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
| 7 | `lote_07_atipicos.py` | Acota atipicos con el RIC del entrenamiento y agrega una bandera por columna acotada |
| 8 | `lote_08_imputacion.py` | Rellena con mediana y moda del entrenamiento |
| 9 | `lote_09_codificacion.py` | Convierte categorias en columnas 0/1 |
| 10 | `lote_10_salida.py` | Ordena columnas y guarda `support2_train.csv` y `support2_test.csv` |
| 11 | `lote_11_validacion.py` | Comprueba que la salida este lista para modelar |

`modelado_base.py` no es parte del pipeline: entrena tres clasificadores sencillos sobre la
salida y los compara. Cada uno decide de una forma distinta, a proposito: `logistica` traza una
frontera lineal, `arbol` aplica reglas de corte y `vecinos` vota entre los pacientes mas
parecidos. Los dos que comparan magnitudes llevan `StandardScaler` dentro del pipeline; el arbol
no lo necesita porque parte por umbrales. Suma una referencia tonta que contesta siempre la clase
mayoritaria, para tener contra que medir. Compara con validacion cruzada y evalua en prueba.

`prueba_pca.py` tampoco es parte del pipeline: mide si se pueden reducir las variables,
comparando PCA contra seleccion directa de las k mejores.

`config.py` concentra rutas y parametros (objetivo, semilla, limites, columnas excluidas).
`utilidades.py` maneja los archivos intermedios y la separacion numericas/categoricas.

El orden importa: se acota **antes** de rellenar, porque calcular el RIC sobre datos ya
imputados aplasta las columnas con muchos nulos. Todo lo que se calcula (mediana, moda, limites,
categorias) sale unicamente del conjunto de entrenamiento y se aplica igual al de prueba.

## Salida

`support/support2_train.csv` (7284 x 61) y `support/support2_test.csv` (1821 x 61): todo
numerico, sin faltantes, con `hospdead` como ultima columna.

De esas 61, veinte son banderas `<columna>_acotado`: valen 1 en las filas cuyo valor cayo
fuera de los limites del RIC y fue recortado, asi que el modelo puede distinguir un valor
medido de uno acotado. Se crea una bandera por cada columna que efectivamente corto algo.
`MINIMO_BANDERA_ATIPICOS` en `config.py` sube el piso: con `0.01` solo llevan bandera las
columnas que cortan al menos el 1% de las filas de entrenamiento.

Para volver a incluir las columnas posteriores al ingreso (`dnr`, `dnrday`, `charges`, `totcst`,
`totmcst`, `avtisst`) y comparar, poner `INCLUIR_POSTERIORES = True` en `config.py`.

## Modelado: dos versiones del mismo trabajo

Las dos entrenan los mismos tres clasificadores sobre la misma salida y dan los mismos numeros.
Cambia solo la forma de leerlas.

| | `modelado_base.py` | `modelado_secuencial.py` |
|---|---|---|
| Estructura | funciones reutilizables | un flujo de arriba a abajo |
| Pasos | `definir_modelos`, `evaluar`, `comparar` | siete bloques numerados |
| Referencia tonta | si, `DummyClassifier` | solo la tasa de la clase mayoritaria |
| Rutas y parametros | los toma de `config.py` | los declara arriba del archivo |
| Para que sirve | correrlo y extenderlo | leerlo o explicarlo de corrido |

`modelado_secuencial.py` recorre siete pasos:

1. **Particion 80/20**: carga los dos csv que dejo el lote 10 e informa la proporcion de
   `hospdead=1` en cada uno, que da 0.259 en los dos porque la particion fue estratificada.
   No vuelve a partir: las medianas y los limites del RIC se calcularon con ese 80%, asi que una
   particion nueva mandaria a prueba filas que ya influyeron en esos numeros.
2. **Entradas y objetivo**: separa las 60 variables de `hospdead`.
3. **Escalado**: `StandardScaler` ajustado con `fit_transform` sobre entrenamiento y aplicado con
   `transform` a prueba. Va explicito, no dentro de un pipeline, para que se vea de un vistazo
   que el escalador solo aprende del 80%.
4. **Regresion logistica**: sobre los datos escalados.
5. **Arbol de decision**: sobre los datos **sin** escalar. Estandarizar no cambia el orden de los
   valores, y el arbol solo compara umbrales, asi que elige el mismo corte y da el mismo
   resultado: escalarlo no aporta nada y hace pensar que hace falta.
6. **Vecinos mas cercanos**: sobre los datos escalados, porque mide distancias y sin escalar las
   variables de rango grande dominarian el calculo. El `k` se busca con validacion cruzada sobre
   entrenamiento, nunca mirando prueba; es el unico lugar del archivo con un `Pipeline`, y esta
   ahi porque dentro de `cross_val_score` el escalador tiene que reajustarse en cada particion.
7. **Comparacion**: junta las metricas de los tres y compara contra la tasa de la clase
   mayoritaria (0.741), que es lo que acierta contestar siempre "sobrevive".

Se puede correr con `-m` o directo con `python modularizado/modelado_secuencial.py`: las rutas
salen de la ubicacion del archivo, no del directorio desde donde se llama.
