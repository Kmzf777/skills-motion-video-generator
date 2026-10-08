# Fase 06 — Assets da colagem

Toda imagem da colagem entra primeiro na biblioteca da marca (`motion/biblioteca/`), com
procedência, e só então é publicada na peça. Asset não é escasso: a peça de origem publicou 55
peças diferentes para 79 s, porque o parallax pede fundo, cena e primeiro plano em **toda** cena,
e, medido nas referências da origem, o gancho troca de objeto a cada ~0,25 s. Gere à vontade — sempre depois de buscar.

> Bash, da raiz do repositório (as ferramentas recusam rodar de outro lugar). `python` é sempre
> o do `motion/.venv` (fase 00): `motion/.venv/Scripts/python` no Windows,
> `motion/.venv/bin/python` no macOS/Linux.

## Quando

Depois do roteiro aprovado (fase 03) — pode correr junto com as fases 04–05, porque depende do
que a fala diz, não do tempo — e antes da montagem. Peça que faltar na fase 07 volta para cá.

## Entradas

- `roteiro.txt` e `fontes.md` da peça: o que cada bloco mostra.
- `motion/biblioteca/` (`indice.json`, `categorias.json`): a da peça de origem chegou a 74 peças;
  a desta marca começa vazia e cresce a cada peça — `buscar` antes de gerar, sempre.
- O banco de imagens da empresa, com as camadas escritas no dossiê (fase 01).
- `motion/referencias/` e as páginas `navegador/chatgpt.md`, `referencias.md`, `bancos-livres.md`.

## Passos

1. **Faça a lista.** Uma linha por peça: nome (`[a-z0-9-]`, descritivo: `xicara-branca`, não
   `obj1`), categoria de `categorias.json` (categoria nova entra lá antes), cena e palavra,
   plano (fundo · cena · primeiro plano) e tipo (objeto · foto real · textura · produto). Papel
   e grão de filme o motor gera por código; textura real (ex.: `colagem/kraft.png`, pela prop
   `textura` do `Fundo`) só se a cena pedir, e vem da biblioteca como as outras peças. Nada se
   copia à mão de uma peça para outra: o que for reaproveitado se publica de novo (passo 10).

2. **Busque nesta ordem e pare na primeira fonte que serve:**

   | Ordem | Fonte | Para | Como |
   |---|---|---|---|
   | 1 | biblioteca | peça já recortada | `python motion/ferramentas/biblioteca.py buscar <termos>` · `listar [categoria]` |
   | 2 | banco da empresa | produto, lugar, gente e processo reais | camada 1, ou camada 2 confirmada (passo 7) |
   | 3 | Unsplash/Pexels | lugar ou textura real que a empresa não tem | `navegador/bancos-livres.md` |
   | 4 | ChatGPT | objeto, utensílio, alimento, natureza, papelaria | folha sobre branco (passos 3–6) |

   Nunca viram pixel: foto de terceiro (Pinterest, Google, Instagram), camada de quarentena,
   rosto sintetizado. Banco livre nunca se apresenta como foto da empresa.

3. **Folha do ChatGPT.** Mecânica e molde do prompt em `navegador/chatgpt.md` (conversa nova
   por folha). O conteúdo é desta fase:
   - fundo **branco liso #FFFFFF** até a borda: é o que torna o recorte exato em resolução cheia;
   - 3 a 6 objetos **afastados** e inteiros, nenhum encostado ou cortado pela borda;
   - **sem texto, sem embalagem, sem marca, sem rosto** (mão pode); só sombra de contato;
   - a lista em **ordem de leitura** (linhas de cima para baixo, cada uma da esquerda para a
     direita): é nessa ordem que o `--nomes` do recorte batiza as peças.

   Objeto errado numa folha boa: nunca "mude só isso" na mesma conversa — o follow-up regenera o
   quadro inteiro (79% dos pixels mudaram por um pedido que cobria 1%). Pinte de branco o objeto
   ruim na folha (os outros estão afastados) e recorte só os bons, ou gere de novo em conversa nova.

