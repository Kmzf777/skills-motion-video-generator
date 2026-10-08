// Peça modelo — a RAIZ: escolhe a cena pelo quadro, aplica o CHICOTE colado nas trocas
// e põe por cima de tudo o grão de filme, a pílula (legenda A) e o som. A colagem
// (legenda B) mora nas cenas.
//
// PEÇA NOVA: depois de copiar a pasta, registre em `src/Raiz.tsx`:
//   import * as P01 from './pecas/01-tema/Peca';
//   <Composition id="P01-tema" component={P01.Peca} durationInFrames={P01.DURACAO}
//     fps={P01.FPS} width={1080} height={1920} />

import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import '../../colagem/fontes-colagem';
import {REPOUSO} from '../../colagem/camera';
import {cenaEm, chicoteEm, problemasDosChicotes, type Chicote} from '../../colagem/chicote';
import {Palco} from '../../colagem/palco';
import {Pilula} from '../../colagem/tipos';
import {COR} from '../../identidade/tokens';
import {FPS, fq, GraoFilme} from './apoio';
import {Cena1, Cena2, Cena3} from './cenas';
import {BLOCOS_A, CENA_INICIO, FIM, TROCA} from './roteiro';
import {Sons} from './Sons';

export {FPS};

/** Duração da peça em quadros: derivada do FIM, que é derivado da última palavra. */
export const DURACAO = fq(FIM);

const CENAS = [Cena1, Cena2, Cena3];
const LIMITES = CENA_INICIO.map(fq);

/**
 * Trocas por CHICOTE: quadro, eixo e sentido. As de papel (Cobertura) moram nas cenas
 * (aqui, a 1 → 2). As internas leem `TROCA`, o mesmo número que a cena usa para mudar de
 * fase. Toda troca de enquadramento tem chicote OU cobertura -- corte seco é salto.
 */
export const CHICOTES: Chicote[] = [
  {q: fq(TROCA.resto), eixo: 'y', dir: 1}, // a câmera desce: a fase nova entra por baixo
  {q: LIMITES[2], eixo: 'x', dir: -1},
];

// Janela fora da peça ou chicotes a menos de 12 quadros um do outro: falha no bundle,
// não no meio do render.
const problemas = problemasDosChicotes(CHICOTES, DURACAO);
if (problemas.length) throw new Error(`Peça: chicotes inválidos — ${problemas.join('; ')}`);

/** Tema da pílula pelo FUNDO da cena: 'escuro' = pílula clara, 'claro' = pílula profunda. */
function temaEm(q: number): 'claro' | 'escuro' {
  const i = cenaEm(q, LIMITES);
  if (i === 0) return 'escuro';
  if (i === 1) return q >= fq(TROCA.resto) ? 'escuro' : 'claro';
  return 'claro';
}

export const Peca: React.FC = () => {
  const q = useCurrentFrame();
  const Cena = CENAS[cenaEm(q, LIMITES)];
  const ch = chicoteEm(q, CHICOTES);
  // No chicote, a imagem que sai e a que entra andam COLADAS, uma tela inteira, cada uma
  // congelada no seu último/primeiro quadro durante a janela. Assim a troca de fase
  // dentro de uma cena (TROCA) também funciona: a mesma cena, dois quadros diferentes.
  let conteudo = <Cena q={q} />;
  if (ch) {
    const W = ch.eixo === 'x' ? 1080 : 1920;
    const sai = -ch.dir * ch.u * W;
    const tr = (v: number) => (ch.eixo === 'x' ? `translateX(${v}px)` : `translateY(${v}px)`);
    const Sai = CENAS[cenaEm(ch.q - 1, LIMITES)];
    const Entra = CENAS[cenaEm(ch.q, LIMITES)];
    conteudo = (
      <>
        <AbsoluteFill style={{transform: tr(sai)}}><Sai q={Math.min(q, ch.q - 1)} /></AbsoluteFill>
        <AbsoluteFill style={{transform: tr(sai + ch.dir * W)}}><Entra q={Math.max(q, ch.q)} /></AbsoluteFill>
      </>
    );
  }
  return (
    <AbsoluteFill style={{background: COR.escuro}}>
      <Palco cam={REPOUSO} id="raiz" chicote={ch ? {k: ch.k, eixo: ch.eixo} : null}>
        <AbsoluteFill>{conteudo}</AbsoluteFill>
      </Palco>
      <GraoFilme q={q} forca={0.1} />
      <Pilula q={q} fps={FPS} blocos={BLOCOS_A} formato="organico" tema={temaEm(q)} />
      <Sons />
    </AbsoluteFill>
  );
};
