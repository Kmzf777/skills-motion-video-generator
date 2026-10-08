// As peças de papel da colagem. Cada uma recebe o quadro ABSOLUTO da peça (`q`) e o
// quadro em que começa (`ini`), e devolve a pose pela gramática de
// `movimento-colagem.ts`. Nada aqui sorteia: toda variação vem da semente do nome.
//
// Coordenadas em pixel do quadro 1080x1920, sempre do CENTRO da peça.
//
// DE ONDE VÊM AS IMAGENS
//   Recorte, Fita, Tachinha  -> `public/colagem/<nome>-b0|b1|b2.png` da peça, publicados
//                               da biblioteca por `motion/ferramentas/biblioteca.py
//                               publicar`. As 3 variantes de borda (boil) são cortadas
//                               pela UNIÃO dos bboxes -- bbox próprio por variante faz o
//                               objeto "respirar" 2,4% a cada 3 quadros.
//   ProdutoRecortado         -> `public/colagem/<produto>.png`: o recorte REAL do produto,
//                               registrado na biblioteca e publicado como peça única por
//                               `biblioteca.py publicar` (todo asset da peça mora em
//                               public/colagem/).
//   LogoMarca                -> `motion/marca/logo-*` pelo identidade.json (ver
//                               identidade/arquivos-marca.ts).
// Arquivo que falta derruba o render (o `<Img>` do Remotion cancela): é de propósito.

import React, {useEffect, useState} from 'react';
import {cancelRender, continueRender, delayRender, Img, staticFile} from 'remotion';
import {urlDaMarca} from '../identidade/arquivos-marca';
import {COR, IDENTIDADE} from '../identidade/tokens';
import {PILHA} from '../identidade/tipografia';
import {ASSENTAR_QUADROS, assentar, boil, carimbar, posterizar, progresso, saida} from './movimento-colagem';
import {PAPEL, SOMBRA} from './papel';
import {sorteio} from './semente';

/** Saída "arrancada": a peça voa para o lado a partir de `fora`. */
function arranque(q: number, fora: number | undefined, chave: string) {
  if (fora === undefined || q < fora) return {dx: 0, dy: 0, rot: 0};
  const t = saida((q - fora) / 7);
  const lado = sorteio(`${chave}#lado`, 0, 1) < 0.5 ? -1 : 1;
  return {dx: lado * 1500 * t * t, dy: -260 * t, rot: lado * 45 * t};
}

/**
 * Recorte da biblioteca: assenta em passo de stop-motion, depois ferve entre b0/b1/b2.
 * `fora` arranca a peça do quadro; `treme` sacode a peça a partir de um quadro (o
 * objeto que destoa); `unico` lê `<nome>.png` sem variantes (textura, fundo);
 * `deriva` = px por quadro, para a peça escorregar devagar.
 */
export const Recorte: React.FC<{
  q: number; ini: number; nome: string; x: number; y: number; w: number; rot?: number; fora?: number;
  semBoil?: boolean; treme?: number; sombra?: boolean; opacidade?: number; unico?: boolean; deriva?: [number, number];
}> = ({q, ini, nome, x, y, w, rot = 0, fora, semBoil, treme, sombra = true, opacidade = 1, unico, deriva = [0, 0]}) => {
  const chave = nome + x;
  const p = assentar(posterizar(q, 3, ini), ini, chave);
  if (!p.visivel) return null;
  const assentou = q >= ini + ASSENTAR_QUADROS;
  const b = assentou && !semBoil && !unico ? boil(q, chave) : {variante: 0 as const, rot: 0};
  const a = arranque(q, fora, chave);
  const tr = treme !== undefined && q >= treme ? Math.sin(posterizar(q, 2) * 1.7) * 7 : 0;
  const vivo = Math.max(0, q - ini);
  const src = unico ? `colagem/${nome}.png` : `colagem/${nome}-b${b.variante}.png`;
  return (
    <Img src={staticFile(src)} style={{
      position: 'absolute', left: x - w / 2, top: y, width: w,
      transform: `translate(${a.dx + deriva[0] * vivo}px, ${p.dy + a.dy + deriva[1] * vivo}px) translateY(-50%) ` +
        `rotate(${rot + p.rot + b.rot + a.rot + tr}deg) scale(${p.escala})`,
      opacity: p.opacidade * opacidade, filter: sombra ? SOMBRA.recorte : undefined,
    }} />
  );
};

