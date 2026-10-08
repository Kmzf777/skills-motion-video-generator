// Peça modelo, as 3 cenas: gancho → conteúdo → fecho.
//
// Cada cena = um Palco (câmera 2.5D) com planos de profundidade: fundo p 0,5–0,85,
// cena p 1, primeiro plano p 2,4 (borra sozinho acima de 1,4). A câmera nunca para
// (`deriva`), dá `pulso` nas palavras-colagem e `tremor` só nos impactos.
//
// NENHUM SEGUNDO DIGITADO: todo quadro vem do roteiro (`fq(S1.tres.inicio)`,
// `em(S2.vira, 'colagem')`, `fala(S2.escrita)`, `TROCA.resto`, `CENA_INICIO[i]`). Desvio
// relativo pode (`fq(...) + 6`); número absoluto, não.
//
// ÁREA SEGURA: texto em x ≈ 140–940 com a câmera em repouso (ela anda até ~120 px e
// amplia até ~1,16×), fora dos 5% do topo e dos 16% da base (interface do Reels). A
// pílula mora em y = 1500.
//
// Peças da biblioteca (publicadas por `biblioteca.py publicar` em public/colagem/) entram
// assim -- o exemplo não usa nenhuma porque não tem peça publicada:
//   <Recorte q={q} ini={fq(S2.vira.inicio)} nome="xicara-branca" x={540} y={900} w={600} />
//   <ProdutoRecortado q={q} ini={fq(S3.salva.inicio)} arquivo="colagem/<produto>.png" x={540} y={900} h={1000} />

import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COR} from '../../identidade/tokens';
import {cameraCena} from '../../colagem/camera';
import {Asterisco, Brilho, Cruz, Elipse, Seta, Sublinhado} from '../../colagem/grafismos';
import {Palco, Plano} from '../../colagem/palco';
import {Dymo, Marcador, Recortadas, Serifa} from '../../colagem/tipos';
import {Cobertura, fala, fq, Fundo, LogoMarca, Vinheta} from './apoio';
import {CENA_INICIO, em, FIM, S1, S2, S3, TROCA} from './roteiro';

type C = {q: number};

// ===================================================================== 1 · gancho
export const Cena1: React.FC<C> = ({q}) => {
  const tres = fq(S1.tres.inicio);
  const segundos = fq(em(S1.tres, 'segundos'));
  const prender = fq(S1.prender.inicio);
  const c = cameraCena(q, [
    {q: 0, x: 0, y: 40, zoom: 1.0, rot: 0},
    {q: prender - 2, x: 0, y: -10, zoom: 1.1, rot: -0.5, curva: 'linear'},
    {q: fq(CENA_INICIO[1]), x: 0, y: -30, zoom: 1.15, rot: -0.5},
  ], 'c1', 1.4, [tres, segundos, prender], [tres]);
  return (
    <AbsoluteFill>
      <Fundo cor={COR.escuro} forca={0.3} />
      <Palco cam={c} id="c1">
        <Plano p={0.5}>
          <Asterisco q={q} ini={0} cx={860} cy={300} r={60} cor={COR.profundo} chave="c1-ast" />
          <Cruz q={q} ini={0} x={170} y={1500} s={70} cor={COR.profundo} chave="c1-cr0" />
        </Plano>
        <Plano p={1}>
          <Recortadas q={q} ini={tres} texto="3" x={540} y={590} tamanho={340} chave="c1-tres" />
          <Recortadas q={q} ini={segundos} texto="SEGUNDOS" x={540} y={965} tamanho={104} chave="c1-seg" />
          <Elipse q={q} ini={fq(em(S1.tempo, 'tempo'))} cx={540} cy={590} rx={185} ry={225} cor={COR.acento} chave="c1-el" espessura={10} />
          <Sublinhado q={q} ini={segundos + 10} x1={250} x2={830} y={1050} cor={COR.claro} chave="c1-sub" />
          <Serifa q={q} ini={prender} texto="prender alguém." x={540} y={1240} tamanho={118} cor={COR.claro} rot={-3} />
          <Brilho q={q} ini={prender + 3} x={880} y={1120} r={60} cor={COR.acento} />
          <Cruz q={q} ini={tres + 5} x={210} y={430} cor={COR.claro} chave="c1-cr1" />
        </Plano>
        <Plano p={2.4}>
          <Cruz q={q} ini={0} x={990} y={240} s={200} cor={COR.acento} chave="c1-perto1" />
          <Cruz q={q} ini={0} x={70} y={1700} s={240} cor={COR.profundo} chave="c1-perto2" />
        </Plano>
      </Palco>
      <Vinheta forca={0.6} />
      {/* transição por cobertura de papel, na cor do fundo da cena 2, 7 quadros antes dela */}
      <Cobertura q={q} ini={fq(CENA_INICIO[1]) - 7} cor={COR.claro} chave="c1-cob" />
    </AbsoluteFill>
  );
};

