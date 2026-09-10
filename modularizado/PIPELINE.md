# Narración del pipeline

Esta es la versión en lotes `.py` del preprocesamiento que estaba en `support/notebook.ipynb`.
La idea es la misma: dejar el dataset SUPPORT2 listo para entrenar un modelo que prediga
`hospdead`, o sea, si el paciente **muere durante esa hospitalización**. Lo que cambia es la
forma: en vez de un notebook que se corre de arriba a abajo, son once lotes que se corren en
orden y cada uno deja su resultado en un archivo para que el siguiente lo levante.

## Por qué en lotes

Un notebook guarda todo en memoria. Si se cae en la celda 30, se pierde lo de las 29 anteriores
y hay que volver a empezar. Con lotes, cada paso escribe su salida en `intermedios/`, así que si
algo falla en el lote 7 se arregla y se corre solo el lote 7, que va a leer lo que dejó el 6.
También sirve para revisar en clase un paso puntual sin cargar todo lo demás.

Cada lote es un archivo con funciones cortas y una función `ejecutar()` que las encadena.
Los parámetros (semilla, objetivo, límites, qué columnas se excluyen) están todos juntos en
`config.py`, para no andar buscándolos repartidos entre archivos.

## 0. El contexto

El dataset viene del estudio SUPPORT, sobre pronóstico de pacientes hospitalizados con
enfermedades graves. Cada fila es un paciente, son 9,105 en total, clasificados en 8 grupos de
enfermedad (insuficiencia respiratoria aguda, insuficiencia cardíaca, cáncer de colon o de
pulmón, cirrosis, coma, EPOC, fallo multiorgánico).

Hay tres columnas que podrían ser la variable objetivo: `death` (murió en cualquier momento del
seguimiento), `hospdead` (murió en esa hospitalización) y `sfdm2` (nivel de discapacidad en una
entrevista posterior). Se elige `hospdead`, y todo el preprocesamiento se hace con ese fin.

## 1. Descarga

`lote_01_descarga.py` baja el dataset 880 desde UCI con `ucimlrepo` y lo guarda como
`support2.csv`. Si el archivo ya existe, no lo pisa: compara forma y columnas y avisa si
coinciden. Si no hay conexión, usa el archivo local y sigue adelante. Esto último es a propósito,
para que el pipeline se pueda correr sin internet.

## 2. Auditoría inicial

`lote_02_auditoria.py` lee el csv crudo y antes de mirar nada estandariza:

- `na_values=["?", "NA", "N/A", "", "null"]` para que pandas reconozca como faltante todo lo que
  en realidad lo es.
- Renombra las columnas a minúsculas con guion bajo, porque nombres como `num.co` con punto en
  medio dan problemas al usarlos.
- `dropna(how="all")` para quitar filas completamente vacías, por seguridad.

Después arma la tabla de diagnóstico: por cada columna, el tipo, cuántos nulos tiene, qué
porcentaje representa y cuántos valores distintos hay. Sobre el porcentaje: `datos[columna].isna()`
marca cada valor como `True` o `False`, y al sacar el `.mean()` pandas trata `True` como 1 y
`False` como 0, así que el resultado ya es la proporción de faltantes. Por 100 queda en
porcentaje.

También guarda `estadisticas_descriptivas.csv` con el `describe()` de todas las columnas.

## 3. Elegir el objetivo y quitar lo que no se puede usar

Este es el lote más importante y el que más cambió respecto al notebook.
`lote_03_seleccion.py` saca dos tipos de columnas.

**Las que contienen la respuesta.** `death` es casi la misma pregunta que `hospdead`. `sfdm2`
solo tiene valor si al paciente le hicieron la entrevista de seguimiento dos meses después, lo
cual solo pasa si sobrevivió: tener dato en `sfdm2` es casi decirle al modelo que no murió.
`surv2m` y `surv6m` son la estimación de supervivencia que calculó el propio modelo estadístico
del estudio, y `prg2m` y `prg6m` son la estimación subjetiva del médico tratante. Usarlas sería
copiarle la respuesta a otro modelo o a un médico en vez de aprender de los datos clínicos.

**Las que son la misma información repetida.** El cruce de `dzgroup` con `dzclass` muestra que
cada categoría de `dzgroup` cae siempre en una sola de `dzclass`, sin excepciones: `dzclass` es
un resumen derivado, no aporta nada nuevo, se conserva `dzgroup` que tiene más detalle. Y `adlsc`
es, según la ficha oficial, la versión calibrada e imputada de `adls`, sin huecos, así que se
conserva `adlsc` y se elimina `adls`. En cambio `sps` y `aps` están relacionadas pero no son
copia exacta (la correlación no da 1.0), así que se conservan las dos.

