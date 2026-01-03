
# PDF Fields Extractor (Fecha y CUIT)

Extrae **Fecha** (DD/MM/YYYY) y **CUIT/CUIL** (NN-NNNNNNNN-N) desde PDFs usando:
- **PyMuPDF** (texto embebido y renders selectivos)
- **LLM Vision** (OpenAI o Azure OpenAI) como fallback y para mejorar robustez

## Características
- Portátil (rutas multiplataforma con `pathlib`)
- Configurable por CLI y variables de entorno
- Rate limiting con backoff exponencial
- Exporta CSV y/o Excel
- Proveedor LLM intercambiable: `openai` | `azure`

## Requisitos
- Python 3.10+
- `pip install -r requirements.txt`
- Variables de entorno para el proveedor seleccionado
  - OpenAI: `OPENAI_API_KEY`
  - Azure:  `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`

## Uso rápido

```bash
python -m pdf_fields.cli \
  --input-dir ./samples \
  --out-dir ./out \
  --max-files 20 \
  --model gpt-4o-mini \
  --provider openai
