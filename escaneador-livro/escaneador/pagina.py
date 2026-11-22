"""Processamento completo de uma página: do recorte bruto à página "escaneada"."""

from __future__ import annotations

import cv2
import numpy as np

from .desentortar import desentortar, medir_letra
from .livro import Pagina
from .realce import acabamento, normalizar_iluminacao

LARGURA_ALVO = 1800  # px de largura por página na saída (≈ 200-300 dpi)


def _recortar(img: np.ndarray, mascara: np.ndarray, linhas: list, hc: float) -> tuple[np.ndarray, tuple]:
    """Recorta a página em volta do texto, com margem branca uniforme.

    Usa as linhas de texto detectadas para achar o bloco principal e depois
    inclui componentes pequenos com cara de letra que estejam perto (número
    da página, notas), ignorando manchas grandes (mão, mesa, sombra).
    """
    H, W = img.shape[:2]
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if linhas:
        xa = np.array([l[0] for l in linhas])
        xb = np.array([l[1] for l in linhas])
        ys = np.array([l[2] for l in linhas])
        x0, x1 = np.percentile(xa, 1), np.percentile(xb, 99)
        y0, y1 = ys.min() - hc, ys.max() + hc
    else:
        x0, y0, x1, y1 = 0, 0, W, H

    tinta = (cinza < 140).astype(np.uint8)
    tinta[mascara == 0] = 0
    n, _, st, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    perto = 5 * hc
    # a distância é medida sempre a partir do bloco das linhas (sem encadear:
    # um fragmento incluído não puxa o próximo)
    bx0, by0, bx1, by1 = x0, y0, x1, y1
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if not (0.35 * hc <= h <= 2.5 * hc and w <= 6 * hc and a >= 0.05 * hc * hc):
            continue
        # letra tem preenchimento parcial; resto de mesa/sombra é mancha sólida
        if w > 0.6 * hc and a / float(w * h) > 0.75:
            continue
        if x + w < bx0 - perto or x > bx1 + perto or y + h < by0 - perto or y > by1 + perto:
            continue
        x0, x1 = min(x0, x), max(x1, x + w)
        y0, y1 = min(y0, y), max(y1, y + h)

    # núcleo = bloco de texto; margem = faixa estreita em volta, que é
    # pintada de branco (some sobra de mesa, sombra da lombada, outra folha)
    # sem nunca encostar no texto
    x0, y0 = int(max(0, x0)), int(max(0, y0))
    x1, y1 = int(min(W, x1)), int(min(H, y1))
    nucleo = img[y0:y1, x0:x1]
    m = int(round(0.6 * hc))
    branco = 255 if img.ndim == 2 else (255, 255, 255)
    recorte = cv2.copyMakeBorder(nucleo, m, m, m, m, cv2.BORDER_CONSTANT, value=branco)
    return recorte, (x0, y0, x1, y1)


def processar_pagina(pag: Pagina, colorido: bool = False, largura_alvo: int = LARGURA_ALVO) -> tuple[np.ndarray, dict]:
    img = pag.imagem
    h, w = img.shape[:2]
    escala = float(np.clip(largura_alvo / max(1, w), 1.0, 4.0))
    grande = cv2.resize(img, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
    mascara = cv2.resize(pag.mascara, (grande.shape[1], grande.shape[0]), interpolation=cv2.INTER_NEAREST)

    cinza = cv2.cvtColor(grande, cv2.COLOR_BGR2GRAY)
    # 1ª passada com tamanho de letra estimado; mede a letra; 2ª passada ajustada
    norm = normalizar_iluminacao(cinza, grande.shape[0] / 90.0)
    estimativa_letra = medir_letra(norm)
    norm = normalizar_iluminacao(cinza, estimativa_letra)

    extras = [mascara]
    if colorido:
        canais = [normalizar_iluminacao(grande[..., c], estimativa_letra) for c in range(3)]
        extras.append(np.dstack(canais))

    corrigida, extras_c, info = desentortar(norm, extras)
    mascara_c = extras_c[0]
    base = extras_c[1] if colorido else corrigida
    final = acabamento(base, colorido=colorido)

    # o que não é papel (mesa, outra página) vira branco
    branco = 255 if final.ndim == 2 else (255, 255, 255)
    final[mascara_c == 0] = branco

    hc = info.get("hc", estimativa_letra)
    recorte, caixa = _recortar(final, mascara_c, info.get("linhas", []), hc)

    # moldura branca como numa página escaneada
    borda = int(round(0.045 * max(recorte.shape[1], 1)))
    recorte = cv2.copyMakeBorder(recorte, borda, borda, borda, borda, cv2.BORDER_CONSTANT, value=branco)

    info_limpa = {k: v for k, v in info.items() if k not in ("linhas", "hc", "mapa")}
    info_limpa |= {"escala": round(escala, 2), "tamanho_final": [int(recorte.shape[1]), int(recorte.shape[0])]}
    return recorte, info_limpa