/** Troca de objeto NO MESMO LUGAR (match cut): um recorte por janela. */
export const Troca: React.FC<{q: number; itens: Array<{nome: string; ini: number; w: number; rot?: number}>; x: number; y: number; ate?: number}> = ({
  q, itens, x, y, ate,
}) => {
  const atual = [...itens].reverse().find((i) => q >= i.ini);
  if (!atual || (ate !== undefined && q >= ate)) return null;
  return <Recorte q={q} ini={atual.ini} nome={atual.nome} x={x} y={y} w={atual.w} rot={atual.rot ?? 0} />;
};

/** Fita adesiva: chega um pouco grande e cola em 3 quadros. `nome` = o recorte da fita. */
export const Fita: React.FC<{q: number; ini: number; x: number; y: number; w?: number; rot?: number; chave: string; nome?: string; fora?: number}> = ({
  q, ini, x, y, w = 200, rot = 0, chave, nome = 'fita', fora,
}) => {
  if (q < ini || (fora !== undefined && q >= fora)) return null;
  const v = q >= ini + 3 ? boil(q, chave).variante : 0;
  const s = 1.15 - 0.15 * progresso(q, ini, ini + 3);
  return (
    <Img src={staticFile(`colagem/${nome}-b${v}.png`)} style={{
      position: 'absolute', left: x - w / 2, top: y - w * 0.13, width: w, transform: `rotate(${rot}deg) scale(${s})`,
    }} />
  );
};

/** Tachinha: bate (1,4 → 1) e fica. `nome` = o recorte da tachinha (usa a variante b0). */
export const Tachinha: React.FC<{q: number; ini: number; x: number; y: number; nome?: string; s?: number}> = ({
  q, ini, x, y, nome = 'tachinha', s = 70,
}) => {
  if (q < ini) return null;
  const e = q - ini < 2 ? 1.4 : 1;
  return (
    <Img src={staticFile(`colagem/${nome}-b0.png`)} style={{
      position: 'absolute', left: x - s / 2, top: y - s / 2, width: s, transform: `scale(${e})`,
      filter: 'drop-shadow(2px 6px 4px rgba(0,0,0,0.4))',
    }} />
  );
};

/** Carimbo de borda (veredito): bate grande e assenta em 3 quadros, com tremor no impacto. */
export const Carimbo: React.FC<{
  q: number; ini: number; x: number; y: number; rot?: number; tamanho?: number;
  cor?: string; fundo?: string; children: React.ReactNode; fora?: number; chave: string;
}> = ({q, ini, x, y, rot = -6, tamanho = 90, cor = COR.acento, fundo = 'transparent', children, fora, chave}) => {
  const c = carimbar(q, ini);
  if (!c.visivel) return null;
  const tremor = q - ini < 2 ? sorteio(`${chave}#t${q}`, -1.2, 1.2) : 0;
  const a = arranque(q, fora, chave);
  return (
    <div style={{
      position: 'absolute', left: x, top: y,
      transform: `translate(-50%,-50%) translate(${a.dx}px,${a.dy}px) rotate(${rot + tremor + a.rot}deg) scale(${c.escala})`,
      border: `${Math.round(tamanho * 0.08)}px solid ${cor}`, color: cor, background: fundo,
      padding: `${tamanho * 0.12}px ${tamanho * 0.28}px`, fontFamily: PILHA.manchete,
      fontSize: tamanho, lineHeight: 1, whiteSpace: 'nowrap', letterSpacing: 1,
    }}>{children}</div>
  );
};

/**
 * Manchete RECORTADA: cada palavra numa tira de papel própria, colada na hora em que é
 * dita (`palavras: [texto, quadro]`). A letra é código (fonte de manchete da marca); o
 * "recorte" é só a caixa.
 */
