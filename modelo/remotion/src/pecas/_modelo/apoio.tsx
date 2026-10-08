// Apoio da peça: o relógio (segundos → quadros) e o KIT de componentes que as cenas
// usam, num import só.
//
// Os componentes moram no motor (`src/colagem/`), compartilhados por todas as peças do
// repositório; aqui eles só são reexportados. Componente que só ESTA peça usa pode
// nascer aqui -- e, se servir para a próxima, sobe para `src/colagem/`.

export const FPS = 30;

/** Segundos → quadro. Todo tempo de cena passa por aqui, sempre a partir do roteiro. */
export const fq = (s: number) => Math.round(s * FPS);

/** Quadros que a voz leva para dizer uma faixa — o `dur` de um Marcador que escreve junto com ela. */
export const fala = (f: {inicio: number; fim: number}) => fq(f.fim - f.inicio) + 2;

export {Cobertura, Divisoria, Foco, Fundo, GraoFilme, Rodape, Sombra, Vinheta} from '../../colagem/atmosfera';
export {Carimbo, Fita, LogoMarca, Manchete, ProdutoRecortado, Recorte, Rotulo, Tachinha, Tira, Troca} from '../../colagem/pecas';
