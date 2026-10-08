# Bancos livres — Unsplash e Pexels

Foto real de **lugar** (campo, cozinha, rua, céu, oficina) ou de **textura** (papel, madeira,
tecido, parede) quando o banco da empresa não tem.
Ordem da fase 06: biblioteca → banco da empresa → banco livre → ChatGPT. Regras comuns em
`chrome.md`; *(a validar no piloto)* = tela não vista pela sessão que escreveu a semente.
Nenhum dos dois deveria pedir conta para baixar *(a validar no piloto)*: se pedir, pare e
pergunte — nunca crie conta.

## Licença — confira na primeira peça

Unsplash e Pexels publicam licença de uso comercial gratuito, sem atribuição obrigatória, que
proíbe revender a foto sem alteração e sugerir que pessoa ou marca da foto endossa o produto
*(a validar no piloto: leia a página de licença de cada site e anote a data no dossiê)*. Não são
livres:

- **Unsplash+** (selo na miniatura) e fotos **patrocinadas** (iStock/Getty) que aparecem no meio
  da busca — pule;
- o que está **dentro** da foto: a licença cobre a fotografia, não o rosto de quem aparece nem a
  marca no fundo.

## O que escolher

- Pule: rosto identificável, logo ou embalagem de outra marca, texto legível, obra de arte.
- Prefira: vertical, luz parecida com a do resto da peça, sem filtro pesado.
- Foto de banco **nunca** se apresenta como da empresa ("nossa fazenda", "nossa loja"): só se diz
  real o que veio do banco próprio verificado (fase 09).

## Unsplash

1. `tabs_create_mcp` → `https://unsplash.com/s/photos/<termos-com-hifen>?orientation=portrait`
   *(a validar no piloto)*.
   - Procure: o filtro de orientação marcado como retrato/vertical.
   - Se falhar: o filtro não pegou pela URL → use o menu de orientação da página. Cookies → a
     opção mais restritiva.
2. Abra a página da foto (`https://unsplash.com/photos/<slug>`; o id é o fim do slug)
   *(a validar no piloto)*.
   - Confira: sem selo Unsplash+; autor e linha de licença gratuita visíveis; dimensões no
     painel de informações *(a validar no piloto)*.
3. Baixe em **resolução cheia**: o botão principal de download, não os tamanhos menores do menu
   ao lado *(a validar no piloto)*. Modal de agradecimento → `Escape`.
   - Confira: arquivo novo em Downloads, achado pelo **id da foto no nome** (`chrome.md` §4); o
     nome costuma ser `<autor>-<id>-unsplash.jpg` *(a validar no piloto)*.
   - Se falhar: nada chegou → aba nova (um download por aba) e baixe de novo.

## Pexels

1. `tabs_create_mcp` → `https://www.pexels.com/pt-br/procurar/<termos>/?orientation=portrait`
   *(a validar no piloto)*.
   - Se falhar: a URL em português mudou → `https://www.pexels.com/search/<termos>/` e o filtro
     de orientação vertical da página.
2. Abra a página da foto (`https://www.pexels.com/pt-br/foto/<slug>-<id>/`)
   *(a validar no piloto)*.
   - Confira: não é patrocinada (iStock); autor visível.
3. "Baixar grátis" → o tamanho **original** no menu, se houver *(a validar no piloto)*.
   - Confira: arquivo novo achado pelo id no nome; costuma ser `pexels-<autor>-<id>.jpg`
     *(a validar no piloto)*.
   - Se falhar: nada chegou → aba nova e baixe de novo.

## Depois do download (os dois sites)

1. **Conferir o arquivo.** A largura da área que vai ser usada precisa passar de 900 px (o
   `--largura` padrão do `foto_papel.py`). A dimensão de exibição vem com a rotação do EXIF
   aplicada: foto "deitada" no arquivo pode ser vertical na tela — meça com a rotação antes de
   descartar.
2. **Mover o download** para `motion/biblioteca/brutos/<AAAA-MM-DD>_<nome>.jpg`.
3. **Registrar com a origem.** `--fonte` é a URL da **página da foto**, não a do CDN: é ela que
   guarda autor e licença (sem ela, `banco-livre` é recusado).
   - **Lugar**, que entra como foto impressa, com borda rasgada:
     ```bash
     python motion/ferramentas/foto_papel.py motion/biblioteca/brutos/<AAAA-MM-DD>_<nome>.jpg <nome> \
       --categoria foto-real --tags <a,b> --origem banco-livre --fonte <URL da página da foto>
     ```
   - **Textura**, que entra inteira (fundo, papel, madeira). O `registrar` converte o JPG em PNG
     mas não reduz: antes, leve o lado maior a 2000 px
     (`python -c "import sys; from PIL import Image, ImageOps; im=ImageOps.exif_transpose(Image.open(sys.argv[1])); im.thumbnail((2000,2000)); im.save(sys.argv[1])" "<arquivo>"`).
     A foto de lugar não precisa: o `foto_papel.py` já a reduz a `--largura` (900).
     ```bash
     python motion/ferramentas/biblioteca.py registrar <nome> textura motion/biblioteca/brutos/<AAAA-MM-DD>_<nome>.jpg \
       --tags <a,b> --origem banco-livre --fonte <URL da página da foto>
     ```
4. **Publicar na peça** pela fase 06 (`biblioteca.py publicar <NN-tema> <ids...>`).

Sem `--fonte`, a foto fica órfã: ninguém prova depois que ela era livre, e a próxima sessão não a
acha de novo.
