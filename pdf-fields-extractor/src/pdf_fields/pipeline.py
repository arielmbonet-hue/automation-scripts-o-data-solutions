
# -*- coding: utf-8 -*-
from __future__ import annotations
import csv
import logging
from pathlib import Path
from typing import List, Optional, Tuple

import fitz
import pandas as pd
from openpyxl.styles import Font, Alignment

from .config import Settings
from .llm_provider import BaseLLMProvider, OpenAIProvider, AzureOpenAIProvider, Throttle
from .extractors import (
    normalize_date_textlike, 
    normalize_cuit_textlike, 
    SEARCH_TERMS_CUIT, SEARCH_TERMS_FECHA,
    dedup_rects, clip_right_rect, render, pick_closest_past_date
)

log = logging.getLogger(__name__)

def ensure_out_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def build_provider(cfg: Settings) -> BaseLLMProvider:
    throttle = Throttle(
        min_call_interval_s=cfg.min_call_interval_s,
        max_retries=cfg.max_retries,
        initial_backoff_s=cfg.initial_backoff_s,
        max_backoff_s=cfg.max_backoff_s,
    )
    if cfg.llm_provider == "azure":
        log.info("Usando Azure OpenAI provider")
        return AzureOpenAIProvider(model_name=cfg.model_vision, throttle=throttle)
    log.info("Usando OpenAI provider")
    return OpenAIProvider(model_name=cfg.model_vision, throttle=throttle)

def llm_extract_field_from_image(llm: BaseLLMProvider, pil_img, field: str, cfg: Settings) -> Optional[str]:
    val = llm.extract_field(pil_img, field)
    if not val:
        return None
    if field == "fecha":
        return normalize_date_textlike(val, cfg.min_year, cfg.max_year)
    return normalize_cuit_textlike(val)

def llm_extract_all_from_page(llm: BaseLLMProvider, pil_img, cfg: Settings) -> Tuple[List[str], List[str]]:
    fechas_raw, cuits_raw = llm.extract_all(pil_img)
    fechas = [f for f in (normalize_date_textlike(fr, cfg.min_year, cfg.max_year) for fr in fechas_raw) if f]
    cuits  = [c for c in (normalize_cuit_textlike(cr) for cr in cuits_raw) if c]
    return fechas, cuits

