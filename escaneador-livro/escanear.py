#!/usr/bin/env python3
"""Escaneador de livro: transforma um vídeo (ou fotos) folheando um livro em
páginas "escaneadas", um PDF pesquisável e o texto (OCR em português).

Uso rápido:
    python escanear.py video_do_livro.mp4
    python escanear.py fotos/            # pasta com fotos das páginas
    python escanear.py foto1.jpg foto2.jpg -o saida/meu_livro

Veja `python escanear.py --help` e o README.md para todas as opções.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shutil
import sys
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault("OMP_THREAD_LIMIT", "1")  # tesseract: 1 thread por processo

import cv2  # noqa: E402

from escaneador.livro import separar_paginas  # noqa: E402
from escaneador.ocr import (completar_numeros, montar_pdf, numero_da_pagina,  # noqa: E402
                            ocr_pagina, preparar_tessdata, tesseract_disponivel)
from escaneador.pagina import processar_pagina  # noqa: E402
from escaneador.quadros import (analisar_video, escolher_quadros, ler_quadros,  # noqa: E402
                                nitidez, remover_repetidos)

VIDEOS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp", ".mts"}
IMAGENS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic"}
DPI = 300
# "spawn" evita travamentos do fork com OpenCV/OpenMP (e é o modo do Windows)
CONTEXTO = multiprocessing.get_context("spawn")


def log(msg: str) -> None:
    print(msg, flush=True)


def barra(fracao: float, largura: int = 30) -> str:
    n = int(round(fracao * largura))
    return "[" + "#" * n + "." * (largura - n) + f"] {fracao * 100:5.1f}%"


# ------------------------------------------------------------ entradas ----

def coletar_entradas(caminhos: list[str]) -> list[Path]:
    arquivos: list[Path] = []
    for c in caminhos:
        p = Path(c)
        if p.is_dir():
            arquivos += sorted(q for q in p.iterdir() if q.suffix.lower() in VIDEOS | IMAGENS)
        elif p.exists():
            arquivos.append(p)
        else:
            sys.exit(f"Arquivo não encontrado: {c}")
    if not arquivos:
        sys.exit("Nenhum vídeo ou imagem encontrado.")
    return arquivos


def quadros_do_video(video: Path, pasta: Path, fps_amostra: float, inicio: int) -> list[dict]:
    log(f"\n▶ Analisando o vídeo {video.name} …")
    ultimo = [0.0]

    def prog(f):
        if f - ultimo[0] >= 0.05:
            ultimo[0] = f
            print("\r  " + barra(f), end="", flush=True)

    fps, amostras = analisar_video(video, fps_amostra, prog)
    print("\r  " + barra(1.0))
    duracao = amostras[-1].tempo if amostras else 0
    log(f"  {duracao:.1f}s de vídeo, {len(amostras)} quadros analisados ({fps:.0f} fps)")
    escolhas = escolher_quadros(amostras, fps_amostra)
    log(f"  {len(escolhas)} momentos com o livro parado")
    ler_quadros(video, escolhas)
    escolhas = remover_repetidos(escolhas)
    log(f"  {len(escolhas)} aberturas diferentes do livro após remover repetidos")
    saida = []
    for k, e in enumerate(escolhas):
        nome = pasta / f"quadro_{inicio + k + 1:03d}.jpg"
        cv2.imwrite(str(nome), e.imagem, [cv2.IMWRITE_JPEG_QUALITY, 95])
        saida.append({"arquivo": str(nome), "origem": video.name, "tempo_s": round(e.tempo, 2),
                      "parado_de_s": round(e.inicio, 2), "parado_ate_s": round(e.fim, 2),
                      "nitidez": round(e.nitidez, 1)})
    return saida


def quadro_de_imagem(img_path: Path, pasta: Path, indice: int) -> dict | None:
    img = cv2.imread(str(img_path))
    if img is None:
        log(f"  ⚠ não consegui ler {img_path.name} (formato não suportado?) — pulando")
        return None
    nome = pasta / f"quadro_{indice:03d}.jpg"
    cv2.imwrite(str(nome), img, [cv2.IMWRITE_JPEG_QUALITY, 97])
    return {"arquivo": str(nome), "origem": img_path.name, "nitidez": round(nitidez(img), 1)}


# ------------------------------------------------------------ páginas -----

def _trabalho_quadro(args: tuple) -> list[dict]:
    caminho, modo, colorido, pasta_paginas, n_quadro = args
    cv2.setNumThreads(1)
    img = cv2.imread(caminho)
    paginas, info_livro = separar_paginas(img, modo)
    resultados = []
    for pag in paginas:
        t = time.time()
        final, info = processar_pagina(pag, colorido=colorido)
        destino = Path(pasta_paginas) / f"_q{n_quadro:03d}_{pag.lado}.png"
        cv2.imwrite(str(destino), final)
        resultados.append({"tmp": str(destino), "quadro": n_quadro, "lado": pag.lado,
                           "livro": info_livro, "correcao": info, "segundos": round(time.time() - t, 1)})
    return resultados


def _trabalho_ocr(args: tuple) -> tuple[str, str | None, float]:
    png, tessdata, dpi = args
    base = Path(png).with_suffix("")
    texto, pdf, conf = ocr_pagina(Path(png), base, Path(tessdata), dpi)
    return texto, str(pdf), conf


def uniformizar_tamanho(pngs: list[Path]) -> None:
    """Deixa todas as páginas do mesmo tamanho (como num livro escaneado).

    Completa com branco: alinhado pelo topo e centralizado na horizontal.
    Feito antes do OCR para a camada de texto do PDF ficar no lugar certo.
    """
    imgs = [cv2.imread(str(p), cv2.IMREAD_UNCHANGED) for p in pngs]
    if len(imgs) < 2:
        return
    W = max(i.shape[1] for i in imgs)
    H = max(i.shape[0] for i in imgs)
    for p, img in zip(pngs, imgs):
        h, w = img.shape[:2]
        if (h, w) == (H, W):
            continue
        esq = (W - w) // 2
        branco = 255 if img.ndim == 2 else (255, 255, 255)
        img = cv2.copyMakeBorder(img, 0, H - h, esq, W - w - esq, cv2.BORDER_CONSTANT, value=branco)
        cv2.imwrite(str(p), img)


def similaridade(a: str, b: str) -> float:
    pa, pb = re.findall(r"\w+", a.lower()), re.findall(r"\w+", b.lower())
    if len(pa) < 15 or len(pb) < 15:
        return 0.0
    return difflib.SequenceMatcher(None, pa, pb, autojunk=False).ratio()


# ------------------------------------------------------------ principal ---

def main() -> None:
    ap = argparse.ArgumentParser(description="Transforma vídeo/fotos de um livro em páginas escaneadas + PDF pesquisável.")
    ap.add_argument("entradas", nargs="+", help="vídeo(s), foto(s) ou pasta(s) com fotos")
    ap.add_argument("-o", "--saida", help="pasta de saída (padrão: saida/<nome da entrada>)")
    ap.add_argument("--modo", choices=["auto", "duplo", "simples"], default="auto",
                    help="duplo = livro aberto (2 páginas por quadro); simples = 1 página; auto = decide sozinho")
    ap.add_argument("--cor", action="store_true", help="mantém as cores (padrão: tons de cinza, como escâner)")
    ap.add_argument("--sem-ocr", action="store_true", help="não faz OCR (só imagens e PDF sem texto)")
    ap.add_argument("--fps", type=float, default=6.0, help="quadros por segundo analisados no vídeo (padrão 6)")
    ap.add_argument("--titulo", default=None, help="título gravado no PDF")
    ap.add_argument("--processos", type=int, default=max(1, (os.cpu_count() or 2)), help="processos em paralelo")
    a = ap.parse_args()

    entradas = coletar_entradas(a.entradas)
    nome_base = entradas[0].stem if len(entradas) == 1 else entradas[0].parent.name or "livro"
    saida = Path(a.saida) if a.saida else Path("saida") / nome_base
    pasta_quadros, pasta_paginas = saida / "quadros", saida / "paginas"
    pasta_quadros.mkdir(parents=True, exist_ok=True)
    pasta_paginas.mkdir(parents=True, exist_ok=True)
    for velho in list(pasta_paginas.glob("*")) + list(pasta_quadros.glob("*")):
        velho.unlink()
    titulo = a.titulo or nome_base
    t0 = time.time()

    # 1) quadros
    quadros: list[dict] = []
    for e in entradas:
        if e.suffix.lower() in VIDEOS:
            quadros += quadros_do_video(e, pasta_quadros, a.fps, len(quadros))
        else:
            q = quadro_de_imagem(e, pasta_quadros, len(quadros) + 1)
            if q:
                quadros.append(q)
    if not quadros:
        sys.exit("Nenhum quadro utilizável.")
    log(f"\n▶ Corrigindo páginas ({len(quadros)} quadro(s), {a.processos} processo(s)) …")

    # 2) páginas
    tarefas = [(q["arquivo"], a.modo, a.cor, str(pasta_paginas), k + 1) for k, q in enumerate(quadros)]
    resultados: list[dict] = []
    with ProcessPoolExecutor(max_workers=a.processos, mp_context=CONTEXTO) as ex:
        for k, res in enumerate(ex.map(_trabalho_quadro, tarefas)):
            resultados += res
            print("\r  " + barra((k + 1) / len(tarefas)), end="", flush=True)
    print()
    resultados.sort(key=lambda r: (r["quadro"], {"unica": 0, "esquerda": 0, "direita": 1}[r["lado"]]))
    uniformizar_tamanho([Path(r["tmp"]) for r in resultados])

    # 3) OCR
    tem_ocr = not a.sem_ocr and tesseract_disponivel()
    if not a.sem_ocr and not tem_ocr:
        log("  ⚠ Tesseract não encontrado: seguindo sem OCR (veja o README para instalar).")
    modelo = None
    if tem_ocr:
        tessdata, modelo = preparar_tessdata(saida / "_tessdata")
        log(f"\n▶ Lendo o texto (OCR {modelo}) …")
        tarefas = [(r["tmp"], str(tessdata), DPI) for r in resultados]
        with ProcessPoolExecutor(max_workers=a.processos, mp_context=CONTEXTO) as ex:
            for k, (texto, pdf, conf) in enumerate(ex.map(_trabalho_ocr, tarefas)):
                resultados[k] |= {"texto": texto, "pdf_texto": pdf, "confianca_ocr": round(conf, 1),
                                  "numero_impresso": numero_da_pagina(texto)}
                print("\r  " + barra((k + 1) / len(tarefas)), end="", flush=True)
        print()

        # repetidas: mesma página lida duas vezes (quadros diferentes)
        manter = []
        for r in resultados:
            rep = next((m for m in manter[-3:] if similaridade(m["texto"], r["texto"]) > 0.85), None)
            if rep:
                log(f"  página repetida descartada (quadro {r['quadro']}, {r['lado']} = quadro {rep['quadro']}, {rep['lado']})")
                if r["confianca_ocr"] > rep["confianca_ocr"]:
                    manter[manter.index(rep)] = r
                continue
            manter.append(r)
        resultados = manter
        for r, (n, deduzido) in zip(resultados, completar_numeros([r["numero_impresso"] for r in resultados])):
            r["numero_livro"] = n
            r["numero_deduzido"] = deduzido

    # 4) nomes finais
    for k, r in enumerate(resultados, 1):
        destino = pasta_paginas / f"pagina_{k:03d}.png"
        Path(r["tmp"]).replace(destino)
        r["arquivo"] = str(destino)
        r["pagina"] = k
        if r.get("pdf_texto"):
            novo_pdf = pasta_paginas / f"_texto_{k:03d}.pdf"
            Path(r["pdf_texto"]).replace(novo_pdf)
            r["pdf_texto"] = str(novo_pdf)
    for resto in pasta_paginas.glob("_q*"):
        resto.unlink()

    # 5) PDF + texto
    log("\n▶ Montando o PDF …")
    pdf_final = saida / f"{nome_base}.pdf"
    montar_pdf([Path(r["arquivo"]) for r in resultados],
               [Path(r["pdf_texto"]) if r.get("pdf_texto") else None for r in resultados],
               pdf_final, DPI, titulo)
    for p in pasta_paginas.glob("_texto_*.pdf"):
        p.unlink()
    for p in pasta_paginas.glob("*.txt"):
        p.unlink()
    shutil.rmtree(saida / "_tessdata", ignore_errors=True)

    avisos = []
    if tem_ocr:
        with open(saida / f"{nome_base}.txt", "w", encoding="utf-8") as f:
            for r in resultados:
                imp = f" (página {r['numero_livro']} do livro)" if r.get("numero_livro") else ""
                f.write(f"\n===== Página {r['pagina']}{imp} =====\n\n{r['texto'].strip()}\n")
        nums = [r.get("numero_livro") for r in resultados]
        conhecidos = [(i, n) for i, n in enumerate(nums) if n]
        for (i1, n1), (i2, n2) in zip(conhecidos, conhecidos[1:]):
            esperado = n1 + (i2 - i1)
            if n2 > esperado:
                avisos.append(f"Possível falta de página(s) entre a nº {n1} e a nº {n2} (arquivos {i1 + 1} e {i2 + 1}).")
            elif n2 < esperado and n2 <= n1:
                avisos.append(f"Ordem estranha: nº {n2} depois da nº {n1} (arquivos {i1 + 1} e {i2 + 1}).")
        for r in resultados:
            if r["confianca_ocr"] < 70:
                avisos.append(f"Página {r['pagina']}: OCR com confiança baixa ({r['confianca_ocr']}%): confira o texto.")
    for r in resultados:
        if r["correcao"].get("aviso"):
            avisos.append(f"Página {r['pagina']}: {r['correcao']['aviso']}.")

    relatorio = {
        "titulo": titulo,
        "entradas": [str(e) for e in entradas],
        "quadros": quadros,
        "modelo_ocr": modelo,
        "paginas": [{k: v for k, v in r.items() if k not in ("texto", "tmp", "pdf_texto")} for r in resultados],
        "avisos": avisos,
        "tempo_total_s": round(time.time() - t0, 1),
    }
    (saida / "relatorio.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")

    linhas = [f"Escaneamento: {titulo}", f"Páginas geradas: {len(resultados)}", ""]
    for r in resultados:
        imp = r.get("numero_livro")
        conf = r.get("confianca_ocr")
        marca = "*" if r.get("numero_deduzido") else " "
        linhas.append(f"  pagina_{r['pagina']:03d}.png  quadro {r['quadro']:>3} ({r['lado']:<8})"
                      + (f"  pág. do livro {imp:>4}{marca}" if imp else "  pág. do livro    ? ")
                      + (f"  OCR {conf:5.1f}%" if conf is not None else ""))
    if any(r.get("numero_deduzido") for r in resultados):
        linhas += ["", "  * número deduzido pela sequência (não foi lido com segurança na página)"]
    linhas += ["", "Avisos:" if avisos else "Sem avisos."] + [f"  - {x}" for x in avisos]
    (saida / "relatorio.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    log("\n✔ Pronto!")
    log(f"  PDF:      {pdf_final}")
    if tem_ocr:
        log(f"  Texto:    {saida / (nome_base + '.txt')}")
    log(f"  Páginas:  {pasta_paginas}/")
    log(f"  Relatório:{saida / 'relatorio.txt'}")
    for x in avisos:
        log(f"  ⚠ {x}")
    log(f"  Tempo total: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
