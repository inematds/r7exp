# Qual bot você vai usar? — 4 agentes pessoais (r7exp, 22/10/2026)

Pedido do Nei (22/10): "no final faz um r7exp do conteúdo e manda para mim e no lives1" — comparação Grok Bot, Meta Muse,
ChatGPT Dots, Claude Duet (Duet ainda não no Brasil), a Carla (consultora, 41) atravessa os 4. Par do refazvideo
`~/projetos/output/explica-D-pz8L1orVI`.

## Publicado (lives1 · INEMA TDS, público)
- Completo 16:9 (1m56s): https://www.youtube.com/watch?v=uQfbAferwaI · v3 msg 2252
- Reels 9:16 (v3 msgs 2254/2256/2258/2260/2262):
  - índice 4 bots https://www.youtube.com/watch?v=fn3C-whcqtk
  - bot 1 Grok Bot https://www.youtube.com/watch?v=QRU4YseZJgA
  - bot 2 Meta Muse https://www.youtube.com/watch?v=XKIPB3NGACs
  - bot 3 ChatGPT Dots https://www.youtube.com/watch?v=rruXCkoaNak
  - bot 4 Claude Duet https://www.youtube.com/watch?v=G1qJGvbuFi8
- Links no inemaytbot: msg 2554.

## Correções da fase 2 (antes de enviar)
- Zoom no quadro do bot 3/4 empurrava os blocos para baixo do PiP do avatar: `zoom_tile` com origem presa à esquerda, z 1,08/1,06.
- Whisper escreveu "Duet" como "Doué": CORRIGE Doué→Duet (completo e reels).
- Pílula "AINDA NÃO NO BRASIL" mais larga que o texto; reel-índice não repete a capa na banda (usa `final-carla.png`).

## Como refazer
- `bots/avatar.sh enviar|baixar` → `bash bots/cadeia.sh` (monta avatar, completo, limpo, reels).
- Só re-render (avatar já baixado): `bash bots/build/refaz.sh`.
