// GRAFISMOS desenhados na hora, como nas referências de colagem: seta curva apontando a
// palavra, elipse de giz em volta dela, X de marcador, asterisco, brilho de 4 pontas
// com raios tracejados, cruz "+", sublinhado, check.
//
// Cada traço é desenhado em 5 quadros (stroke-dashoffset) e depois "ferve" (boil):
// a cada 3 quadros troca para uma das 3 variantes do mesmo traço, com tremor de
// semente. Tudo determinístico.

import React from 'react';
import {COR} from '../identidade/tokens';
import {posterizar, progresso} from './movimento-colagem';
import {semente} from './semente';

type Pt = [number, number];

function caminho(pts: Pt[]): string {
  if (pts.length < 2) return '';
  let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
  for (let i = 1; i < pts.length; i++) {
    const p0 = pts[i - 2] ?? pts[i - 1];
    const p1 = pts[i - 1];
    const p2 = pts[i];
    const p3 = pts[i + 1] ?? p2;
    const c1: Pt = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2: Pt = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
  }
  return d;
}

function comprimento(pts: Pt[]): number {
  let L = 0;
  for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  return L * 1.08;
}

function tremer(pts: Pt[], chave: string, amp: number): Pt[] {
  const s = semente(chave);
  return pts.map(([x, y]) => [x + (s() - 0.5) * amp, y + (s() - 0.5) * amp]);
}

/** Um ou mais traços, desenhados em `quadros` e depois fervendo. */
const Tracos: React.FC<{
  q: number; ini: number; chave: string; tracos: (v: number) => Pt[][]; cor?: string; espessura?: number;
  quadros?: number; fora?: number; opacidade?: number;
}> = ({q, ini, chave, tracos, cor = COR.escuro, espessura = 9, quadros = 5, fora, opacidade = 1}) => {
  if (q < ini || (fora !== undefined && q >= fora)) return null;
  const desenhado = q >= ini + quadros;
  const v = desenhado ? Math.floor(posterizar(q, 3) / 3) % 3 : 0;
  const lista = tracos(v);
  const total = lista.reduce((a, t) => a + comprimento(t), 0);
  let resto = total * (desenhado ? 1 : progresso(q, ini, ini + quadros));
  return (
    <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      {lista.map((pts, i) => {
        const L = comprimento(pts);
        const mostra = Math.max(0, Math.min(L, resto));
        resto -= L;
        return (
          <path key={i} d={caminho(tremer(pts, `${chave}#${v}#${i}`, espessura * 0.35))} fill="none" stroke={cor}
            strokeWidth={espessura} strokeLinecap="round" strokeLinejoin="round" opacity={opacidade}
            strokeDasharray={L} strokeDashoffset={L - mostra} />
        );
      })}
    </svg>
  );
};

/** Elipse de giz feita à mão: 1,15 volta, a ponta passa do começo. */
export const Elipse: React.FC<{q: number; ini: number; cx: number; cy: number; rx: number; ry: number; cor?: string; espessura?: number; chave: string; fora?: number; inclina?: number}> = (p) => (
  <Tracos {...p} cor={p.cor ?? COR.claro} espessura={p.espessura ?? 8} quadros={6}
    tracos={() => {
      const pts: Pt[] = [];
      const a0 = -2.4;
      const inc = ((p.inclina ?? -6) * Math.PI) / 180;
      for (let k = 0; k <= 40; k++) {
        const a = a0 + (k / 40) * Math.PI * 2 * 1.15;
        const r = 1 + 0.05 * Math.sin(k * 0.7);
        const x = Math.cos(a) * p.rx * r;
        const y = Math.sin(a) * p.ry * r * (k > 34 ? 0.92 : 1);
        pts.push([p.cx + x * Math.cos(inc) - y * Math.sin(inc), p.cy + x * Math.sin(inc) + y * Math.cos(inc)]);
      }
      return [pts];
    }} />
);

