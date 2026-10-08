import {registerRoot} from 'remotion';

// Import de EFEITO COLATERAL, e por isso vem antes da raiz: este módulo carrega as três
// famílias da marca (identidade.json) e abre um `delayRender` que segura o primeiro
// quadro até elas estarem aplicadas e provadas. Sem ele o Chrome headless desenha Times
// New Roman e não reclama. Ver `identidade/tipografia.ts`.
//
// Está aqui, no entrypoint, para valer para QUALQUER composição registrada.
import './identidade/tipografia';

import {Raiz} from './Raiz';

registerRoot(Raiz);
