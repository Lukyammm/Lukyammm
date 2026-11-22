"""Análise de layout: ordem de leitura com colunas e títulos de largura total.

O OCR "automático" erra quando o espaço entre colunas é estreito: mistura
linhas de colunas diferentes. Aqui dividimos a página em regiões retangulares
na ordem de leitura:

- faixas de largura total (cabeçalho, títulos que atravessam as colunas);
- entre elas, as colunas (da esquerda para a direita).
"""

from __future__ import annotations

import cv2
import numpy as np

from .desentortar import limiar_texto, medir_letra, so_letras


def _pedacos(img: np.ndarray, hc: float) -> np.ndarray:
    """Caixas (x, y, w, h) de pedaços de linha (palavras grudadas)."""
    th = so_letras(limiar_texto(img, hc), hc)
    k = max(3, int(round(hc * 0.45)))  # junta letras em palavras, não colunas
    junto = cv2.morphologyEx(th, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1)))
    junto = cv2.morphologyEx(junto, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(1, int(hc * 0.3)))))
    n, _, st, _ = cv2.connectedComponentsWithStats(junto, connectivity=8)
    caixas = st[1:, :4]
    ok = (caixas[:, 3] >= 0.4 * hc) & (caixas[:, 3] <= 4 * hc) & (caixas[:, 2] >= 0.5 * hc)
    return caixas[ok]


def _vaos_de_coluna(caixas: np.ndarray, largura: int, hc: float) -> list[tuple[int, int]]:
    """Faixas verticais sem texto que separam colunas."""
    cobertura = np.zeros(largura, np.float64)
    for x, y, w, h in caixas:
        cobertura[x:x + w] += h
    if cobertura.max() <= 0:
        return []
    ocupado = cobertura > 0.08 * np.median(cobertura[cobertura > 0])
    xs = np.nonzero(ocupado)[0]
    if len(xs) == 0:
        return []
    x_ini, x_fim = xs.min(), xs.max()
    vaos = []
    x = x_ini
    while x <= x_fim:
        if not ocupado[x]:
            a = x
            while x <= x_fim and not ocupado[x]:
                x += 1
            b = x
            # vão precisa ter largura mínima e texto relevante dos dois lados
            if b - a >= 0.6 * hc and cobertura[x_ini:a].sum() > 0.15 * cobertura.sum() \
                    and cobertura[b:x_fim + 1].sum() > 0.15 * cobertura.sum():
                vaos.append((a, b))
        x += 1
    return vaos


def regioes_de_leitura(img: np.ndarray, hc: float | None = None) -> list[tuple[int, int, int, int]]:
    """Lista de retângulos (x, y, w, h) na ordem de leitura."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = cinza.shape
    hc = hc or medir_letra(cinza)
    caixas = _pedacos(cinza, hc)
    if len(caixas) == 0:
        return [(0, 0, W, H)]

    # 1ª estimativa dos vãos: ignora pedaços largos (títulos atravessando)
    vaos = _vaos_de_coluna(caixas, W, hc)
    if not vaos:
        return [(0, 0, W, H)]
    centros = [(a + b) / 2 for a, b in vaos]

    def atravessa(c):
        x, y, w, h = c
        return any(x < m - 0.3 * hc and x + w > m + 0.3 * hc for m in centros)

    largas = [c for c in caixas if atravessa(c)]
    # cabeçalho/rodapé: linha isolada no topo/fundo vira faixa de largura total
    ordem_y = caixas[np.argsort(caixas[:, 1])]
    topo_linha = ordem_y[ordem_y[:, 1] < ordem_y[0, 1] + 0.6 * hc]
    resto = ordem_y[ordem_y[:, 1] >= ordem_y[0, 1] + 0.6 * hc]
    if len(resto) and resto[:, 1].min() - (topo_linha[:, 1] + topo_linha[:, 3]).max() > 1.0 * hc:
        largas += [tuple(c) for c in topo_linha]
    fundo = (caixas[:, 1] + caixas[:, 3]).max()
    base_linha = caixas[caixas[:, 1] + caixas[:, 3] > fundo - 0.6 * hc]
    resto = caixas[caixas[:, 1] + caixas[:, 3] <= fundo - 0.6 * hc]
    if len(resto) and base_linha[:, 1].min() - (resto[:, 1] + resto[:, 3]).max() > 1.5 * hc:
        largas += [tuple(c) for c in base_linha]
    # refaz os vãos só com os pedaços que não atravessam (mais limpo)
    estreitas = np.array([c for c in caixas if not atravessa(c)])
    if len(estreitas):
        vaos2 = _vaos_de_coluna(estreitas, W, hc)
        if vaos2:
            cab = [c for c in largas if not atravessa(c)]  # cabeçalho/rodapé
            vaos = vaos2
            centros = [(a + b) / 2 for a, b in vaos]
            largas = [c for c in caixas if atravessa(c)] + cab

    # faixas horizontais ocupadas por pedaços largos (com uma folga)
    faixas = []
    for x, y, w, h in sorted(largas, key=lambda c: c[1]):
        a, b = y - 0.25 * hc, y + h + 0.25 * hc
        if faixas and a <= faixas[-1][1]:
            faixas[-1][1] = max(faixas[-1][1], b)
        else:
            faixas.append([a, b])

    limites_x = [0] + [int((a + b) / 2) for a, b in vaos] + [W]
    regioes = []
    topo = 0.0
    for a, b in faixas + [[H, H]]:
        if a - topo > 0.8 * hc:  # bloco com colunas entre topo e a
            for i in range(len(limites_x) - 1):
                x0, x1 = limites_x[i], limites_x[i + 1]
                y0, y1 = int(max(0, topo)), int(min(H, a))
                tem_texto = any(x0 <= cx + cw / 2 < x1 and y0 <= cy + ch / 2 < y1 for cx, cy, cw, ch in caixas)
                if tem_texto:
                    regioes.append((x0, y0, x1 - x0, y1 - y0))
        if b > a:
            y0, y1 = int(max(0, a)), int(min(H, b))
            regioes.append((0, y0, W, y1 - y0))
        topo = max(topo, b)
    return regioes or [(0, 0, W, H)]
