
# Power BI + Power Automate: plantillas DAX y esquemas JSON

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-stable-blue)
![Templates](https://img.shields.io/badge/templates-DAX%20%7C%20JSON-orange)

Este repositorio contiene **consultas DAX** para la acción de Power Automate  
**“Ejecutar una consulta con un conjunto de datos”**, y **esquemas JSON**  
para la acción **“Analizar archivo JSON”**.  
El objetivo es usar **Power BI como preprocesador de datos**, reducir el volumen y acelerar flujos.

---

## 📌 Índice
- [Cómo usar](#cómo-usar)
- [Ejemplo](#ejemplo)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Buenas prácticas](#buenas-prácticas)
- [Licencia](#licencia)

---

## ✅ Cómo usar
1. En Power Automate, configurá el **Área de trabajo** y el **Conjunto de datos**.
2. Pegá la consulta DAX (archivos en `dax/*.dax`) en el campo **Texto de la consulta**.
3. La respuesta será un **array JSON**. Usá el esquema correspondiente  
   (archivos en `json-schema/*.json`) en la acción **Analizar archivo JSON**.

> **Tip:** mantené nombres de columnas consistentes (sin espacios o con alias)  
> para simplificar el esquema JSON y evitar errores por cambios de layout.

---

## 🧪 Ejemplo mínimo

**Consulta DAX:**
```sql
EVALUATE
SELECTCOLUMNS(
    'Tabla1',
    "Nombre", 'Tabla1'[Nombre],
    "Direccion", 'Tabla1'[Direccion],
    "Fecha    "Fecha", 'Tabla1'[ReqmtsDate]
)

## 🧪 JSON
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "Nombre": { "      "Nombre": { "type": "string" },
      "Direccion": { "type": "string" },
      "Fecha": { "type": ["string", "null"] }
    },
    "required": ["Nombre", "Direccion"]
  }

## Estructura del repo
powerbi-powerautomate-dax-json/
├─ README.md
├─ dax/
│  ├─ 01_select_basico.dax
│  ├─ 02_select_ordenado.dax
│  ├─ 03_filtrado_parametrico.dax
│  ├─ 04_summarize_agrupado.dax
│  ├─ 05_topn_con_orden.dax
│  ├─ 06_join_lookupvalue.dax
│  └─ 07_paginacion_skip_take.dax
└─ json-schema/
   ├─ schema_tabla_simple.json
   ├─ schema_tabla_con_alias.json
   ├─ schema_summarize.json
   ├─ schema_topn.json
   └─ schema_parametrico.json

✅ Buenas prácticas

Alias en DAX: usar SELECTCOLUMNS para simplificar el JSON.
Validación previa:
@greater(length(body('Ejecutar_una_consulta_con_un_conjunto_de_datos')), 0)
Paginación: para grandes volúmenes, usar 07_paginacion_skip_take.dax.
TopN: limitar filas cuando no se necesita todo el dataset.
Tipos permisivos: si hay valores vacíos, usar ["string","null"] en el esquema.
Orden en DAX: ordenar en la consulta evita trabajo extra en Power Automate.

📜 Licencia
Este proyecto está bajo licencia MIT – libre para usar y adaptar.
