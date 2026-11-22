"""Realce da imagem para ficar com cara de página escaneada."""

from __future__ import annotations

import cv2
import numpy as np


def normalizar_iluminacao(cinza: np.ndarray, tamanho_texto: float) -> np.ndarray:
    """Remove sombras e variações de luz: divide a imagem pelo fundo estimado.

    O fundo é estimado com um fechamento morfológico (apaga as letras, que são
    finas e escuras) seguido de um borramento grande. O resultado tem papel
    perto de 255 e texto escuro, mesmo com sombra da lombada ou da mão.
    """
    k = int(max(7, tamanho_texto * 1.4)) | 1
    fundo = cv2.morphologyEx(cinza, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    fundo = cv2.GaussianBlur(fundo, (0, 0), 0.6 * k)
    fundo = np.maximum(fundo.astype(np.float32), 1.0)
    norm = cinza.astype(np.float32) / fundo * 245.0
    return np.clip(norm, 0, 255).astype(np.uint8)


def acabamento(img: np.ndarray, colorido: bool = False) -> np.ndarray:
    """Nitidez + níveis: papel branco, texto preto bem definido."""
    f = img.astype(np.float32)
    borrada = cv2.GaussianBlur(f, (0, 0), 1.4)
    f = cv2.addWeighted(f, 1.7, borrada, -0.7, 0)

    cinza = f if f.ndim == 2 else cv2.cvtColor(np.clip(f, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    tinta = cinza[cinza < 160]
    preto = float(np.percentile(tinta, 3)) if tinta.size > 100 else 0.0
    branco = 228.0
    f = (f - preto) * (255.0 / max(1.0, branco - preto))
    f = np.clip(f, 0, 255)
    # leve curva gama para escurecer o miolo das letras sem sujar o papel
    f = 255.0 * (f / 255.0) ** 1.15
    out = f.astype(np.uint8)
    if colorido or out.ndim == 2:
        return out
    return cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