export const Manchete: React.FC<{
  q: number; palavras: Array<[string, number]>; x?: number; y: number; tamanho?: number;
  papel?: string; tinta?: string; quebraDepois?: number[]; chave: string; alinhar?: 'centro' | 'esquerda';
}> = ({q, palavras, x = 0, y, tamanho = 120, papel = COR.claro, tinta = COR.profundo, quebraDepois = [], chave, alinhar = 'centro'}) => {
  const linhas: Array<Array<[string, number, number]>> = [[]];
  palavras.forEach(([p, ini], i) => {
    linhas[linhas.length - 1].push([p, ini, i]);
    if (quebraDepois.includes(i)) linhas.push([]);
  });
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, transform: 'translateY(-50%)',
                 display: 'flex', flexDirection: 'column',
                 alignItems: alinhar === 'centro' ? 'center' : 'flex-start',
                 paddingLeft: alinhar === 'centro' ? 0 : x, gap: tamanho * 0.12}}>
      {linhas.map((l, li) => (
        <div key={li} style={{display: 'flex', gap: tamanho * 0.14}}>
          {l.map(([p, ini, i]) => {
            const pose = assentar(q, ini, `${chave}${i}`);
            const r = sorteio(`${chave}${i}#r`, -2.5, 2.5);
            return (
              <div key={i} style={{
                visibility: pose.visivel ? 'visible' : 'hidden', background: papel, color: tinta,
                fontFamily: PILHA.manchete, fontSize: tamanho, lineHeight: 1,
                padding: `${tamanho * 0.1}px ${tamanho * 0.16}px ${tamanho * 0.04}px`,
                transform: `translateY(${pose.dy}px) rotate(${r + pose.rot * 0.5}deg) scale(${pose.escala})`,
                boxShadow: SOMBRA.tira, opacity: pose.opacidade,
              }}>{p}</div>
            );
          })}
        </div>
      ))}
    </div>
  );
};

/** Rótulo em mono, com ou sem papel: o "carimbo de máquina de escrever" da peça. */
export const Rotulo: React.FC<{
  q: number; ini: number; x: number; y: number; texto: string; tamanho?: number; cor?: string;
  centro?: boolean; papel?: string; chave: string;
}> = ({q, ini, x, y, texto, tamanho = 44, cor = COR.claro, centro = true, papel, chave}) => {
  const pose = assentar(q, ini, chave);
  if (!pose.visivel) return null;
  return (
    <div style={{
      position: 'absolute', left: x, top: y,
      transform: `translate(${centro ? '-50%' : '0'},-50%) translateY(${pose.dy * 0.5}px) rotate(${pose.rot * 0.4}deg)`,
      fontFamily: PILHA.dado, fontSize: tamanho, color: cor, letterSpacing: tamanho * 0.08,
      whiteSpace: 'nowrap', opacity: pose.opacidade, background: papel,
      padding: papel ? `${tamanho * 0.25}px ${tamanho * 0.45}px` : 0,
    }}>{texto}</div>
  );
};

