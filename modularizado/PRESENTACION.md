# Preprocesamiento del dataset SUPPORT2

Proyecto de preparación de datos para un modelo de clasificación.

---

## De qué trata

Este repositorio toma un dataset médico crudo y lo deja listo para entrenar un modelo.

Los datos vienen del **estudio SUPPORT**, hecho en hospitales de Estados Unidos. El estudio seguía a pacientes internados con enfermedades graves para ver qué tan bien se podía anticipar su pronóstico.

Cada fila del archivo es un paciente. Son 9,105 pacientes y 45 columnas.

El dataset está publicado en el repositorio de UCI, con el id 880.

---

## Los grupos de variables

Las 45 columnas no son todas del mismo tipo. Las agrupamos así para entenderlas mejor.

### 1. Quién es el paciente

Datos personales y de contexto social.

| Columna | Qué es |
|---|---|
| `age` | Edad en años |
| `sex` | Sexo |
| `race` | Raza |
| `edu` | Años de educación |
| `income` | Ingreso anual, en tramos |
| `hday` | En qué día de su internación entró al estudio |

Así se ven tres pacientes reales:

```
        age     sex      dzgroup  num_co      income   race   edu
0  62.84998    male  Lung Cancer       0    $11-$25k  other  11.0
1  60.33899  female    Cirrhosis       2    $11-$25k  white  12.0
2  52.74698  female    Cirrhosis       2  under $11k  white  12.0
```

La edad viene con decimales porque está calculada por días, no redondeada a años.

### 2. Qué tiene el paciente

El diagnóstico.

| Columna | Qué es |
|---|---|
| `dzgroup` | Enfermedad principal, 8 categorías |
| `dzclass` | La misma agrupada en 4 categorías más amplias |
| `num_co` | Cuántas enfermedades tiene al mismo tiempo (0 a 9) |
| `diabetes` | Si tiene diabetes (0 o 1) |
| `dementia` | Si tiene demencia (0 o 1) |
| `ca` | Si tiene cáncer: no / sí / con metástasis |

Cómo se reparten los pacientes por enfermedad:

```
ARF/MOSF w/Sepsis    3515     (falla respiratoria o de órganos, con sepsis)
CHF                  1387     (insuficiencia cardíaca)
COPD                  967     (enfermedad pulmonar obstructiva)
Lung Cancer           908
MOSF w/Malig          712     (falla de órganos con cáncer)
Coma                  596
Colon Cancer          512
Cirrhosis             508
```

### 3. Cómo está el paciente

Signos vitales y análisis de sangre, todos medidos **al día 3** de estar en el estudio.

| Columna | Qué es |
|---|---|
| `meanbp` | Presión arterial media |
| `hrt` | Frecuencia cardíaca |
| `resp` | Frecuencia respiratoria |
| `temp` | Temperatura en grados |
| `wblc` | Glóbulos blancos |
| `pafi` | Nivel de oxígeno en sangre |
| `alb` | Albúmina |
| `bili` | Bilirrubina |
| `crea` | Creatinina, mide función del riñón |
| `sod` | Sodio |
| `ph` | pH de la sangre |
| `glucose` | Glucosa |
| `bun` | Urea, también del riñón |
| `urine` | Orina producida |

Los mismos tres pacientes de arriba:

```
   meanbp    hrt  resp      temp      crea    sod        ph  glucose
0    97.0   69.0  22.0  36.00000  1.199951  141.0  7.459961      NaN
1    43.0  112.0  34.0  34.59375  5.500000  132.0  7.250000      NaN
2    70.0   88.0  28.0  37.39844  2.000000  134.0  7.459961      NaN
```

Ya acá se ve algo. El paciente 1 tiene presión 43 (muy baja), pulso 112 (acelerado) y creatinina 5.5 (el riñón fallando). Está bastante peor que los otros dos. Y a los tres les falta la glucosa: ese `NaN` es como pandas marca un dato que no está.

### 4. Qué tan grave está

Puntajes que resumen la gravedad en un solo número.

| Columna | Qué es |
|---|---|
| `scoma` | Nivel de coma, escala de Glasgow. 0 es normal |
| `sps` | Puntaje de gravedad del estudio SUPPORT |
| `aps` | Puntaje de gravedad APACHE III |
| `adlp`, `adls`, `adlsc` | Qué tanto depende de otros para actividades diarias |

