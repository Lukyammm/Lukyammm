# O Visitante Espacial: material de Instagram

Esta pasta guarda o material de divulgação do livro no Instagram, feito em 27/11/2026: capas, stories, o carrossel da capa final e os scripts que geram as imagens. O projeto do livro inteiro (manuscrito, edições, regras, histórico) não está aqui. Ele está no Google Drive, em `03_Projetos_Literarios_VSE/`, com o `CLAUDE.md` e o `HISTORICO.md` de lá, e no repositório privado `Lukyammm/o-visitante-espacial`. Fato do livro se confere lá ou com o Lukyam, nunca de memória.

## Próximo trabalho pedido

O post da capa oficial, a da edição brasileira, "mais completo" que o da capa inglesa. O pedido é de 27/11/2026, e ele vai avisar quando quiser começar. Antes, leia [`A_FAZER_post_capa_oficial.md`](A_FAZER_post_capa_oficial.md) e faça as perguntas de lá. A legenda pode terminar com a parte em inglês (ideia em teste, veja abaixo).

## Antes de mexer

1. Leia o `README.md` desta pasta (índice e como refazer cada imagem) e o `DIARIO.md` (o que foi pedido, decidido e aprendido).
2. Não refaça uma decisão do `DIARIO.md` sem motivo novo, e diga qual é o motivo.

## Como o Lukyam quer as coisas

São preferências que ele mostrou nas conversas, não regras fixas. Nas palavras dele (27/11/2026): "tudo que eu falo aqui também é uma conversa, quando for mandatório eu aviso". Quando ele trouxer uma ideia, registre como sugestão e diga se acha que vale a pena.

- **Texto no jeito dele.** Parta das palavras dele e mexa pouco. O tom, nas palavras dele: "irreverente sem ser rude e engraçado sem ser brega". Ele escreve em frases corridas, com vírgula, e às vezes solta um comentário com kkk. Isso não é fórmula: em 27/11 ele avisou que eu estava "só repetindo os mesmos padrões". Varie a abertura, não reaproveite frases de legendas anteriores, use um kkk só quando couber e complemente os slides em vez de repetir o que eles dizem. Se o post já explica, a legenda é curta ("pode ser consiso, afinal de contas a postagem já explica muito"). Ele reconhece como IA: frase de efeito curta, título com metáfora, dois-pontos de revelação, slogan, pergunta-gancho e emoji. Hashtag só quando ele pede, e no máximo 5, o limite do Instagram desde dezembro de 2025. Travessão não entra em texto de entrega (no romance, sim).
- **Ideia em teste: parte em inglês no fim da legenda.** Pedido de 27/11/2026, como sugestão: no fim da legenda, um resumo curto em inglês, para quem é de fora ("eu não estou fazendo ainda conteúdo em inglês... só que eu quero ter também um suporte para quem falar"). Ele ainda está vendo se vale a pena. Curto mesmo: duas ou três frases, não a tradução de cada slide ("nada tão extenso, é algo bem resumido mesmo"). Proponha quando a imagem tiver texto, porque o Instagram traduz a legenda sozinho mas não o que está escrito na imagem. Quando a imagem não tiver texto, diga que não faz falta. A legenda inteira tem que caber em 2.200 caracteres. O primeiro exemplo está em `post_capa_final/legenda.txt`.
- **Visual sem "cara de Claude".** Nada de título pequeno espaçado em cima de título grande em itálico, nem de caixa arredondada com borda dourada. O estilo aprovado é letra branca (Archivo) em caixa preta reta, número dourado e riscos à mão com traço de caneta (perfect-freehand).
- **Realismo por foto ou por simulação de luz.** Quando ele diz que algo não parece real, troque de técnica: foto (Gemini) ou render físico (Blender). Não insista no desenho feito em código.
- **Luz bonita, sombra sutil.** Luz principal na capa, lombada em meia-sombra (com o nome dele aparecendo de leve), contraluz fina e nada de preto total no fundo.
- **Opções lado a lado.** Quando o visual está em aberto, mostre duas ou três direções juntas. Ele escolhe rápido vendo.
- **Ele pede curto e quer que se pense além.** Interprete o pedido, proponha o passo seguinte e diga o que foi feito além do pedido.
- **Ao terminar, registre.** Atualize o `DIARIO.md` e o `README.md` desta pasta. Se tiver o Drive, ponha o registro também em `04_Midia_e_Divulgacao/05_Instagram/` e, no formato do `HISTORICO.md`, num arquivo para mesclar na raiz do projeto.

## Fatos confirmados por ele

- O disco de ouro da Voyager cai num lago em Árret, na frente do Áslan e do avô dele (cap. 1).
- A placa da capa inglesa está molhada (o lago) e queimada (a entrada em Árret).
- Akaihi é o nome que o povo de Árret dá à estrela vermelha que começa a apagar. Aqui da Terra, ela é a Betelgeuse.
- A frase "more than eleven million years later", da contracapa inglesa, não vale para a história.
- Não falar da rota marcada na placa em legenda.

## Ferramentas

- **Slides:** `post_capa_final/fonte/slides.html`, renderizado no Chromium com `shot.js`, `st=misto`.
- **Livro 3D:** `post_capa_final/fonte/blender/book_scene.py`, com o Blender como módulo Python (`pip install bpy`; a versão 5.3 tem wheel para Python 3.13). O render a 1620 x 2025 com 96 amostras leva cerca de 7 minutos em 4 núcleos.
- **Brilhos no veludo:** `glints.py` põe Órion pelas coordenadas reais das estrelas.

## Git

Cada sessão tem o branch dela. Abra o PR como rascunho e não force push.
