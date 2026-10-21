# ESTADO — reel r7exp 9:16 "Musk: humanoides" (21/10/2026) — PUBLICADO

- Publicado no lives6 (INEMA Robot): https://youtube.com/shorts/LgBkOTBVTxw — v3 msg 2174, link no inemaytbot.
- 58,6 s, 1080×1920. Revisor r7ex: aprovado, impacto 7 (build/revisor.json). Folha: build/folha.jpg.
- Gerador: gera_v.py (molde reels/thwaites). Novidade: avatar abre em MEIA TELA (1080×960 embaixo) e vai ao PiP
  só com transform (quadro fixo + clip-path inset + scale/x/y no vídeo); animar left/top reprova o check do HyperFrames.
- Legenda: grupo de até 20 caracteres (com mais quebrava em 2 linhas e encostava no painel).
- HeyGen (estúdio): e137f826dc134995b01f22ff64e38db7. O avatar troca "IA" por "inteligência artificial" na fala.
- Refazer: ffmpeg avatar-raw → cena/assets/avatar.mp4; transcrever_v1 --words → tempos/w; python3 gera_v.py; check; render.