```
   scoma        sps   aps  adlsc  hospdead  death
0    0.0  33.898438  20.0    7.0         0      0
1   44.0  52.695312  74.0    1.0         1      1
2    0.0  20.500000  45.0    0.0         0      1
```

El paciente 1 tiene `scoma` 44 y los puntajes más altos. Es el que murió.

### 5. Cuánto costó

| Columna | Qué es |
|---|---|
| `charges` | Lo que se le cobró al paciente en total |
| `totcst` | Costo total |
| `totmcst` | Costo total detallado |
| `avtisst` | Promedio de intervenciones, días 3 al 25 |

### 6. Decisiones y pronósticos

| Columna | Qué es |
|---|---|
| `dnr` | Si hay orden de no reanimar, y si se firmó antes o después de entrar |
| `dnrday` | Qué día se firmó |
| `surv2m`, `surv6m` | Probabilidad de sobrevivir 2 y 6 meses, según un modelo del estudio |
| `prg2m`, `prg6m` | Lo mismo, pero estimado por el médico que lo atendía |

Estos dos últimos grupos van a dar problema más adelante. Lo vemos en el lote 3.

---

## Las variables objetivo

El dataset trae **tres** columnas que podrían ser lo que queremos predecir.

| Columna | Qué significa |
|---|---|
| `death` | Murió en algún momento del seguimiento, que podía durar años |
| `hospdead` | Murió durante esa internación |
| `sfdm2` | Nivel de discapacidad en una entrevista a los 2 meses |

Elegimos **`hospdead`**.

Que sean distintas se ve en los datos. Miren al paciente 2 de la tabla de arriba:

```
   hospdead  death
2         0      1
```

Salió vivo del hospital (`hospdead` = 0) pero murió después (`death` = 1). Son preguntas diferentes.

`hospdead` se reparte así:

```
0    6745    (sobrevivió la internación)
1    2360    (murió en el hospital)
```

O sea, muere el **25.9%**. Es un problema de clasificación binaria, y las clases están desbalanceadas. Eso va a importar al final.

---

# El pipeline

Lo armamos en once archivos `.py` que se corren en orden. Le decimos lotes.

Cada lote guarda su resultado en un archivo y el siguiente lo levanta. Así, si algo falla en el paso 7, arreglamos el 7 y corremos solo el 7. No hay que rehacer todo.

```
python -m modularizado.pipeline           # corre todo
python -m modularizado.lote_07_atipicos   # corre solo uno
```

---

## Lote 1 — Descargar los datos

Baja el dataset directo desde UCI usando la librería `ucimlrepo`.

```python
from ucimlrepo import fetch_ucirepo

support2 = fetch_ucirepo(id=880)
datos = support2.data.features.join(support2.data.targets)
diccionario = support2.variables[["name", "role", "description"]]
```

El `join` pega las columnas de entrada con las columnas objetivo, porque UCI las entrega separadas.

También bajamos el **diccionario de variables**, que es la ficha oficial donde UCI explica qué es cada columna. Sirve para no adivinar.

Si no hay internet, el lote usa el archivo que ya está guardado y sigue.

---

## Lote 2 — Auditoría estadística

Antes de tocar nada, ver qué tenemos.

Primero hay que dejar los datos parejos:

```python
datos = pd.read_csv(ruta, na_values=["?", "NA", "N/A", "", "null"])
datos.columns = [c.strip().lower().replace(" ", "_").replace(".", "_")
                 for c in datos.columns]
```

Dos cosas pasan ahí:

- `na_values` le dice a pandas qué cosas tiene que contar como dato faltante. Si no lo ponemos, un `"?"` lo lee como texto válido.
- Renombrar las columnas. `num.co` tiene un punto en el medio y eso da problemas después. Queda `num_co`.

Después armamos una tabla con el estado de cada columna. Esto fue lo que nos salió:

```
columna    tipo     nulos  pct_nulos  unicos
   adlp float64      5641       62.0       8
  urine float64      4862       53.4    1494
glucose float64      4500       49.4     439
    bun float64      4352       47.8     159
totmcst float64      3475       38.2    5516
    alb float64      3372       37.0      60
 income  object      2982       32.8       4
   adls float64      2867       31.5       8
   bili float64      2601       28.6     295
   pafi float64      2325       25.5    1457
```

