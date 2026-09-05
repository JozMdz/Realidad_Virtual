"""Auditoría estadística reproducible del conjunto de datos Support2.

Esta etapa solo inspecciona el dataset y genera artefactos de auditoría; no
imputa, codifica ni transforma las variables. Esas operaciones corresponden a
las etapas posteriores del pipeline.
"""

from pathlib import Path

import pandas as pd


def auditar_datos(ruta: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
	"""Devuelve los datos sin transformar y un resumen estadístico por columna."""
	datos = pd.read_csv(ruta, na_values=["?", "NA", "N/A", "", "null"])
	datos = datos.dropna(how="all").copy()
	datos.columns = [str(columna).strip().lower().replace(" ", "_") for columna in datos.columns]

	resumen = pd.DataFrame({
		"columna": datos.columns,
		"tipo": [str(datos[columna].dtype) for columna in datos.columns],
		"filas": len(datos),
		"nulos": [datos[columna].isna().sum() for columna in datos.columns],
		"porcentaje_nulos": [datos[columna].isna().mean() * 100 for columna in datos.columns],
		"unicos": [datos[columna].nunique(dropna=True) for columna in datos.columns],
		"minimo": [datos[columna].min() if pd.api.types.is_numeric_dtype(datos[columna]) else pd.NA for columna in datos.columns],
		"maximo": [datos[columna].max() if pd.api.types.is_numeric_dtype(datos[columna]) else pd.NA for columna in datos.columns],
	})
	return datos, resumen


if __name__ == "__main__":
	archivo = Path(__file__).parent / "support2.csv"
	datos, resumen = auditar_datos(archivo)
	salida = Path(__file__).resolve().parent / "estadisticas_descriptivas.csv"
	datos.describe(include="all").transpose().to_csv(salida)
	print(datos.describe(include="all").transpose())
	print(f"Estadísticas descriptivas guardadas en: {salida}")
