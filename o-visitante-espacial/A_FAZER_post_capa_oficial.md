# A fazer: post da capa oficial (edição brasileira)

Pedido do Lukyam em 27/11/2026, para depois: "eu vou pedir para fazer mais ou menos a mesma coisa, só que com a outra capa. A capa da versão oficial. E vai ser mais completo, mas deixa isso como a fazer".

Situação: pendente, à espera do pedido dele. Nada foi feito ainda.

## O que é

Um carrossel no mesmo estilo do post da capa inglesa (`post_capa_final/`), agora com a capa da edição brasileira, que é a oficial, publicada na Amazon em Kindle e impresso. A capa tem o disco de ouro desenhado de forma geométrica, a estrela vermelha e o título em Jost. "Mais completo" quer dizer mais slides e mais camadas do que o da capa inglesa.

## O que já se sabe da capa

- **Nas palavras dele:** "A capa da versão brasileira não é menos trabalhada que a versão americana, apenas com um intuito de ser mais clean, com a forma do disco de uma maneira geométrica e fazendo uma referência ao olho, algo semelhante ao livro 1984, que gosto bastante, uma referência ao vilão da obra, Salazar Saddler (quem entende sabe de quem foi a referência que tive ao nomear o vilão kkk)".
- **Versões:** disco claro em 25/09/2026 e disco em ouro em 29/09/2026 (a final). O azul foi aprovado por ele em 29/09.
- **Texto da capa:** o título está em Jost; o subtítulo é "Talvez não se trate apenas de uma ficção científica"; o autor é "Lukyam Madeira".
- **Akaihi** é a estrela vermelha, e aqui da Terra é a Betelgeuse. A cor dela na capa ainda é provisória, até a prova impressa.
- **Publicação:** Kindle e impresso já estavam na Amazon em 27/10/2026, quando ele avisou que tinha publicado. O impresso é 6 x 9, papel creme, 340 páginas, com lombada de uns 2,2 cm.

## Primeira ideia de slides (para ele ajustar)

1. **O livro brasileiro em 3D realista.** É o mesmo pipeline do Blender do slide 1 da capa inglesa. O cenário é a decidir: o mesmo veludo, para formar uma série, ou algo mais limpo, que combine com uma capa "clean".
2. **O disco:** o Disco de Ouro da Voyager, desenhado de forma geométrica.
3. **O olho:** o disco também é um olho, como em *1984*, e é uma referência a Salazar Saddler, sem spoiler.
4. **A estrela vermelha e a linha tracejada.** É Akaihi, ou seja, a Betelgeuse. Antes, perguntar se a linha pode ser chamada de rota.
5. **A evolução:** do disco claro (25/09) ao disco em ouro (29/09).
6. **Brasileira e americana lado a lado.** Já existe no post da capa inglesa.
7. **Onde comprar** (Kindle e impresso), se ele quiser um slide de venda.
8. **Opcional:** um trecho curto do livro, escolhido por ele, ou um reels curto com a câmera girando em volta do livro.

A legenda parte do texto dele sobre a capa, citado acima.

## Perguntas para ele antes de começar

1. Mesmo cenário de veludo, para virar série, ou um cenário próprio?
2. O olho e o Saddler podem ser explicados no slide, ou só sugeridos?
3. A linha tracejada até a estrela pode ser chamada de rota?
4. Entra um slide de venda, com Amazon, Kindle e impresso?
5. Entra um trecho do livro? Qual?

## Onde está o material

- **Capa em alta:** no Drive, a capa do Kindle de 29/09 (1600 x 2560) e a capa aberta "G1" de 29/09, a mesma usada no slide 5 deste post. As cópias tratadas para o Instagram estão em `capas_todas/06_PT_29-09_disco_ouro.jpg` e `stories_capas/06_PT_capa_aberta_ouro_29-09.jpg`.
- **Livro 3D:** `post_capa_final/fonte/blender/book_scene.py --book pt` precisa da `wrap_pt.png`, montada com o verso, a lombada e a frente da capa aberta. O recorte da frente é `(1906,34)-(3546,2494)`, a lombada vai de 1674 a 1906 px e a escala é de 273,3 px por polegada.
- **Slides:** `post_capa_final/fonte/slides.html` (`st=misto`), com as mesmas regras de texto e visual do `CLAUDE.md` desta pasta.