**Las que se saben recién al final.** Estas no estaban en el notebook y son la corrección más
grande. Son columnas que parecen datos normales pero que en la práctica describen lo que pasó
*durante* la internación, no lo que se sabía al ingresar:

| Columna | Por qué se va |
|---|---|
| `dnr`, `dnrday` | La orden de no reanimar se firma cuando el paciente ya está empeorando. En los datos: de los que mueren, el 77.9% tiene una orden firmada después del ingreso, contra el 16.8% de los que sobreviven. |
| `charges`, `totcst`, `totmcst` | Son el cobro y el costo total de la hospitalización. Ese número existe recién cuando el paciente se va, vivo o muerto. |
| `avtisst` | Es el promedio de intervenciones de los días 3 al 25, o sea que se calcula sobre toda la estancia. |

El notebook ya había marcado `dnr` y `dnrday` como algo "a interpretar", pero quedó sin resolver
y las dos terminaron entrando al modelo. Más abajo, en la sección de correcciones, están los
números de cuánto cambia esto.

Si en algún momento se quieren volver a incluir para comparar en clase, en `config.py` está
`INCLUIR_POSTERIORES = False`: se cambia a `True` y vuelven a entrar.

## 4. Filas repetidas

`lote_04_duplicados.py` cuenta y elimina las filas duplicadas por completo. En este dataset no
hay ninguna, pero el paso se deja igual, y sobre todo se deja **antes** de partir en
entrenamiento y prueba: si una fila repetida quedara una en cada grupo, el modelo estaría siendo
evaluado con una fila que ya vio al entrenar.

## 5. Separar entrenamiento y prueba

Acá está la parte que en el notebook ya estaba bien resuelta y que conviene explicar despacio.

De acá en adelante, varios pasos necesitan aprender un número de los datos: una mediana para
rellenar, un límite para acotar, una lista de categorías para codificar. Si ese número se calcula
con el 100% de los datos, parte de la información de las filas que después se van a usar para
*evaluar* ya se coló adentro de ese número. Eso también es fuga, aunque no venga de una columna
sino del orden de los pasos.

Por eso `lote_05_particion.py` separa primero: 80% entrenamiento, 20% prueba. La separación es
estratificada, o sea que mantiene la misma proporción de fallecidos en los dos grupos (0.259 en
ambos), para que ninguno quede con una mezcla distinta por azar. La semilla es 42, así que la
partición es siempre la misma.

De acá en adelante, **todo lo que se calcula sale solo de entrenamiento y se aplica igual a los
dos grupos**.

## 6. Columnas con demasiados nulos

`lote_06_nulos.py` mide el porcentaje de faltantes por columna, medido solo en entrenamiento, y
elimina de los dos grupos las que pasan del 50%. Se van `urine` (53.5%) y `adlp` (61.8%):
rellenar más de la mitad de una columna es inventar más de lo que se sabe.

## 7. Valores atípicos

`lote_07_atipicos.py` usa el rango intercuartílico. Con el primer cuartil (Q1) y el tercero (Q3),
todo lo que quede por debajo de `Q1 - 1.5 * RIC` o por encima de `Q3 + 1.5 * RIC` se considera
atípico. Los límites se calculan solo con entrenamiento y se aplican a los dos grupos acotando el
valor, sin borrar filas.

La regla no se aplica a las columnas binarias (`diabetes`, `dementia`, y el propio `hospdead`):
en una columna de 0 y 1 no existe el concepto de valor extremo, y aplicarle el RIC podría borrar
una de las dos categorías entera.

**Este lote va antes de rellenar, no después.** En el notebook estaba al revés y eso rompía los
límites. Está explicado con números en la sección de correcciones.

## 8. Rellenar los faltantes

`lote_08_imputacion.py` rellena lo que queda: las columnas numéricas con la **mediana** de
entrenamiento, las de categoría con el valor **más frecuente** en entrenamiento (la moda). El
mismo número se usa para los dos grupos, para no calcular nada nuevo a partir de prueba.

## 9. Convertir categorías en números

`lote_09_codificacion.py` primero fija, según lo que aparece en entrenamiento, cuáles son las
categorías válidas de cada columna, y le impone esa misma lista a prueba. Si en prueba apareciera
una categoría que no está en entrenamiento, avisa (en este dataset no pasa).

Después codifica: las columnas de dos valores quedan como una sola columna de 0 y 1, y las de
tres o más quedan como varias columnas de 0 y 1, una por categoría. Se usa `drop_first=True`, que
descarta la primera categoría de cada columna porque es información redundante: si un paciente no
es de ninguna de las otras, ya se sabe que es de la primera.

Al final, prueba se realinea con `reindex` a las columnas de entrenamiento, para que los dos
grupos queden con exactamente las mismas columnas en el mismo orden, que es como lo va a esperar
el modelo.

## 10. Resultado