def process_one_pdf(pdf_path: Path, cfg: Settings, llm: BaseLLMProvider, hoy=None) -> Tuple[Optional[str], Optional[str]]:
    fechas: List[str] = []
    cuits:  List[str] = []
    try:
        doc = fitz.open(pdf_path.as_posix())
    except Exception as e:
        log.warning("No se pudo abrir %s: %s", pdf_path, e)
        return None, None

    for i in range(doc.page_count):
        try:
            page = doc.load_page(i)
            page_found_dates: List[str] = []
            page_found_cuits: List[str] = []

            # 1) Texto embebido (barato)
            txt = page.get_text("text") or ""
            tf = normalize_date_textlike(txt, cfg.min_year, cfg.max_year)
            tc = normalize_cuit_textlike(txt)
            if tf: page_found_dates.append(tf)
            if tc: page_found_cuits.append(tc)

            need_fecha = not page_found_dates
            need_cuit  = not page_found_cuits

            # 2) Anclas -> recortes a la derecha (si falta)
            rects_fecha, rects_cuit = [], []
            if need_fecha:
                for term in SEARCH_TERMS_FECHA:
                    rects_fecha.extend(page.search_for(term) or [])
                rects_fecha = dedup_rects(rects_fecha)
                rects_fecha.sort(key=lambda r: (r.y0, r.x0))
            if need_cuit:
                for term in SEARCH_TERMS_CUIT:
                    rects_cuit.extend(page.search_for(term) or [])
                rects_cuit = dedup_rects(rects_cuit)
                rects_cuit.sort(key=lambda r: (r.y0, r.x0))

            if need_fecha and rects_fecha:
                for rect in rects_fecha[:cfg.max_rects_per_anchor]:
                    clip = clip_right_rect(page, rect)
                    img  = render(page, clip_rect=clip, zoom=cfg.render_zoom_clip)
                    fval = llm_extract_field_from_image(llm, img, "fecha", cfg)
                    if fval:
                        page_found_dates.append(fval)
                        break

            if need_cuit and rects_cuit:
                for rect in rects_cuit[:cfg.max_rects_per_anchor]:
                    clip = clip_right_rect(page, rect)
                    img  = render(page, clip_rect=clip, zoom=cfg.render_zoom_clip)
                    cval = llm_extract_field_from_image(llm, img, "cuit", cfg)
                    if cval:
                        page_found_cuits.append(cval)
                        break

            # 3) Fallback full-page (si aún falta)
            need_fecha = not page_found_dates
            need_cuit  = not page_found_cuits
            if need_fecha or need_cuit:
                full_img = render(page, clip_rect=None, zoom=cfg.render_zoom_full)
                f_all, c_all = llm_extract_all_from_page(llm, full_img, cfg)
                if need_fecha and f_all:
                    page_found_dates.extend(f_all)
                if need_cuit and c_all:
                    page_found_cuits.extend(c_all)

            # 4) Acumular deduplicado
            if page_found_dates:
                seen = set(); ordered = []
                for f in page_found_dates:
                    if f not in seen:
                        seen.add(f); ordered.append(f)
                fechas.extend(ordered)
            if page_found_cuits:
                seen = set(); ordered = []
                for c in page_found_cuits:
                    if c not in seen:
                        seen.add(c); ordered.append(c)
                cuits.extend(ordered)

        except Exception as e:
            log.debug("Página %s de %s falló: %s", i, pdf_path.name, e)
            continue

    fecha_obj = pick_closest_past_date(fechas, hoy=hoy)
    cuit_unico = None
    if cuits:
        seen, dedup = set(), []
        for c in cuits:
            if c not in seen:
                seen.add(c); dedup.append(c)
        cuit_unico = dedup[0] if dedup else None

    return fecha_obj, cuit_unico

def process_folder(cfg: Settings, hoy=None) -> List[dict]:
    ensure_out_dir(cfg.out_dir)
    pdf_files = sorted(Path(cfg.input_dir).glob("*.pdf"))
    if cfg.max_files is not None:
        pdf_files = pdf_files[:cfg.max_files]
    if not pdf_files:
        log.warning("No hay PDFs en: %s", cfg.input_dir)
        return []

    llm = build_provider(cfg)
    resultados = []
    for path in pdf_files:
        fecha, cuit = process_one_pdf(path, cfg, llm, hoy=hoy)
        resultados.append({
            "archivo": path.name,
            "fecha_ddmmyyyy": fecha or "",
            "cuit": cuit or ""
        })
        # Pausa corta adicional por archivo
        # (el throttling fino está dentro del provider)
        # time.sleep(0.25)  -> no necesario si tu tasa ya está ok

    if cfg.write_csv:
        with cfg.csv_path().open("w", encoding="utf-8", newline="") as fh:
            wr = csv.writer(fh, delimiter=';')
            wr.writerow(["archivo", "fecha_ddmmyyyy", "cuit"])
            for row in resultados:
                wr.writerow([row["archivo"], row["fecha_ddmmyyyy"], row["cuit"]])

    if cfg.write_xlsx:
        df = pd.DataFrame(resultados, columns=["archivo", "fecha_ddmmyyyy", "cuit"])
        with pd.ExcelWriter(cfg.xlsx_path(), engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Resumen Lote")
            ws = writer.sheets["Resumen Lote"]
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")
            # auto width
            for col in ws.columns:
                max_len = 0
                col_letter = col[0].column_letter
                for cell in col:
                    val = "" if cell.value is None else str(cell.value)
                    max_len = max(max_len, len(val))
                ws.column_dimensions[col_letter].width = min(max_len + 2, 60)

    return resultados
