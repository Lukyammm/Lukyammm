"""OCR em português (Tesseract) e montagem do PDF pesquisável."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np

from .layout import regioes_de_leitura

PASTA_MODELOS = Path(__file__).resolve().parent.parent / "modelos"


def tesseract_disponivel() -> bool:
    return shutil.which("tesseract") is not None


def _tessdata_do_sistema() -> Path | None:
    try:
        r = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True)
    except FileNotFoundError:
        return None
    m = re.search(r'"(.+?)"', r.stdout + r.stderr)
    return Path(m.group(1)) if m else None


def preparar_tessdata(destino: Path) -> tuple[Path, str]:
    """Monta uma pasta tessdata com o modelo de português mais preciso.

    Usa `modelos/por.traineddata` (tessdata_best) se existir; senão, o do
    sistema. Copia junto as configurações (necessárias para gerar PDF).
    Retorna (pasta, descrição do modelo usado).
    """
    sistema = _tessdata_do_sistema()
    destino.mkdir(parents=True, exist_ok=True)
    if sistema and sistema.exists():
        for nome in ("configs", "tessconfigs"):
            if (sistema / nome).is_dir() and not (destino / nome).exists():
                shutil.copytree(sistema / nome, destino / nome)
        for nome in ("pdf.ttf", "osd.traineddata", "eng.traineddata"):
            if (sistema / nome).exists() and not (destino / nome).exists():
                shutil.copy2(sistema / nome, destino / nome)
    melhor = PASTA_MODELOS / "por.traineddata"
    if melhor.exists():
        shutil.copy2(melhor, destino / "por.traineddata")
        return destino, "português (tessdata_best)"
    if sistema and (sistema / "por.traineddata").exists():
        shutil.copy2(sistema / "por.traineddata", destino / "por.traineddata")
        return destino, "português (modelo padrão do sistema)"
    raise RuntimeError("Modelo de português do Tesseract não encontrado (instale tesseract-ocr-por).")


def ocr_pagina(png: Path, base: Path, tessdata: Path, dpi: int) -> tuple[str, Path, float]:
    """OCR de uma página. Gera `base.txt` e `base.pdf` (só a camada de texto).

    As regiões de leitura (colunas/faixas) vão num arquivo .uzn ao lado da
    imagem: o Tesseract lê região por região, na ordem certa.
    Retorna (texto, pdf_texto, confiança média 0-100).
    """
    img = cv2.imread(str(png), cv2.IMREAD_GRAYSCALE)
    regioes = regioes_de_leitura(img)
    png.with_suffix(".uzn").write_text("".join(f"{x} {y} {w} {h} Text\n" for x, y, w, h in regioes))
    cmd = ["tesseract", str(png), str(base), "--tessdata-dir", str(tessdata), "-l", "por",
           "--psm", "4", "--dpi", str(dpi), "-c", "textonly_pdf=1", "txt", "pdf", "tsv"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Tesseract falhou: {r.stderr[-500:]}")
    png.with_suffix(".uzn").unlink(missing_ok=True)
    texto = base.with_suffix(".txt").read_text(encoding="utf-8", errors="replace")
    conf = _confianca(base.with_suffix(".tsv"))
    base.with_suffix(".tsv").unlink(missing_ok=True)
    return texto, base.with_suffix(".pdf"), conf


def _confianca(tsv: Path) -> float:
    vals = []
    try:
        for linha in tsv.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            partes = linha.split("\t")
            if len(partes) >= 12 and partes[11].strip():
                c = float(partes[10])
                if c >= 0:
                    vals.append(c)
    except (OSError, ValueError):
        return 0.0
    return float(np.mean(vals)) if vals else 0.0


def numero_da_pagina(texto: str) -> int | None:
    """Número impresso da página (no cabeçalho ou rodapé), se der para ler."""
    # descarta lixo curto de OCR (sobras de borda) que não tem letras/dígitos
    linhas = [l.strip() for l in texto.splitlines() if len(re.findall(r"\w", l)) >= 1]
    if not linhas:
        return None

    def numero_na_ponta(l: str) -> int | None:
        for padrao in (r"^(\d{1,4})(?=\s|$)(?![.,/º°ª])", r"(?<![\d.,;/:])\s(\d{1,4})$", r"^(\d{1,4})$"):
            m = re.search(padrao, l)
            if m and 0 < int(m.group(1)) < 3000:
                return int(m.group(1))
        return None

    # 1º cabeçalho (primeiras linhas), número na ponta da linha
    for l in linhas[:3]:
        n = numero_na_ponta(l)
        if n is not None:
            return n
    # 2º rodapé: só linha curta (um número sozinho, "— 12 —"), para não pegar
    # números do fim de uma referência ("2004; 38")
    for l in linhas[-2:]:
        s = re.sub(r"[^\w]", " ", l).strip()
        if len(s) <= 8 and re.fullmatch(r"\d{1,4}", s.replace(" ", "")):
            return int(s.replace(" ", ""))
    return None


def completar_numeros(nums: list[int | None]) -> list[tuple[int | None, bool]]:
    """Corrige/deduz números de página pela sequência (vizinhos consecutivos).

    Retorna [(numero, deduzido?)]. Um número que não combina com os dois
    vizinhos (erro de OCR) é trocado pelo valor esperado.
    """
    n = len(nums)
    saida: list[tuple[int | None, bool]] = [(x, False) for x in nums]
    for i in range(n):
        ant = next(((j, nums[j]) for j in range(i - 1, -1, -1) if nums[j]), None)
        dep = next(((j, nums[j]) for j in range(i + 1, n) if nums[j]), None)
        if ant and dep and dep[1] - ant[1] == dep[0] - ant[0]:
            esperado = ant[1] + (i - ant[0])
            if nums[i] != esperado:
                saida[i] = (esperado, True)
        elif nums[i] is None and ant and not dep:
            saida[i] = (ant[1] + (i - ant[0]), True)
        elif nums[i] is None and dep and not ant:
            v = dep[1] - (dep[0] - i)
            saida[i] = (v if v > 0 else None, v > 0)
    return saida


def montar_pdf(paginas: list[Path], pdfs_texto: list[Path | None], saida: Path, dpi: int, titulo: str) -> None:
    """Junta imagem (JPEG compacto) + camada de texto invisível em um único PDF."""
    import img2pdf
    from pypdf import PdfReader, PdfWriter

    tmp = saida.parent / "_tmp_pdf"
    tmp.mkdir(exist_ok=True)
    jpgs = []
    for p in paginas:
        img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
        j = tmp / (p.stem + ".jpg")
        cv2.imwrite(str(j), img, [cv2.IMWRITE_JPEG_QUALITY, 88])
        jpgs.append(j)
    layout = img2pdf.get_fixed_dpi_layout_fun((dpi, dpi))
    (tmp / "imagens.pdf").write_bytes(img2pdf.convert([str(j) for j in jpgs], layout_fun=layout))

    imagens = PdfReader(str(tmp / "imagens.pdf"))
    escritor = PdfWriter()
    for i, pagina in enumerate(imagens.pages):
        pdf_t = pdfs_texto[i] if i < len(pdfs_texto) else None
        if pdf_t and pdf_t.exists():
            camada = PdfReader(str(pdf_t)).pages[0]
            # ajusta a escala caso os tamanhos difiram por arredondamento
            sx = float(pagina.mediabox.width) / float(camada.mediabox.width)
            sy = float(pagina.mediabox.height) / float(camada.mediabox.height)
            from pypdf import Transformation

            pagina.merge_transformed_page(camada, Transformation().scale(sx, sy))
        escritor.add_page(pagina)
    escritor.add_metadata({"/Title": titulo, "/Producer": "escaneador-livro"})
    with open(saida, "wb") as f:
        escritor.write(f)
    shutil.rmtree(tmp, ignore_errors=True)
