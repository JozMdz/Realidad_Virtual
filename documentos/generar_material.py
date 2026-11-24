"""Genera las figuras y las tablas LaTeX que usan los documentos."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from modularizado import config

RAIZ = Path(__file__).resolve().parent
FIGURAS = RAIZ / "figuras"
TABLAS = RAIZ / "tablas"

# Traduccion de las descripciones de la ficha oficial de UCI. Cada entrada
# corresponde al texto de support/diccionario_variables.csv; el script falla si
# alguna columna del csv no tiene su equivalente, para que la tabla no contenga
# descripciones inventadas.
TRADUCCIONES = {
    "age": "Edad del paciente en años",
    "death": "Fallecimiento en cualquier momento hasta el registro del National Death "
             "Index al 31 de diciembre de 1994",
    "sex": "Sexo del paciente",
    "hospdead": "Fallecimiento durante la hospitalización",
    "slos": "Días desde el ingreso al estudio hasta el alta",
    "d_time": "Días de seguimiento",
    "dzgroup": "Subcategoría de enfermedad del paciente",
    "dzclass": "Categoría de enfermedad del paciente",
    "num_co": "Número de enfermedades simultáneas o comorbilidades",
    "edu": "Años de educación",
    "income": "Ingreso del paciente",
    "scoma": "Puntaje de coma SUPPORT al día 3, basado en la escala de Glasgow "
             "(estimado por un modelo)",
    "charges": "Cobro hospitalario",
    "totcst": "Costo total según la razón costo-cobro (RCC)",
    "totmcst": "Costo total por micro-costeo",
    "avtisst": "Puntaje TISS promedio de los días 3 al 25, método de costeo de "
               "intervenciones terapéuticas",
    "race": "Raza del paciente",
    "sps": "Puntaje de fisiología SUPPORT al día 3 (estimado por un modelo)",
    "aps": "Puntaje de fisiología APACHE III al día 3",
    "surv2m": "Estimación de supervivencia a 2 meses del modelo SUPPORT al día 3",
    "surv6m": "Estimación de supervivencia a 6 meses del modelo SUPPORT al día 3",
    "hday": "Día de hospitalización en que el paciente ingresó al estudio",
    "diabetes": "Presencia de diabetes como comorbilidad",
    "dementia": "Presencia de demencia como comorbilidad",
    "ca": "Presencia de cáncer: sí, metastásico o no",
    "prg2m": "Estimación del médico sobre la supervivencia a 2 meses",
    "prg6m": "Estimación del médico sobre la supervivencia a 6 meses",
    "dnr": "Existencia de orden de no reanimar",
    "dnrday": "Día de la orden de no reanimar; negativo si es previa al estudio",
    "meanbp": "Presión arterial media, medida al día 3",
    "wblc": "Recuento de glóbulos blancos en miles, medido al día 3",
    "hrt": "Frecuencia cardíaca, medida al día 3",
    "resp": "Frecuencia respiratoria, medida al día 3",
    "temp": "Temperatura en grados Celsius, medida al día 3",
    "pafi": "Razón PaO$_2$/FiO$_2$, medida al día 3",
    "alb": "Albúmina sérica, medida al día 3",
    "bili": "Bilirrubina, medida al día 3",
    "crea": "Creatinina sérica, medida al día 3",
    "sod": "Concentración sérica de sodio, medida al día 3",
    "ph": "pH de la sangre arterial",
    "glucose": "Glucosa, medida al día 3",
    "bun": "Nitrógeno ureico en sangre, medido al día 3",
    "urine": "Volumen de orina, medido al día 3",
    "adlp": "Índice de actividades de la vida diaria, respondido por el paciente",
    "adls": "Índice de actividades de la vida diaria, respondido por un allegado",
    "sfdm2": "Nivel de discapacidad funcional en escala de 1 a 5",
    "adlsc": "Índice de actividades de la vida diaria imputado y calibrado al allegado",
}

ROLES = {"Feature": "Entrada", "Target": "Objetivo", "Other": "Otro"}


def cargar_diccionario():
    """Lee la ficha oficial de UCI y devuelve el rol y la descripcion de cada variable."""
    if not config.RUTA_DICCIONARIO.exists():
        raise FileNotFoundError(
            f"Falta {config.RUTA_DICCIONARIO}. Ejecutar antes el lote 1 con conexion a UCI."
        )
    ficha = pd.read_csv(config.RUTA_DICCIONARIO)
    ficha["name"] = [
        n.strip().lower().replace(" ", "_").replace(".", "_") for n in ficha["name"]
    ]
    return ficha.set_index("name")


def cargar_crudo():
    """Lee el csv original con los nombres de columna ya estandarizados."""
    datos = pd.read_csv(config.RUTA_CSV, na_values=config.VALORES_NULOS)
    datos.columns = [c.strip().lower().replace(" ", "_").replace(".", "_") for c in datos.columns]
    return datos


def escapar(texto):
    """Escapa los caracteres que LaTeX interpreta de forma especial."""
    return str(texto).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def figura_clases(entrenamiento):
    """Grafica la distribucion de la variable objetivo."""
    conteo = entrenamiento[config.OBJETIVO].value_counts().sort_index()
    total = conteo.sum()
    figura, eje = plt.subplots(figsize=(5.2, 2.9))
    barras = eje.bar(["Sobrevive", "Muere"], conteo.values, color=["#1F4E79", "#C00000"])
    for barra, valor in zip(barras, conteo.values):
        eje.text(barra.get_x() + barra.get_width() / 2, valor + total * 0.015,
                 f"{valor}\n({valor / total * 100:.1f}\\%)".replace("\\%", "%"),
                 ha="center", fontsize=9)
    eje.set_ylabel("Pacientes")
    eje.set_ylim(0, conteo.max() * 1.22)
    eje.spines[["top", "right"]].set_visible(False)
    figura.tight_layout()
    figura.savefig(FIGURAS / "clases.png", dpi=200)
    plt.close(figura)


def tabla_variables(crudo, ficha):
    """Tabla de variables con rol, descripcion oficial y porcentaje de nulos."""
    sin_ficha = [c for c in crudo.columns if c not in ficha.index]
    sin_traducir = [c for c in crudo.columns if c not in TRADUCCIONES]
    if sin_ficha:
        raise KeyError(f"Columnas ausentes en la ficha oficial: {sin_ficha}")
    if sin_traducir:
        raise KeyError(f"Columnas sin traduccion: {sin_traducir}")

    filas = []
    for columna in crudo.columns:
        serie = crudo[columna]
        tipo = "Categórica" if serie.dtype == object else (
            "Binaria" if serie.nunique(dropna=True) <= 2 else "Numérica")
        rol = ROLES.get(ficha.loc[columna, "role"], ficha.loc[columna, "role"])
        filas.append((escapar(columna), TRADUCCIONES[columna], rol, tipo,
                      f"{serie.isna().mean() * 100:.1f}"))

    cuerpo = "\n".join(f"{n} & {d} & {r} & {t} & {p} \\\\" for n, d, r, t, p in filas)
    (TABLAS / "variables.tex").write_text(
        "\\begin{longtable}{p{1.7cm} p{5.1cm} p{1.4cm} p{1.6cm} r}\n"
        "\\caption{Variables del conjunto de datos original. Descripciones tomadas de la "
        "ficha oficial del repositorio UCI.}\n"
        "\\label{tab:variables}\\\\\n"
        "\\toprule\n"
        "\\textbf{Variable} & \\textbf{Descripción} & \\textbf{Rol} & \\textbf{Tipo} & "
        "\\textbf{\\% nulos} \\\\\n"
        "\\midrule\n\\endfirsthead\n"
        "\\toprule\n"
        "\\textbf{Variable} & \\textbf{Descripción} & \\textbf{Rol} & \\textbf{Tipo} & "
        "\\textbf{\\% nulos} \\\\\n"
        "\\midrule\n\\endhead\n"
        "\\bottomrule\n\\endfoot\n"
        f"{cuerpo}\n"
        "\\end{longtable}\n", encoding="utf-8")


def tabla_referencia(crudo):
    """Tabla con el AUC de las estimaciones del propio estudio frente al objetivo."""
    from sklearn.metrics import roc_auc_score

    etiquetas = {
        "surv2m": "Modelo SUPPORT, supervivencia a 2 meses",
        "surv6m": "Modelo SUPPORT, supervivencia a 6 meses",
        "prg2m": "Estimación del médico, 2 meses",
        "prg6m": "Estimación del médico, 6 meses",
    }
    filas = []
    for columna, etiqueta in etiquetas.items():
        sub = crudo[[columna, config.OBJETIVO]].dropna()
        # Son probabilidades de supervivencia: se invierte el signo para predecir muerte.
        auc = roc_auc_score(sub[config.OBJETIVO], -sub[columna])
        filas.append((etiqueta, len(sub), f"{auc:.3f}"))

    cuerpo = "\n".join(f"{e} & {n} & {a} \\\\" for e, n, a in filas)
    (TABLAS / "referencia.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Capacidad discriminante de las estimaciones incluidas en el propio conjunto "
        "de datos, evaluadas frente a \\texttt{hospdead}}\n"
        "\\label{tab:referencia}\n\\small\n"
        "\\begin{tabular}{p{6.4cm} r r}\n\\toprule\n"
        "\\textbf{Estimación} & \\textbf{Casos} & \\textbf{AUC} \\\\\n\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")
    return filas


def tabla_exclusiones():
    """Tabla de las columnas excluidas con el motivo de cada una."""
    motivos = config.motivos_exclusion()
    cuerpo = "\n".join(f"\\texttt{{{escapar(c)}}} & {escapar(m)} \\\\" for c, m in motivos.items())
    (TABLAS / "exclusiones.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Columnas excluidas del conjunto de modelado}\n"
        "\\label{tab:exclusiones}\n\\small\n"
        "\\begin{tabular}{p{2.2cm} p{8.5cm}}\n\\toprule\n"
        "\\textbf{Columna} & \\textbf{Motivo de exclusión} \\\\\n\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")


def tabla_atipicos():
    """Tabla con los limites del RIC y las filas acotadas en cada columna."""
    from modularizado.utilidades import cargar_intermedio, columnas_por_tipo
    from modularizado.lote_07_atipicos import limites_ric, separar_binarias

    entrenamiento = cargar_intermedio("06_entrenamiento")
    prueba = cargar_intermedio("06_prueba")
    numericas, _ = columnas_por_tipo(entrenamiento)
    _, revisables = separar_binarias(entrenamiento, numericas)

    filas = []
    for columna in revisables:
        inferior, superior = limites_ric(entrenamiento[columna])
        fuera_train = int(((entrenamiento[columna] < inferior) |
                           (entrenamiento[columna] > superior)).sum())
        fuera_test = int(((prueba[columna] < inferior) | (prueba[columna] > superior)).sum())
        if fuera_train or fuera_test:
            filas.append((escapar(columna), f"{inferior:.2f}", f"{superior:.2f}",
                          fuera_train, fuera_test))
    filas.sort(key=lambda f: -f[3])

    cuerpo = "\n".join(f"\\texttt{{{c}}} & {i} & {s} & {a} & {b} \\\\"
                       for c, i, s, a, b in filas)
    (TABLAS / "atipicos.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Límites del rango intercuartílico y registros acotados por columna}\n"
        "\\label{tab:atipicos}\n\\small\n"
        "\\begin{tabular}{l r r r r}\n\\toprule\n"
        "\\textbf{Columna} & \\textbf{Límite inf.} & \\textbf{Límite sup.} & "
        "\\textbf{Entrenamiento} & \\textbf{Prueba} \\\\\n\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")
    return len(filas)


def tabla_orden_ric():
    """Compara los limites del RIC calculados antes y despues de imputar."""
    from modularizado.utilidades import cargar_intermedio, columnas_por_tipo
    from modularizado.lote_07_atipicos import limites_ric, separar_binarias

    entrenamiento = cargar_intermedio("06_entrenamiento")
    numericas, _ = columnas_por_tipo(entrenamiento)
    _, revisables = separar_binarias(entrenamiento, numericas)

    filas, total_real, total_imputado = [], 0, 0
    for columna in revisables:
        serie = entrenamiento[columna]
        inf_real, sup_real = limites_ric(serie)
        imputada = serie.fillna(serie.median())
        inf_imp, sup_imp = limites_ric(imputada)
        rec_real = int(((serie < inf_real) | (serie > sup_real)).sum())
        rec_imp = int(((imputada < inf_imp) | (imputada > sup_imp)).sum())
        total_real += rec_real
        total_imputado += rec_imp
        if columna in ("glucose", "bun", "alb", "edu", "crea"):
            filas.append((escapar(columna), f"{serie.isna().mean() * 100:.1f}",
                          f"{inf_real:.1f} a {sup_real:.1f}", f"{inf_imp:.1f} a {sup_imp:.1f}",
                          rec_real, rec_imp))

    cuerpo = "\n".join(f"\\texttt{{{c}}} & {n} & {a} & {b} & {d} & {e} \\\\"
                       for c, n, a, b, d, e in filas)
    (TABLAS / "orden-ric.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Efecto del orden entre imputación y acotamiento sobre los límites del RIC}\n"
        "\\label{tab:ordenric}\n\\small\n"
        "\\begin{tabular}{l r p{2.4cm} p{2.4cm} r r}\n\\toprule\n"
        "\\textbf{Columna} & \\textbf{\\% nulos} & \\textbf{Límites reales} & "
        "\\textbf{Límites tras imputar} & \\textbf{Rec. real} & \\textbf{Rec. imp.} \\\\\n"
        "\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")
    return total_real, total_imputado


def main():
    """Genera todo el material y reporta los archivos producidos."""
    FIGURAS.mkdir(exist_ok=True)
    TABLAS.mkdir(exist_ok=True)

    crudo = cargar_crudo()
    ficha = cargar_diccionario()
    entrenamiento = pd.read_csv(config.RUTA_TRAIN)

    figura_clases(entrenamiento)
    tabla_variables(crudo, ficha)
    tabla_exclusiones()
    referencia = tabla_referencia(crudo)
    acotadas = tabla_atipicos()
    total_real, total_imputado = tabla_orden_ric()

    print(f"Variables en el csv original: {crudo.shape[1]}")
    print(f"Variables verificadas contra la ficha oficial: {crudo.columns.isin(ficha.index).sum()}")
    print(f"Columnas excluidas: {len(config.motivos_exclusion())}")
    print("AUC de las estimaciones del propio estudio frente a hospdead:")
    for etiqueta, casos, auc in referencia:
        print(f"  {etiqueta}: {auc} (n={casos})")
    print(f"Columnas con registros acotados: {acotadas}")
    print(f"Registros acotados -- antes de imputar: {total_real}, despues: {total_imputado}")
    print("Generado: figuras/clases.png y las tablas en tablas/")


if __name__ == "__main__":
    main()
