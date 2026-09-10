# modularizado

Version en lotes `.py` del preprocesamiento que en el repositorio esta en `support/notebook.ipynb`.
Cada lote es un modulo ejecutable por separado: lee el archivo intermedio que dejo el lote
anterior en `intermedios/` y escribe el suyo.

## Ejecucion

Desde la raiz del repositorio:

```bash
python -m modularizado.pipeline          # todos los lotes en orden
python -m modularizado.lote_05_particion # un lote suelto
```

Requiere `pandas` (y `ucimlrepo` solo si se quiere volver a descargar el csv desde UCI;
sin conexion el lote 1 reutiliza `support/support2.csv`).

## Lotes

| Lote | Archivo | Que hace |
|---|---|---|
| 1 | `lote_01_descarga.py` | Descarga el dataset de UCI o reutiliza el csv local |
| 2 | `lote_02_auditoria.py` | Estandariza nombres, audita nulos y guarda estadisticas descriptivas |
| 3 | `lote_03_seleccion.py` | Excluye columnas con fuga de informacion y redundantes |
| 4 | `lote_04_duplicados.py` | Elimina filas repetidas |
| 5 | `lote_05_particion.py` | Divide 80/20 estratificado por `hospdead` |
| 6 | `lote_06_faltantes.py` | Descarta columnas con mas de 50% de nulos e imputa el resto |
| 7 | `lote_07_atipicos.py` | Acota atipicos con el RIC del entrenamiento |
| 8 | `lote_08_codificacion.py` | Convierte categorias en columnas 0/1 |
| 9 | `lote_09_salida.py` | Ordena columnas y guarda `support2_train.csv` y `support2_test.csv` |

`config.py` concentra rutas y parametros (objetivo, semilla, limites).
`utilidades.py` maneja los archivos intermedios y la separacion numericas/categoricas.

Todo lo que se calcula (mediana, moda, limites del RIC, categorias) sale unicamente del
conjunto de entrenamiento y se aplica igual al de prueba.

## Salida

Reproduce exactamente los archivos `support/support2_train.csv` (7284 x 48) y
`support/support2_test.csv` (1821 x 48) generados por el notebook.
