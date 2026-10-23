# Estado — completo "5 futuros" (21/10/2026)

Pedido do Nei: dois vídeos completos 16:9 — (a) "Em qual destes 5 futuros você vai acordar em 2040? / Um deles é a extinção"
e (b) "O mundo vai mudar. E você vai junto. / Será que você tem escolha?" (AI 2027 + Stanford) — com avatar nas 2 aberturas,
nos 5 caminhos e no final "como se preparar"; cada caminho ensina como se adaptar e não ser a massa.

1. falas/*.txt (8 falas) → `completo/avatar.sh enviar` (estúdio HeyGen, TEMPLATE-AVATAR16) → ids em avatar/*.id ✅ 21/10 00h
2. `completo/avatar.sh baixar` → avatar/*.mp4 (espera o HeyGen)
3. imagens/ (Codex image_gen com ana-2026.png de referência; pedido.txt) + print-guia.png
4. `motor/monta_avatar.py completo a|b` → build/avatar-<v>.mp4 + segmentos + tempos/ (whisper)
5. `motor/gera.py completo a|b` → cena-<v>/index.html; copiar assets (imagens, fontes, avatar) → check → snapshot → render
6. v3 ✅ 21/10 ~02h (A e B, cópias de 39 MB) — sem YouTube até o Nei aprovar

## Publicado (21/10/2026 ~02h15)
- A → lives11 (INEMA Futuros): https://www.youtube.com/watch?v=ddWUJbfPgPk — thumb NÃO aplicada (canal sem verificação de telefone); arte em build/thumb-a.jpg
- B → lives1 (INEMA TDS): https://www.youtube.com/watch?v=W2tBGNYlzi4 — capa nova capa-b1 ("2027. VOCÊ TEM ESCOLHA?"), thumb aplicada
- v3: vídeos A/B identificados + capas + 3 opções de capa B; links no inemaytbot

## Reels 9:16 (21/10/2026 ~18h)
- `gera.py . a|b limpo` → reels/limpo-*.mp4; `motor/gera_reels.py .` → reels/<slug>/; render → reels/final/ (cópias v3 em final/v3)
- v3 msgs 2160 (índice) · 2162 · 2164 · 2166 · 2170 · 2172 (caminhos 1–5). Sem YouTube até o Nei decidir.

## Playlist (21/10/2026)
- lives11 (INEMA Futuros): https://www.youtube.com/playlist?list=PLGR_G3hBAAaM — A ddWUJbfPgPk · B W2tBGNYlzi4 · r7ex dt5ekPf7znY. Reels entram quando forem publicados (`CANAL=lives11 python3 ~/projetos/wifi/fila-espanhol/yt_api.py add PLGR_G3hBAAaM <id>`).
- Reels na fila do lives11 (r7ex/fila, na frente, com --playlist PLGR_G3hBAAaM): índice 21h de 21/10, caminhos 1–5 em 22/10 9–17h.
- Publicados (lives11, todos na playlist): índice iWGJf2IwiRs · 1 IbSbkQmBEaM · 2 cPS1mv96H_g · 3 vaIWnSm3nkY · 4 hju4LeqC3Ds · 5 cNv5tblLd-8. Links no inemaytbot em 22/10.
- Playlist espelho no lives1 (INEMA TDS): https://www.youtube.com/playlist?list=PLCTFUR8YB1Os — mesmos 9 vídeos, B primeiro (23/10).
- Telegram 23/10: INEMA.VIP Novidades (t.me/c/2405283087/306) + tópico novo INEMA.IA 6169 (no MENU msg 6180), link da playlist lives11.
