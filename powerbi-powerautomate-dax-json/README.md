
# Power BI + Power Automate: plantillas DAX y esquemas JSON

Este repositorio contiene consultas DAX para la acción de Power Automate
**“Ejecutar una consulta con un conjunto de datos”**, y esquemas JSON
para la acción **“Analizar archivo JSON”**. El objetivo es usar Power BI
como preprocesador de datos, reducir el volumen y acelerar flujos.

## Cómo usar
1. En Power Automate, configurá el área de trabajo y conjunto de datos.
2. Pegá la consulta DAX (archivos `dax/*.dax`) en el campo **Texto de la consulta**.
3. La respuesta es un arreglo JSON. Usá el esquema correspondiente
   (archivos `json-schema/*.json`) en **Analizar archivo JSON**.

> Tip: mantené **nombres de columnas** consistentes (sin espacios o con alias)
> para simplificar el esquema JSON y evitar errores por cambios de layout.
