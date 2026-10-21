#!/usr/bin/env bash
# Manda cada fala de musk/falas/*.txt ao estúdio HeyGen (assinatura, TEMPLATE-AVATAR16, tela :99) e baixa o avatar.
# Igual ao completo/avatar.sh, com a trava (flock) do perfil do estúdio — r7ex/explicavideos usam o mesmo perfil.
# Uso: musk/avatar.sh enviar | baixar
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"; HG="$HOME/projetos/r7ex/heygen"
PERFIL="$HOME/.cache/inemaccbot/perfil-heygen"; mkdir -p "$AQUI/avatar"
TRAVA="$HOME/.cache/inemaccbot/heygen-estudio.lock"
case "${1:-}" in
  enviar)
    for f in "$AQUI"/falas/*.txt; do
      n=$(basename "$f" .txt); [ -s "$AQUI/avatar/$n.id" ] && { echo "já enviado: $n"; continue; }
      tr '\n' ' ' < "$f" | sed 's/  */ /g; s/ $//' > "$AQUI/avatar/$n.1linha.txt"
      echo "enviando $n… ($(date +%T))"
      (
        flock -w 3600 9 || { echo "ERRO: perfil do HeyGen ocupado há 60 min"; exit 5; }
        cd "$HG" && DISPLAY=:99 timeout 12000 node heygen-studio.mjs --titulo "R7EXP-musk-$n" --fala-arquivo "$AQUI/avatar/$n.1linha.txt" \
           --perfil "$PERFIL" --template TEMPLATE-AVATAR16
      ) 9>"$TRAVA" > "$AQUI/avatar/$n.studio.log" 2>&1
      id=$(grep -oE 'create-v4/[0-9a-f]{32}' "$AQUI/avatar/$n.studio.log" | tail -1 | cut -d/ -f2)
      if [ -n "$id" ]; then echo "$id" > "$AQUI/avatar/$n.id"; echo "OK $n $id · $(grep -o '[0-9:]* est\.' "$AQUI/avatar/$n.studio.log" | tail -1)"; else echo "FALHOU $n: $(grep -o 'ERRO:.*' "$AQUI/avatar/$n.studio.log" | head -1)"; fi
    done ;;
  baixar)
    for f in "$AQUI"/avatar/*.id; do
      n=$(basename "$f" .id); [ -s "$AQUI/avatar/$n.mp4" ] && continue
      (cd "$HG" && env -u DISPLAY node heygen-estudio-baixar.mjs --id "$(cat "$f")" --saida "$AQUI/avatar/$n.mp4" --minutos 290 --intervalo 120) \
        > "$AQUI/avatar/$n.baixar.log" 2>&1 && echo "pronto $n" || echo "não baixou $n: $(tail -1 "$AQUI/avatar/$n.baixar.log")"
    done ;;
  *) echo "uso: $0 enviar | baixar"; exit 2 ;;
esac
