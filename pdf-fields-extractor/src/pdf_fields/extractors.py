
# -*- coding: utf-8 -*-
from __future__ import annotations
import re
from datetime import datetime, date
from typing import List, Optional, Tuple
import fitz                       # PyMuPDF
from PIL import Image
from pathlib import Path

DATE_STRICT = re.compile(r"\b(\d{2})\D?(\d{2})\D?(\d{2}|\d{4})\b")
CUIT_RE     = re.compile(r"\b(\d{2})\D?(\d{8})\D?(\d)\b")

SEARCH_TERMS_FECHA = (
    "Fecha de visita", "FECHA DE VISITA", "fecha de visita",
    "Fecha:", "FECHA:", "fecha:",
    "Fecha", "FECHA", "fecha",
)

SEARCH_TERMS_CUIT = (
    "CUIT", "C.U.I.T", "C.U.I.T.", "Nº CUIT", "N° CUIT",
    "CUIL", "C.U.I.L", "C.U.I.L.", "C.U.I.L:", "CUIL:",
)

def normalize_date(dd: str, mm: str, yy: str, min_year: int, max_year: int) -> Optional[str]:
    try:
        d, m, y = int(dd), int(mm), int(yy)
    except Exception:
        return None
    if not (1 <= d <= 31 and 1 <= m <= 12):
        return None
    if len(str(yy)) == 2:
        y = 2000 + int(yy)
    if y < min_year or y > max_year:
        return None
    return f"{d:02d}/{m:02d}/{y:04d}"

def normalize_date_textlike(val: str, min_year: int, max_year: int) -> Optional[str]:
    m = DATE_STRICT.search(val or "")
    if not m:
        return None
    return normalize_date(m.group(1), m.group(2), m.group(3), min_year, max_year)

def cuit_check_digit(n11: str) -> Optional[int]:
    if len(n11) != 11 or not n11.isdigit():
        return None
    nums = list(map(int, n11))
    weights = [5,4,3,2,7,6,5,4,3,2]
    s = sum(n*w for n, w in zip(nums[:10], weights))
    dv = 11 - (s % 11)
    if dv == 11: dv = 0
    elif dv == 10: dv = 9
    return dv

def normalize_cuit_textlike(text: str) -> Optional[str]:
    m = CUIT_RE.search(text or "")
    if not m:
        return None
    p1, p2, p3 = m.groups()
    dv = cuit_check_digit(f"{p1}{p2}{p3}")
    if dv is None or dv != int(p3):
        return None
    return f"{p1}-{p2}-{p3}"

def clip_right_rect(page, rect: fitz.Rect) -> fitz.Rect:
    RIGHT_WIDTH_FACTOR   = 6.0
    EXTRA_TOP_FACTOR     = 0.5
    EXTRA_BOTTOM_FACTOR  = 2.5
    right_width  = rect.width * RIGHT_WIDTH_FACTOR
    extra_top    = rect.height * EXTRA_TOP_FACTOR
    extra_bottom = rect.height * EXTRA_BOTTOM_FACTOR
    return fitz.Rect(
        rect.x1,
        max(0, rect.y0 - extra_top),
        min(page.rect.x1, rect.x1 + right_width),
        min(page.rect.y1, rect.y1 + extra_bottom),
    )

def render(page, clip_rect=None, zoom=2.5) -> Image.Image:
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=clip_rect, alpha=False) if clip_rect else page.get_pixmap(matrix=mat, alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

def dedup_rects(rects, tol=1.0):
    uniq = []
    for r in rects:
        is_dup = False
        for u in uniq:
            if (abs(r.x0 - u.x0) < tol and abs(r.y0 - u.y0) < tol and
                abs(r.x1 - u.x1) < tol and abs(r.y1 - u.y1) < tol):
                is_dup = True
                break
        if not is_dup:
            uniq.append(r)
    return uniq

def pick_closest_past_date(fechas_str: List[str], hoy: Optional[date] = None) -> Optional[str]:
    if hoy is None:
        hoy = date.today()
    fechas_dt = []
    for f in fechas_str:
        try:
            fechas_dt.append(datetime.strptime(f, "%d/%m/%Y").date())
        except Exception:
            pass
    candidatas = [d for d in fechas_dt if d <= hoy]
    return candidatas and max(candidatas).strftime("%d/%m/%Y") or None
