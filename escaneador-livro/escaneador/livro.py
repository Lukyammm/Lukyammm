"""Detecção do livro na imagem, localização da lombada e separação das páginas."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Pagina:
    """Recorte de uma página ainda sem correção de curvatura."""

    imagem: np.ndarray       # BGR, já com o fundo (mesa, outra página) pintado de "papel"
    mascara: np.ndarray      # uint8 255 = papel desta página
    lado: str                # "esquerda", "direita" ou "unica"
    origem: tuple[int, int]  # (x, y) do canto superior esquerdo no quadro original


def _suavizar(a: np.ndarray, k: int) -> np.ndarray:
    k = max(1, int(k))
    return np.convolve(a, np.ones(k) / k, mode="same")


def mascara_do_livro(img: np.ndarray) -> np.ndarray:
    """Máscara (255) da maior região clara e pouco saturada: o papel do livro."""
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v, s = hsv[..., 2], hsv[..., 1]
    limiar, _ = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    papel = ((v > limiar) & (s < 70)).astype(np.uint8) * 255

    k = max(15, int(min(h, w) * 0.02))
    papel = cv2.morphologyEx(papel, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)))
    # abertura forte: separa o livro de objetos claros que encostam nele
    k2 = max(21, int(min(h, w) * 0.08))
    aberta = cv2.morphologyEx(papel, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k2, k2)))

    n, rotulos, stats, _ = cv2.connectedComponentsWithStats(aberta)
    if n <= 1:
        return np.full((h, w), 255, np.uint8)
    maior = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    if stats[maior, cv2.CC_STAT_AREA] < 0.10 * h * w:
        return np.full((h, w), 255, np.uint8)

    comp = (rotulos == maior).astype(np.uint8) * 255
    # a abertura arredonda os cantos: recupera o papel vizinho que foi perdido
    # (sem usar o envelope convexo, que incluiria a mesa no "V" entre as duas
    # páginas, junto à lombada)
    comp = cv2.bitwise_and(cv2.dilate(comp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k2, k2))), papel)
    n, rotulos, stats, _ = cv2.connectedComponentsWithStats(comp)
    if n > 1:
        maior = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        comp = (rotulos == maior).astype(np.uint8) * 255
    contornos, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    mascara = np.zeros((h, w), np.uint8)
    cv2.drawContours(mascara, [max(contornos, key=cv2.contourArea)], -1, 255, thickness=cv2.FILLED)
    # tira regiões escuras grandes ligadas ao lado de fora (mesa que o
    # fechamento "pulou" junto da borda do papel). Figuras escuras do livro
    # ficam cercadas de papel e não encostam no lado de fora: são mantidas.
    escuro = (v < 0.6 * limiar).astype(np.uint8) * 255
    ke = max(5, int(min(h, w) * 0.01)) | 1
    escuro = cv2.morphologyEx(escuro, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ke, ke)))
    fora = cv2.dilate(255 - mascara, np.ones((3, 3), np.uint8))
    n, rot = cv2.connectedComponents(escuro)
    if n > 1:
        ids = np.unique(rot[(fora > 0) & (escuro > 0)])
        ids = ids[ids > 0]
        if len(ids):
            mascara[np.isin(rot, ids)] = 0
    # afina a borda: tira a lasca de mesa que o fechamento grudou no papel
    # (na borda da imagem o erode não come nada, então texto cortado fica)
    e = max(3, int(min(h, w) * 0.007))
    return cv2.erode(mascara, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * e + 1, 2 * e + 1)))


def localizar_lombada(img: np.ndarray, mascara: np.ndarray) -> tuple[float, float, float]:
    """Retorna (a, b, confianca) da reta da lombada x = a*y + b.

    A lombada é a faixa vertical perto do centro com menos tinta e com a sombra
    da dobra. É medida em várias faixas horizontais e ajustada por uma reta,
    porque o livro quase nunca fica perfeitamente alinhado com a câmera.
    """
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    ys, xs = np.nonzero(mascara)
    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()
    largura = x1 - x0
    altura = y1 - y0
    lo, hi = int(x0 + 0.30 * largura), int(x0 + 0.70 * largura)

    pontos = []
    pontuacoes = []
    n_faixas = 8
    for i in range(n_faixas):
        a = int(y0 + altura * (0.06 + 0.88 * i / n_faixas))
        b = int(y0 + altura * (0.06 + 0.88 * (i + 1) / n_faixas))
        faixa = cinza[a:b, :]
        if faixa.shape[0] < 5:
            continue
        fundo = cv2.GaussianBlur(faixa, (0, 0), 12)
        tinta = _suavizar((faixa < fundo - 20).mean(0), max(5, largura // 60))
        brilho = _suavizar(faixa.mean(0), max(5, largura // 90))
        t, br = tinta[lo:hi], brilho[lo:hi]
        tn = (t - t.min()) / (np.ptp(t) + 1e-6)
        bn = (br - br.min()) / (np.ptp(br) + 1e-6)
        score = tn + 0.6 * bn
        j = int(np.argmin(score))
        pontos.append(((a + b) / 2, lo + j))
        pontuacoes.append(t[j] / (np.median(t) + 1e-6))

    if len(pontos) < 3:
        return 0.0, (x0 + x1) / 2, 0.0

    p = np.array(pontos)
    # ajuste robusto: descarta faixas muito fora da mediana
    med = np.median(p[:, 1])
    ok = np.abs(p[:, 1] - med) < 0.06 * largura
    if ok.sum() < 3:
        ok[:] = True
    a, b = np.polyfit(p[ok, 0], p[ok, 1], 1)
    confianca = float(1.0 - np.clip(np.median(np.array(pontuacoes)[ok]), 0, 1))
    return float(a), float(b), confianca


def _recorte(img: np.ndarray, mascara: np.ndarray, lado_mask: np.ndarray, lado: str) -> Pagina:
    m = cv2.bitwise_and(mascara, lado_mask)
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    sub = img[y0:y1, x0:x1].copy()
    msub = m[y0:y1, x0:x1].copy()
    # pinta o que não é papel desta página com a cor média do papel
    cor_papel = np.median(sub[msub > 0].reshape(-1, 3), axis=0).astype(np.uint8)
    sub[msub == 0] = cor_papel
    return Pagina(sub, msub, lado, (int(x0), int(y0)))


def separar_paginas(img: np.ndarray, modo: str = "auto") -> tuple[list[Pagina], dict]:
    """Separa um quadro em 1 ou 2 páginas.

    modo: "duplo" (livro aberto, duas páginas), "simples" (uma página) ou
    "auto" (decide pela proporção do livro: aberto é mais largo que alto).
    """
    h, w = img.shape[:2]
    mascara = mascara_do_livro(img)
    ys, xs = np.nonzero(mascara)
    prop = (xs.max() - xs.min()) / max(1, ys.max() - ys.min())
    info = {"proporcao_livro": round(float(prop), 3)}

    if modo == "auto":
        modo = "duplo" if prop > 0.95 else "simples"
    info["modo"] = modo

    if modo == "simples":
        return [_recorte(img, mascara, np.full((h, w), 255, np.uint8), "unica")], info

    a, b, conf = localizar_lombada(img, mascara)
    info["lombada"] = {"a": round(a, 5), "b": round(b, 1), "confianca": round(conf, 2)}
    yy, xx = np.mgrid[0:h, 0:w]
    xl = a * yy + b
    esquerda = (xx < xl).astype(np.uint8) * 255
    direita = (xx >= xl).astype(np.uint8) * 255
    paginas = [_recorte(img, mascara, esquerda, "esquerda"), _recorte(img, mascara, direita, "direita")]
    return paginas, info
