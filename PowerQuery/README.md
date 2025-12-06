
# Power Query Scripts

Ejemplos de consultas M para automatización y transformación de datos.

## SAP_HTML_Example.pq
Este script:
- Lee un archivo HTML exportado desde SAP (spool → email → SharePoint).
- Extrae tablas usando `Html.Table` con selectores CSS.
- Incluye parámetros editables:
  - `SiteUrl` (URL de SharePoint)
  - `CarpetaFiltro` (carpeta donde se guarda el archivo)
  - `NombreArchivoHtml` (nombre del archivo HTML)
  - `RangoTablas` (índice de tablas en el HTML)

### Cómo usar:
1. Abrí Power Query (Power BI o Excel).
2. Creá una **consulta en blanco** → **Editor avanzado**.
33. Pegá el contenido del archivo `.pq`.