// ===================================================================== 2 · conteúdo
export const Cena2: React.FC<C> = ({q}) => {
  const ini = fq(CENA_INICIO[1]);
  const troca = fq(TROCA.resto);
  const vira = fq(S2.vira.inicio);
  const colagem = fq(em(S2.vira, 'colagem'));
  const escrita = fq(S2.escrita.inicio);
  const dita = fq(S2.dita.inicio);
  const aqui = fq(em(S2.resto, 'aqui'));

  // fase b: a câmera desce para a pílula ("o resto passa aqui embaixo"), com chicote
  if (q >= troca) {
    const c = cameraCena(q, [
      {q: troca, x: 0, y: -50, zoom: 1.0, rot: 0},
      {q: fq(CENA_INICIO[2]), x: 0, y: 30, zoom: 1.05, rot: 0.3, curva: 'linear'},
    ], 'c2b', 0.8, [aqui]);
    return (
      <AbsoluteFill>
        <Fundo cor={COR.profundo} forca={0.4} />
        <Palco cam={c} id="c2b">
          <Plano p={1}>
            <Seta q={q} ini={troca + 3} de={[540, 820]} para={[540, 1360]} curva={0.12} cor={COR.claro} espessura={12} chave="c2-seta-baixo" />
            <Cruz q={q} ini={troca + 5} x={230} y={980} cor={COR.acento} chave="c2-cr" />
            <Brilho q={q} ini={aqui + 4} x={880} y={1330} r={60} cor={COR.claro} />
          </Plano>
          <Plano p={2.4}>
            <Cruz q={q} ini={troca} x={1000} y={300} s={220} cor={COR.acento} chave="c2b-perto" />
          </Plano>
        </Palco>
        {/* a elipse cerca a PÍLULA, que mora na raiz e não anda com a câmera: fica fora do Palco */}
        <Elipse q={q} ini={aqui} cx={540} cy={1500} rx={330} ry={88} cor={COR.acento} chave="c2-el-pilula" espessura={9} inclina={-3} />
      </AbsoluteFill>
    );
  }

  const c = cameraCena(q, [
    {q: ini, x: 0, y: 0, zoom: 1.08, rot: 0},
    {q: ini + 12, x: 0, y: 0, zoom: 1.0, rot: 0, curva: 'rapida'},
    {q: colagem, x: -40, y: -30, zoom: 1.04, rot: -0.4, curva: 'suave'},
    {q: dita, x: 30, y: 60, zoom: 1.07, rot: 0.4, curva: 'linear'},
    {q: troca, x: 40, y: 90, zoom: 1.1, rot: 0.4, curva: 'linear'},
  ], 'c2a', 1, [vira, colagem, escrita, dita]);
  return (
    <AbsoluteFill>
      <Fundo cor={COR.claro} forca={0.5} />
      <Palco cam={c} id="c2a">
        <Plano p={0.6}>
          <Asterisco q={q} ini={ini} cx={900} cy={1380} r={50} cor={COR.profundo} chave="c2-ast" />
        </Plano>
        <Plano p={1}>
          <Dymo q={q} ini={vira} texto="VIRA" x={360} y={520} tamanho={120} rot={-2} />
          <Dymo q={q} ini={colagem} texto="COLAGEM" x={590} y={690} tamanho={120} fundo={COR.acento} rot={2} />
          <Sublinhado q={q} ini={colagem + 8} x1={320} x2={860} y={790} cor={COR.escuro} chave="c2-sub" />
          <Marcador q={q} ini={escrita} dur={fala(S2.escrita)} texto="ESCRITA NA HORA" x={540} y={960} tamanho={70} rot={-3} chave="c2-escrita" />
          <Marcador q={q} ini={dita} dur={fala(S2.dita)} texto="EM QUE É DITA." x={570} y={1135} tamanho={70} rot={2} chave="c2-dita" />
          <Seta q={q} ini={escrita + 8} de={[205, 1010]} para={[270, 770]} curva={0.3} cor={COR.acento} chave="c2-seta" />
          <Brilho q={q} ini={dita + fala(S2.dita)} x={905} y={1050} r={55} cor={COR.acento} />
        </Plano>
        <Plano p={2.4}>
          <Cruz q={q} ini={ini} x={80} y={260} s={220} cor={COR.acento} chave="c2a-perto1" />
          <Cruz q={q} ini={ini} x={1010} y={1720} s={260} cor={COR.profundo} chave="c2a-perto2" />
        </Plano>
      </Palco>
    </AbsoluteFill>
  );
};

// ===================================================================== 3 · fecho
export const Cena3: React.FC<C> = ({q}) => {
  const ini = fq(CENA_INICIO[2]);
  const marca = fq(S3.marca.inicio);
  const salva = fq(S3.salva.inicio);
  const esse = fq(em(S3.salva, 'esse'));
  const video = fq(em(S3.salva, 'vídeo'));
  const c = cameraCena(q, [
    {q: ini, x: 0, y: -30, zoom: 1.0, rot: 0},
    {q: fq(FIM), x: 0, y: -10, zoom: 1.06, rot: 0.3, curva: 'linear'},
  ], 'c3', 0.8, [marca, salva, esse], [salva]);
  return (
    <AbsoluteFill>
      <Fundo cor={COR.claro} forca={0.45} />
      <Palco cam={c} id="c3">
        <Plano p={1}>
          {/* "a sua marca" é `mudo`: o logo diz isso por ele (pixel de motion/marca/, nunca redesenhado) */}
          <LogoMarca q={q} ini={marca} x={540} y={640} largura={620} fundo="claro" />
          <Brilho q={q} ini={marca + 8} x={880} y={450} r={60} cor={COR.acento} />
          <Cruz q={q} ini={marca + 4} x={190} y={850} cor={COR.acento} chave="c3-cr" />
          <Dymo q={q} ini={salva} texto="SALVA" x={400} y={1090} tamanho={120} rot={-2} />
          <Dymo q={q} ini={esse} texto="ESSE VÍDEO" x={580} y={1240} tamanho={92} fundo={COR.acento} rot={2} />
          <Seta q={q} ini={video + 4} de={[790, 1330]} para={[960, 1440]} curva={-0.3} cor={COR.escuro} chave="c3-seta" />
        </Plano>
        <Plano p={2.4}>
          <Cruz q={q} ini={ini} x={70} y={300} s={220} cor={COR.profundo} chave="c3-perto" />
        </Plano>
      </Palco>
    </AbsoluteFill>
  );
};