### Hallazgos

**Hay muchísimos datos faltantes.** No es un detalle: a `adlp` le falta el 62% de sus valores. A `glucose` y `bun`, que son análisis de sangre normales, casi la mitad.

Esto tiene explicación. A los pacientes de un estudio no les hacen todos los análisis. Si el médico no pidió la glucosa, no hay glucosa.

**Hay 12 columnas sin ningún hueco:**

```
adlsc, age, ca, death, dementia, diabetes, dzclass, dzgroup, hday,
hospdead, num_co, sex
```

Están las dos variables objetivo, que es lo importante. Si a `hospdead` le faltaran valores tendríamos un problema mucho más grande.

**`income` es la única categórica con muchos huecos**, 32.8%. Tiene sentido: es un dato que se pregunta y la gente no siempre contesta.

**Un detalle con el redondeo.** Hay 10 columnas (`scoma`, `sps`, `aps`, `meanbp`, `hrt`, `resp`, `temp`, `sod`, `surv2m`, `surv6m`) que en la tabla aparecen con 0.0% de nulos, pero no están vacías de huecos: cada una tiene exactamente 1.

Un solo valor sobre 9,105 filas da 0.01%, y al redondear a un decimal queda 0.0.

Fuimos a ver quiénes eran y son solo dos pacientes, las filas 5393 y 5440. A los dos les faltan 18 columnas de 45. Uno no tiene ningún puntaje de gravedad y el otro no tiene ningún signo vital.

Conviene mirar la columna `nulos` y no solo el porcentaje, porque el porcentaje redondeado esconde los casos chicos.

Sobre cómo se calcula el porcentaje: `datos[columna].isna()` devuelve `True` o `False` por cada fila. Al sacarle el promedio con `.mean()`, pandas cuenta `True` como 1 y `False` como 0, así que ya sale la proporción directo. Por 100 y queda en porcentaje.

---

## Lote 3 — Sacar las variables que no se pueden usar

Ya que definimos que la variable objetivo es `hospdead`, hay columnas que no podemos usar aunque parezcan datos normales.

El problema se llama **fuga de información**. Es cuando el modelo recibe, escondida en una columna, la respuesta que le estamos pidiendo adivinar. Entrena bárbaro y después en la vida real no sirve, porque ese dato no existe al momento de predecir.

Sacamos tres tipos.

### Las que son la respuesta

`death`, `sfdm2`, `surv2m`, `surv6m`, `prg2m`, `prg6m`.

`death` es casi la misma pregunta. `sfdm2` solo tiene valor si al paciente lo entrevistaron a los 2 meses, y eso solo pasa si sobrevivió: que tenga dato ya dice que no murió.

Las otras cuatro son estimaciones de supervivencia. Dos las calculó un modelo del estudio y dos las dio el médico. Usarlas sería copiarle la respuesta a alguien más.

Acá hay que tener cuidado con una cosa. La ficha de UCI dice que `surv2m` es *"predicted by a model"*, pero también dice lo mismo de `scoma` y de `sps`, y esas nos las quedamos. La diferencia no es quién las calculó, es **qué calculan**:

| Variable | Qué estima | |
|---|---|---|
| `surv2m`, `prg2m`... | Si el paciente va a vivir | se va |
| `scoma`, `sps` | Qué tan grave está hoy | se queda |

### Las repetidas

`dzclass` y `adls`.

Cruzamos `dzgroup` contra `dzclass` con `pd.crosstab`, que cuenta cuántas filas hay en cada combinación:

```
dzclass            ARF/MOSF  COPD/CHF/Cirrhosis  Cancer  Coma
dzgroup
ARF/MOSF w/Sepsis      3515                   0       0     0
CHF                       0                1387       0     0
COPD                      0                 967       0     0
Cirrhosis                 0                 508       0     0
Colon Cancer              0                   0     512     0
Coma                      0                   0       0   596
Lung Cancer               0                   0     908     0
MOSF w/Malig            712                   0       0     0
```

Cada fila tiene un solo número y el resto en cero. Eso quiere decir que `dzclass` no agrega nada, es un resumen de `dzgroup`. Nos quedamos con `dzgroup` que tiene más detalle.

