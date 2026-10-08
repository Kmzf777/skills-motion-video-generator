// Tolerância de ÁUDIO, só para a composição de exemplo.
//
// Numa peça de verdade o `Sons.tsx` exige todos os arquivos: narração, trilha e efeitos.
// Arquivo que falta derruba o render do vídeo com 404 -- é a trava que impede uma peça
// de sair muda. O EXEMPLO (motion/pecas/00-exemplo) não tem narração gravada; envolto em
// `<SomTolerante>`, ele toca só o que existir em public/, para a conferência do motor
// sair limpa e, depois do `sons.py`, dar para ouvir a trilha e os efeitos.
//
// A tolerância é ligada em `Raiz.tsx`, na linha do Exemplo, e não dentro da peça: copiar
// `_modelo` para uma peça nova nunca a leva junto.

import React, {createContext, useContext} from 'react';

const Tolerante = createContext(false);

export const SomTolerante: React.FC<{children: React.ReactNode}> = ({children}) => (
  <Tolerante.Provider value={true}>{children}</Tolerante.Provider>
);

/** true só dentro de `<SomTolerante>` (a composição de exemplo). */
export const useSomTolerante = () => useContext(Tolerante);
