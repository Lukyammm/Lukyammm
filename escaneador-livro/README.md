# 📖 Escaneador de livro (vídeo → PDF)

Transforma um **vídeo do celular folheando um livro** (ou fotos das páginas) em:

- **páginas "escaneadas"**: retas, sem curvatura da lombada, sem perspectiva, papel branco e texto nítido;
- **um PDF pesquisável**: dá para buscar palavras e copiar o texto;
- **o texto completo** em `.txt` (OCR em português), separado por página;
- **um relatório**: quais quadros do vídeo viraram quais páginas, o número impresso de cada página e avisos (página faltando, OCR fraco).

Roda no computador, não manda nada para a internet.

---

## 🎥 Como gravar o vídeo (isso é o que mais faz diferença)

| Faça | Por quê |
|---|---|
| **Celular na horizontal (deitado)**, com o livro aberto **ocupando a tela toda** | No modo em pé o livro aberto fica pequeno no meio do quadro: perde-se metade da resolução. |
| **Enquadre as duas páginas inteiras**, com um pouquinho de mesa em volta | Se a margem de fora da página ficar fora do quadro, o começo/fim das linhas se perde (não dá para recuperar depois). |
| Câmera **de cima, paralela ao livro** (apoie em algo ou use um suporte) | Quanto menos inclinada, menos distorção. O programa corrige, mas texto pequeno na parte "longe" perde nitidez. |
| **Pause ~1 segundo em cada abertura** antes de virar a folha | O programa escolhe o quadro mais nítido de cada pausa. |
| Aperte o livro perto da lombada (mão na borda, sem cobrir o texto) | Perto da dobra as letras ficam espremidas; quanto mais plano, melhor. |
| Luz uniforme, **sem reflexo** no papel e sem sombra do celular | Brilho estourado apaga letras. |
| Grave em **1080p ou 4K**, 30 fps | Mais pixels por letra = OCR melhor. |
| Mande o **arquivo original** do vídeo (não pelo WhatsApp) | O WhatsApp comprime e reduz a resolução. Use Google Drive, cabo ou "enviar como documento". |

---

## ▶️ Como usar

```bash
python3 escanear.py video_do_livro.mp4
```

Outros exemplos:

```bash
python3 escanear.py fotos/                      # pasta com fotos (na ordem do nome)
python3 escanear.py parte1.mp4 parte2.mp4       # vários vídeos, em sequência
python3 escanear.py video.mov -o saida/meu_livro --titulo "Nome do Livro"
python3 escanear.py video.mp4 --cor             # mantém as cores (padrão: tons de cinza)
python3 escanear.py fotos/ --modo simples       # cada foto mostra só uma página
```

| Opção | O que faz |
|---|---|
| `-o PASTA` | Onde salvar (padrão: `saida/<nome do arquivo>`). |
| `--modo auto/duplo/simples` | `duplo` = livro aberto (2 páginas por quadro); `simples` = 1 página; `auto` (padrão) decide pela proporção. |
| `--cor` | Mantém as cores (bom para livros com figuras coloridas). |
| `--titulo "..."` | Título gravado no PDF. |
| `--sem-ocr` | Só imagens e PDF, sem texto. |
| `--fps N` | Quadros por segundo analisados no vídeo (padrão 6). |
| `--processos N` | Quantos núcleos usar (padrão: todos). |

### O que sai na pasta

```
saida/<nome>/
├── <nome>.pdf          ← PDF pesquisável (imagem + texto invisível por cima)
├── <nome>.txt          ← texto de todas as páginas, com "===== Página N =====" entre elas
├── paginas/            ← pagina_001.png, pagina_002.png … (300 dpi, todas do mesmo tamanho)
├── quadros/            ← os quadros do vídeo que foram usados (para conferência)
├── relatorio.txt       ← resumo legível: página do livro de cada arquivo, OCR, avisos
└── relatorio.json      ← o mesmo, completo, para uso em outros programas
```

---

## 💻 Instalação

