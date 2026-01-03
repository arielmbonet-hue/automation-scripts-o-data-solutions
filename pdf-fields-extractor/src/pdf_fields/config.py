
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Valores por defecto razonables
DEFAULT_MODEL_VISION = os.getenv("MODEL_VISION", "gpt-4o-mini")

@dataclass
class Settings:
    input_dir: Path
    out_dir: Path
    csv_name: str = "lote_resultados.csv"
    xlsx_name: str = "lote_resultados.xlsx"
    model_vision: str = DEFAULT_MODEL_VISION
    max_files: Optional[int] = None

    # throttling / backoff
    min_call_interval_s: float = float(os.getenv("MIN_CALL_INTERVAL_S", "0.35"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "6"))
    initial_backoff_s: float = float(os.getenv("INITIAL_BACKOFF_S", "0.6"))
    max_backoff_s: float = float(os.getenv("MAX_BACKOFF_S", "5.0"))

    # render zooms
    render_zoom_clip: float = float(os.getenv("RENDER_ZOOM_CLIP", "5.0"))
    render_zoom_full: float = float(os.getenv("RENDER_ZOOM_FULL", "2.5"))

    # anchors
    max_rects_per_anchor: int = int(os.getenv("MAX_RECTS_PER_ANCHOR", "2"))

    # output toggles
    write_csv: bool = os.getenv("WRITE_CSV", "1") != "0"
    write_xlsx: bool = os.getenv("WRITE_XLSX", "1") != "0"

    # fecha plausible
    min_year: int = int(os.getenv("MIN_YEAR", "1990"))
    max_year: int = int(os.getenv("MAX_YEAR", "2100"))

    # LLM provider: "openai" o "azure"
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai").lower()

    def csv_path(self) -> Path:
        return self.out_dir / self.csv_name

    def xlsx_path(self) -> Path:
        return self.out_dir / self.xlsx_name
