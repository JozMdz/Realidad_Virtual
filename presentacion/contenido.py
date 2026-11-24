# -*- coding: utf-8 -*-
# Contenido de la presentacion del proyecto integrador.
# Cada entrada: (tipo, titulo, cuerpo, extra)

import os
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "documentos", "figuras") + os.sep

# B = parrafo en negrita (encabezado interno); 0/1/2 = nivel de vineta
SLIDES = [

("texto", "Introducción", [
    ("B", "El conjunto de datos"),
    (0, "Proviene del estudio Study to Understand Prognoses and Preferences for Outcomes "
        "and Risks of Treatments, sobre el pronóstico de pacientes hospitalizados con "
        "enfermedades graves."),
    (0, "9,105 registros y 45 columnas; cada registro corresponde a un paciente hospitalizado."),
    (0, "Ocho grupos diagnósticos: insuficiencia respiratoria aguda con sepsis, insuficiencia "
        "cardíaca congestiva, EPOC, cirrosis, cáncer de colon, cáncer de pulmón, coma y fallo "
        "multiorgánico con neoplasia."),
    ("B", "La situación a resolver"),
    (0, "El archivo original presenta valores ausentes, variables categóricas en texto y "
        "columnas que anticipan el desenlace que se pretende predecir."),
    (0, "Se requiere transformarlo en dos conjuntos numéricos y completos, aptos para entrenar "
        "y evaluar un clasificador."),
], None),

("texto", "Planteamiento del problema", [
    ("B", "Tarea"),
    (0, "Predecir hospdead: si el paciente falleció durante la hospitalización analizada."),
    (0, "La variable admite dos valores y está registrada en la totalidad de los casos. "
        "Corresponde por tanto a clasificación binaria supervisada."),
    ("B", "Conjunto resultante"),
    (0, "7,284 registros de entrenamiento y 1,821 de prueba, con 40 variables de entrada."),
    (0, "Todas numéricas y sin valores ausentes."),
    ("B", "Condición que determina la lectura de los resultados"),
    (0, "Las clases están desbalanceadas: los fallecimientos representan el 25.9%."),
    (0, "Un clasificador que asignara siempre la clase mayoritaria acertaría en el 74.1% de los "
        "casos sin utilizar información alguna."),
], None),

("texto", "Objetivos", [
    ("B", "Objetivo general"),
    (0, "Construir y evaluar un clasificador que prediga el fallecimiento durante la "
        "hospitalización a partir de la información disponible al ingreso."),
    ("B", "Objetivos específicos"),
    (0, "Transformar el archivo original en conjuntos numéricos y completos aptos para el "
        "entrenamiento y la evaluación."),
    (0, "Determinar qué variables constituyen información legítima de entrada y cuáles "
        "anticipan el desenlace."),
    (0, "Entrenar clasificadores con mecanismos de decisión distintos, acompañados de un modelo "
        "de referencia que no aprende de los datos."),
    (0, "Evaluar el desempeño con métricas adecuadas al desbalance y determinar si las "
        "diferencias observadas son estadísticamente significativas."),
], None),

("diagrama", "Metodología", [], (FIG + "flujo.png", 1.85, 1.85, 9.62, 3.85,
  "Estructura secuencial del preprocesamiento. Las etapas destacadas corresponden a las dos "
  "decisiones que condicionan la validez del resultado.")),

("texto", "Las dos decisiones críticas", [
    ("B", "Fuga por columna"),
    (0, "Catorce columnas excluidas. Seis de ellas —dnr, dnrday, charges, totcst, totmcst y "
        "avtisst— registran hechos posteriores al ingreso."),
    ("B", "Fuga por orden de operaciones"),
    (0, "El acotamiento de valores atípicos se ejecuta antes de la imputación."),
    (0, "El orden inverso, aparentemente equivalente, habría acotado 18,507 registros en lugar "
        "de 6,477, suprimiendo valores dentro del recorrido observado."),
    ("B", "Ninguna de las dos produce error visible: su detección exige examinar el significado "
          "de cada variable y el momento en que cada operación se ejecuta."),
], ("tabla", ["Conjunto de variables", "Columnas", "AUC"],
    [["Con las variables posteriores al ingreso", "48", "0.948"],
     ["Sin las variables posteriores al ingreso", "41", "0.879"]],
    "Efecto de las variables posteriores al ingreso sobre el desempeño. El modelo pronóstico del "
    "propio estudio alcanza 0.841 y la estimación del médico tratante 0.814.")),

("texto", "Protocolo de trabajo", [
    ("B", "Organización"),
    (0, "Once lotes secuenciales: cada etapa recibe el resultado de la anterior y produce un "
        "archivo intermedio, de modo que cualquiera puede ejecutarse o revisarse de manera "
        "aislada."),
    ("B", "Partición"),
    (0, "80/20 estratificada con semilla fija. La verificación de duplicados se ejecuta antes de "
        "particionar, para que ninguna fila repetida quede en ambos conjuntos."),
    ("B", "Ajuste de parámetros"),
    (0, "Medianas, límites de acotamiento y repertorios de categorías se calculan exclusivamente "
        "sobre el conjunto de entrenamiento y se aplican sin recalcular sobre el de prueba."),
    ("B", "Estandarización"),
    (0, "Incorporada al flujo de modelado y no al archivo: el escalador se ajusta sobre los "
        "datos de entrenamiento de cada partición."),
    ("B", "Validación"),
    (0, "Validación cruzada estratificada de diez particiones sobre el conjunto de entrenamiento. "
        "El conjunto de prueba se reserva para la evaluación final."),
], None),

("texto", "Origen y explicación de los datos", [
    ("B", "Procedencia"),
    (0, "Estudio SUPPORT. La ficha del repositorio documenta 47 variables; slos y d.time no "
        "están presentes en el archivo distribuido, que contiene las 45 restantes."),
    ("B", "Contenido de las variables de entrada"),
    (1, "Datos demográficos y de contexto social."),
    (1, "Información diagnóstica."),
    (1, "Puntajes de severidad medidos al tercer día del estudio."),
    (1, "Signos vitales y resultados de laboratorio."),
    (1, "Indicadores de funcionalidad en actividades de la vida diaria."),
    ("B", "Elección de la variable objetivo"),
    (0, "El conjunto admite tres: death, hospdead y sfdm2. Se seleccionó hospdead por tratarse "
        "de un desenlace delimitado temporalmente y observable para la totalidad de los registros."),
], None),

("figura", "La variable objetivo", [
    ("B", "hospdead"),
    (0, "Registra el fallecimiento durante la hospitalización analizada."),
    ("B", "Distribución en el conjunto de entrenamiento"),
    (0, "Los fallecimientos constituyen aproximadamente una cuarta parte de los casos."),
    (0, "El desbalance condiciona la elección de las métricas de evaluación: la exactitud por sí "
        "sola resulta insuficiente."),
], (FIG + "clases.png", 6.95, 2.30, 6.00, 3.10,
  "Distribución de la variable objetivo hospdead en el conjunto de entrenamiento.")),

("texto", "Limpieza", [
    ("B", "Registros duplicados"),
    (0, "El conjunto no presentó filas idénticas; las 9,105 originales se conservaron íntegramente."),
    ("B", "Columnas con exceso de valores ausentes"),
    (0, "Umbral del 50%. Excluidas adlp, con 61.8%, y urine, con 53.5%. Imputar más de la mitad "
        "de una columna describiría el procedimiento de imputación antes que el fenómeno medido."),
    ("B", "Valores atípicos"),
    (0, "Acotamiento por rango intercuartílico con factor 1.5. Los valores fuera del intervalo se "
        "llevan al límite en lugar de eliminarse, lo que preserva el tamaño del conjunto."),
    (0, "Se excluyen las columnas binarias: 20 de las 21 columnas numéricas evaluadas presentaron "
        "registros fuera de los límites."),
    ("B", "Imputación"),
    (0, "Mediana para las numéricas y moda para las categóricas, calculadas sobre entrenamiento. "
        "Se completaron 24,379 valores ausentes."),
], None),

("texto", "Transformación", [
    ("B", "Codificación de variables categóricas"),
    (0, "Cinco variables en texto: sex, ca, income, race y dzgroup."),
    (0, "El repertorio de categorías se fija en entrenamiento y se impone a prueba, de modo que "
        "ambos conjuntos generen las mismas columnas en el mismo orden."),
    (0, "Codificación indicadora con descarte de la primera categoría. El número de columnas "
        "pasó de 29 a 41."),
    ("B", "Estandarización de escalas"),
    (0, "Las unidades difieren considerablemente: la edad abarca de 21 a 102 años; el pH se "
        "concentra en un rango intercuartílico inferior a una décima; la glucosa alcanza 318 "
        "tras el acotamiento."),
    (0, "No se aplicó al archivo sino al flujo de modelado, porque su necesidad depende del "
        "algoritmo y el escalador debe ajustarse por partición."),
], None),

("texto", "Reducción de la dimensionalidad", [
    ("B", "Reducción aplicada"),
    (0, "Operó por criterio sobre el significado de cada variable, no por proyección algebraica: "
        "catorce columnas excluidas por fuga o redundancia más dos por exceso de ausentes."),
    (0, "El conjunto pasó de 45 a 29 columnas previas a la codificación."),
    ("B", "Componentes principales"),
    (0, "El primer componente explica el 8.4% de la varianza y se requieren 24 de 40 componentes "
        "para alcanzar el 80%: el conjunto no presenta redundancia lineal concentrada."),
], ("tabla", ["Variables", "Componentes principales", "Selección directa"],
    [["40 (todas)", "0.8791", "0.8791"], ["30", "0.8779", "0.8798"],
     ["20", "0.8663", "0.8723"], ["10", "0.8620", "0.8723"], ["5", "0.8517", "0.8691"]],
    "Componentes principales frente a selección directa de variables. AUC sobre el conjunto de "
    "prueba; se conservaron las 40 variables.")),

("texto", "Modelos y algoritmos aplicados", [
    ("B", "Por qué tres modelos y no uno"),
    (0, "El desempeño de un modelo aislado no permite distinguir si el algoritmo es adecuado "
        "para el problema o si la señal predictiva está en los datos con independencia del "
        "algoritmo. Comparar mecanismos de decisión distintos separa ambos efectos."),
    (1, "La regresión logística construye una frontera lineal: pondera cada variable y combina "
        "las ponderaciones en una única puntuación."),
    (1, "El árbol de decisión construye reglas: formula preguntas encadenadas sobre una variable "
        "por vez."),
    (1, "Los vecinos más cercanos no construyen regla alguna: clasifican cada caso según los "
        "registros que más se le parecen."),
], ("tabla", ["Modelo", "Configuración", "Escalado"],
    [["Regresión logística", "Penalización L2, hasta 3000 iteraciones", "Sí"],
     ["Árbol de decisión", "Profundidad máxima 5, criterio Gini", "No"],
     ["Vecinos más cercanos", "25 vecinos, distancia euclidiana", "Sí"],
     ["Referencia trivial", "Predice siempre la clase mayoritaria", "No"]],
    "Configuración de los modelos evaluados.")),

("figura", "Regresión logística", [
    ("B", "Mecanismo"),
    (0, "Pondera cada variable y combina las ponderaciones en una única puntuación."),
    ("B", "Variables de mayor peso"),
    (0, "Los dos coeficientes mayores corresponden a sps y aps, los puntajes de fisiología "
        "medidos al tercer día, seguidos por el indicador de coma y el puntaje scoma."),
    (0, "El modelo concede el mayor peso a las mediciones de gravedad clínica."),
    (0, "Entre los coeficientes negativos figuran indicadores de grupo diagnóstico: "
        "insuficiencia cardíaca congestiva, cáncer de colon y EPOC."),
], (FIG + "coeficientes.png", 6.95, 1.85, 6.05, 3.60,
  "Coeficientes de mayor magnitud de la regresión logística. En rojo los que incrementan el "
  "riesgo estimado, en azul los que lo reducen.")),

("figura", "Árbol de decisión", [
    ("B", "Mecanismo"),
    (0, "Formula preguntas encadenadas sobre una variable por vez."),
    ("B", "Profundidad"),
    (0, "Fijada en cinco niveles, que producen 32 hojas. Un árbol sin restricción sigue "
        "dividiendo mientras encuentre separaciones útiles en entrenamiento, con riesgo de "
        "ajustarse a él en lugar de generalizar."),
    ("B", "Estructura obtenida"),
    (0, "La primera división utiliza aps con un umbral de 50.5; las subsiguientes recurren a "
        "scoma y sps."),
    ("B", "Sin estandarización"),
    (0, "El árbol compara cada valor contra un umbral, operación que no se altera al restar la "
        "media y dividir por la desviación."),
], (FIG + "arbol.png", 6.90, 2.20, 6.15, 3.20,
  "Primeros dos niveles del árbol de decisión. La profundidad completa es de cinco niveles y "
  "32 hojas.")),

("figura", "Vecinos más cercanos", [
    ("B", "Mecanismo"),
    (0, "Clasifica cada caso según los registros que más se le parecen; requiere estandarización, "
        "dado que la distancia depende de las unidades."),
    ("B", "Selección del número de vecinos"),
    (0, "Determinado por validación cruzada sobre el conjunto de entrenamiento, no sobre el de "
        "prueba."),
    (0, "El AUC aumenta de forma sostenida: 0.762 con cinco vecinos, 0.817 con veinticinco y "
        "0.833 con doscientos uno."),
    (0, "Se adoptó k = 25 por constituir un valor intermedio que conserva el carácter local del "
        "método."),
], (FIG + "vecinos.png", 6.95, 2.15, 6.00, 3.15,
  "AUC promedio en validación cruzada según el número de vecinos.")),

("texto", "Resultados en el conjunto de prueba", [
    ("B", "1,821 registros que no intervinieron en el entrenamiento ni en la elección de los "
          "hiperparámetros."),
    (0, "La regresión logística obtiene el mayor AUC. Los tres modelos superan la referencia "
        "trivial, cuyo AUC es 0.500."),
    (0, "La exactitud de 0.741 de la referencia ilustra por qué esa métrica resulta insuficiente "
        "en conjuntos desbalanceados."),
], ("tabla", ["Modelo", "AUC", "Exactitud", "Precisión", "Recall", "F1"],
    [["Regresión logística", "0.879", "0.827", "0.736", "0.519", "0.609"],
     ["Árbol de decisión", "0.847", "0.807", "0.701", "0.447", "0.546"],
     ["Vecinos más cercanos", "0.835", "0.797", "0.721", "0.356", "0.477"],
     ["Referencia trivial", "0.500", "0.741", "0.000", "0.000", "0.000"]],
    "Métricas sobre el conjunto de prueba. Precisión, recall y F1 corresponden a la clase fallece.")),

("figura", "Curvas ROC", [
    ("B", "Qué describe el AUC"),
    (0, "La capacidad de ordenar a los pacientes por riesgo, con independencia del umbral de "
        "decisión."),
    ("B", "Lectura de la figura"),
    (0, "La curva de la regresión logística domina a las otras dos en prácticamente todo el "
        "recorrido."),
    (0, "La diagonal corresponde al modelo de referencia, que no ordena."),
    ("B", "Lo que el AUC no informa"),
    (0, "El comportamiento en el umbral de decisión, que es donde el ordenamiento se traduce en "
        "una predicción."),
], (FIG + "roc.png", 7.05, 1.70, 5.80, 3.60,
  "Curvas ROC sobre el conjunto de prueba. La diagonal corresponde a un clasificador que no "
  "ordena.")),

("texto", "Matrices de confusión", [
    ("B", "Qué tipo de error comete cada modelo"),
    (0, "La regresión logística detecta 245 de los 472 fallecimientos del conjunto de prueba."),
    (0, "Los vecinos más cercanos producen menos falsas alarmas que los otros dos, pero dejan sin "
        "detectar 304 fallecimientos."),
    (0, "La diferencia entre modelos se concentra en los falsos negativos, que son los casos de "
        "mayor costo en este problema."),
], ("tabla", ["Modelo", "VN", "FP", "FN", "VP"],
    [["Regresión logística", "1261", "88", "227", "245"],
     ["Árbol de decisión", "1259", "90", "261", "211"],
     ["Vecinos más cercanos", "1284", "65", "304", "168"]],
    "Matrices de confusión sobre el conjunto de prueba. VN y VP son los aciertos; FP las falsas "
    "alarmas y FN los fallecimientos no detectados.")),

("texto", "Pruebas de significancia", [
    ("B", "Estabilidad"),
    (0, "En las diez particiones de validación cruzada la regresión logística obtiene el mayor "
        "AUC en todas, con un promedio de 0.854 frente a 0.817 de los otros dos."),
    ("B", "Friedman"),
    (0, "Sobre los diez resultados por modelo: χ² = 15.000 con p = 0.0006. Existe al menos una "
        "diferencia entre los tres."),
    ("B", "Wilcoxon y McNemar"),
    (0, "Wilcoxon compara los AUC por partición; McNemar, los aciertos y errores caso por caso "
        "sobre el conjunto de prueba. Ambas con corrección de Bonferroni para tres comparaciones."),
], ("tabla", ["Comparación", "Wilcoxon", "Aciertos exclusivos", "McNemar"],
    [["Regresión logística vs. Árbol", "0.0059*", "95 / 59", "0.0139*"],
     ["Regresión logística vs. Vecinos", "0.0059*", "123 / 69", "0.0004*"],
     ["Árbol vs. Vecinos", "1.0000", "118 / 100", "0.7485"]],
    "Comparación por pares. Los valores p incluyen corrección de Bonferroni para tres "
    "comparaciones; el asterisco indica significancia al 5%.")),

("texto", "El problema del recall", [
    ("B", "El mejor modelo identifica el 51.9% de los pacientes que fallecen."),
    (0, "El resultado es consistente con el desbalance: el umbral predeterminado de 0.5 deja "
        "fuera a buena parte de la clase minoritaria."),
    ("B", "Ponderación de clases"),
    (0, "Al pesar más los errores sobre la clase minoritaria, el punto de operación se desplaza: "
        "el recall asciende a 0.790 y la precisión desciende a 0.569."),
    (0, "El AUC se mantiene en 0.879: la ponderación no altera el ordenamiento por riesgo, sino "
        "el umbral a partir del cual ese ordenamiento se traduce en una decisión."),
    ("B", "La elección entre ambas configuraciones no se resuelve con criterios estadísticos: "
          "requiere determinar el costo de una falsa alarma frente al de un fallecimiento no "
          "detectado."),
], ("tabla", ["Configuración", "AUC", "Exactitud", "Precisión", "Recall"],
    [["Sin ponderación", "0.879", "0.827", "0.736", "0.519"],
     ["Con ponderación balanceada", "0.879", "0.791", "0.569", "0.790"]],
    "Efecto de la ponderación de clases sobre la regresión logística, sobre el conjunto de prueba.")),

("texto", "Recomendaciones de mejora", [
    ("B", "1. Fijar el umbral según el costo de cada error"),
    (0, "La ponderación de clases eleva el recall de 0.519 a 0.790. La decisión corresponde al "
        "contexto de aplicación, no al modelo."),
    ("B", "2. Incorporar la ausencia como información"),
    (0, "Añadir una variable indicadora de ausencia por columna, de modo que el modelo pueda "
        "utilizarla; la imputación por mediana concentra masa en un único valor."),
    ("B", "3. Evaluar la reducción sobre un conjunto independiente"),
    (0, "La comparación entre componentes principales y selección directa se realizó sobre el "
        "conjunto de prueba, de modo que la decisión de conservar las 40 variables no es "
        "independiente de él."),
    ("B", "4. Revisar el umbral de valores ausentes"),
    (0, "glucose, con 49.6%, y bun, con 47.9%, se sitúan próximas al límite del 50%: un umbral "
        "del 45% las habría excluido."),
    ("B", "5. Extender la validación al significado y al orden"),
    (0, "Las comprobaciones actuales verifican la forma del resultado; ninguna rechazaría una "
        "fuga de información."),
], None),

("texto", "Conclusiones", [
    ("B", "Sobre el preprocesamiento"),
    (0, "El resultado estuvo determinado principalmente por dos decisiones que no corresponden a "
        "limpieza, transformación ni reducción, sino al criterio sobre qué información es "
        "admisible y en qué orden debe procesarse."),
    (0, "Ambas producen archivos que ninguna comprobación de forma podría rechazar, y la primera "
        "genera además un modelo aparentemente superior."),
    ("B", "Sobre los modelos"),
    (0, "La regresión logística supera a los otros dos y la diferencia es estadísticamente "
        "significativa por ambos procedimientos."),
    (0, "El árbol y los vecinos no se distinguen entre sí: la diferencia de doce milésimas de AUC "
        "no sobrevive a las pruebas de significancia."),
    ("B", "Sobre la evaluación"),
    (0, "La exactitud resulta insuficiente; el AUC describe el ordenamiento pero no el umbral. "
        "La matriz de confusión y el par precisión–recall son los que permiten determinar qué "
        "tipo de error comete cada modelo."),
], None),
]
