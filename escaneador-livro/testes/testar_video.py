#!/usr/bin/env python3
"""Teste de ponta a ponta: gera o vídeo sintético, roda o escaneador e confere.

Verifica: quantidade de páginas (a tremida não pode duplicar página), números
de página lidos na ordem certa e taxa de acerto do OCR contra o gabarito.

Uso: python testes/testar_video.py   (sai com código 1 se algo falhar)
"""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def palavras(t: str) -> list[str]:
    return re.findall(r"[\wÀ-ÿ]+", t.lower())


def acerto(gabarito: str, lido: str) -> float:
    g, l = palavras(gabarito), palavras(lido)
    sm = difflib.SequenceMatcher(None, g, l, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks()) / max(1, len(g))


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        video = tmp / "video_teste.mp4"
        subprocess.run([sys.executable, str(RAIZ / "testes" / "gerar_video_teste.py"), str(video)], check=True)
        saida = tmp / "saida"
        subprocess.run([sys.executable, str(RAIZ / "escanear.py"), str(video), "-o", str(saida)], check=True, cwd=RAIZ)

        gabarito = {int(k): v for k, v in json.loads(video.with_suffix(".json").read_text()).items()}
        rel = json.loads((saida / "relatorio.json").read_text())
        texto = (saida / "video_teste.txt").read_text()
        blocos = re.split(r"\n===== Página \d+.*=====\n", texto)[1:]

        falhas = []
        paginas = rel["paginas"]
        print(f"\nPáginas geradas: {len(paginas)} (esperado {len(gabarito)})")
        if len(paginas) != len(gabarito):
            falhas.append("quantidade de páginas")
        nums = [p.get("numero_livro") for p in paginas]
        print(f"Números de página: {nums} (esperado {sorted(gabarito)})")
        if nums != sorted(gabarito):
            falhas.append("números de página")
        for p, bloco in zip(paginas, blocos):
            n = p.get("numero_livro")
            if n in gabarito:
                a = acerto(gabarito[n], bloco)
                print(f"  página {n}: OCR {a * 100:.1f}% das palavras")
                if a < 0.90:
                    falhas.append(f"OCR página {n}")
        print("\nRESULTADO:", "OK ✔" if not falhas else f"FALHOU: {', '.join(falhas)}")
        return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
