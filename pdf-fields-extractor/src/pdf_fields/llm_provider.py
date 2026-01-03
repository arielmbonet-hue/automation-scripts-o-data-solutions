
# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image
import io, base64

# OpenAI oficial (funciona para Vision con chat.completions)
from openai import OpenAI
import openai


def pil_to_data_url(pil_img: Image.Image) -> str:
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


@dataclass
class Throttle:
    min_call_interval_s: float
    max_retries: int
    initial_backoff_s: float
    max_backoff_s: float

    _last_call_ts: float = 0.0

    def _pause(self) -> None:
        now = time.monotonic()
        delta = now - self._last_call_ts
        if delta < self.min_call_interval_s:
            time.sleep(self.min_call_interval_s - delta)
        self._last_call_ts = time.monotonic()

    def call_with_backoff(self, fn, *args, **kwargs):
        backoff = self.initial_backoff_s
        for attempt in range(1, self.max_retries + 1):
            try:
                self._pause()
                return fn(*args, **kwargs)
            except openai.RateLimitError as e:
                msg = str(e)
                sleep_ms = None
                try:
                    import re as _re
                    m = _re.search(r"try again in (\d+)ms", msg)
                    if m:
                        sleep_ms = int(m.group(1))
                except Exception:
                    pass
                wait_s = (sleep_ms / 1000.0) if sleep_ms else backoff
                time.sleep(wait_s + random.uniform(0.0, 0.25))
                backoff = min(backoff * 2, self.max_backoff_s)
            except Exception:
                if attempt >= self.max_retries:
                    return None
                time.sleep(backoff + random.uniform(0.0, 0.25))
                backoff = min(backoff * 2, self.max_backoff_s)
        return None


class BaseLLMProvider:
    def extract_field(self, img: Image.Image, field: str) -> Optional[str]:
        raise NotImplementedError

    def extract_all(self, img: Image.Image) -> Tuple[List[str], List[str]]:
        raise NotImplementedError


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model_name: str, throttle: Throttle):
        self.model = model_name
        self.client = OpenAI()  # requiere OPENAI_API_KEY en el entorno
        self.throttle = throttle

    def _chat(self, messages, response_format=None):
        def _do():
            return self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format=response_format or {"type": "json_object"},
                messages=messages,
            )
        return self.throttle.call_with_backoff(_do)

    def extract_field(self, img: Image.Image, field: str) -> Optional[str]:
        data_url = pil_to_data_url(img)
        system = "Devolvé SOLO JSON válido. Si no está el dato, devolvé {}."
        user_prompt = (
            f'Extraé "{field}" si aparece en el recorte. '
            'Formato fecha: "DD/MM/YYYY" (años de 2 dígitos => 2000+YY). '
            'Para CUIT/CUIL: "NN-NNNNNNNN-N".'
        )
        resp = self._chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ]},
            ]
        )
        if not resp:
            return None
        try:
            obj = json.loads(resp.choices[0].message.content or "{}")
            val = obj.get(field)
            return val or None
        except Exception:
            return None

    def extract_all(self, img: Image.Image):
        data_url = pil_to_data_url(img)
        system = 'Devolvé SOLO JSON válido: {"fechas":[], "cuits":[]}. No inventes.'
        user_prompt = (
            "Detectá TODAS las fechas (DD/MM/YYYY; años 2 dígitos => 2000+YY) "
            "y TODOS los CUIT/CUIL (NN-NNNNNNNN-N) visibles en la página."
        )
        resp = self._chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ]},
            ]
        )
        if not resp:
            return [], []
        try:
            obj = json.loads(resp.choices[0].message.content or "{}")
            return obj.get("fechas", []) or [], obj.get("cuits", []) or []
        except Exception:
            return [], []


# Habilitar Azure OpenAI es opcional: setear LLM_PROVIDER=azure y las envs adecuadas.
# Para simplificar, usamos el SDK "openai" con Azure mediante variables de entorno:
# AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION.
class AzureOpenAIProvider(OpenAIProvider):
    # Si tu entorno ya está configurado con variables de Azure, el cliente OpenAI las toma.
    # Reutilizamos la lógica de OpenAIProvider.
    pass
``