Con `adls` pasa parecido: `adlsc` es la misma información ya calibrada y sin huecos.

### Las que se saben recién al final

Estas son las que más nos costó ver.

`dnr`, `dnrday`, `charges`, `totcst`, `totmcst`, `avtisst`.

**La orden de no reanimar.** Se firma cuando el equipo médico ya ve que el paciente se está muriendo. Los números:

```
                 sobrevive   muere
dnr after sadm      16.8%    77.9%
no dnr              80.8%    18.9%
```

De los que mueren, casi el 78% tiene una orden firmada después de entrar. No es un dato de ingreso, es una consecuencia de estar empeorando.

**Los costos.** Promedio de `charges`: 48,683 en los que sobreviven, 92,638 en los que mueren. Pero ese número no existe hasta que el paciente se va del hospital. Al momento de querer predecir, no lo tenemos.

**`avtisst`.** La ficha de UCI dice que TISS es *"un método para calcular costos en terapia intensiva"*. O sea que ni siquiera es un dato clínico.

### Un respaldo que encontramos en la ficha

El diccionario de UCI tiene 47 variables pero el CSV tiene 45. Las dos que faltan son `slos` (días hasta el alta) y `d.time` (días de seguimiento), y están marcadas con rol **"Other"**.

Eso significa que UCI mismo dice que no son predictoras, por la misma razón: la duración de la internación depende de cuándo terminó.

Así que el criterio que usamos no es invento nuestro. Es el que el repositorio ya venía usando y que dejó a medias.

---

## Lote 4 — Duplicados

Buscamos filas repetidas enteras.

```python
duplicados = datos.duplicated().sum()
datos = datos.drop_duplicates().reset_index(drop=True)
```

Resultado: **0 duplicados**. No había ninguna.

Igual dejamos el paso, y sobre todo lo dejamos **antes** de partir los datos. Si una fila estuviera repetida y quedara una copia en entrenamiento y otra en prueba, estaríamos evaluando el modelo con una fila que ya vio. Eso infla el resultado.

---

## Lote 5 — Partir en entrenamiento y prueba

Acá está la parte más importante de todo el pipeline, y la más fácil de hacer mal.

De acá en adelante varios pasos necesitan **aprender un número de los datos**: una mediana para rellenar, un límite para recortar, una lista de categorías para codificar.

Si esos números los calculamos con todos los datos, la información de las filas que después vamos a usar para *evaluar* ya se metió adentro del número. Eso también es fuga, pero no viene de una columna: viene del **orden en que hacemos las cosas**.

Por eso partimos primero.

```python
entrenamiento = datos.groupby("hospdead", group_keys=False).sample(
    frac=0.8, random_state=42
)
prueba = datos.drop(entrenamiento.index)
```

Qué hace cada cosa:

- `groupby("hospdead")` separa a los que murieron de los que no, y saca el 80% **de cada grupo por separado**. A eso se le dice partición estratificada. Sirve para que los dos conjuntos queden con la misma mezcla.
- `random_state=42` fija el azar. Si alguien más corre esto, le va a dar exactamente la misma partición.
- `drop(entrenamiento.index)` se queda con todo lo que no cayó en entrenamiento. Es más seguro que volver a sortear.

Nos quedó:

```
Entrenamiento: 7284 filas
Prueba:        1821 filas

Proporción de hospdead=1
  Total:          0.259
  Entrenamiento:  0.259
  Prueba:         0.259
```

Los tres iguales. La estratificación funcionó.

**Regla para el resto del pipeline:** todo lo que se calcule sale solo de entrenamiento, y se aplica igual a los dos.

---

## Lote 6 — Columnas con demasiados nulos

Medimos el porcentaje de faltantes, pero ahora **solo en entrenamiento**, siguiendo la regla de arriba.

Pusimos el corte en 50%. Si a una columna le falta más de la mitad, se va.

Se fueron dos:

| Columna | % nulos | Qué era |
|---|---|---|
| `adlp` | 61.8% | Índice de actividades diarias, contestado por el paciente |
| `urine` | 53.5% | Cantidad de orina producida en el día 3 |

### Por qué elegimos eso

