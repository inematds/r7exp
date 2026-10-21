#!/usr/bin/env bash
# Manda cada fala de completo/falas/*.txt ao estúdio HeyGen (assinatura, TEMPLATE-AVATAR16, tela :99) e baixa o avatar.
# Uso: completo/avatar.sh enviar | baixar      (ids em completo/avatar/<nome>.id, vídeos em completo/avatar/<nome>.mp4)
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"; HG="$HOME/projetos/r7ex/heygen"
PERFIL="$HOME/.cache/inemaccbot/perfil-heygen"; mkdir -p "$AQUI/avatar"
case "${1:-}" in
  enviar)
    for f in "$AQUI"/falas/*.txt; do
      n=$(basename "$f" .txt); [ -s "$AQUI/avatar/$n.id" ] && { echo "já enviado: $n"; continue; }
      echo "enviando $n…"
      (cd "$HG" && DISPLAY=:99 timeout 12000 node heygen-studio.mjs --titulo "R7EXP-$n" --fala-arquivo "$f" \
         --perfil "$PERFIL" --template TEMPLATE-AVATAR16) > "$AQUI/avatar/$n.studio.log" 2>&1
      id=$(grep -oE 'create-v4/[0-9a-f]{32}' "$AQUI/avatar/$n.studio.log" | tail -1 | cut -d/ -f2)
      if [ -n "$id" ]; then echo "$id" > "$AQUI/avatar/$n.id"; echo "OK $n $id"; else echo "FALHOU $n: $(grep -o 'ERRO:.*' "$AQUI/avatar/$n.studio.log" | head -1)"; fi
    done ;;
  baixar)
    for f in "$AQUI"/avatar/*.id; do
      n=$(basename "$f" .id); [ -s "$AQUI/avatar/$n.mp4" ] && continue
      (cd "$HG" && node heygen-estudio-baixar.mjs --id "$(cat "$f")" --saida "$AQUI/avatar/$n.mp4" --minutos 290 --intervalo 120) \
        > "$AQUI/avatar/$n.baixar.log" 2>&1 && echo "pronto $n" || echo "não baixou $n: $(tail -1 "$AQUI/avatar/$n.baixar.log")"
    done ;;
  *) echo "uso: $0 enviar | baixar"; exit 2 ;;
esac