`lote_10_salida.py` deja `hospdead` como última columna y guarda `support2_train.csv` y
`support2_test.csv`. Quedan 7,284 filas de entrenamiento y 1,821 de prueba, 41 columnas cada uno,
sin ningún valor faltante y todo numérico.

## 11. Validación

Este lote no estaba en el notebook. `lote_11_validacion.py` vuelve a leer los dos archivos ya
guardados y revisa que de verdad estén listos:

- Que no queden valores faltantes.
- Que todas las columnas sean numéricas.
- Que los dos archivos tengan las mismas columnas en el mismo orden.
- Que `hospdead` sea la última y valga solo 0 o 1.
- Que no haya columnas constantes ni columnas repetidas (que no aportarían nada).
- Que ninguna fila de prueba aparezca también en entrenamiento.
- Que la proporción de fallecidos sea parecida en los dos grupos.

Si algo falla, corta con error en vez de dejar pasar un archivo roto. Hoy pasa todo.

---

# Correcciones respecto al notebook

Se auditó el pipeline completo. Aparecieron tres cosas: dos errores y una falta.

## 1. El RIC se calculaba después de rellenar

Este es el error más claro y el más fácil de mostrar.

El notebook rellenaba primero y acotaba después. El problema es que si una columna tiene la mitad
de los datos faltantes y se rellena con la mediana, entonces la mitad de la columna **es** la
mediana. Los cuartiles se pegan al centro, el RIC casi desaparece, y los límites salen absurdos.

`glucose` tiene 49.4% de faltantes. Comparando los límites:

| Columna | % nulos | Límites con datos reales | Límites después de rellenar |
|---|---|---|---|
| `glucose` | 49.6% | -26.0 a 318.0 | 131.0 a 139.0 |
| `bun` | 47.9% | -28.0 a 84.0 | 19.0 a 27.0 |
| `alb` | 36.9% | 0.6 a 5.4 | 2.1 a 3.7 |
| `edu` | 18.0% | 4.0 a 20.0 | 9.5 a 13.5 |
| `crea` | 0.6% | -0.6 a 3.4 | -0.6 a 3.4 |

(porcentajes y límites medidos sobre entrenamiento, que es como lo hace el pipeline)

Un paciente con glucosa en 300, que es un dato clínico real y grave, terminaba aplastado a 139.
En `glucose` se acotaban 3,509 filas de entrenamiento; con el orden corregido se acotan 216. En
`alb` se pasaba de 1,776 a 10. Y se ve que en `crea`, que casi no tiene faltantes, los límites no
cambian nada: es justamente lo que confirma que el problema era el relleno.

La corrección es solo cambiar el orden: acotar primero, con los valores que de verdad se midieron
(los cuartiles de pandas ignoran los nulos por su cuenta), y rellenar después. Por eso el lote de
atípicos quedó como 7 y el de relleno como 8.

## 2. Quedaban columnas que se conocen recién al final

El notebook sacó bien las columnas que contienen la respuesta directa (`death`, `sfdm2`, las
estimaciones de supervivencia), pero quedaron adentro seis que describen lo que pasó durante la
internación: `dnr`, `dnrday`, `charges`, `totcst`, `totmcst` y `avtisst`.

La señal de alarma es el rendimiento. Entrenando una regresión logística y un boosting sobre la
salida:

| Versión | Columnas | AUC logística | AUC boosting |
|---|---|---|---|
| Como estaba el notebook | 48 | 0.948 | 0.957 |
| Sin `dnr` ni `dnrday` | 45 | 0.913 | 0.916 |
| Sin `avtisst` | 47 | 0.931 | 0.942 |
| Sin las seis | 41 | 0.879 | 0.866 |

Un AUC de 0.95 prediciendo muerte hospitalaria es demasiado bueno para ser verdad: los modelos
publicados sobre este mismo dataset andan entre 0.80 y 0.86. El 0.879 que queda es un número
creíble. Ese salto de 0.95 a 0.88 **no es perder precisión, es dejar de hacer trampa**: el modelo
anterior no predecía la muerte, en buena medida la estaba leyendo.

El caso de `dnr` es el más fácil de contar: de los pacientes que mueren en el hospital, el 77.9%
tiene una orden de no reanimar firmada después del ingreso, contra el 16.8% de los que sobreviven.
Esa orden no es un dato clínico de entrada, es una decisión que se toma cuando el equipo médico ya
ve que el paciente se está muriendo.

Y los costos: quien muere en el hospital tiene en promedio 92,638 de cobro contra 48,683 de quien
sobrevive. Pero ese número no existe hasta que el paciente se va. Al momento de querer predecir,
no está disponible.

Quedó `hday` (día de hospitalización al entrar al estudio), que también da distinto entre los dos
grupos pero sí se conoce al ingresar, así que no es fuga.

## 3. No había forma de saber si la salida estaba bien