`adlp` es una encuesta que el paciente tenía que contestar. Muchos estaban en coma o intubados, así que no la contestaron. Y de todas formas tenemos `adlsc`, que mide lo mismo y no tiene huecos.

`urine` es un dato clínico útil, pero rellenar más de la mitad de una columna es inventar más de lo que sabemos.

### Lo que quedó justo en el límite

`glucose` tiene 49.6% de faltantes y `bun` 47.9%. Pasaron el corte por poco.

Es una decisión discutible. Con un corte del 45% se hubieran ido también. Lo dejamos así pero vale saber que casi la mitad de esas dos columnas es un valor que pusimos nosotros.

---

## Lote 7 — Valores atípicos

Un valor atípico es un dato que se sale mucho del resto. Puede ser un error de carga, o puede ser un paciente que de verdad estaba muy mal.

### Con qué lo buscamos

Usamos el **rango intercuartílico**, que se abrevia RIC. La idea:

- **Q1** es el valor que deja al 25% de los datos por debajo.
- **Q3** es el que deja al 75% por debajo.
- El **RIC** es la distancia entre los dos. Ahí adentro está la mitad central de los datos.

Todo lo que quede más allá de **1.5 veces el RIC** para cualquiera de los dos lados se considera atípico.

```python
q1 = entrenamiento[columna].quantile(0.25)
q3 = entrenamiento[columna].quantile(0.75)
ric = q3 - q1
limite_inferior = q1 - 1.5 * ric
limite_superior = q3 + 1.5 * ric
```

El 1.5 es la convención de siempre, la misma que usa el diagrama de caja.

### Cómo justificamos el recorte

No borramos filas. Al valor que se pasa lo dejamos en el límite. A eso se le dice acotar, y en pandas es `.clip()`:

```python
entrenamiento[columna] = entrenamiento[columna].clip(lower=limite_inferior,
                                                    upper=limite_superior)
```

Preferimos acotar y no borrar porque borrar una fila entera por una sola columna rara es tirar a la basura los otros 40 datos de ese paciente.

Los límites salen **de entrenamiento** y se aplican a los dos conjuntos.

Esto es lo que nos salió (las que más se recortaron):

```
columna  atipicos_entrenamiento  atipicos_prueba  limite_inferior  limite_superior
  scoma                    1587              368           -13.50            22.50
   hday                    1222              321            -2.00             6.00
   crea                     788              199            -0.60             3.40
   bili                     760              166            -1.60             4.00
   wblc                     314               85            -5.45            27.75
   resp                     238               75             3.00            43.00
glucose                     216               49           -26.00           318.00
    bun                     207               60           -28.00            84.00
    sod                     203               53           123.50           151.50
   temp                      12                2            33.20            41.20
```

Un par de cosas de esa tabla:

Los límites de abajo salen negativos en varias (`crea` en -0.6, `glucose` en -26). No pasa nada: como ningún valor real es negativo, ese límite no recorta a nadie. Solo actúa el de arriba.

`scoma` y `hday` son las que más se recortan, y es porque están muy amontonadas. La mayoría de los pacientes tiene `scoma` en 0 y entró al estudio en su primer día de internación (`hday` = 1). Entonces los cuartiles quedan pegados y cualquier valor un poco distinto ya cae afuera.

En `sod` y `temp` se recorta de los dos lados, porque hay pacientes con sodio bajo y con hipotermia.

### Las binarias quedan afuera

`diabetes`, `dementia` y `hospdead` valen 0 o 1. En una columna así no existe el valor extremo, y si le aplicamos la regla podríamos borrar una de las dos categorías entera. Las salteamos.

### Un error que corregimos

Esto lo teníamos mal al principio y lo encontramos revisando.

Estábamos rellenando los huecos **antes** de recortar. El problema: si a una columna le falta la mitad y la rellenamos con la mediana, entonces la mitad de la columna **es** la mediana. Los cuartiles se juntan en el centro, el RIC casi desaparece y los límites salen ridículos.

| Columna | % nulos | Límites bien | Límites que nos salían |
|---|---|---|---|
| `glucose` | 49.6% | -26 a 318 | 131 a 139 |
| `bun` | 47.9% | -28 a 84 | 19 a 27 |
| `crea` | 0.6% | -0.6 a 3.4 | -0.6 a 3.4 |