**Linux / macOS**

```bash
./instalar.sh
```

(instala o Tesseract com português, as bibliotecas Python e baixa o modelo de OCR mais preciso).

**Windows**

1. Instale o [Python 3](https://www.python.org/downloads/) (marque *Add Python to PATH*).
2. Instale o Tesseract pelo instalador da [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) e marque o idioma **Portuguese** em *Additional language data*. Adicione `C:\Program Files\Tesseract-OCR` ao PATH.
3. No terminal, dentro desta pasta: `pip install -r requirements.txt`
4. (Recomendado) Baixe o [modelo preciso de português](https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/por.traineddata) e salve em `modelos\por.traineddata`.

Sem o modelo da etapa 4 o programa usa o modelo de português do próprio Tesseract (um pouco menos preciso).

---

## ⚙️ Como funciona

1. **Escolha dos quadros** (`escaneador/quadros.py`): mede o movimento entre quadros; cada pausa vira uma candidata e fica o quadro mais nítido (variância do Laplaciano). Pausas vizinhas que mostram as mesmas páginas (a câmera tremeu) são unidas comparando pontos de interesse (ORB + homografia) só dentro do papel.
2. **Livro e lombada** (`escaneador/livro.py`): o papel é a maior região clara e pouco saturada; a mesa que encosta nele é removida. A lombada é a faixa vertical com menos tinta e com a sombra da dobra, medida em várias alturas e ajustada por uma reta (o livro pode estar torto).
3. **Desentortar** (`escaneador/desentortar.py`): acha os trechos de linha de texto e ajusta um campo suave de deslocamento vertical (splines em x × polinômio em y) que deixa todas as linhas retas — inclusive a dobra forte perto da lombada. Depois, as margens, bordas de coluna e recuos (que numa página plana são verticais) corrigem a perspectiva/trapézio. Bordas cortadas pela foto são ignoradas.
4. **Realce** (`escaneador/realce.py`): divide pela iluminação estimada (some a sombra da mão e da lombada), nitidez e níveis: papel branco, texto preto.
5. **Layout e OCR** (`escaneador/layout.py`, `escaneador/ocr.py`): detecta colunas e títulos de largura total e entrega as regiões ao Tesseract na ordem de leitura (o modo automático mistura colunas quando o espaço entre elas é estreito). Lê o número impresso da página e deduz pela sequência quando não dá para ler.
6. **PDF** : imagem JPEG + camada de texto invisível, uma página por arquivo, todas do mesmo tamanho.

---

## ✅ Testes

```bash
python3 testes/testar_video.py
```

Gera um vídeo sintético (livro aberto curvado, em perspectiva, sobre uma mesa, com tremida de câmera e a mão virando 2 folhas), roda o escaneador e confere: quantidade de páginas (a tremida não pode duplicar página), números de página e acerto do OCR. Resultado atual: **6/6 páginas, números 10–15 corretos, OCR de 95,5% a 100% das palavras**.

### Teste com a foto real (páginas 2 e 3 de um livro técnico)

Foto enviada pelo WhatsApp (900×1600 px, celular em pé, livro ocupando só metade de baixo, margens externas cortadas): as duas páginas saíram retas e limpas, mas o OCR acertou ~80% das palavras — limite da resolução (cada letra tinha ~6 px de altura) e do texto espremido junto à lombada. Com um vídeo original em 1080p/4K seguindo as dicas acima, a qualidade fica no nível do teste sintético.

---

## Limitações conhecidas

- Texto que **não aparece** na gravação (margem cortada, dedo em cima, reflexo) não tem como ser recuperado.
- Letras muito espremidas dentro da dobra da lombada ficam difíceis de ler: aperte o livro ao gravar.
- Páginas só com imagem (sem texto) não são desentortadas (não há linhas para medir a curvatura) — saem só recortadas e realçadas.
- O OCR é bom, mas não perfeito: para uso acadêmico, revise o `.txt` (o relatório aponta as páginas com confiança baixa).