El notebook terminaba imprimiendo un resumen, pero nada verificaba que el resultado sirviera.
Se agregó el lote 11 con las revisiones automáticas listadas arriba.

---

# Lo que dijo el diccionario oficial

El lote 1 ahora descarga `diccionario_variables.csv`, la ficha que publica UCI. Contrastarla con
los datos confirmó tres cosas y corrigió una.

## Confirma que el criterio de exclusión ya lo usaba UCI

La ficha trae 47 variables, pero el CSV tiene 45. Las dos que faltan están marcadas con rol
**"Other"**, o sea que UCI mismo dice que no son predictoras:

- `slos`: días desde el ingreso al estudio hasta el alta.
- `d.time`: días de seguimiento.

Son fuga pura: la duración de la estancia sale de cuándo terminó, vivo o muerto. Nunca entraron
porque el notebook armó el dataset con `features.join(targets)` y estas quedan fuera de los dos
grupos.

Esto respalda lo que se hizo con `dnr`, los costos y `avtisst`: **no es una regla inventada, es
la misma que el repositorio ya venía aplicando y que dejó incompleta.** El lote 3 ahora lo
verifica solo: lee la ficha, busca columnas con rol "Other" y las descarta si aparecen.

## Confirma que `avtisst` es un método de costeo

La ficha lo dice textual: TISS es *"a method for calculating costs in the intensive care unit"*.
No es una variable clínica, es contabilidad de la estancia.

## Obliga a precisar por qué se van `surv2m` y `surv6m`

La ficha describe `surv2m` y `surv6m` como *"predicted by a model"*. El problema es que `scoma` y
`sps` dicen exactamente lo mismo, y esas se conservan.

El criterio real no es "lo calculó un modelo" sino **qué cosa estima**:

- `surv2m`, `surv6m`, `prg2m`, `prg6m` estiman **el desenlace**. Son la respuesta.
- `scoma` y `sps` son puntajes de **gravedad al día 3**. Describen al paciente.

El lote 3 ahora imprime esa distinción junto a la ficha, para que quede contestada antes de que
la pregunten.

## Corrige un error de la propia ficha

El diccionario dice que en `adlp` y `adls` *"higher values indicate more chance of survival"*.
Los datos dicen lo contrario:

| | `adlsc` promedio |
|---|---|
| Sobreviven | 1.74 |
| Mueren | **2.32** |

La correlación con `hospdead` es **+0.126**. El índice ADL cuenta *dependencias*: más alto es más
dependiente, o sea peor. La descripción de UCI está invertida.

No cambia nada del código, porque la columna se usa como número igual. Pero si se repite la frase
de la ficha al explicar la variable, se dice al revés.

---

# Lo que queda abierto

Cosas que no son errores pero conviene tener presentes:

- **`glucose` y `bun` quedan con casi la mitad de los valores inventados** (49.6% y 47.9%). Pasan
  el corte del 50% por poco. Una opción es agregar una columna extra que marque si el dato
  faltaba o no, así el modelo puede usar esa ausencia como información. No está implementado.
- **El corte del 50% es arbitrario.** Es una decisión, no una regla. Con 40% se irían más
  columnas, con 60% se quedaría `urine`.
- **No hay escalado.** Las columnas quedan en sus unidades originales. La regresión logística y
  las redes lo necesitan; los árboles y el boosting no. Conviene hacerlo dentro del modelo, no
  acá, para que se ajuste solo con entrenamiento.
- **`pafi` podría ir en rangos.** La propia ficha sugiere agruparla por umbrales clínicos de
  hipoxemia en vez de usarla continua. No está hecho.
- **`num_co` es ordinal (0 a 9) y el RIC la acota en 6.** Recorta la punta de la escala. Son 22
  filas, pero conviene saberlo.
- **Las clases están desbalanceadas**: 25.9% muere, 74.1% sobrevive. Un modelo que diga siempre
  "sobrevive" acierta el 74.1%, así que la exactitud sola no dice nada. Hay que mirar AUC,
  precisión y recall de la clase minoritaria.
- **`race_hispanic`, `race_other` y `dementia` valen casi siempre lo mismo** (más del 96% en un
  solo valor). No son un error, pero aportan poco.

# Punto de partida para el modelado

Con los archivos actuales, entrenando directo sin tocar nada más:

| Modelo | AUC | Exactitud |
|---|---|---|
| Siempre la clase mayoritaria | — | 0.741 |
| Regresión logística (escalada) | 0.879 | 0.827 |
| Boosting | 0.866 | 0.824 |

Sobre la clase que interesa (los que mueren), el boosting da precisión 0.718 y recall 0.528: de
cada 10 pacientes que marca como que van a morir acierta en 7, pero se le escapan casi la mitad de
los que efectivamente mueren. Ese recall bajo es el problema a atacar en el modelado, y tiene que
ver con el desbalance.