Con los límites malos, un paciente con glucosa en 300 quedaba aplastado en 139. Se recortaban 3,509 filas en vez de 216.

Fíjense en `crea`, que casi no tiene huecos: ahí los límites no cambian. Eso es lo que nos confirmó que el problema era el relleno y no otra cosa.

La solución fue solo cambiar el orden: **recortar primero, rellenar después.**

---

## Lote 8 — Imputación

Imputar es rellenar los huecos. Elegimos dos métodos distintos según el tipo de columna.

### Numéricas: mediana

```python
mediana = entrenamiento[columna].median()
entrenamiento[columna] = entrenamiento[columna].fillna(mediana)
prueba[columna] = prueba[columna].fillna(mediana)
```

Usamos mediana y no promedio porque la mediana no se mueve por los valores extremos. Si hay un paciente con glucosa 1092, el promedio se estira, la mediana no.

Los valores que se usaron:

| Columna | Mediana | Huecos que rellenó |
|---|---|---|
| `glucose` | 135.0 | 3,610 |
| `bun` | 23.0 | 3,489 |
| `alb` | 2.9 | 2,686 |
| `pafi` | 224.0 | 1,869 |
| `ph` | 7.42 | 1,841 |
| `edu` | 12.0 | 1,312 |

### Categóricas: moda

La moda es el valor que más se repite.

| Columna | Moda | Huecos que rellenó |
|---|---|---|
| `income` | `under $11k` | 2,366 |
| `race` | `white` | 33 |
| `ca` | `no` | 0 |

### Lo importante

El número sale de entrenamiento y se usa para los dos conjuntos. No calculamos una mediana nueva para prueba, porque eso sería usar información de prueba.

### Una limitación

En `income` rellenamos 2,366 filas con `under $11k`. Es mucho. Estamos asumiendo que el que no contestó es de ingreso bajo, y eso no necesariamente es cierto.

Una opción mejor sería agregar una columna que marque si el dato faltaba, así el modelo puede usar esa ausencia como información. No lo hicimos, pero queda anotado.

---

## Lote 9 — Codificar las categorías

Los modelos trabajan con números. `dzgroup` dice `"Lung Cancer"`, así que hay que convertirlo.

### Primero fijamos las categorías

```python
categorias = sorted(entrenamiento[columna].dropna().unique().tolist())
entrenamiento[columna] = pd.Categorical(entrenamiento[columna], categories=categorias)
prueba[columna] = pd.Categorical(prueba[columna], categories=categorias)
```

Esto es para que las dos tablas terminen con exactamente las mismas columnas. Si en prueba apareciera una categoría que no está en entrenamiento, el lote avisa. En nuestro caso no pasó.

### Después codificamos

```python
entrenamiento = pd.get_dummies(entrenamiento, columns=categoricas, drop_first=True)
prueba = pd.get_dummies(prueba, columns=categoricas, drop_first=True)
prueba = prueba.reindex(columns=entrenamiento.columns, fill_value=0)
```

### Qué le pasó a cada variable

Se codificaron 5 columnas: `sex`, `dzgroup`, `income`, `race` y `ca`.

Un ejemplo con los tres pacientes de siempre.

Antes:

```
      sex      dzgroup          ca
0    male  Lung Cancer  metastatic
1  female    Cirrhosis          no
2  female    Cirrhosis          no
```

Después:

```
   sex_male  dzgroup_Lung Cancer  ca_no
0         1                    1      0
1         0                    0      1
2         0                    0      1
```

`sex` tenía dos valores y quedó en una sola columna: 1 es hombre, 0 es mujer.

`dzgroup` tenía 8 y quedó en 7 columnas, una por categoría menos la primera.

### Por qué `drop_first=True`

Descarta la primera categoría de cada variable. No perdemos información: si un paciente tiene 0 en todas las columnas de `dzgroup`, ya sabemos que es de la que sacamos.

Dejarla sería repetir un dato, y a algunos modelos eso les molesta.

Al final `reindex` acomoda prueba para que tenga las mismas columnas en el mismo orden que entrenamiento.

De 29 columnas pasamos a 41.

---

## Lote 10 — Guardar el resultado

Ponemos `hospdead` al final, que es la convención, y guardamos.

```python
orden = [c for c in datos.columns if c != "hospdead"] + ["hospdead"]
```

