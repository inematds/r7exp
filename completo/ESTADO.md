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
