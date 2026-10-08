// Conferência da IDENTIDADE: uma tela com o que `motion/marca/identidade.json` declara --
// as 5 cores, as 3 famílias com os acentos do idioma, as 2 vozes da colagem, os logos em
// fundo claro e escuro e a pílula nas duas versões.
//
//   npx remotion still src/index.ts Marca ../pecas/00-exemplo/saida/marca.png --public-dir=../pecas/00-exemplo/public
//
// É a tela mais barata para conferir a fase 01: se uma fonte não carregou, a guarda
// derruba o still; se uma cor ficou feia ou ilegível, aparece aqui antes de virar peça.

import React from 'react';
import {AbsoluteFill} from 'remotion';
import {PILHA_COLAGEM} from './colagem/fontes-colagem';
import {LogoMarca} from './colagem/pecas';
import {Pilula} from './colagem/tipos';
import {yDaPilula} from './colagem/area-segura';
import {contraste} from './identidade/cor';
import {PAPEIS_COR} from './identidade/identidade';
import {COR, IDENTIDADE, TIPO} from './identidade/tokens';
import {PILHA} from './identidade/tipografia';

/** Centro da pílula dentro da caixa de 120 px. A Pílula prende o y na área segura do quadro
 * (y >= 134), então a caixa sobe a diferença para a pílula não sair cortada. */
const Y_NA_CAIXA = 60;
const AMOSTRA = 'Ação, açúcar e pão: ÁÉÍÓÚ ÂÊÔ ÃÕ Ç 0123456789';

const Linha: React.FC<{rotulo: string; children: React.ReactNode}> = ({rotulo, children}) => (
  <div style={{display: 'flex', flexDirection: 'column', gap: 6}}>
    <div style={{fontFamily: PILHA.dado, fontSize: 22, color: COR.profundo, letterSpacing: 1}}>{rotulo}</div>
    {children}
  </div>
);

export const Marca: React.FC = () => (
  <AbsoluteFill style={{background: COR.claro, padding: '70px 70px', gap: 34, display: 'flex', flexDirection: 'column'}}>
    <div style={{fontFamily: PILHA.manchete, fontSize: 76, color: COR.escuro, lineHeight: 1}}>{IDENTIDADE.marca}</div>
    {IDENTIDADE.exemplo && (
      <div style={{fontFamily: PILHA.dado, fontSize: 26, color: COR.claro, background: COR.acento, padding: '10px 16px'}}>
        IDENTIDADE DE EXEMPLO ("exemplo": true) — a fase 01 substitui; nenhuma peça vai ao ar assim
      </div>
    )}
    <Linha rotulo="CORES (escuro · claro · profundo · acento · apoio)">
      <div style={{display: 'flex', gap: 12}}>
        {PAPEIS_COR.map((p) => (
          <div key={p} style={{flex: 1, height: 150, background: COR[p], border: `2px solid ${COR.escuro}`,
            display: 'flex', alignItems: 'flex-end', padding: 8, fontFamily: PILHA.dado, fontSize: 20,
            color: contraste(COR[p], COR.escuro) > contraste(COR[p], COR.claro) ? COR.escuro : COR.claro}}>
            {p}<br />{COR[p]}
          </div>
        ))}
      </div>
    </Linha>
    {(['manchete', 'corpo', 'dado'] as const).map((papel) => (
      <Linha key={papel} rotulo={`${papel.toUpperCase()} · ${TIPO[papel].familia} ${TIPO[papel].peso}`}>
        <div style={{fontFamily: PILHA[papel], fontWeight: TIPO[papel].peso, fontSize: 46, color: COR.escuro, lineHeight: 1.1}}>{AMOSTRA}</div>
      </Linha>
    ))}
    <Linha rotulo="COLAGEM · Instrument Serif Italic / Permanent Marker">
      <div style={{fontFamily: PILHA_COLAGEM.serifa, fontStyle: 'italic', fontSize: 52, color: COR.escuro, lineHeight: 1}}>{AMOSTRA}</div>
      <div style={{fontFamily: PILHA_COLAGEM.marcador, fontSize: 40, color: COR.acento, lineHeight: 1.1}}>{AMOSTRA}</div>
    </Linha>
    <Linha rotulo="LOGO sobre claro · sobre escuro">
      <div style={{display: 'flex', gap: 12, height: 300}}>
        <div style={{flex: 1, position: 'relative', background: COR.claro, border: `2px solid ${COR.escuro}`}}>
          <LogoMarca q={0} ini={-30} x={235} y={150} largura={360} fundo="claro" />
        </div>
        <div style={{flex: 1, position: 'relative', background: COR.escuro}}>
          <LogoMarca q={0} ini={-30} x={235} y={150} largura={360} fundo="escuro" />
        </div>
      </div>
    </Linha>
    <Linha rotulo="PÍLULA sobre fundo claro · sobre fundo escuro">
      <div style={{display: 'flex', gap: 12, height: 120}}>
        <div style={{flex: 1, position: 'relative', background: COR.claro, border: `2px solid ${COR.escuro}`, overflow: 'hidden'}}>
          <div style={{position: 'absolute', left: -305, top: Y_NA_CAIXA - yDaPilula('organico', Y_NA_CAIXA)}}>
            <Pilula q={0} fps={30} y={Y_NA_CAIXA} blocos={[{texto: 'O RESTO PASSA', inicio: 0, fim: 1, palavras: [0]}]} tema="claro" />
          </div>
        </div>
        <div style={{flex: 1, position: 'relative', background: COR.escuro, overflow: 'hidden'}}>
          <div style={{position: 'absolute', left: -305, top: Y_NA_CAIXA - yDaPilula('organico', Y_NA_CAIXA)}}>
            <Pilula q={0} fps={30} y={Y_NA_CAIXA} blocos={[{texto: 'AQUI EMBAIXO.', inicio: 0, fim: 1, palavras: [0]}]} tema="escuro" />
          </div>
        </div>
      </div>
    </Linha>
  </AbsoluteFill>
);
