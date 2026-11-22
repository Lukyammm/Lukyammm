"""Correção da curvatura da página e da perspectiva a partir das linhas de texto.

Ideia: numa página plana as linhas de texto são retas horizontais. Na foto do
livro aberto elas entortam (perto da lombada) e inclinam (câmera torta). Então:

1. Encontramos pedaços de linhas de texto (palavras/trechos) e a linha central
   de cada pedaço.
2. Ajustamos um campo de deslocamento vertical suave D(x, y) tal que, para
   cada linha, y - D(x, y) seja constante ao longo dela. D é um polinômio em
   (x, y); termos que dependem só de y ficam de fora (não mudam a forma).
3. Juntamos os pedaços em linhas inteiras e refinamos o ajuste.
4. As margens de texto (justificado) viram retas verticais: isso corrige a
   perspectiva horizontal (página "trapézio").
5. Remapeamos a imagem: cada pixel de saída (X, Y) busca o pixel de origem
   (x, y) com x = h(X, Y) e y = Y + D(x, y).
"""

from __future__ import annotations

import cv2
import numpy as np


# ---------------------------------------------------------------- texto ----

def limiar_texto(norm: np.ndarray, tamanho: float) -> np.ndarray:
    bloco = int(max(15, tamanho * 3)) | 1
    return cv2.adaptiveThreshold(norm, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, bloco, 18)


def altura_caractere(th: np.ndarray) -> float:
    """Altura típica das letras (mediana dos componentes com cara de letra)."""
    _, _, st, _ = cv2.connectedComponentsWithStats(th, connectivity=8)
    hs, ws, area = st[1:, 3], st[1:, 2], st[1:, 4]
    H = th.shape[0]
    ok = (hs > H * 0.003) & (hs < H * 0.05) & (ws < hs * 2.5) & (area > 12)
    if ok.sum() < 30:
        return max(8.0, H / 90.0)
    return float(np.median(hs[ok]))


def medir_letra(norm: np.ndarray) -> float:
    """Altura típica da letra em px, em duas passadas (estimativa → medida)."""
    hc = altura_caractere(limiar_texto(norm, norm.shape[0] / 90.0))
    return altura_caractere(limiar_texto(norm, hc))


def so_letras(th: np.ndarray, hc: float) -> np.ndarray:
    """Remove da máscara o que não tem tamanho de letra.

    Sombras da lombada, bordas da página, fios de tabela e figuras viram
    componentes enormes que "colam" linhas diferentes; letras são pequenas.
    """
    n, rot, st, _ = cv2.connectedComponentsWithStats(th, connectivity=8)
    h, w = st[:, 3], st[:, 2]
    ok = (h <= 2.5 * hc) & (w <= 12 * hc)
    ok[0] = False
    return np.where(ok[rot], 255, 0).astype(np.uint8)


