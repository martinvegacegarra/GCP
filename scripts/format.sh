#!/bin/bash

# Directorio de entrada y salida
INPUT_DIR="users_json"
OUTPUT_DIR="iam_policies_format"

# Crear el directorio de salida si no existe
mkdir -p $OUTPUT_DIR

# Iterar sobre cada archivo JSON en el directorio de entrada
for file in $INPUT_DIR/*.json; do
    # Obtener el nombre base del archivo
    filename=$(basename "$file")
    
    # Formatear el JSON a una sola línea
    jq -c . "$file" > "$OUTPUT_DIR/$filename"
    
    echo "Procesado $file"
done

echo "Formateo completado."

