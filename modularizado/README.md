# modularizado

Version en lotes `.py` del preprocesamiento que en el repositorio esta en `support/notebook.ipynb`.
Cada lote es un modulo ejecutable por separado: lee el archivo intermedio que dejo el lote
anterior en `intermedios/` y escribe el suyo.

La narracion completa del pipeline, la auditoria y las correcciones respecto al notebook estan
en [PIPELINE.md](PIPELINE.md).

## Ejecucion

Desde la raiz del repositorio:

```bash
python -m modularizado.pipeline           # todos los lotes en orden
python -m modularizado.lote_07_atipicos   # un lote suelto
```

Requiere `pandas` (y `ucimlrepo` solo si se quiere volver a descargar el csv desde UCI;
sin conexion el lote 1 reutiliza `support/support2.csv`).

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

## Salida

`support/support2_train.csv` (7284 x 41) y `support/support2_test.csv` (1821 x 41): todo
numerico, sin faltantes, con `hospdead` como ultima columna.

Para volver a incluir las columnas posteriores al ingreso (`dnr`, `dnrday`, `charges`, `totcst`,
`totmcst`, `avtisst`) y comparar, poner `INCLUIR_POSTERIORES = True` en `config.py`.