| Archivo | Filas | Columnas | Faltantes |
|---|---|---|---|
| `support2_train.csv` | 7,284 | 41 | 0 |
| `support2_test.csv` | 1,821 | 41 | 0 |

Las 41 columnas finales:

```
age, num_co, edu, scoma, sps, aps, hday, diabetes, dementia, meanbp, wblc,
hrt, resp, temp, pafi, alb, bili, crea, sod, ph, glucose, bun, adlsc,
sex_male, dzgroup_CHF, dzgroup_COPD, dzgroup_Cirrhosis, dzgroup_Colon Cancer,
dzgroup_Coma, dzgroup_Lung Cancer, dzgroup_MOSF w/Malig, income_$25-$50k,
income_>$50k, income_under $11k, race_black, race_hispanic, race_other,
race_white, ca_no, ca_yes, hospdead
```

---

## Lote 11 — Validación

Este lote no transforma nada. Vuelve a abrir los dos archivos ya guardados y revisa que estén bien.

Lo agregamos porque nos dimos cuenta de que nada comprobaba el resultado. El pipeline terminaba imprimiendo un resumen y listo.

Qué revisa:

- Que no queden valores faltantes.
- Que todas las columnas sean numéricas.
- Que los dos archivos tengan las mismas columnas en el mismo orden.
- Que `hospdead` esté al final y valga solo 0 o 1.
- Que no haya columnas constantes ni repetidas, que no le sirven a nadie.
- Que ninguna fila de prueba esté también en entrenamiento.
- Que la proporción de muertos sea parecida en los dos.

Si algo falla corta con error. Hoy pasa todo.

---

# Modelos base

Con los archivos listos, entrenamos algunos modelos para ver de dónde partimos.

Usamos validación cruzada de 5 particiones sobre entrenamiento, y después medimos en prueba.

El escalado va adentro del pipeline de sklearn, no antes:

```python
Pipeline([("escalado", StandardScaler()), ("modelo", LogisticRegression())])
```

Es la misma idea del lote 5. Si escalamos antes, el escalador aprende de todos los datos.

## Resultados

| Modelo | AUC | Exactitud | Precisión (muere) | Recall (muere) |
|---|---|---|---|---|
| Logística | 0.879 | 0.827 | 0.736 | 0.519 |
| Logística balanceada | 0.879 | 0.791 | 0.569 | 0.790 |
| Bosque aleatorio | 0.870 | 0.826 | 0.752 | 0.489 |
| Boosting | 0.866 | 0.824 | 0.718 | 0.528 |
| Árbol | 0.847 | 0.807 | 0.701 | 0.447 |
| Referencia | 0.500 | 0.741 | 0.000 | 0.000 |

La fila de abajo es un modelo tonto que contesta siempre "sobrevive". Acierta el **74.1%**.

Lo pusimos a propósito, porque muestra que la exactitud sola no sirve para nada acá. Un modelo que no hace nada ya llega a 74%.

## El problema que sigue

La logística detecta solo el **51.9%** de los pacientes que mueren. Se le escapa casi la mitad.

Poniéndole `class_weight="balanced"`, que hace que los casos de la clase chica pesen más, el recall sube a **79.0%**. Pero la precisión baja de 0.736 a 0.569, o sea que se llena de falsas alarmas.

Ese intercambio es la decisión que viene: ¿qué es peor, avisar de más o dejar pasar a un paciente grave?

---

# Cierre

Lo que hicimos:

- Los pasos de siempre del preprocesamiento, en orden y sin saltearnos ninguno.
- Revisamos el resultado y encontramos dos errores propios, que corregimos: el orden del recorte de atípicos y seis columnas que le pasaban la respuesta al modelo.
- Agregamos una validación para que no se nos escape un archivo roto.
- Contrastamos todo contra el diccionario oficial de UCI.
- Dejamos los modelos base corriendo.

Un dato para cerrar. Antes de sacar las seis columnas con fuga, el modelo daba **AUC 0.948**. Después dio **0.879**.

Parece que empeoró, pero es al revés: los modelos publicados sobre este mismo dataset andan entre 0.80 y 0.86. El 0.95 era demasiado bueno para ser verdad. No estaba prediciendo la muerte, la estaba leyendo.
