# Presentación del proyecto integrador

Mazo de 26 diapositivas armado sobre la plantilla institucional de la Facultad de
Ingeniería Tampico, con el contenido de los tres informes de `documentos/`.

## Archivos

| Archivo | Contenido |
|---|---|
| `plantilla.pptx` | Plantilla institucional: portada, contraportada y los seis diseños |
| `contenido.py` | Texto, tablas y figuras de cada diapositiva |
| `construir.py` | Arma el mazo sobre la plantilla y escribe `proyecto_integrador.pptx` |
| `generar_flujo.py` | Genera `documentos/figuras/flujo.png`, el diagrama de las once etapas |
| `proyecto_integrador.pptx` | Mazo generado |

## Uso

```bash
python3 generar_flujo.py
python3 construir.py
```

## Estructura del mazo

1. Portada y contenido
2. Introducción y planteamiento del problema
3. Objetivos
4. Metodología: diagrama de las once etapas, las dos decisiones críticas y el protocolo
5. Origen y explicación de los datos, variable objetivo
6. Limpieza, transformación y reducción de la dimensionalidad
7. Modelos y algoritmos: regresión logística, árbol de decisión y vecinos más cercanos
8. Resultados, curvas ROC, matrices de confusión y pruebas de significancia
9. Recomendaciones de mejora y conclusiones
10. Referencias y contraportada

Las cifras provienen de `modularizado/` y de las tablas de `documentos/tablas/`.
