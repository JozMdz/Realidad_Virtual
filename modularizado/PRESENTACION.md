# Preprocesamiento SUPPORT2

**Objetivo:** predecir `hospdead` — si el paciente muere durante esa hospitalización.

De un CSV crudo de 9,105 pacientes a dos archivos listos para entrenar.

---

## El dataset

- Estudio SUPPORT: pacientes hospitalizados con enfermedades graves.
- 9,105 filas, 45 columnas, 8 grupos de enfermedad.
- Cada fila es un paciente.
- Clasificación binaria: muere / sobrevive.

Se eligió `hospdead` entre tres candidatas (`death`, `hospdead`, `sfdm2`).

---

## Cómo está armado

Once lotes `.py`, se corren en orden.

Cada lote deja su resultado en un archivo y el siguiente lo levanta.

```bash
python -m modularizado.pipeline           # todo
python -m modularizado.lote_07_atipicos   # un paso suelto
```

**Por qué así:** si falla el paso 7, se arregla el 7 y se corre el 7.
No hay que volver a empezar de cero.

---

## Los pasos elementales — se hicieron todos

| | Paso | Lote |
|---|---|---|
| ✓ | Cargar y estandarizar nombres de columna | 2 |
| ✓ | Auditar tipos, nulos y estadísticas | 2 |
| ✓ | Seleccionar variables | 3 |
| ✓ | Quitar filas duplicadas | 4 |
| ✓ | Separar entrenamiento y prueba | 5 |
| ✓ | Tratar valores faltantes | 6 y 8 |
| ✓ | Tratar valores atípicos | 7 |
| ✓ | Codificar categorías | 9 |
| ✓ | Guardar la salida | 10 |

---

## Paso 2 — Estandarizar y auditar

- Se declara qué cuenta como faltante: `?`, `NA`, `N/A`, vacío, `null`.
- Nombres a minúsculas con guion bajo (`num.co` → `num_co`).
- Tabla de diagnóstico: tipo, nulos, % de nulos, valores únicos.

Sin esto, pandas cuenta como dato válido cosas que no lo son.

---

## Paso 3 — Seleccionar variables

Se sacan tres tipos de columna.

**1. Las que contienen la respuesta**
`death`, `sfdm2`, `surv2m`, `surv6m`, `prg2m`, `prg6m`.
Son la misma pregunta, o la respuesta de otro modelo, o la opinión del médico.

**2. Las repetidas**
`dzclass` es un resumen de `dzgroup`. `adls` es `adlsc` con huecos.

**3. Las que se saben recién al final** ← esto no estaba
`dnr`, `dnrday`, `charges`, `totcst`, `totmcst`, `avtisst`.

---

## Paso 5 — Separar antes de tocar nada

**El orden importa.**

Rellenar, acotar y codificar necesitan aprender un número de los datos:
una mediana, un límite, una lista de categorías.

Si ese número se calcula con el 100% de los datos, la información de las
filas de prueba ya se coló adentro.

Por eso: **primero se parte** (80/20 estratificado), después se calcula todo
sobre entrenamiento y se aplica igual a los dos.

---

## Pasos 6 a 8 — Faltantes y atípicos

- Se eliminan columnas con más del 50% de nulos: `urine`, `adlp`.
- Se acotan atípicos con el rango intercuartílico (RIC).
- Se rellena: mediana en numéricas, moda en categóricas.

Las columnas binarias (`diabetes`, `dementia`) quedan fuera del RIC:
en una columna de 0 y 1 no existe el valor extremo.

---

## Paso 9 — Codificar

- Dos valores → una columna de 0 y 1.
- Tres o más → una columna por categoría.
- Las categorías se fijan según entrenamiento y se le imponen a prueba.

Resultado: los dos archivos con exactamente las mismas columnas, en el mismo orden.

---

# Y un poco más

Tres cosas que salieron de auditar el pipeline.

1. Un error en el orden de los pasos.
2. Seis columnas que le pasaban la respuesta al modelo.
3. Nada verificaba que la salida sirviera.

---

## 1. El RIC estaba mal calculado

Se rellenaba **antes** de acotar.

Si media columna está vacía y se rellena con la mediana,
media columna **es** la mediana → los cuartiles se pegan → el RIC desaparece.

| Columna | % nulos | Límites reales | Límites que salían |
|---|---|---|---|
| `glucose` | 49.6% | -26 a 318 | **131 a 139** |
| `bun` | 47.9% | -28 a 84 | 19 a 27 |
| `crea` | 0.6% | -0.6 a 3.4 | -0.6 a 3.4 |

Una glucosa de 300 terminaba aplastada a 139.

`crea` casi no tiene nulos y no cambia: eso confirma quién era el culpable.

**Se corrigió:** acotar primero, rellenar después.

---

## 2. Seis columnas pasaban la respuesta

`dnr`, `dnrday`, `charges`, `totcst`, `totmcst`, `avtisst`.

**La orden de no reanimar:**

| | Firma DNR después del ingreso |
|---|---|
| Pacientes que mueren | **77.9%** |
| Pacientes que sobreviven | 16.8% |

No es un dato de ingreso. Se firma cuando el equipo ya ve que el paciente se muere.

**Los costos:** 92,638 promedio en quien muere, 48,683 en quien sobrevive.
Pero ese número no existe hasta que el paciente se va del hospital.

---

## 2. El efecto en el rendimiento

| Versión | Columnas | AUC |
|---|---|---|
| Con esas seis | 48 | **0.948** |
| Sin esas seis | 41 | 0.879 |

Un AUC de 0.95 prediciendo muerte hospitalaria es demasiado bueno.
Los modelos publicados sobre este dataset andan entre 0.80 y 0.86.

