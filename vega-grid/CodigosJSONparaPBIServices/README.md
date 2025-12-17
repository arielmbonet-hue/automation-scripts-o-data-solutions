
# Visualización Vega en DENEB: Grilla de Cursos

Este código Vega se puede **copiar y pegar directamente** en la visualización **DENEB** dentro de Power BI.

---

## 📌 Requisitos de los datos

La tabla que alimenta la visualización debe contener **exactamente estos campos** (con estos nombres):

- `NombreApellido` → Nombre y Apellido del participante
- `Cod_Grilla` → Código o identificador del curso
- `First Estado_Grilla` → Estado del curso (por ejemplo: `C`, `I`, `N`)
- `Activo` → Indicador si el registro está activo (booleano o texto)
- `Cumplimiento` → Valor numérico (porcentaje o ratio)

---

## 📌 Pasos para usar en DENEB

1. En Power BI, agrega la visualización **DENEB** desde el marketplace.
2. Inserta la visualización en tu reporte y selecciona el **modo Vega**.
3. Copia el código Vega completo (el `spec.json` que está en este repositorio) y pégalo en el editor de DENEB.
4. Asigna los campos del dataset a las columnas correspondientes:
   - `NombreApellido` → Campo de nombres
   - `Cod_Grilla` → Campo de cursos
   - `First Estado_Grilla` → Estado
   - `Activo` → Activo
   - `Cumplimiento` → Cumplimiento
     
---

## 📌 Interacciones soportadas

- **Pan y scroll**: Arrastrar con el mouse para mover la grilla.
- **Zoom horizontal/vertical**: Rueda del mouse.
- **Reset**: Doble click sobre la grilla.

---

## 📌 DEMO: Archivos incluidos

- `spec.json` → Código Vega para la visualización.
- `example.json` → Datos de ejemplo para pruebas.
- `index.html` → Demo en GitHub Pages.

---

## ✅ Demo en GitHub Pages

[[Ver demo aquí]
https://arielmbonet-hue.github.io/automation-scripts-o-data-solutions/vega-grid/GrillaCursos/

---

¿Querés que te genere este `README.md` como **archivo listo para subir al repo** y además te incluya el bloque de código Vega dentro del README para que quede todo en un solo lugar?  
¿O preferís que lo mantenga separado (README + spec.json)?
