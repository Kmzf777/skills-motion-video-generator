// A ATMOSFERA da colagem: fundo de papel, grão de filme, vinheta, foco, sombra
// projetada, cobertura de papel (transição), divisória e nota de rodapé.
//
// Fundo e grão são PROCEDURAIS por padrão (feTurbulence com semente fixa): a peça
// nunca sai em cor chapada digital, mesmo antes de existir textura na biblioteca, e o
// render continua determinístico. Uma textura real (ex.: `colagem/kraft.png` publicado
// da biblioteca) entra por `textura`.

import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {rgba} from '../identidade/cor';
import {COR} from '../identidade/tokens';
import {PILHA} from '../identidade/tipografia';
import {progresso} from './movimento-colagem';
import {semente} from './semente';

/**
 * Textura de papel procedural: fibra fina + manchas largas e fracas, para multiplicar
 * sobre a cor. Centrada perto do branco: escurece só as fibras, sem mudar a cor da marca.
 */
const PapelProcedural: React.FC<{forca: number}> = ({forca}) => (
  <svg width={1080} height={1920} viewBox="0 0 1080 1920"
    style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'multiply', opacity: forca}}>
    <filter id="colagem-papel" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={3} seed={11} result="fibra" />
      <feColorMatrix in="fibra" type="matrix" result="fibraCinza"
        values="0.34 0.34 0 0 0.7  0.34 0.34 0 0 0.69  0.34 0.34 0 0 0.67  0 0 0 0 1" />
      <feTurbulence type="fractalNoise" baseFrequency="0.009" numOctaves={2} seed={5} result="mancha" />
      <feColorMatrix in="mancha" type="matrix" result="manchaCinza"
        values="0.14 0.14 0 0 0.86  0.14 0.14 0 0 0.855  0.14 0.14 0 0 0.85  0 0 0 0 1" />
      <feBlend in="fibraCinza" in2="manchaCinza" mode="multiply" />
    </filter>
    <rect width={1080} height={1920} filter="url(#colagem-papel)" />
  </svg>
);

/**
 * Fundo de cena: a cor (da marca) com textura de papel por cima. `textura` = arquivo em
 * `public/` (ex.: 'colagem/kraft.png'); sem ela, papel procedural. `forca` 0..1.
 */
export const Fundo: React.FC<{cor: string; textura?: string | null; forca?: number}> = ({cor, textura = null, forca = 0.5}) => (
  <AbsoluteFill style={{background: cor}}>
    {textura
      ? <Img src={staticFile(textura)} style={{width: '100%', height: '100%', mixBlendMode: 'multiply', opacity: forca}} />
      : <PapelProcedural forca={forca} />}
  </AbsoluteFill>
);

/**
 * Grão de filme: 4 variantes de ruído que trocam a cada 2 quadros (grão "segurado"
 * 2 quadros, como película), em overlay. Procedural e semeado.
 */
export const GraoFilme: React.FC<{q: number; forca?: number}> = ({q, forca = 0.12}) => {
  const v = Math.floor(q / 2) % 4;
  return (
    <svg width={1080} height={1920} viewBox="0 0 1080 1920"
      style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'overlay', opacity: forca, pointerEvents: 'none'}}>
      <filter id={`colagem-grao-${v}`} x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={3 + v * 17} />
        <feColorMatrix type="matrix" values="0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0 0 0 0 1" />
      </filter>
      <rect width={1080} height={1920} filter={`url(#colagem-grao-${v})`} />
    </svg>
  );
};

/** Vinheta: escurece as bordas na cor escura da marca. */
export const Vinheta: React.FC<{forca?: number; cor?: string}> = ({forca = 0.55, cor = COR.escuro}) => (
  <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 46%, ${rgba(cor, 0)} 42%, ${rgba(cor, forca)} 100%)`}} />
);

/** Foco de luz: só o centro aceso (o "segredo" de uma cena), fecha em 8 quadros. */
export const Foco: React.FC<{q: number; ini: number; raio?: number; cor?: string}> = ({q, ini, raio = 620, cor = COR.escuro}) => {
  const k = progresso(q, ini, ini + 8);
  return (
    <AbsoluteFill style={{
      background: `radial-gradient(circle at 50% 44%, ${rgba(cor, 0)} ${raio * (0.5 + 0.5 * k)}px, ${rgba(cor, 0.82 * k)} ${raio * (0.5 + 0.5 * k) + 260}px)`,
    }} />
  );
};

/**
 * Sombra projetada (gobo): uma imagem de `public/colagem/<nome>.png` (ex.: sombra de
 * folhas tirada de foto real) multiplicada por cima da cena, andando devagar.
 */
export const Sombra: React.FC<{q: number; nome: string; opacidade?: number; vel?: number}> = ({q, nome, opacidade = 0.3, vel = 0.35}) => (
  <Img src={staticFile(`colagem/${nome}.png`)} style={{
    position: 'absolute', left: -270 - Math.sin(q / 90) * 60, top: -120 - q * vel * 0.2, width: 1620,
    mixBlendMode: 'multiply', opacity: opacidade, filter: 'blur(5px)',
  }} />
);

/**
 * Cobertura (transição de papel): uma folha na cor da cena que ENTRA sobe de baixo, com
 * a borda de cima rasgada, e cobre o quadro em `dur` quadros. Comece `dur` quadros antes
 * da troca: `<Cobertura ini={fq(CENA_INICIO[i]) - 7} .../>`.
 */
export const Cobertura: React.FC<{q: number; ini: number; dur?: number; cor: string; chave: string}> = ({q, ini, dur = 7, cor, chave}) => {
  if (q < ini) return null;
  const t = progresso(q, ini, ini + dur);
  const s = semente(chave);
  let d = 'M0,30';
  for (let x = 0; x <= 1080; x += 18) d += ` L${x},${12 + s() * 30}`;
  d += ' L1080,2100 L0,2100 Z';
  return (
    <svg width={1080} height={2100} viewBox="0 0 1080 2100" style={{position: 'absolute', left: 0, top: 1960 - 2020 * t,
      filter: 'drop-shadow(0 -8px 12px rgba(0,0,0,0.35))'}}>
      <path d={d} fill={cor} />
    </svg>
  );
};

/** Linha fina que divide a tela, desenhada de cima para baixo em 6 quadros. */
export const Divisoria: React.FC<{q: number; ini: number; x?: number; cor?: string}> = ({q, ini, x = 540, cor = COR.escuro}) => {
  if (q < ini) return null;
  const k = progresso(q, ini, ini + 6);
  return <div style={{position: 'absolute', left: x - 3, top: 0, width: 6, height: 1920 * k, background: cor}} />;
};

/** Nota de rodapé miúda — a fonte do dado, para o fato falado ter procedência na tela. */
export const Rodape: React.FC<{q: number; ini: number; x: number; y: number; texto: string; cor?: string; tamanho?: number}> = ({
  q, ini, x, y, texto, cor = COR.claro, tamanho = 26,
}) =>
  q < ini ? null : (
    <div style={{position: 'absolute', left: x, top: y, transform: 'translate(-50%,-50%)', whiteSpace: 'nowrap',
      fontFamily: PILHA.dado, fontSize: tamanho, color: cor, opacity: 0.85, letterSpacing: 1}}>
      {texto}
    </div>
  );