**Bajar de 0.95 a 0.88 no es perder precisión. Es dejar de hacer trampa.**

El modelo anterior no predecía la muerte: en buena parte la estaba leyendo.

---

## 3. Validación automática

El lote 11 vuelve a abrir los archivos guardados y revisa:

- Cero valores faltantes.
- Todas las columnas numéricas.
- Mismas columnas, mismo orden, en los dos archivos.
- `hospdead` al final y solo 0 o 1.
- Sin columnas constantes ni repetidas.
- Ninguna fila de prueba aparece en entrenamiento.
- Misma proporción de fallecidos en ambos.

Si algo falla, corta con error. Hoy pasa todo.

---

## El diccionario oficial respalda el criterio

La ficha de UCI trae **47** variables. El CSV tiene **45**.

Las dos que faltan están marcadas con rol **"Other"**:

- `slos` — días desde el ingreso al estudio hasta el alta.
- `d.time` — días de seguimiento.

Fuga pura: la duración de la estancia sale de cuándo terminó.

**UCI ya había aplicado este criterio. Nosotros lo extendimos a las seis que se le escaparon.**

El lote 3 ahora lo verifica solo: lee la ficha y descarta lo marcado "Other".

---

## Una precisión que exige la ficha

La ficha dice que `surv2m` y `surv6m` son *"predicted by a model"*.

Pero `scoma` y `sps` dicen **lo mismo**, y esas se conservan.

El criterio no es "lo calculó un modelo". Es **qué estima**:

| Variable | Qué estima | |
|---|---|---|
| `surv2m`, `prg2m`... | El desenlace | se va |
| `scoma`, `sps` | La gravedad al día 3 | se queda |

---

## Ojo: el diccionario tiene un error

Dice que en `adlp` y `adls` *"higher values indicate more chance of survival"*.

Los datos dicen lo contrario:

| | `adlsc` promedio |
|---|---|
| Sobreviven | 1.74 |
| Mueren | **2.32** |

El índice ADL cuenta **dependencias**: más alto = más dependiente = peor.

No cambia el código. Pero si se repite la frase de la ficha, se dice al revés.

---

## Resultado

| | Filas | Columnas | Faltantes |
|---|---|---|---|
| `support2_train.csv` | 7,284 | 41 | 0 |
| `support2_test.csv` | 1,821 | 41 | 0 |

Todo numérico. `hospdead` como última columna.

---

# Modelos base

`modelado_base.py` — ya corriendo sobre esta salida.

Validación cruzada de 5 particiones sobre entrenamiento, más evaluación en prueba.

---

## El diccionario oficial respalda el criterio

La ficha de UCI trae **47** variables. El CSV tiene **45**.

Las dos que faltan están marcadas con rol **"Other"**:

- `slos` — días desde el ingreso al estudio hasta el alta.
- `d.time` — días de seguimiento.

Fuga pura: la duración de la estancia sale de cuándo terminó.

**UCI ya había aplicado este criterio. Nosotros lo extendimos a las seis que se le escaparon.**

El lote 3 ahora lo verifica solo: lee la ficha y descarta lo marcado "Other".

---

## Una precisión que exige la ficha

La ficha dice que `surv2m` y `surv6m` son *"predicted by a model"*.

Pero `scoma` y `sps` dicen **lo mismo**, y esas se conservan.

El criterio no es "lo calculó un modelo". Es **qué estima**:

| Variable | Qué estima | |
|---|---|---|
| `surv2m`, `prg2m`... | El desenlace | se va |
| `scoma`, `sps` | La gravedad al día 3 | se queda |

---

## Ojo: el diccionario tiene un error

Dice que en `adlp` y `adls` *"higher values indicate more chance of survival"*.

Los datos dicen lo contrario:

| | `adlsc` promedio |
|---|---|
| Sobreviven | 1.74 |
| Mueren | **2.32** |

El índice ADL cuenta **dependencias**: más alto = más dependiente = peor.

No cambia el código. Pero si se repite la frase de la ficha, se dice al revés.

---

## Resultados en prueba

| Modelo | AUC | Exactitud | Precisión (muere) | Recall (muere) |
|---|---|---|---|---|
| Logística | **0.879** | 0.827 | 0.736 | 0.519 |
| Logística balanceada | 0.879 | 0.791 | 0.569 | **0.790** |
| Bosque | 0.870 | 0.826 | 0.752 | 0.489 |
| Boosting | 0.866 | 0.824 | 0.718 | 0.528 |
| Árbol | 0.847 | 0.807 | 0.701 | 0.447 |
| Referencia | 0.500 | 0.741 | 0.000 | 0.000 |

**La referencia dice siempre "sobrevive" y acierta el 74.1%.**
Por eso la exactitud sola no sirve acá.

---

## El problema que sigue

Las clases están desbalanceadas: 25.9% muere, 74.1% sobrevive.

La logística detecta solo el **51.9%** de los que mueren.

Con `class_weight="balanced"` sube a **79.0%**, pero la precisión baja de 0.736 a 0.569.

Ese intercambio es la decisión que viene:
¿cuánto cuesta una falsa alarma contra dejar pasar un paciente grave?

---

## Cierre

- Se siguieron los pasos elementales del preprocesamiento, en orden y sin saltos.
- Se auditó el resultado y aparecieron dos errores reales, ya corregidos.
- Se agregó una validación que impide entregar un archivo roto.
- Se contrastó todo contra el diccionario oficial de UCI.
- Los modelos base ya corren sobre esa salida.

**Detalle completo:** `PIPELINE.md`