4. **Referência de terceiro — opcional, só estilo, luz e paleta** (spec §7.3):
   - **a regra do repositório vence**: se o `CLAUDE.md` ou os docs proíbem imagem de terceiro
     como guidance, a referência é só texto;
   - sobe só imagem sem rosto identificável, logo ou embalagem de outra marca e marca d'água; o
     resto vira descritor em `motion/referencias/` (`navegador/referencias.md`);
   - o prompt a declara referência de estilo e proíbe copiar composição, objeto, texto e logo
     (frase em `navegador/chatgpt.md`, passo 4); o arquivo fica fora do repositório.

   **Conferência anti-cópia** em toda folha feita com referência — as duas lado a lado. A
   montagem tem pixel de terceiro, então nasce na pasta temporária do sistema, nunca no repositório:

   ```bash
   python - <referencia> motion/biblioteca/brutos/<AAAA-MM-DD>_<folha>.png <<'EOF'
   import pathlib, sys, tempfile
   from PIL import Image, ImageOps
   a, b = (ImageOps.exif_transpose(Image.open(p)).convert("RGB") for p in sys.argv[1:3])
   a, b = (im.resize((round(im.width * 900 / im.height), 900)) for im in (a, b))
   tela = Image.new("RGB", (a.width + b.width + 30, 900), "black")
   tela.paste(a, (0, 0)); tela.paste(b, (a.width + 30, 0))
   saida = pathlib.Path(tempfile.gettempdir()) / "estudio-reels-assets" / f"anticopia-{pathlib.Path(sys.argv[2]).stem}.png"
   saida.parent.mkdir(parents=True, exist_ok=True); tela.save(saida); print(saida.as_posix())
   EOF
   ```

   Olhe a imagem no caminho impresso. Mesmo arranjo, objeto-assinatura, enquadramento ou texto
   da referência → descarte e refaça em conversa nova, com a referência mais fraca ou só em
   texto. O veredito vai ao descritor; a pasta temporária se apaga no fim desta fase (passo 10).

5. **Guarde a folha** em `motion/biblioteca/brutos/<AAAA-MM-DD>_<folha>.png` e o **prompt exato** enviado.

6. **Recorte local:**

   ```bash
   python motion/ferramentas/recortar_folha.py motion/biblioteca/brutos/2026-10-07_utensilios.png \
     --nomes xicara-branca,colher-inox,lupa-latao --categoria utensilio --tags porcelana,inox,vidro \
     --prompt "<o prompt exato enviado ao ChatGPT>" --convexo xicara-branca --lente lupa-latao
   ```

   | Opção | Padrão | Quando mexer |
   |---|---|---|
   | `--limiar` | 22 | 55 quando a sombra suave entra no recorte e vira mancha |
   | `--juntar` | 24 | objeto em pedaços → suba (30–40); dois objetos viraram um → desça (18) |
   | `--area-min` | 2500 | farelo virou peça → suba |
   | `--convexo a,b` | — | branco sobre branco (porcelana, papel): o casco devolve a borda que o limiar comeu |
   | `--lente a` | — | vidro e lente: o miolo branco vira quase transparente |
   | `--filete` | 9 | borda de papel em px; `0` no primeiro plano, que passa desfocado na lente |
   | `--reticula` | desligado | retícula de revista; desligado quando o objeto precisa ser reconhecido |

   Contagem errada falha dizendo quantos objetos achou: ajuste `--juntar`, `--limiar` ou
   `--area-min`, ou gere com mais espaço. As 3 variantes do boil (b0/b1/b2) saem cortadas pela
   **união** dos bboxes — bbox por variante faz o objeto pulsar 2,4% a cada 3 quadros — e cada
   peça é registrada com o prompt. Olhe cada uma sobre magenta (halo vira franja rosa; buraco e
   sombra aparecem) e confira se o nome caiu no objeto certo:

   ```bash
   python - motion/biblioteca/pecas/<categoria>/<AAAA-MM-DD>_<nome>-b0.png <<'EOF'
   import pathlib, sys, tempfile
   from PIL import Image
   im = Image.open(sys.argv[1]).convert("RGBA")
   saida = pathlib.Path(tempfile.gettempdir()) / "estudio-reels-assets" / f"magenta-{pathlib.Path(sys.argv[1]).stem}.png"
   saida.parent.mkdir(parents=True, exist_ok=True)
   Image.alpha_composite(Image.new("RGBA", im.size, (255, 0, 255, 255)), im).save(saida); print(saida.as_posix())
   EOF
   ```

