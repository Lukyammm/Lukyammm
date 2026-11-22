"""Monta um PDF novo, digitado e limpo, a partir da transcrição página a página.

Formato da transcrição (um arquivo por página do livro, pagina_NN.txt):

    @pagina N                      página do livro onde o texto começa
    +texto                         continua o parágrafo da página anterior
    ## Título  /  ### Subtítulo
    - item de lista
    @item Negrito. | texto         item com seta (ex.: "▸ Faturamento. ...")
    @abertura N | Título           abertura de capítulo (seguida de @autores e @objetivos ... @fim)
    @tabela Nome | Legenda         linhas "a | b | c" (a 1ª é o cabeçalho), @fonte ..., @fim
    @ref N texto  /  @ref+ texto   referência bibliográfica (ou continuação dela)
    @continua texto                nota final
    ^12^ = sobrescrito, *x* = itálico

uso: python3 -m escaneador.diagramar PASTA_TRANSCRICAO saida.pdf --titulo "..."
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def _inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\^([^^]+)\^", r"<sup>\1</sup>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"(https?://\S+?|www\.\S+?)([.,;)]?)(?=\s|$)",
               lambda m: f'<span class="url">{m.group(1)}</span>{m.group(2)}', t)
    return t


def _marca(n: int) -> str:
    return f'<span class="pg" title="início da página {n} do livro">{n}</span>'


class Montador:
    def __init__(self):
        self.out: list[str] = []
        self.capitulo = None          # (numero, titulo)
        self.lista: str | None = None  # "ul" ou "refs"
        self.marca_pendente: int | None = None

    # ---------- utilidades ----------
    def fechar_lista(self):
        if self.lista == "ul":
            self.out.append("</ul>")
        elif self.lista == "itens":
            self.out.append("</div>")
        elif self.lista == "refs":
            self.out.append("</ol>")
        self.lista = None

    def abrir_lista(self, tipo: str, extra: str = ""):
        if self.lista == tipo:
            return
        self.fechar_lista()
        self.out.append({"ul": "<ul>", "itens": '<div class="itens">',
                         "refs": f'<ol class="refs"{extra}>'}[tipo])
        self.lista = tipo

    def marca(self) -> str:
        if self.marca_pendente is None:
            return ""
        m = _marca(self.marca_pendente)
        self.marca_pendente = None
        return m

    def continuar(self, texto: str):
        """Junta texto ao último elemento (parágrafo, item ou referência)."""
        for i in range(len(self.out) - 1, -1, -1):
            fim = re.search(r"</(p|li)>$", self.out[i])
            if fim:
                tag = fim.group(1)
                corpo = self.out[i][: -len(f"</{tag}>")]
                self.out[i] = f"{corpo} {self.marca()}{_inline(texto)}</{tag}>"
                return
        self.out.append(f"<p>{self.marca()}{_inline(texto)}</p>")

    # ---------- blocos ----------
    def abertura(self, num: str, titulo: str, autores: str, objetivos: list[str], intro: str):
        self.fechar_lista()
        self.capitulo = (num, titulo)
        itens = "".join(f"<li>{_inline(o)}</li>" for o in objetivos)
        self.out.append(f"""
<section class="abertura">
  <div class="cap-rotulo">Capítulo</div>
  <div class="cap-num">{html.escape(num)}</div>
  <h1>{_inline(titulo)}</h1>
  <div class="autores">{_inline(autores)}</div>
  <div class="objetivos">
    <div class="obj-tit">Objetivos de aprendizagem</div>
    <p>{_inline(intro)}</p>
    <ul>{itens}</ul>
  </div>
</section>""")

    def tabela(self, nome: str, legenda: str, linhas: list[list[str]], fonte: str):
        self.fechar_lista()
        cab = "".join(f"<th>{_inline(c)}</th>" for c in linhas[0])
        corpo = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in l) + "</tr>" for l in linhas[1:])
        self.out.append(f"""
<figure class="tabela">
  <figcaption><b>{_inline(nome)}</b> {_inline(legenda)}</figcaption>
  <table><thead><tr>{cab}</tr></thead><tbody>{corpo}</tbody></table>
  <div class="fonte">{_inline(fonte)}</div>
