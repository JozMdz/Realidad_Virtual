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


def tabla_dnr(crudo):
    """Distribucion de la orden de no reanimar segun el desenlace."""
    reparto = pd.crosstab(crudo["dnr"], crudo[config.OBJETIVO], normalize="columns") * 100
    etiquetas = {
        "dnr before sadm": "Suscrita antes del ingreso",
        "dnr after sadm": "Suscrita después del ingreso",
        "no dnr": "Sin orden de no reanimar",
    }
    cuerpo = "\n".join(
        f"{etiquetas[i]} & {reparto.loc[i, 0]:.1f}\\% & {reparto.loc[i, 1]:.1f}\\% \\\\"
        for i in etiquetas if i in reparto.index)
    (TABLAS / "dnr.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Distribución de la orden de no reanimar según el desenlace hospitalario}\n"
        "\\label{tab:dnr}\n\\small\n"
        "\\begin{tabular}{p{5cm} r r}\n\\toprule\n"
        "\\textbf{Estado de la orden} & \\textbf{Sobrevive} & \\textbf{Fallece} \\\\\n"
        "\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")


def _preparar(excluidas):
    """Reproduce el pipeline excluyendo el conjunto de columnas indicado."""
    from sklearn.model_selection import train_test_split  # noqa: F401

    datos = cargar_crudo().dropna(how="all")
    datos = datos.drop(columns=[c for c in excluidas if c in datos.columns])
    datos = datos.drop_duplicates().reset_index(drop=True)

    entrenamiento = datos.groupby(config.OBJETIVO, group_keys=False).sample(
        frac=config.FRACCION_ENTRENAMIENTO, random_state=config.SEMILLA)
    prueba = datos.drop(entrenamiento.index).copy()
    entrenamiento = entrenamiento.copy()

    faltantes = entrenamiento.isna().mean() * 100
    descartadas = faltantes[faltantes > config.LIMITE_FALTANTES].index.tolist()
    entrenamiento = entrenamiento.drop(columns=descartadas)
    prueba = prueba.drop(columns=descartadas)

    numericas = entrenamiento.select_dtypes(include="number").columns.tolist()
    categoricas = [c for c in entrenamiento.columns if c not in numericas]
    for columna in [c for c in numericas if entrenamiento[c].nunique() > 2]:
        q1, q3 = entrenamiento[columna].quantile(0.25), entrenamiento[columna].quantile(0.75)
        inferior, superior = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
        entrenamiento[columna] = entrenamiento[columna].clip(inferior, superior)
        prueba[columna] = prueba[columna].clip(inferior, superior)
    for columna in numericas:
        mediana = entrenamiento[columna].median()
        entrenamiento[columna] = entrenamiento[columna].fillna(mediana)
        prueba[columna] = prueba[columna].fillna(mediana)
    for columna in categoricas:
        moda = entrenamiento[columna].mode(dropna=True)[0]
        entrenamiento[columna] = entrenamiento[columna].fillna(moda)
        prueba[columna] = prueba[columna].fillna(moda)

    a = pd.get_dummies(entrenamiento, columns=categoricas, drop_first=True)
    b = pd.get_dummies(prueba, columns=categoricas, drop_first=True).reindex(
        columns=a.columns, fill_value=0)
    booleanas = [c for c in a.columns if a[c].dtype == bool]
    a[booleanas] = a[booleanas].astype(int)
    b[booleanas] = b[booleanas].astype(int)
    return a, b


def _auc_logistica(a, b, reductor=None):
    """AUC de una regresion logistica sobre el conjunto de prueba."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = a.drop(columns=config.OBJETIVO), a[config.OBJETIVO]
    Xp, yp = b.drop(columns=config.OBJETIVO), b[config.OBJETIVO]
    pasos = [("escalado", StandardScaler())]
    if reductor is not None:
        pasos.append(("reductor", reductor))
    pasos.append(("modelo", LogisticRegression(max_iter=3000, random_state=config.SEMILLA)))
    modelo = Pipeline(pasos).fit(X, y)
    return roc_auc_score(yp, modelo.predict_proba(Xp)[:, 1])


def tabla_fuga():
    """Compara el desempeno con y sin las columnas posteriores al ingreso."""
    base = set(config.COLUMNAS_EXCLUIDAS)
    posteriores = set(config.COLUMNAS_POSTERIORES)
    filas = []
    for etiqueta, excluidas in [("Con las variables posteriores al ingreso", base),
                                ("Sin las variables posteriores al ingreso", base | posteriores)]:
        a, b = _preparar(excluidas)
        filas.append((etiqueta, a.shape[1], f"{_auc_logistica(a, b):.3f}"))

    cuerpo = "\n".join(f"{e} & {n} & {v} \\\\" for e, n, v in filas)
    (TABLAS / "fuga.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Efecto de las variables posteriores al ingreso sobre el desempeño}\n"
        "\\label{tab:fuga}\n\\small\n"
        "\\begin{tabular}{p{6.5cm} r r}\n\\toprule\n"
        "\\textbf{Configuración} & \\textbf{Columnas} & \\textbf{AUC} \\\\\n\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")
    return filas


def tabla_reduccion():
    """Compara componentes principales contra seleccion directa de variables."""
    from sklearn.decomposition import PCA
    from sklearn.feature_selection import SelectKBest, f_classif

    a = pd.read_csv(config.RUTA_TRAIN)
    b = pd.read_csv(config.RUTA_TEST)
    total = a.shape[1] - 1
    completo = _auc_logistica(a, b)

    filas = [(f"{total} (todas)", f"{completo:.4f}", f"{completo:.4f}")]
    for k in (30, 20, 15, 10, 5):
        pca = _auc_logistica(a, b, PCA(n_components=k, random_state=config.SEMILLA))
        mejores = _auc_logistica(a, b, SelectKBest(f_classif, k=k))
        filas.append((str(k), f"{pca:.4f}", f"{mejores:.4f}"))

    cuerpo = "\n".join(f"{v} & {p} & {m} \\\\" for v, p, m in filas)
    (TABLAS / "reduccion.tex").write_text(
        "\\begin{table}[H]\n\\centering\n"
        "\\caption{Componentes principales frente a selección directa de variables}\n"
        "\\label{tab:reduccion}\n\\small\n"
        "\\begin{tabular}{r r r}\n\\toprule\n"
        "\\textbf{Variables} & \\textbf{Componentes principales} & "
        "\\textbf{Selección directa} \\\\\n\\midrule\n"
        f"{cuerpo}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n", encoding="utf-8")
    return filas


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
    tabla_dnr(crudo)
    fuga = tabla_fuga()
    reduccion = tabla_reduccion()

    print(f"Variables en el csv original: {crudo.shape[1]}")
    print(f"Variables verificadas contra la ficha oficial: {crudo.columns.isin(ficha.index).sum()}")
    print(f"Columnas excluidas: {len(config.motivos_exclusion())}")
    print("AUC de las estimaciones del propio estudio frente a hospdead:")
    for etiqueta, casos, auc in referencia:
        print(f"  {etiqueta}: {auc} (n={casos})")
    print(f"Columnas con registros acotados: {acotadas}")
    print(f"Registros acotados -- antes de imputar: {total_real}, despues: {total_imputado}")
    print("AUC con y sin las columnas posteriores al ingreso:")
    for etiqueta, columnas, auc in fuga:
        print(f"  {etiqueta}: {columnas} columnas, AUC={auc}")
    print(f"Reduccion evaluada en {len(reduccion)} tamanos")
    print("Generado: figuras/clases.png y las tablas en tablas/")


if __name__ == "__main__":
    main()
