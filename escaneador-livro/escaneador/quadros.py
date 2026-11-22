"""Escolha dos melhores quadros do vídeo: um quadro nítido por página virada.

Num vídeo folheando o livro, a imagem alterna entre momentos parados (livro
aberto numa página) e momentos de movimento (a mão virando a folha). Medimos
o movimento entre quadros; cada trecho parado vira um candidato, e dentro dele
escolhemos o quadro mais nítido. Trechos vizinhos que mostram as mesmas
páginas (a mão tremeu, a câmera mexeu) são unidos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np


@dataclass
class Amostra:
    indice: int      # número do quadro no vídeo
    tempo: float     # segundos
    movimento: float
    nitidez: float


@dataclass
class Escolha:
    indice: int
    tempo: float
    nitidez: float
    inicio: float
    fim: float
    imagem: np.ndarray | None = field(default=None, repr=False)


def _pequeno(fr: np.ndarray, largura: int = 320) -> np.ndarray:
    h, w = fr.shape[:2]
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (largura, max(1, int(h * largura / w))), interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(g, (3, 3), 0)


def nitidez(fr: np.ndarray) -> float:
    """Variância do Laplaciano no miolo da imagem (maior = mais nítido)."""
    h, w = fr.shape[:2]
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    esc = 960.0 / max(h, w)
    if esc < 1:
        g = cv2.resize(g, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA)
    hh, ww = g.shape
    miolo = g[int(hh * 0.15):int(hh * 0.85), int(ww * 0.1):int(ww * 0.9)]
    return float(cv2.Laplacian(miolo, cv2.CV_64F).var())


def analisar_video(caminho: Path, fps_amostra: float = 6.0, progresso=None) -> tuple[float, list[Amostra]]:
    cap = cv2.VideoCapture(str(caminho))
    if not cap.isOpened():
        raise RuntimeError(f"Não consegui abrir o vídeo: {caminho}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    passo = max(1, int(round(fps / fps_amostra)))
    amostras: list[Amostra] = []
    anterior = None
    i = 0
    while cap.grab():
        if i % passo == 0:
            ok, fr = cap.retrieve()
            if not ok:
                break
            peq = _pequeno(fr)
            mov = float(np.mean(cv2.absdiff(peq, anterior))) if anterior is not None else float("nan")
            amostras.append(Amostra(i, i / fps, mov, nitidez(fr)))
            anterior = peq
            if progresso and total:
                progresso(i / total)
        i += 1
    cap.release()
    return fps, amostras


def escolher_quadros(amostras: list[Amostra], fps_amostra: float = 6.0, duracao_min: float = 0.4) -> list[Escolha]:
    if not amostras:
        return []
    mov = np.array([a.movimento for a in amostras], np.float64)
    if len(mov) > 1:
        mov[0] = mov[1]
    else:
        mov[0] = 0.0
    # mediana de 3: um pico isolado (ruído de compressão) não quebra o trecho
    mov_s = np.array([np.median(mov[max(0, k - 1):k + 2]) for k in range(len(mov))])
    base = float(np.percentile(mov_s, 20))
    limiar = max(1.2, 2.5 * base, base + 1.0)
    limiar = min(limiar, float(np.percentile(mov_s, 75)))
    parado = mov_s <= limiar
    minimo = max(2, int(round(duracao_min * fps_amostra)))

    escolhas: list[Escolha] = []
    k = 0
    while k < len(parado):
        if not parado[k]:
            k += 1
            continue
        a = k
        while k < len(parado) and parado[k]:
            k += 1
        b = k  # trecho [a, b)
        if b - a < minimo:
            continue
        miolo = range(a + 1, b - 1) if b - a >= 4 else range(a, b)
        melhor = max(miolo, key=lambda j: amostras[j].nitidez)
        s = amostras[melhor]
        escolhas.append(Escolha(s.indice, s.tempo, s.nitidez, amostras[a].tempo, amostras[b - 1].tempo))
    return escolhas


def ler_quadros(caminho: Path, escolhas: list[Escolha]) -> None:
    """Lê do vídeo os quadros escolhidos (leitura sequencial, mais confiável que saltar)."""
    alvo = {e.indice: e for e in escolhas}
    cap = cv2.VideoCapture(str(caminho))
    i = 0
    ultimo = max(alvo) if alvo else -1
    while i <= ultimo and cap.grab():
        if i in alvo:
            ok, fr = cap.retrieve()
            if ok:
                alvo[i].imagem = fr
        i += 1
    cap.release()


def _orb_regiao_livro(fr: np.ndarray):
    from .livro import mascara_do_livro

    esc = 960.0 / max(fr.shape[:2])
    peq = cv2.resize(fr, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA) if esc < 1 else fr
    mascara = mascara_do_livro(peq)
    mascara = cv2.erode(mascara, np.ones((15, 15), np.uint8))
    orb = cv2.ORB_create(3000)
    kp, des = orb.detectAndCompute(cv2.cvtColor(peq, cv2.COLOR_BGR2GRAY), mascara)
    return kp, des


def mesmas_paginas(a: np.ndarray, b: np.ndarray) -> bool:
    """True se os dois quadros mostram as mesmas páginas (só a câmera mexeu).

    Compara pontos de interesse apenas dentro do papel do livro e exige que
    muitos deles concordem numa mesma transformação (homografia).
    """
    kpa, da = _orb_regiao_livro(a)
    kpb, db = _orb_regiao_livro(b)
    if da is None or db is None or len(kpa) < 50 or len(kpb) < 50:
        return False
    pares = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(da, db, k=2)
    bons = [m for m, *n in pares if n and m.distance < 0.75 * n[0].distance]
    if len(bons) < 40:
        return False
    pa = np.float32([kpa[m.queryIdx].pt for m in bons])
    pb = np.float32([kpb[m.trainIdx].pt for m in bons])
    _, inl = cv2.findHomography(pa, pb, cv2.RANSAC, 4.0)
    if inl is None:
        return False
    n_inl = int(inl.sum())
    return n_inl >= 120 and n_inl >= 0.12 * min(len(kpa), len(kpb))


def remover_repetidos(escolhas: list[Escolha]) -> list[Escolha]:
    """Une escolhas consecutivas que mostram as mesmas páginas (fica a mais nítida)."""
    final: list[Escolha] = []
    for e in escolhas:
        if e.imagem is None:
            continue
        if final and mesmas_paginas(final[-1].imagem, e.imagem):
            if e.nitidez > final[-1].nitidez:
                e.inicio = final[-1].inicio
                final[-1] = e
            else:
                final[-1].fim = e.fim
            continue
        final.append(e)
    return final
