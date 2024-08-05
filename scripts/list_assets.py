import subprocess
import csv
import requests
from bs4 import BeautifulSoup

# URL de la documentación de Google Cloud sobre tipos de recursos
GCP_ASSET_TYPES_URL = "https://cloud.google.com/asset-inventory/docs/supported-asset-types"

def fetch_asset_type_mapping():
    # Hacer una solicitud GET a la URL de la documentación
    response = requests.get(GCP_ASSET_TYPES_URL)
    response.raise_for_status()  # Lanza un error si la solicitud no fue exitosa

    # Parsear el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Buscar todos los tipos de assets y sus descripciones en la página
    asset_type_mapping = {}
    for section in soup.select('div.devsite-article-body h2'):
        asset_type = section.get_text().strip()
        description = section.find_next_sibling('p').get_text().strip()
        asset_type_mapping[asset_type] = description

    return asset_type_mapping

# Obtener el mapeo actualizado de tipos de asset
asset_type_mapping = fetch_asset_type_mapping()

# Función para traducir el tipo de asset
def translate_asset_type(asset_type):
    return asset_type_mapping.get(asset_type, asset_type)  # Devuelve el nombre amigable o el tipo original si no hay mapeo

# Leer los proyectos desde un archivo de texto
with open('projects.txt') as f:
    projects = f.read().splitlines()

# Cabecera del archivo CSV
fields = ["tipo_de_asset", "displayname", "location", "projectid", "status"]
rows = []

# Iterar sobre cada proyecto y listar los assets
for project in projects:
    print(f"Listando assets para el proyecto: {project}")
    try:
        # Ejecutar el comando gcloud y obtener la salida en CSV
        result = subprocess.run(
            ["gcloud", "asset", "search-all-resources", f"--scope=projects/{project}", "--format=csv(assetType, displayName, location, project, state)"],
            capture_output=True, text=True, check=True
        )
        # Leer los resultados de gcloud y agregarlos a las filas
        output = result.stdout.splitlines()[1:]  # Omitir la primera línea (cabecera)
        for line in output:
            fields_values = line.split(",")
            fields_values[0] = translate_asset_type(fields_values[0])  # Traducir el tipo de asset
            rows.append(fields_values)
    except subprocess.CalledProcessError as e:
        print(f"Error al listar assets para el proyecto {project}: {e}")

# Escribir los resultados en un archivo CSV
with open('all_projects_assets.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)  # Escribir la cabecera
    csvwriter.writerows(rows)   # Escribir las filas

print("Inventario completado y guardado en all_projects_assets.csv")

