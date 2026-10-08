// Configuração de render do motor. Ver https://www.remotion.dev/docs/config
import {Config} from '@remotion/cli/config';

// H.264 em MP4: é o que Instagram, TikTok e Shorts aceitam sem reencode agressivo.
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');

// Overwrite ligado: a conferência reescreve a mesma saída a cada rodada.
Config.setOverwriteOutput(true);