/** Tira de nota: papel claro com rótulo e uma barra que enche até `valor` (0..1) na cor de acento. */
export const Tira: React.FC<{q: number; ini: number; y: number; rotulo: string; valor: number; chave: string}> =
  ({q, ini, y, rotulo, valor, chave}) => {
    const pose = assentar(q, ini, chave);
    if (!pose.visivel) return null;
    const enche = progresso(q, ini + 2, ini + 14) * valor;
    const r = sorteio(`${chave}#r`, -1.6, 1.6);
    return (
      <div style={{position: 'absolute', left: 120, width: 840, top: y, height: 112,
                   transform: `translateY(-50%) translateY(${pose.dy}px) rotate(${r + pose.rot * 0.4}deg) scale(${pose.escala})`,
                   background: COR.claro, boxShadow: '0 8px 12px rgba(10,6,4,0.35)',
                   display: 'flex', alignItems: 'center', padding: '0 30px', gap: 28, opacity: pose.opacidade}}>
        <div style={{fontFamily: PILHA.manchete, fontSize: 52, color: COR.profundo, width: 300}}>{rotulo}</div>
        <div style={{flex: 1, height: 34, background: PAPEL.trilho, position: 'relative'}}>
          <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${enche * 100}%`, background: COR.acento}} />
        </div>
      </div>
    );
  };

/** Dimensões naturais de uma imagem, segurando o render até saber (delayRender). */
function useDimensoes(src: string): {w: number; h: number} | null {
  const [dim, setDim] = useState<{w: number; h: number} | null>(null);
  const [espera] = useState(() => delayRender(`dimensões de ${src}`));
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      setDim({w: img.naturalWidth, h: img.naturalHeight});
      continueRender(espera);
    };
    img.onerror = () => cancelRender(new Error(`não carregou ${src}: confira public/ da peça`));
    img.src = src;
  }, [src, espera]);
  return dim;
}

/**
 * Produto REAL recortado (PNG com alfa publicado em `public/colagem/`), colado na cena
 * com altura `h` em pé. `arquivo` é o caminho dentro de public/:
 *   <ProdutoRecortado q={q} ini={fq(S3.x.inicio)} arquivo="colagem/<produto>.png" x={540} y={900} h={1000} />
 * Nenhum filter sobre o PNG do produto: a sombra de contato é um div irmão.
 *
 * O PNG tem que estar NA ORIENTAÇÃO DE EXIBIÇÃO (EXIF aplicado na publicação). Se um
 * arquivo vier deitado, `giro` (90/-90/180) gira em CSS, sem reamostrar pixel. E o
 * PNG tem margem transparente: antes de pôr texto perto do produto, MEÇA o bbox do alfa
 * do recorte -- texto nunca cobre logotipo nem selo.
 */
export const ProdutoRecortado: React.FC<{
  q: number; ini: number; arquivo: string; x: number; y: number; h: number; rot?: number;
  giro?: 0 | 90 | -90 | 180; sombra?: boolean; chave?: string;
}> = ({q, ini, arquivo, x, y, h, rot = 0, giro = 0, sombra = true, chave}) => {
  const src = staticFile(arquivo);
  const dim = useDimensoes(src);
  const p = assentar(posterizar(q, 3, ini), ini, chave ?? `produto-${arquivo}`);
  if (!dim || !p.visivel) return null;
  const deitado = giro === 90 || giro === -90;
  const escala = h / (deitado ? dim.w : dim.h);
  const w = (deitado ? dim.h : dim.w) * escala;
  const [iw, ih] = [dim.w * escala, dim.h * escala];
  return (
    <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h,
                 transform: `translateY(${p.dy}px) rotate(${rot + p.rot * 0.5}deg) scale(${p.escala})`, opacity: p.opacidade}}>
      {sombra && (
        <div style={{position: 'absolute', left: '8%', right: '8%', bottom: -10, height: Math.max(20, h * 0.04),
                     background: 'rgba(20,16,13,0.35)', filter: 'blur(14px)', borderRadius: '50%'}} />
      )}
      <Img src={src} style={{position: 'absolute', width: iw, height: ih, left: (w - iw) / 2, top: (h - ih) / 2,
                             transform: giro ? `rotate(${giro}deg)` : undefined}} />
    </div>
  );
};

/**
 * O LOGO da marca, como PIXEL (nunca redesenhado), de `motion/marca/` conforme o
 * identidade.json. `fundo` diz onde ele pousa: 'claro' usa `logo.sobre_claro`,
 * 'escuro' usa `logo.sobre_escuro`.
 *
 * Sem arquivo de logo: na identidade de EXEMPLO (`"exemplo": true`) desenha o nome da
 * marca como marcador de lugar, com moldura tracejada; numa identidade real, derruba o
 * render -- logo de marca real não se improvisa.
 */
export const LogoMarca: React.FC<{q: number; ini: number; x: number; y: number; largura: number; fundo: 'claro' | 'escuro'; chave?: string}> = ({
  q, ini, x, y, largura, fundo, chave = 'logo',
}) => {
  const p = assentar(posterizar(q, 3, ini), ini, chave);
  if (!p.visivel) return null;
  const lado = fundo === 'claro' ? 'sobre_claro' : 'sobre_escuro';
  const arquivo = IDENTIDADE.logo[lado];
  const pose = `translate(-50%, -50%) translateY(${p.dy}px) rotate(${p.rot * 0.4}deg) scale(${p.escala})`;
  if (arquivo === null) {
    if (!IDENTIDADE.exemplo) {
      throw new Error(
        `identidade.json não tem "logo.${lado}". O logo entra como pixel, nunca redesenhado: ponha o ` +
          `arquivo em motion/marca/logo-<nome>.png e o nome em identidade.json.`,
      );
    }
    const tinta = fundo === 'claro' ? COR.escuro : COR.claro;
    const nome = IDENTIDADE.marca.toUpperCase();
    return (
      <div style={{position: 'absolute', left: x, top: y, width: largura, transform: pose, opacity: p.opacidade,
                   border: `4px dashed ${tinta}`, padding: '22px 16px', textAlign: 'center', color: tinta}}>
        <div style={{fontFamily: PILHA.manchete, fontSize: Math.min(110, (largura * 1.5) / Math.max(4, nome.length)), lineHeight: 1}}>{nome}</div>
        <div style={{fontFamily: PILHA.dado, fontSize: 24, marginTop: 12, opacity: 0.8}}>logo da marca (exemplo)</div>
      </div>
    );
  }
  return (
    <Img src={urlDaMarca(arquivo)} style={{position: 'absolute', left: x, top: y, width: largura, transform: pose, opacity: p.opacidade}} />
  );
};
