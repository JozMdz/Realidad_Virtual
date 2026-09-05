from ucimlrepo import fetch_ucirepo 
  
# fetch dataset 
support2 = fetch_ucirepo(id=880) 
  
# data (as pandas dataframes) 
X = support2.data.features 
y = support2.data.targets 
  
# metadata 
print(support2.metadata) 
  
# variable information 
print(support2.variables) 

# comparar el CSV del repositorio con los datos recién descargados
import os

descargado = X.join(y)
ruta_csv = "support2.csv"

if os.path.exists(ruta_csv):
	en_repo = __import__("pandas").read_csv(ruta_csv)
	print(f"Misma forma: {en_repo.shape == descargado.shape}")
	print(f"Mismas columnas: {en_repo.columns.equals(descargado.columns)}")
	print(f"Mismos datos: {en_repo.equals(descargado)}")
	if en_repo.shape == descargado.shape and en_repo.columns.equals(descargado.columns):
		diferencias = (en_repo != descargado) & ~(en_repo.isna() & descargado.isna())
		print(f"Celdas diferentes: {diferencias.to_numpy().sum()}")
else:
	print("No existe support2.csv en el repositorio para comparar.")

# descargar a CSV en el repositorio
descargado.to_csv(ruta_csv, index=False)