</figure>""")

    def processar(self, linhas: list[str]):
        i = 0
        while i < len(linhas):
            l = linhas[i].rstrip()
            i += 1
            if not l.strip():
                if self.lista == "ul":
                    self.fechar_lista()
                continue
            if l.startswith("@pagina"):
                self.marca_pendente = int(l.split()[1])
            elif l.startswith("@abertura"):
                num, titulo = [x.strip() for x in l[len("@abertura"):].split("|", 1)]
                autores, intro, objetivos = "", "", []
                while i < len(linhas) and not linhas[i].startswith("@fim"):
                    s = linhas[i].rstrip()
                    if s.startswith("@autores"):
                        autores = s[len("@autores"):].strip()
                    elif s.startswith("@objetivos"):
                        intro = s[len("@objetivos"):].strip()
                    elif s.startswith("- "):
                        objetivos.append(s[2:])
                    i += 1
                i += 1
                self.abertura(num, titulo, autores, objetivos, intro)
            elif l.startswith("@tabela"):
                nome, legenda = [x.strip() for x in l[len("@tabela"):].split("|", 1)]
                rows, fonte = [], ""
                while i < len(linhas) and not linhas[i].startswith("@fim"):
                    s = linhas[i].rstrip()
                    if s.startswith("@fonte"):
                        fonte = s[len("@fonte"):].strip()
                    elif s.strip():
                        rows.append([c.strip() for c in s.split("|")])
                    i += 1
                i += 1
                self.tabela(nome, legenda, rows, fonte)
            elif l.startswith("@ref+"):
                self.continuar(l[len("@ref+"):].strip())
            elif l.startswith("@ref"):
                n, texto = l[len("@ref"):].strip().split(" ", 1)
                if self.lista != "refs":
                    self.abrir_lista("refs", f' start="{int(n)}"')
                self.out.append(f'<li value="{int(n)}">{self.marca()}{_inline(texto)}</li>')
            elif l.startswith("@item"):
                cab, texto = [x.strip() for x in l[len("@item"):].split("|", 1)]
                self.abrir_lista("itens")
                self.out.append(f'<p class="item">{self.marca()}<b>{_inline(cab)}</b> {_inline(texto)}</p>')
            elif l.startswith("@continua"):
                self.fechar_lista()
                self.out.append(f'<p class="continua">{_inline(l[len("@continua"):].strip())}</p>')
            elif l.startswith("+"):
                self.continuar(l[1:].strip())
            elif l.startswith("### "):
                self.fechar_lista()
                self.out.append(f'<h3>{self.marca()}{_inline(l[4:])}</h3>')
            elif l.startswith("## "):
                self.fechar_lista()
                self.out.append(f'<h2>{self.marca()}{_inline(l[3:])}</h2>')
            elif l.startswith("- "):
                self.abrir_lista("ul")
                self.out.append(f"<li>{self.marca()}{_inline(l[2:])}</li>")
            else:
                if self.lista in ("ul", "itens"):
                    self.fechar_lista()
                self.out.append(f"<p>{self.marca()}{_inline(l)}</p>")
        # fim do arquivo: listas de referências continuam na página seguinte


CSS = r"""
@page { size: 170mm 240mm; margin: 17mm 18mm 17mm 18mm; }
* { box-sizing: border-box; }
html { font-family: 'Liberation Serif', 'Times New Roman', serif; font-size: 10.8pt; color: #111;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; }
.capa { height: 204mm; display: flex; flex-direction: column; justify-content: center; text-align: center;
  break-after: page; }
.capa .sup { font: 600 10pt 'Liberation Sans', sans-serif; letter-spacing: .18em; text-transform: uppercase; color: #8a1c1c; }
.capa h1 { font: 700 22pt 'Liberation Sans', sans-serif; margin: 8mm 0 4mm; line-height: 1.2; }
.capa .sub { font-size: 12pt; color: #333; }
.capa .info { margin-top: 18mm; font-size: 9.5pt; color: #444; line-height: 1.6; }
.capa .info b { color: #111; }
.colunas { }
p { margin: 0; text-align: justify; line-height: 1.42; text-indent: 1.2em; orphans: 2; widows: 2; }
h2 + p, h3 + p, .abertura + p, ul + p, .itens + p, figure + p { text-indent: 0; }
h2 { font: 700 12.5pt 'Liberation Sans', sans-serif; margin: 5mm 0 2mm; line-height: 1.2; break-after: avoid;
  padding-left: 2.2mm; border-left: 2.2mm solid #b33a3a; }
h3 { font: 700 10.5pt 'Liberation Sans', sans-serif; margin: 3.5mm 0 1.2mm; break-after: avoid; color: #222; }
h3::before { content: "▸ "; color: #b33a3a; }
ul { margin: 1.5mm 0 2mm; padding-left: 4.5mm; }
ul li { line-height: 1.38; margin: .4mm 0; text-align: justify; }
ul li::marker { content: "■  "; color: #b33a3a; font-size: 7pt; }
.itens { margin: 1mm 0 2mm; }
.item { text-indent: 0; padding-left: 3.5mm; margin: .6mm 0; }
.item b { font-family: 'Liberation Sans', sans-serif; font-size: 9.4pt; }
.item b::before { content: "▸ "; color: #b33a3a; margin-left: -3.5mm; }
sup { font-size: .68em; line-height: 0; }
.url { word-break: break-all; }
.pg { float: none; display: inline-block; font: 600 6.6pt 'Liberation Sans', sans-serif; color: #fff;
  background: #9a9a9a; border-radius: 1.2mm; padding: .1mm 1mm; margin-right: 1mm; vertical-align: .25em;
  text-indent: 0; line-height: 1.25; }
.pg::before { content: "p. "; }
.abertura { column-span: all; break-before: page; margin: 0 0 6mm; }
.abertura:first-child { break-before: auto; }
.cap-rotulo { font: 700 8.5pt 'Liberation Sans', sans-serif; letter-spacing: .2em; text-transform: uppercase;
  color: #fff; background: #b33a3a; display: inline-block; padding: 1mm 3mm; }
.cap-num { font: 700 30pt 'Liberation Sans', sans-serif; color: #b33a3a; line-height: 1; margin: 1mm 0 0; }
.abertura h1 { font: 400 19pt 'Liberation Sans', sans-serif; margin: 3mm 0 2.5mm; line-height: 1.2; }
.autores { font: 9.5pt 'Liberation Sans', sans-serif; color: #444; border-bottom: .3mm solid #ccc; padding-bottom: 3mm; }
.objetivos { background: #f3eeee; border-left: 1.2mm solid #b33a3a; padding: 3mm 4mm; margin-top: 4mm; }
.obj-tit { font: 700 10pt 'Liberation Sans', sans-serif; margin-bottom: 1mm; }
.objetivos p { text-indent: 0; font-style: italic; font-size: 9.4pt; }
.objetivos ul { margin-bottom: 0; }
.tabela { column-span: all; margin: 4mm 0; break-inside: avoid; }
.tabela figcaption { font: 9.5pt 'Liberation Sans', sans-serif; margin-bottom: 1.5mm; }
.tabela figcaption b { color: #b33a3a; }
.tabela table { width: 100%; border-collapse: collapse; font: 8.6pt/1.3 'Liberation Sans', sans-serif; }
.tabela th { text-align: left; background: #e9dede; padding: 1.4mm 2mm; border-bottom: .4mm solid #b33a3a; }
.tabela td { padding: 1.2mm 2mm; border-bottom: .2mm solid #ddd; vertical-align: top; }
.tabela tr:nth-child(even) td { background: #faf7f7; }
.tabela .fonte { font: italic 8pt 'Liberation Sans', sans-serif; color: #555; margin-top: 1mm; }
ol.refs { margin: 1mm 0; padding-left: 7mm; font-size: 9pt; line-height: 1.3; }
ol.refs li { margin: 0 0 1mm; text-align: left; }
.continua { text-indent: 0; font-style: italic; color: #666; margin-top: 3mm; text-align: right; }
.nota { column-span: all; break-before: page; font-size: 9.2pt; color: #333; }
.nota h2 { border: 0; padding: 0; }
.nota p { text-indent: 0; margin-bottom: 2mm; }
"""


def montar_html(pasta: Path, titulo: str, subtitulo: str, origem: str) -> str:
    arquivos = sorted(pasta.glob("pagina_*.txt"))
    if not arquivos:
        raise SystemExit(f"nenhum pagina_*.txt em {pasta}")
    m = Montador()
    for a in arquivos:
        m.processar(a.read_text(encoding="utf-8").splitlines())
    m.fechar_lista()
    pags = [int(re.search(r"(\d+)", a.stem).group(1)) for a in arquivos]
    capa = f"""
<section class="capa">
  <div class="sup">Transcrição digitada</div>
  <h1>{_inline(titulo)}</h1>
  <div class="sub">{"<br>".join(_inline(x.strip()) for x in subtitulo.split("|"))}</div>
  <div class="info">
    Páginas <b>{min(pags)} a {max(pags)}</b> do livro original<br>
    Texto transcrito a partir de {_inline(origem)}<br>
    As etiquetas <span class="pg">{min(pags)}</span> marcam onde começa cada página do livro impresso.
  </div>
</section>"""
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>{html.escape(titulo)}</title><style>{CSS}</style></head>
<body>{capa}<main class="colunas">{''.join(m.out)}</main></body></html>"""


def gerar_pdf(html_path: Path, pdf_path: Path, titulo: str):
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://{html_path.resolve()}', {{ waitUntil: 'load' }});
  await p.pdf({{ path: '{pdf_path.resolve()}', preferCSSPageSize: true, printBackground: true,
                displayHeaderFooter: false, outline: true, tagged: true }});
  await b.close();
}})().catch(e => {{ console.error(e); process.exit(1); }});
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(js)
    subprocess.run(["node", f.name], check=True)
    try:
        from pypdf import PdfReader, PdfWriter
        r = PdfReader(str(pdf_path)); w = PdfWriter(clone_from=r)
        w.add_metadata({"/Title": titulo, "/Producer": "escaneador-livro"})
        with open(pdf_path, "wb") as fh:
            w.write(fh)
    except Exception as e:  # metadados são opcionais
        print("aviso: metadados não gravados:", e, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta", type=Path)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--titulo", default="Livro")
    ap.add_argument("--subtitulo", default="")
    ap.add_argument("--origem", default="vídeo das páginas")
    a = ap.parse_args()
    doc = montar_html(a.pasta, a.titulo, a.subtitulo, a.origem)
    html_path = a.saida.with_suffix(".html")
    html_path.write_text(doc, encoding="utf-8")
    gerar_pdf(html_path, a.saida, a.titulo)
    print(f"PDF: {a.saida}")


if __name__ == "__main__":
    main()
