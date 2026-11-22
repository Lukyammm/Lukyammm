#!/usr/bin/env python3
"""Gera um vídeo sintético de alguém folheando um livro, com texto conhecido.

Serve para testar o escaneador de ponta a ponta sem precisar de um vídeo
real: as páginas são desenhadas com texto (em português), curvadas perto da
lombada, vistas em perspectiva sobre uma mesa, com tremida de câmera, uma
"tremida forte" no meio (que não pode virar página repetida) e a mão virando
as folhas.

Uso: python testes/gerar_video_teste.py saida.mp4
Gera também saida.json com o texto de cada página (gabarito).
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONTE_NEGRITO = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

PARAGRAFOS = [
    "Digitalizar um livro com o celular parece simples, mas cada detalhe conta. A luz precisa ser "
    "uniforme, sem reflexos no papel, e a câmera deve ficar o mais paralela possível às páginas.",
    "Quando o livro está aberto, as folhas se curvam perto da lombada. Essa curvatura faz as linhas "
    "de texto parecerem tortas na foto, e é exatamente isso que o programa precisa corrigir.",
    "O primeiro passo é encontrar o livro na imagem. O papel costuma ser a maior região clara e pouco "
    "colorida do quadro, enquanto a mesa e os objetos ao redor são mais escuros ou mais saturados.",
    "Depois, a lombada é localizada pela faixa vertical com menos tinta e com a sombra da dobra. Com "
    "ela, o quadro é dividido em duas páginas, que são tratadas separadamente.",
    "Cada linha de texto deveria ser reta. Medindo o quanto cada uma se desvia, o programa calcula "
    "um campo suave de deslocamento e desentorta a página inteira de uma só vez.",
    "As margens e as bordas das colunas também ajudam: numa página plana elas são verticais. Se na "
    "foto estiverem inclinadas, a perspectiva da câmera é corrigida a partir delas.",
    "Com a página plana, a iluminação é equalizada. Sombras da mão e da lombada desaparecem, o papel "
    "fica branco e as letras ganham contraste, como numa digitalização feita em escâner.",
    "Por fim, o reconhecimento de caracteres transforma a imagem em texto pesquisável. O resultado é "
    "um arquivo PDF em que se pode procurar palavras, copiar trechos e ler com conforto.",
    "No vídeo, o momento certo de capturar cada página é quando o livro fica parado. O programa mede "
    "o movimento entre os quadros e escolhe, em cada pausa, o quadro mais nítido.",
    "Se a câmera tremer durante uma pausa, a mesma página pode aparecer duas vezes. Por isso os "
    "quadros vizinhos são comparados e as repetições são descartadas automaticamente.",
    "O número impresso de cada página é lido no cabeçalho. Assim é possível conferir se alguma folha "
    "foi pulada durante a gravação e avisar quem está digitalizando.",
    "Uma boa gravação tem o livro inteiro no quadro, as páginas bem abertas e uma pausa de um segundo "
    "em cada abertura antes de virar a folha. Com isso o resultado fica muito melhor.",
]


def desenhar_pagina(numero: int, paragrafos: list[str], largura=1000, altura=1400) -> tuple[np.ndarray, str]:
    img = Image.new("L", (largura, altura), 250)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONTE, 27)
    fc = ImageFont.truetype(FONTE, 22)
    fb = ImageFont.truetype(FONTE_NEGRITO, 34)
    m = 90
    par = numero % 2 == 0
    cab = "Capítulo 3 | Como digitalizar um livro"
    if par:
        d.text((m, 60), f"{numero}", font=fb, fill=20)
        d.text((m + 70, 68), cab, font=fc, fill=60)
    else:
        w = d.textlength(cab, font=fc)
        d.text((largura - m - 70 - w, 68), cab, font=fc, fill=60)
        d.text((largura - m - 40, 60), f"{numero}", font=fb, fill=20)
    y = 150
    texto = [str(numero), cab]
    for p in paragrafos:
        for linha in textwrap.wrap(p, 52):
            d.text((m, y), linha, font=f, fill=25)
            y += 40
        y += 18
        texto.append(p)
    return np.array(img), "\n".join(texto)


def curvar_abertura(abertura: np.ndarray) -> np.ndarray:
    """Curva as páginas perto da lombada (deslocamento vertical + compressão)."""
    H, W = abertura.shape[:2]
    lomb = W / 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.abs(xx - lomb)
    lado = np.sign(xx - lomb)
    # compressão horizontal perto da lombada (inversa: expande a coordenada)
    u = lomb + lado * (dist + 60 * np.exp(-dist / 70) - 60)
    # deslocamento vertical: mais forte perto da lombada e longe do centro vertical
    curva = 55 * np.exp(-dist / 160)
    v = yy - curva * (0.3 + 0.7 * (yy / H))
    return cv2.remap(abertura, u.astype(np.float32), v.astype(np.float32), cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def fundo_mesa(Wf: int, Hf: int, rng) -> np.ndarray:
    mesa = np.full((Hf, Wf, 3), (38, 34, 32), np.uint8)
    mesa = cv2.add(mesa, rng.integers(0, 12, (Hf, Wf, 3), dtype=np.uint8))
    cv2.circle(mesa, (230, 380), 150, (225, 225, 225), -1)          # luminária
    cv2.rectangle(mesa, (420, 80), (800, 620), (90, 140, 170), -1)  # estojo
    cv2.rectangle(mesa, (880, 300), (1040, 700), (170, 120, 200), -1)
    return mesa


def homografia(Wb: int, Hb: int, Wf: int, Hf: int) -> np.ndarray:
    src = np.float32([[0, 0], [Wb, 0], [Wb, Hb], [0, Hb]])
    # trapézio: câmera um pouco inclinada, livro na metade de baixo do quadro
    dst = np.float32([[40, 860], [Wf - 30, 880], [Wf + 25, 1640], [-20, 1660]])
    return cv2.getPerspectiveTransform(src, dst)


def compor(abertura: np.ndarray, mesa: np.ndarray, Hm: np.ndarray, desloc=(0.0, 0.0), ang=0.0) -> np.ndarray:
    Hf, Wf = mesa.shape[:2]
    R = cv2.getRotationMatrix2D((Wf / 2, Hf / 2), ang, 1.0)
    R = np.vstack([R, [0, 0, 1]])
    T = np.array([[1, 0, desloc[0]], [0, 1, desloc[1]], [0, 0, 1]], np.float64)
    M = T @ R @ Hm
    cor = cv2.cvtColor(abertura, cv2.COLOR_GRAY2BGR)
    # leve tom amarelado do papel e sombra na lombada
    cor = (cor.astype(np.float32) * np.array([0.93, 0.98, 1.0])).astype(np.uint8)
    papel = cv2.warpPerspective(cor, M, (Wf, Hf), flags=cv2.INTER_LINEAR)
    masc = cv2.warpPerspective(np.full(abertura.shape[:2], 255, np.uint8), M, (Wf, Hf))
    # a curvatura deixa pixels pretos (fora da página) dentro do retângulo: são mesa
    vazio = cv2.warpPerspective((abertura < 5).astype(np.uint8) * 255, M, (Wf, Hf))
    masc[vazio > 128] = 0
    saida = mesa.copy()
    saida[masc > 128] = papel[masc > 128]
    # sombra suave na lombada e luz desigual
    xs = np.arange(Wf)[None, :]
    sombra = 1 - 0.35 * np.exp(-((xs - Wf / 2 - desloc[0]) ** 2) / (2 * 25 ** 2))
    luz = np.linspace(1.0, 0.82, Hf)[:, None]
    fator = (sombra * luz)[..., None]
    saida = np.where(masc[..., None] > 128, (saida * fator).astype(np.uint8), saida)
    return saida


def mao(frame: np.ndarray, x: float, y: float) -> None:
    cv2.ellipse(frame, (int(x), int(y)), (120, 80), 25, 0, 360, (120, 160, 205), -1)
    cv2.ellipse(frame, (int(x) - 60, int(y) - 70), (35, 90), 10, 0, 360, (115, 155, 200), -1)


def main() -> None:
    destino = Path(sys.argv[1] if len(sys.argv) > 1 else "video_teste.mp4")
    rng = np.random.default_rng(7)
    Wf, Hf, fps = 1080, 1920, 30
    mesa = fundo_mesa(Wf, Hf, rng)

    aberturas, gabarito = [], {}
    numeros = [(10, 11), (12, 13), (14, 15)]
    k = 0
    for esq, dir_ in numeros:
        pe, te = desenhar_pagina(esq, PARAGRAFOS[k:k + 2]); k += 2
        pd, td = desenhar_pagina(dir_, PARAGRAFOS[k:k + 2]); k += 2
        gabarito[esq], gabarito[dir_] = te, td
        aberturas.append(curvar_abertura(np.hstack([pe, pd])))
    Hb, Wb = aberturas[0].shape[:2]
    Hm = homografia(Wb, Hb, Wf, Hf)

    quadros: list[np.ndarray] = []

    def parado(ab, segundos, tremor=1.2):
        for _ in range(int(segundos * fps)):
            dx, dy = rng.normal(0, tremor, 2)
            quadros.append(compor(ab, mesa, Hm, (dx, dy), rng.normal(0, 0.05)))

    def tremida_forte(ab):  # câmera mexe e volta (não é página nova)
        for t in np.linspace(0, 1, int(0.3 * fps)):
            s = np.sin(np.pi * t)
            quadros.append(compor(ab, mesa, Hm, (40 * s, -25 * s), 1.5 * s))

    def virar(ab1, ab2):
        n = int(0.9 * fps)
        for i in range(n):
            t = i / (n - 1)
            base = compor(ab1 if t < 0.5 else ab2, mesa, Hm, tuple(rng.normal(0, 2, 2)), 0)
            # folha virando: faixa branca varrendo da direita para a esquerda
            x = int(Wf * (0.95 - 0.9 * t))
            larg = int(260 * np.sin(np.pi * t)) + 20
            pts = np.array([[x, 840], [x + larg, 820], [x + larg + 40, 1680], [x + 30, 1700]], np.int32)
            cv2.fillPoly(base, [pts], (232, 236, 240))
            mao(base, x + larg, 1500 - 300 * np.sin(np.pi * t))
            quadros.append(base)

    parado(aberturas[0], 1.4)
    tremida_forte(aberturas[0])
    parado(aberturas[0], 1.0)
    virar(aberturas[0], aberturas[1])
    parado(aberturas[1], 1.5)
    virar(aberturas[1], aberturas[2])
    parado(aberturas[2], 1.5)

    escritor = cv2.VideoWriter(str(destino), cv2.VideoWriter_fourcc(*"mp4v"), fps, (Wf, Hf))
    for q in quadros:
        q = cv2.GaussianBlur(q, (3, 3), 0.6)
        escritor.write(q)
    escritor.release()
    destino.with_suffix(".json").write_text(json.dumps(gabarito, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"vídeo: {destino} ({len(quadros)} quadros, {len(quadros) / fps:.1f}s); gabarito: {destino.with_suffix('.json')}")


if __name__ == "__main__":
    main()
