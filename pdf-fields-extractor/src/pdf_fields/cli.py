
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import logging
import os
from pathlib import Path

from .config import Settings
from .pipeline import process_folder

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Extractor de Fecha/CUIT desde PDFs (LLM Vision + PyMuPDF)")
    p.add_argument("--input-dir", type=Path, required=True, help="Carpeta con PDFs de entrada")
    p.add_argument("--out-dir",   type=Path, required=True, help="Carpeta de salida")
    p.add_argument("--max-files", type=int, default=None, help="Máximo de PDFs a procesar (ej. 20)")
    p.add_argument("--model",     type=str, default=os.getenv("MODEL_VISION", "gpt-4o-mini"), help="Modelo Vision (ej. gpt-4o-mini)")
    p.add_argument("--provider",  type=str, default=os.getenv("LLM_PROVIDER", "openai"), choices=["openai","azure"], help="Proveedor LLM (openai/azure)")
    p.add_argument("--no-csv",    action="store_true", help="No exportar CSV")
    p.add_argument("--no-xlsx",   action="store_true", help="No exportar XLSX")
    p.add_argument("--verbose",   action="store_true", help="Verbose logging")
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    cfg = Settings(
        input_dir=args.input_dir,
        out_dir=args.out_dir,
        model_vision=args.model,
        max_files=args.max_files,
        write_csv=not args.no_csv,
        write_xlsx=not args.no_xlsx,
        llm_provider=args.provider.lower(),
    )
    res = process_folder(cfg)
    print(f"[OK] Procesados {len(res)} PDFs")
    if cfg.write_csv:
        print(f"[OK] CSV:  {cfg.csv_path()}")
    if cfg.write_xlsx:
        print(f"[OK] XLSX: {cfg.xlsx_path()}")

if __name__ == "__main__":
    main()
