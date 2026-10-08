// O PALCO: câmera 2.5D aplicada a planos de profundidade.
//
//   <Palco cam={...} chicote={{k, eixo}}>
//     <Plano p={0.3}>fundo</Plano>             anda devagar
//     <Plano p={1}>colagem</Plano>              o plano da cena
//     <Plano p={2.4}>primeiro plano</Plano>     anda rápido e borra
//   </Palco>
//
// O chicote (whip) é blur DIRECIONAL de verdade: um filtro SVG feGaussianBlur com
// stdDeviation só no eixo do movimento. CSS `blur()` borra em todas as direções e
// denunciaria o truque.

import React, {createContext, useContext} from 'react';
import {AbsoluteFill} from 'remotion';
import {desfoqueDoPlano, REPOUSO, transformarPlano, type Cam} from './camera';

const CamCtx = createContext<Cam>(REPOUSO);

export const Palco: React.FC<{
  cam: Cam;
  chicote?: {k: number; eixo: 'x' | 'y'} | null;
  id: string;
  children: React.ReactNode;
}> = ({cam, chicote, id, children}) => {
  const k = chicote?.k ?? 0;
  const filtro = k > 0.01 ? `chicote-${id}` : null;
  const sd = chicote?.eixo === 'y' ? `0 ${Math.round(k * 60)}` : `${Math.round(k * 60)} 0`;
  return (
    <CamCtx.Provider value={cam}>
      {filtro && (
        <svg width={0} height={0} style={{position: 'absolute'}}>
          <filter id={filtro} x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation={sd} />
          </filter>
        </svg>
      )}
      <AbsoluteFill style={{overflow: 'hidden', filter: filtro ? `url(#${filtro})` : undefined}}>{children}</AbsoluteFill>
    </CamCtx.Provider>
  );
};

export const Plano: React.FC<{p: number; desfoque?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
  p,
  desfoque,
  children,
  style,
}) => {
  const cam = useContext(CamCtx);
  const {transform} = transformarPlano(cam, p);
  const b = desfoque ?? desfoqueDoPlano(p);
  return (
    <AbsoluteFill style={{transform, transformOrigin: '540px 960px', filter: b ? `blur(${b}px)` : undefined, ...style}}>
      {children}
    </AbsoluteFill>
  );
};

export const useCamera = () => useContext(CamCtx);
