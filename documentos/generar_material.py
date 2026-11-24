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

DESCRIPCIONES = {
    "age": "Edad en anos", "sex": "Sexo", "dzgroup": "Grupo de enfermedad",
    "dzclass": "Categoria amplia de enfermedad", "num_co": "Numero de comorbilidades",
    "edu": "Anos de educacion", "income": "Ingreso anual declarado",
    "scoma": "Puntaje de coma al dia 3", "charges": "Cobro total de la hospitalizacion",
    "totcst": "Costo total estimado", "totmcst": "Costo total detallado",
    "avtisst": "Promedio de intervenciones, dias 3 a 25", "race": "Raza",
    "sps": "Puntaje de fisiologia SUPPORT", "aps": "Puntaje de fisiologia APACHE III",
    "surv2m": "Supervivencia a 2 meses estimada por el modelo",
    "surv6m": "Supervivencia a 6 meses estimada por el modelo",
    "hday": "Dia de internacion al entrar al estudio", "diabetes": "Presencia de diabetes",
    "dementia": "Presencia de demencia", "ca": "Estado del cancer",
    "prg2m": "Supervivencia a 2 meses estimada por el medico",
    "prg6m": "Supervivencia a 6 meses estimada por el medico",
    "dnr": "Orden de no reanimar", "dnrday": "Dia de la orden de no reanimar",
    "meanbp": "Presion arterial media", "wblc": "Glóbulos blancos",
    "hrt": "Frecuencia cardiaca", "resp": "Frecuencia respiratoria",
    "temp": "Temperatura corporal", "pafi": "Relacion PaO2/FiO2",
    "alb": "Albumina en sangre", "bili": "Bilirrubina", "crea": "Creatinina",
    "sod": "Sodio", "ph": "pH arterial", "glucose": "Glucosa",
    "bun": "Urea en sangre", "urine": "Volumen de orina",
    "adlp": "Actividades diarias segun el paciente",
    "adls": "Actividades diarias segun un familiar",
    "adlsc": "Actividades diarias, version imputada",
    "death": "Fallecimiento en el seguimiento",
    "hospdead": "Fallecimiento durante la hospitalizacion",
    "sfdm2": "Nivel de discapacidad a los dos meses",
}


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


def tabla_variables(crudo):
    """Tabla de las variables del dataset con su tipo y porcentaje de nulos."""
    filas = []
    for columna in crudo.columns:
        serie = crudo[columna]
        tipo = "Categórica" if serie.dtype == object else (
            "Binaria" if serie.nunique(dropna=True) <= 2 else "Numérica")
        filas.append((escapar(columna), DESCRIPCIONES.get(columna, ""), tipo,
                      f"{serie.isna().mean() * 100:.1f}"))

    cuerpo = "\n".join(f"{n} & {d} & {t} & {p} \\\\" for n, d, t, p in filas)
    (TABLAS / "variables.tex").write_text(
        "\\begin{longtable}{p{1.9cm} p{5.4cm} p{1.9cm} r}\n"
        "\\caption{Variables del conjunto de datos original}\n"
        "\\label{tab:variables}\\\\\n"
        "\\toprule\n"
        "\\textbf{Variable} & \\textbf{Descripción} & \\textbf{Tipo} & \\textbf{\\% nulos} \\\\\n"
        "\\midrule\n\\endfirsthead\n"
        "\\toprule\n"
        "\\textbf{Variable} & \\textbf{Descripción} & \\textbf{Tipo} & \\textbf{\\% nulos} \\\\\n"
        "\\midrule\n\\endhead\n"
        "\\bottomrule\n\\endfoot\n"
        f"{cuerpo}\n"
        "\\end{longtable}\n", encoding="utf-8")


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


def main():
    """Genera todo el material y reporta los archivos producidos."""
    FIGURAS.mkdir(exist_ok=True)
    TABLAS.mkdir(exist_ok=True)

    crudo = cargar_crudo()
    entrenamiento = pd.read_csv(config.RUTA_TRAIN)

    figura_clases(entrenamiento)
    tabla_variables(crudo)
    tabla_exclusiones()

    print(f"Variables en el csv original: {crudo.shape[1]}")
    print(f"Columnas excluidas: {len(config.motivos_exclusion())}")
    print("Generado: figuras/clases.png, tablas/variables.tex, tablas/exclusiones.tex")


if __name__ == "__main__":
    main()