/** Seta curva com ponta em dois traços. */
export const Seta: React.FC<{q: number; ini: number; de: Pt; para: Pt; curva?: number; cor?: string; espessura?: number; chave: string; fora?: number}> = (p) => (
  <Tracos {...p} espessura={p.espessura ?? 9} quadros={6}
    tracos={() => {
      const [x0, y0] = p.de;
      const [x1, y1] = p.para;
      const mx = (x0 + x1) / 2;
      const my = (y0 + y1) / 2;
      const nx = -(y1 - y0);
      const ny = x1 - x0;
      const k = p.curva ?? 0.25;
      const cx = mx + nx * k;
      const cy = my + ny * k;
      const corpo: Pt[] = [];
      for (let t = 0; t <= 1.0001; t += 0.1) {
        corpo.push([(1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1]);
      }
      const ang = Math.atan2(y1 - cy, x1 - cx);
      const tam = 42;
      const ponta1: Pt[] = [[x1 - Math.cos(ang - 0.5) * tam, y1 - Math.sin(ang - 0.5) * tam], [x1, y1]];
      const ponta2: Pt[] = [[x1, y1], [x1 - Math.cos(ang + 0.5) * tam, y1 - Math.sin(ang + 0.5) * tam]];
      return [corpo, ponta1, ponta2];
    }} />
);

/** Sublinhado ondulado de canetão. */
export const Sublinhado: React.FC<{q: number; ini: number; x1: number; x2: number; y: number; cor?: string; espessura?: number; chave: string; fora?: number}> = (p) => (
  <Tracos {...p} cor={p.cor ?? COR.acento} espessura={p.espessura ?? 10} quadros={5}
    tracos={() => {
      const pts: Pt[] = [];
      for (let k = 0; k <= 12; k++) pts.push([p.x1 + ((p.x2 - p.x1) * k) / 12, p.y + Math.sin(k * 1.3) * 5]);
      return [pts];
    }} />
);

/** X de marcador (dois traços em sequência). */
export const Xis: React.FC<{q: number; ini: number; cx: number; cy: number; r: number; cor?: string; espessura?: number; chave: string; fora?: number}> = (p) => (
  <Tracos {...p} cor={p.cor ?? COR.acento} espessura={p.espessura ?? 16} quadros={5}
    tracos={() => [
      [[p.cx - p.r, p.cy - p.r], [p.cx + p.r * 0.1, p.cy - p.r * 0.05], [p.cx + p.r, p.cy + p.r]],
      [[p.cx + p.r, p.cy - p.r], [p.cx, p.cy + p.r * 0.05], [p.cx - p.r, p.cy + p.r]],
    ]} />
);

/** Check de aprovação. */
export const Check: React.FC<{q: number; ini: number; cx: number; cy: number; r: number; cor?: string; espessura?: number; chave: string; fora?: number}> = (p) => (
  <Tracos {...p} cor={p.cor ?? COR.apoio} espessura={p.espessura ?? 18} quadros={5}
    tracos={() => [[[p.cx - p.r, p.cy], [p.cx - p.r * 0.35, p.cy + p.r * 0.7], [p.cx + p.r, p.cy - p.r * 0.8]]]} />
);

/** Asterisco de 3 traços. */
export const Asterisco: React.FC<{q: number; ini: number; cx: number; cy: number; r: number; cor?: string; chave: string; fora?: number}> = (p) => (
  <Tracos {...p} cor={p.cor ?? COR.acento} espessura={8} quadros={4}
    tracos={() => [0, 60, 120].map((g) => {
      const a = (g * Math.PI) / 180;
      return [[p.cx - Math.cos(a) * p.r, p.cy - Math.sin(a) * p.r], [p.cx + Math.cos(a) * p.r, p.cy + Math.sin(a) * p.r]] as Pt[];
    })} />
);

/** Brilho de 4 pontas: estoura (0 → 1,25 → 1) com raios tracejados e some em ~12 quadros. */
export const Brilho: React.FC<{q: number; ini: number; x: number; y: number; r?: number; cor?: string; dura?: number}> = ({
  q, ini, x, y, r = 70, cor = COR.claro, dura = 12,
}) => {
  const k = posterizar(q, 2, ini) - ini;
  if (k < 0 || k > dura) return null;
  const esc = k < 2 ? 0.6 : k < 4 ? 1.25 : 1 - Math.max(0, (k - 8) / (dura - 8));
  const estrela = (s: number) => {
    const pts: string[] = [];
    for (let i = 0; i < 8; i++) {
      const a = (i * Math.PI) / 4 - Math.PI / 2;
      const rr = i % 2 === 0 ? s : s * 0.26;
      pts.push(`${(x + Math.cos(a) * rr).toFixed(1)},${(y + Math.sin(a) * rr).toFixed(1)}`);
    }
    return pts.join(' ');
  };
  const raio = Math.min(1, k / 5);
  return (
    <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <polygon points={estrela(r * esc)} fill={cor} />
      {[45, 135, 225, 315].map((g) => {
        const a = (g * Math.PI) / 180;
        const r0 = r * 0.9;
        const r1 = r * (0.9 + 0.9 * raio);
        return (
          <line key={g} x1={x + Math.cos(a) * r0} y1={y + Math.sin(a) * r0} x2={x + Math.cos(a) * r1} y2={y + Math.sin(a) * r1}
            stroke={cor} strokeWidth={7} strokeDasharray="14 12" strokeLinecap="round" opacity={1 - Math.max(0, (k - 8) / 4)} />
        );
      })}
    </svg>
  );
};

/** Cruz "+" chapada, que gira um pouco a cada 3 quadros (boil). */
export const Cruz: React.FC<{q: number; ini: number; x: number; y: number; s?: number; cor?: string; chave: string; fora?: number}> = ({
  q, ini, x, y, s = 60, cor = COR.claro, chave, fora,
}) => {
  if (q < ini || (fora !== undefined && q >= fora)) return null;
  const v = Math.floor(posterizar(q, 3) / 3);
  const rot = (semente(`${chave}#${v % 3}`)() - 0.5) * 16;
  const e = q - ini < 2 ? 0.5 : 1;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: s, height: s, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${e})`}}>
      <div style={{position: 'absolute', left: '36%', top: 0, width: '28%', height: '100%', background: cor}} />
      <div style={{position: 'absolute', top: '36%', left: 0, height: '28%', width: '100%', background: cor}} />
    </div>
  );
};
