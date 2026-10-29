#!/usr/bin/env bash
# Avatar do reel cinco-cenarios-v2: fala.txt inteira numa gravação só (estúdio HeyGen, assinatura, TEMPLATE-AVATAR16, tela :99).
# Uso: avatar.sh enviar | baixar | preparar
#   enviar   → avatar/fala.id (exige avatar/APROVADO_HEYGEN)
#   baixar   → avatar/fala.mp4 (espera o estúdio terminar)
#   preparar → build/n-fala.mp4 (30 fps, -14 LUFS) + tempos/fala.json (whisper large-v3 do inemavox)
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"; HG="$HOME/projetos/r7ex/heygen"
PERFIL="$HOME/.cache/inemaccbot/perfil-heygen"; VOX="$HOME/projetos/inemavox"
mkdir -p "$AQUI/avatar" "$AQUI/build" "$AQUI/tempos"
case "${1:-}" in
  enviar)
    [ -s "$AQUI/avatar/APROVADO_HEYGEN" ] || { echo "falta avatar/APROVADO_HEYGEN"; exit 1; }
    [ -s "$AQUI/avatar/fala.id" ] && { echo "já enviado: $(cat "$AQUI/avatar/fala.id")"; exit 0; }
    (cd "$HG" && DISPLAY=:99 timeout 12000 node heygen-studio.mjs --titulo "R7EXP-cinco-cenarios-v2" --fala-arquivo "$AQUI/fala.txt" \
       --perfil "$PERFIL" --template TEMPLATE-AVATAR16) > "$AQUI/avatar/studio.log" 2>&1
    id=$(grep -oE 'create-v4/[0-9a-f]{32}' "$AQUI/avatar/studio.log" | tail -1 | cut -d/ -f2)
    if [ -n "$id" ]; then echo "$id" > "$AQUI/avatar/fala.id"; echo "OK $id"; else echo "FALHOU: $(grep -o 'ERRO:.*' "$AQUI/avatar/studio.log" | head -1)"; exit 1; fi ;;
  baixar)
    [ -s "$AQUI/avatar/fala.mp4" ] && { echo "já baixado"; exit 0; }
    (cd "$HG" && node heygen-estudio-baixar.mjs --id "$(cat "$AQUI/avatar/fala.id")" --saida "$AQUI/avatar/fala.mp4" --minutos 290 --intervalo 120) \
      > "$AQUI/avatar/baixar.log" 2>&1 && echo "pronto" || { echo "não baixou: $(tail -1 "$AQUI/avatar/baixar.log")"; exit 1; } ;;
  preparar)
    ffmpeg -v error -y -i "$AQUI/avatar/fala.mp4" -vf "fps=30,scale=1920:1080,setsar=1,tpad=stop_mode=clone:stop_duration=0.5" \
      -af "aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad=pad_dur=0.5" \
      -c:v libx264 -crf 18 -preset veryfast -c:a aac -b:a 192k -ac 2 -shortest "$AQUI/build/n-fala.mp4" || exit 1
    mkdir -p "$AQUI/tempos/_fala"
    "$VOX/venv/bin/python" "$VOX/transcrever_v1.py" --in "$AQUI/avatar/fala.mp4" --outdir "$AQUI/tempos/_fala" \
      --whisper-model large-v3 --src pt --words > /dev/null || exit 1
    cp "$AQUI/tempos/_fala/words.json" "$AQUI/tempos/fala.json" && echo "preparado" ;;
  *) echo "uso: $0 enviar | baixar | preparar"; exit 2 ;;
esac
