# Estado — completo "Musk: dois caminhos da IA" (21/10/2026)

Pedido do Nei (21/10): r7exp sobre a entrevista de Elon Musk a Walter Isaacson, no lives11 e no v3.
Fonte: ~/projetos/output/musk-isaacson-2026-10-21/fonte.md. Personagem fixa: Marcos, 40, dono de oficina mecânica.

Mapa: escala log da economia (×1 → ×1.000.000), eixo X sem datas ("sem cronograma verificável").
Caminhos: 1 IA digital (+20–30%) · 2 robôs + espaço (até ×1.000.000) · 3 o risco (ninguém controla; a aposta dele) · final "o que fazer".
Layout D16: avatar abre em meia tela (metade direita) até o gráfico, depois PiP; volta à meia tela nas frases (`quote`).

1. falas/*.txt (5) → `musk/avatar.sh enviar` (estúdio HeyGen, TEMPLATE-AVATAR16) ✅ 21/10 15:25
2. `musk/avatar.sh baixar` → avatar/*.mp4
3. imagens/ (Codex image_gen, marcos-2026.png de referência; pedido.txt) + print-inema.png
4. `motor/monta_avatar.py musk a` → build/avatar-a.mp4 + segmentos + tempos/ (whisper)
5. `python3 musk/gera_musk.py` → cena-a/index.html; assets → check → snapshot (`--describe false`: sem API) → render
6. yt-pubx lives11 + v3 + inemaytbot