def segmentos_de_linha(th: np.ndarray, hc: float, cinza: np.ndarray | None = None) -> list[dict]:
    """Pedaços de linhas de texto, cada um com pontos da sua linha central."""
    th = so_letras(th, hc)
    # separa linhas vizinhas que se tocam (ascendentes/descendentes)
    sep = cv2.erode(th, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2)))
    kx = max(3, int(round(hc * 0.9)))
    junto = cv2.morphologyEx(sep, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (kx, 1)))
    n, rot, st, _ = cv2.connectedComponentsWithStats(junto, connectivity=8)

    passo = max(2, int(hc * 0.75))
    janela = max(3, int(hc))
    segs = []
    for i in range(1, n):
        x, y, w, h, _ = st[i]
        if w < 2.5 * hc or h > 0.35 * w + 2.0 * hc:
            continue
        blob = rot[y:y + h, x:x + w] == i
        # espessura real da faixa (independe da inclinação da linha)
        esp = blob.sum(0)
        esp = float(np.median(esp[esp > 0]))
        if esp > 2.0 * hc or esp < 0.45 * hc:
            continue
        sub = (blob & (th[y:y + h, x:x + w] > 0)).astype(np.float32)
        if sub.sum() > 0.8 * blob.sum():  # barra sólida (borda da mesa, fio), não texto
            continue
        # mancha escura (o limiar adaptativo deixa o miolo dela "oco"): texto
        # tem bastante papel claro entre as letras, a média fica clara
        if cinza is not None and float(cinza[y:y + h, x:x + w][blob].mean()) < 120:
            continue
        col = sub.sum(0)
        soma_y = (sub * np.arange(h, dtype=np.float32)[:, None]).sum(0)
        k = np.ones(janela, np.float32)
        col_s = np.convolve(col, k, mode="same")
        cy = np.convolve(soma_y, k, mode="same") / np.maximum(col_s, 1e-6)
        xs = np.arange(janela // 2, w - janela // 2, passo)
        xs = xs[col_s[xs] > 0.5 * janela]
        if len(xs) < 3:
            continue
        pts = np.stack([x + xs, y + cy[xs]], 1).astype(np.float64)
        segs.append({"pts": pts, "x0": float(x), "x1": float(x + w)})
    return segs


# ---------------------------------------------------------------- campo ----

def _bspline_cubica(t: np.ndarray) -> np.ndarray:
    a = np.abs(t)
    return np.where(a < 1, 2 / 3 - a ** 2 + a ** 3 / 2, np.where(a < 2, (2 - a) ** 3 / 6, 0.0))


class CampoVertical:
    """D(x, y): deslocamento vertical suave.

    Em x usa splines cúbicas (flexíveis: acompanham a dobra forte junto à
    lombada); em y um polinômio de grau 2 (a curvatura muda devagar de cima
    para baixo). D(x_ref, y) = 0, ou seja, termos que só dependem de y ficam
    de fora (eles não mudam a forma das linhas). Uma penalidade de suavidade
    entre coeficientes vizinhos evita ondulações onde não há texto.
    """

    def __init__(self, largura: int, altura: int, nos: int = 20, gy: int = 2):
        self.escala = float(max(largura, altura))
        self.yc = altura / 2.0
        self.passo = largura / nos
        self.centros = np.arange(-1, nos + 2) * self.passo  # cobre [0, largura]
        self.x_ref = largura / 2.0
        self.gy = gy
        self.suavidade = 2e-5
        self.K = len(self.centros)
        self.w = np.zeros(self.K * (gy + 1))
        self._b_ref = self._bx(np.array([self.x_ref]))[0]

    def _bx(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, np.float64).reshape(-1)
        return _bspline_cubica((x[:, None] - self.centros[None, :]) / self.passo)

    def _base(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        x = np.asarray(x, np.float64)
        forma = x.shape
        bx = self._bx(x) - self._b_ref
        v = ((np.asarray(y, np.float64).reshape(-1)) - self.yc) / self.escala
        B = np.concatenate([bx * (v ** b)[:, None] for b in range(self.gy + 1)], 1)
        return B.reshape(*forma, -1)

    def D(self, x, y) -> np.ndarray:
        x = np.asarray(x, np.float64)
        forma = x.shape
        bx = self._bx(x) - self._b_ref
        v = (np.asarray(y, np.float64).reshape(-1) - self.yc) / self.escala
        W = self.w.reshape(self.gy + 1, self.K)
        d = sum((bx @ W[b]) * v ** b for b in range(self.gy + 1))
        return (d * self.escala).reshape(forma)

    def _penalidade(self) -> np.ndarray:
        d2 = np.diff(np.eye(self.K), 2, axis=0)
        P = d2.T @ d2
        return np.kron(np.diag([1.0, 4.0, 16.0][: self.gy + 1]), P)

    def ajustar(self, grupos: list[np.ndarray], hc: float, iteracoes: int = 3) -> np.ndarray:
        """Ajuste por mínimos quadrados; cada grupo é uma linha (constante livre).

        A constante de cada linha é eliminada centralizando os dados dentro do
        grupo, então só resolvemos os coeficientes do campo.
        Pontos com resíduo grande (ruído, figuras) são descartados e refaz-se.
        """
        pesos = [np.ones(len(g), bool) for g in grupos]
        for it in range(iteracoes):
            A, b = [], []
            for g, ok in zip(grupos, pesos):
                if ok.sum() < 3:
                    continue
                gg = g[ok]
                B = self._base(gg[:, 0], gg[:, 1])
                v = (gg[:, 1] - self.yc) / self.escala
                A.append(B - B.mean(0))
                b.append(v - v.mean())
            if not A:
                return np.zeros(0)
            A = np.vstack(A)
            b = np.concatenate(b)
            n = len(b)
            M = A.T @ A + self.suavidade * n * self._penalidade() + 1e-9 * n * np.eye(A.shape[1])
            self.w = np.linalg.solve(M, A.T @ b)

            res_todos = []
            residuos = []
            for g, ok in zip(grupos, pesos):
                Y = g[:, 1] - self.D(g[:, 0], g[:, 1])
                r = Y - np.median(Y[ok]) if ok.sum() else Y * 0
                residuos.append(r)
                res_todos.append(r[ok])
            rt = np.concatenate(res_todos)
            sigma = 1.4826 * np.median(np.abs(rt)) + 1e-6
            # tolerante no início: a dobra junto à lombada parece "erro" antes
            # de o campo aprender a curvatura
            lim = max((6.0 if it == 0 else 3.5) * sigma, 0.2 * hc)
            pesos = [np.abs(r) < lim for r in residuos]
        return np.concatenate(res_todos)


def juntar_em_linhas(segs: list[dict], campo: CampoVertical, hc: float) -> list[dict]:
    """Une pedaços que estão na mesma linha (mesmo Y retificado e próximos em x)."""
    for s in segs:
        p = s["pts"]
        s["Y"] = float(np.median(p[:, 1] - campo.D(p[:, 0], p[:, 1])))
    ordem = sorted(range(len(segs)), key=lambda i: segs[i]["Y"])
    pai = list(range(len(segs)))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for a_idx, i in enumerate(ordem):
        for j in ordem[a_idx + 1:]:
            if segs[j]["Y"] - segs[i]["Y"] > 0.3 * hc:
                break
            si, sj = segs[i], segs[j]
            vao = max(sj["x0"] - si["x1"], si["x0"] - sj["x1"])
            if -0.5 * hc < vao < 2.0 * hc:
                pai[raiz(j)] = raiz(i)

    linhas: dict[int, list[dict]] = {}
    for i in range(len(segs)):
        linhas.setdefault(raiz(i), []).append(segs[i])
    resultado = []
    for partes in linhas.values():
        pts = np.vstack([p["pts"] for p in partes])
        pts = pts[np.argsort(pts[:, 0])]
        resultado.append({
            "pts": pts,
            "x0": min(p["x0"] for p in partes),
            "x1": max(p["x1"] for p in partes),
        })
    return resultado


# -------------------------------------------------------------- margens ----

def alinhamentos_verticais(Y: np.ndarray, X: np.ndarray, hc: float, largura: int, maximo: int = 6) -> list[tuple]:
    """Retas quase verticais x = p*Y + q onde muitas linhas começam/terminam.

    São as margens, as bordas das colunas e os recuos de listas: na página
    plana todas são verticais. Pontos colados na borda do recorte são
    ignorados (linha cortada pela foto não é margem de verdade).
    Retorna [(x_no_meio, p, n_pontos), ...].
    """
    ok = (X > 0.6 * hc) & (X < largura - 0.6 * hc)
    Y, X = Y[ok], X[ok]
    retas = []
    if len(Y) < 8:
        return retas
    rng = np.random.default_rng(0)
    restantes = np.ones(len(Y), bool)
    Ym = float(np.median(Y))
    for _ in range(maximo):
        idx = np.nonzero(restantes)[0]
        if len(idx) < 8:
            break
        melhor = None
        for _ in range(500):
            i, j = rng.choice(idx, 2, replace=False)
            if abs(Y[i] - Y[j]) < 6 * hc:
                continue
            p = (X[j] - X[i]) / (Y[j] - Y[i])
            if abs(p) > 0.15:
                continue
            q = X[i] - p * Y[i]
            dentro = restantes & (np.abs(X - (p * Y + q)) < 0.4 * hc)
            if melhor is None or dentro.sum() > melhor.sum():
                melhor = dentro
        if melhor is None or melhor.sum() < 8 or np.ptp(Y[melhor]) < 10 * hc:
            break
        p, q = np.polyfit(Y[melhor], X[melhor], 1)
        retas.append((float(p * Ym + q), float(p), int(melhor.sum())))
        restantes &= ~melhor
    return retas


class MapaHorizontal:
    """x_origem = h(X, Y) = X + p(X)·(Y − Ym), com p(X) = p0 + p1·X.

    Corrige o cisalhamento horizontal (página girada) e o trapézio
    (perspectiva): cada alinhamento vertical do texto tem uma inclinação p;
    ajustamos p variando linearmente com x e endireitamos todos de uma vez.
    """

    def __init__(self, retas: list[tuple], Ym: float, largura: int):
        self.Ym = Ym
        self.p0, self.p1 = 0.0, 0.0
        if not retas:
            return
        xs = np.array([r[0] for r in retas])
        ps = np.array([r[1] for r in retas])
        w = np.array([r[2] for r in retas], np.float64)
        if len(retas) >= 2 and np.ptp(xs) > 0.3 * largura:
            A = np.stack([np.ones_like(xs), xs], 1) * np.sqrt(w)[:, None]
            self.p0, self.p1 = np.linalg.lstsq(A, ps * np.sqrt(w), rcond=None)[0]
        else:
            self.p0 = float(np.average(ps, weights=w))

    def h(self, X, Y):
        X = np.asarray(X, np.float64)
        return X + (self.p0 + self.p1 * X) * (np.asarray(Y, np.float64) - self.Ym)

    def h_inv(self, x, Y):
        dY = np.asarray(Y, np.float64) - self.Ym
        return (np.asarray(x, np.float64) - self.p0 * dY) / (1.0 + self.p1 * dY)


# -------------------------------------------------------------- remapear ---

def _mapas(campo: CampoVertical, horiz: MapaHorizontal, X0: float, X1: float, Y0: float, Y1: float, passo: int = 4):
    Xc = np.arange(X0, X1 + passo, passo, dtype=np.float64)
    Yc = np.arange(Y0, Y1 + passo, passo, dtype=np.float64)
    X, Y = np.meshgrid(Xc, Yc)
    xs = horiz.h(X, Y)
    ys = Y.copy()
    for _ in range(12):
        ys = Y + campo.D(xs, ys)
    Wn = int(round(X1 - X0))
    Hn = int(round(Y1 - Y0))
    # mapa grosso -> resolução cheia (o campo é suave): amostragem bilinear
    # exata, o pixel fino (X, Y) lê a posição (X/passo, Y/passo) da grade grossa
    fx, fy = np.meshgrid(np.arange(Wn, dtype=np.float32) / passo, np.arange(Hn, dtype=np.float32) / passo)
    mx = cv2.remap(xs.astype(np.float32), fx, fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    my = cv2.remap(ys.astype(np.float32), fx, fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return mx, my


def desentortar(norm: np.ndarray, extras: list[np.ndarray] | None = None) -> tuple[np.ndarray, list[np.ndarray], dict]:
    """Corrige a página. `norm` é a página em cinza com iluminação normalizada.

    `extras` são outras imagens do mesmo tamanho (versão colorida, máscara)
    que recebem exatamente a mesma transformação.
    Retorna (pagina_corrigida, extras_corrigidos, info).
    """
    H, W = norm.shape[:2]
    hc = medir_letra(norm)
    th = limiar_texto(norm, hc)
    segs = segmentos_de_linha(th, hc, norm)
    info = {"altura_letra_px": round(hc, 1), "trechos_de_linha": len(segs)}

    # pouco texto (página curta, figura) -> modelo com menos nós, mais rígido
    campo = CampoVertical(W, H, nos=20 if len(segs) >= 40 else 8)
    if len(segs) < 6:
        info["aviso"] = "pouco texto detectado: curvatura não corrigida"
        return norm, list(extras or []), info | {"linhas": [], "hc": hc, "mapa": None}

    campo.ajustar([s["pts"] for s in segs], hc)
    linhas = juntar_em_linhas(segs, campo, hc)
    res = campo.ajustar([l["pts"] for l in linhas], hc)
    info["linhas_de_texto"] = len(linhas)
    info["erro_residual_px"] = round(float(np.sqrt(np.mean(res ** 2))), 2) if res.size else None

    # margens no espaço retificado
    Yl, xa, xb = [], [], []
    for l in linhas:
        p = l["pts"]
        Yl.append(float(np.median(p[:, 1] - campo.D(p[:, 0], p[:, 1]))))
        xa.append(l["x0"])
        xb.append(l["x1"])
    Yl, xa, xb = np.array(Yl), np.array(xa), np.array(xb)
    longas = (xb - xa) > 4 * hc
    retas = alinhamentos_verticais(np.r_[Yl[longas], Yl[longas]], np.r_[xa[longas], xb[longas]], hc, W)
    horiz = MapaHorizontal(retas, float(np.median(Yl)), W)
    info["alinhamentos_verticais"] = len(retas)
    info["cisalhamento"] = [round(horiz.p0, 4), round(horiz.p1 * W, 4)]

    # extensão da saída: para onde vai cada ponto do papel da página original
    gy, gx = np.mgrid[0:H:8, 0:W:8]
    papel = np.ones_like(gx, bool)
    if extras and extras[0].shape[:2] == (H, W) and extras[0].ndim == 2:
        papel = extras[0][::8, ::8] > 0
    gx, gy = gx[papel].astype(np.float64), gy[papel].astype(np.float64)
    Ysrc = gy - campo.D(gx, gy)
    Xsrc = horiz.h_inv(gx, Ysrc)
    Y0, Y1 = float(Ysrc.min()), float(Ysrc.max())
    X0, X1 = float(Xsrc.min()), float(Xsrc.max())
    # proteção contra extrapolação exagerada do modelo
    X0, X1 = max(X0, -0.25 * W), min(X1, 1.25 * W)
    Y0, Y1 = max(Y0, -0.25 * H), min(Y1, 1.25 * H)
    mx, my = _mapas(campo, horiz, X0, X1, Y0, Y1)

    saida = cv2.remap(norm, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    extras_out = []
    for e in extras or []:
        if e.ndim == 2 and e.dtype == np.uint8 and set(np.unique(e[::17, ::17])) <= {0, 255}:
            extras_out.append(cv2.remap(e, mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0))
        else:
            extras_out.append(cv2.remap(e, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE))

    # caixa das linhas no espaço de saída (para recortar depois)
    caixas = []
    for Y, a, b in zip(Yl, xa, xb):
        Xa = float(horiz.h_inv(a, Y))
        Xb = float(horiz.h_inv(b, Y))
        caixas.append((Xa - X0, Xb - X0, Y - Y0))
    info |= {"linhas": caixas, "hc": hc}
    return saida, extras_out, info
