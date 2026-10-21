# CLAUDE.md — r7exp

Explicativo visual do INEMA: gráfico como mapa + personagem fixa atravessando cenários + painéis que entram na palavra +
"o que fazer". Completo 16:9 → reels 9:16. Ler `CONCEITO.md` e `PADRAO.md` antes de produzir.

- Motor: HyperFrames (HTML → MP4). Protótipos em `prototipo/<slug>/`.
- Design: `~/projetos/inema-design/DESIGN.md` + `video/style.md` + `video/camera.md` (zoom ≤ 1,25 com texto, sem whoosh).
- Imagens: Codex image_gen pela assinatura; luz neutra; robô estilo Optimus com visor preto.
- Voz: avatar do Nei pelo estúdio HeyGen no produto final; protótipo pode usar Chatterbox `nei` local.
- Commits: autor `inematds <inematds@gmail.com>`. Publicação só via fila/yt-pubx; protótipo vai só ao v3.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule at the
TOP of the Lessons section below, so it never happens again.

## Lessons
- Gráfico de dado no reel: preencher o palco (barras grossas, valores ≥ 52 px, rótulos claros), entrar já com a 1ª barra e mostrar a fonte embaixo; gráfico pequeno e cinza no fundo preto foi o que o Nei pediu para refazer. (musk-humanoides v2, 21/10/2026)
- Avatar meia tela → PiP: não animar left/top/width/height (check do HyperFrames reprova); quadro fixo no tamanho da meia tela + clip-path inset + scale/x/y no vídeo. Legenda 9:16: grupo ≤ 20 caracteres, senão quebra e encosta no painel. (musk-humanoides, 21/10/2026)
- `hyperframes snapshot` chama o Gemini (API) sozinho quando há GEMINI_API_KEY: sempre `--describe false`. Whisper escreve número em algarismo ("40", "20 %"): âncora do gerador = "40", não "quarenta". (musk, 21/10/2026)