7. **Foto real como papel impresso** (margem clara, borda rasgada; o EXIF é aplicado antes):

   ```bash
   python motion/ferramentas/foto_papel.py <foto do banco> fachada-loja --categoria foto-real \
     --tags fachada,rua --origem real-verificada --largura 900 --recorte 0.05,0.10,0.95,0.80
   ```

   `--recorte x0,y0,x1,y1` em frações da foto já em pé. Camada 1 → `real-verificada`; camada 2
   só depois de o usuário confirmar que a foto é da empresa → `real-nao-verificada`; banco livre
   → `--origem banco-livre --fonte <URL da página da foto>`. O original não se move.

8. **Produto e embalagem: só pixel real**, nunca gerados nem redesenhados (sai um sósia da
   marca; a biblioteca recusa `produto` gerado). Recorte com fundo transparente do banco da
   empresa entra como peça única:

   ```bash
   python motion/ferramentas/biblioteca.py registrar embalagem-frente produto <png-com-alfa> \
     --tags embalagem,frente --origem real-verificada --bruto <foto original>
   ```

   Foto real do produto sobre fundo branco liso: `recortar_folha.py` com `--categoria produto`
   e `--origem real-verificada` (sem `--prompt`); a ferramenta aplica a orientação do EXIF ao
   abrir, e a conferência sobre magenta (passo 6) mostra a peça em pé. Sem nenhuma das duas: a
   foto inteira pelo `foto_papel.py`, ou peça o recorte ao usuário. O logo não passa por aqui
   (fase 07).

9. **Registre com procedência e nome único.** Gerada → `--prompt` (o `biblioteca.py` recusa
   sem); banco livre → `--fonte`; real → `--bruto`. O id é `<AAAA-MM-DD>_<nome>`, e `registrar`
   recusa id que já existe: sobrescreveria o PNG de outra peça. Nome novo, sempre;
   `--substituir` só para a **mesma** peça refeita.

10. **Publique na peça:**

    ```bash
    python motion/ferramentas/biblioteca.py publicar <NN-tema> 2026-10-07_xicara-branca 2026-10-07_fachada-loja
    ```

    Vai para `motion/pecas/<NN-tema>/public/colagem/<nome>-b0.png` … `-b2` (peça única:
    `<nome>.png`). A cena lê pelo **nome**: `publicar` recusa dois nomes iguais na mesma peça.
    Por fim, apague a pasta temporária das conferências (passos 4 e 6):

    ```bash
    python -c "import pathlib, shutil, tempfile; shutil.rmtree(pathlib.Path(tempfile.gettempdir()) / 'estudio-reels-assets', ignore_errors=True)"
    ```

## Saídas

- Biblioteca com procedência, `motion/pecas/<NN-tema>/public/colagem/` com tudo o que a peça usa
  e, em `motion/referencias/`, descritor e veredito anti-cópia de cada referência de terceiro.

## Pronto quando

- toda peça da lista está publicada e foi olhada sobre magenta;
- toda entrada gerada tem `prompt`, banco livre tem `fonte`, real tem `bruto`;
- nenhum pixel de terceiro, de quarentena ou de rosto sintetizado; nenhum texto em imagem gerada;
- toda folha feita com referência passou na conferência anti-cópia, e a pasta temporária
  `estudio-reels-assets` foi apagada (nenhuma montagem com pixel de terceiro ficou para trás).

## Erros comuns

| Sintoma | Causa | Regra |
|---|---|---|
| Duas peças para a mesma coisa | gerou sem `buscar` | `buscar` antes, sempre |
| Mancha em volta do objeto; prato sem borda | sombra no limiar; branco sobre branco | `--limiar 55`; `--convexo` |
| Objeto "respirando" a cada 3 quadros | variantes cortadas uma a uma | só o `recortar_folha.py` (união dos bboxes) |
| PNG de outra peça trocado sem aviso | nome reaproveitado | nome novo; `--substituir` só para a mesma |
| Cena inteira nova em vez de um ajuste | follow-up de edição no ChatGPT | conversa nova ou correção local |
| Embalagem "parecida" com a real | produto gerado | só pixel real, do banco da empresa |

Próxima: fase 07 (`fases/07-montagem.md`).
