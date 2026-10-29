#!/usr/bin/env bash
# r7exp "A IA resolveu 100 anos de ciência?": baixa o avatar -> junta e transcreve -> completo 16:9 -> limpo -> reels 9:16.
# Escreve FIM_R7EXP no fim; qualquer erro escreve "ERRO <passo>" e para (o vigia continua chama a fase 2 nos dois casos).
set -u
B=$HOME/projetos/r7exp/ciencia; R=$HOME/projetos/r7exp
HF="npx --yes hyperframes@0.8.181"
log(){ echo "$(date +%H:%M:%S) $*"; }
falha(){ log "ERRO $*"; exit 1; }
prep(){ for f in hyperframes.json package.json; do [ -s "$1/$f" ] || cp $R/php/cena-a/$f "$1/"; done; }
render(){ # <pasta> <saida.mp4> <log>
  prep "$1"
  ( cd "$1" && systemd-run --user --scope --quiet -p MemoryMax=16G -p MemorySwapMax=0 timeout 5400 $HF render -o "$2" . ) > "$3" 2>&1 \
    && [ -s "$2" ] || falha "render $(basename $1) (ver $3)"
}
cd $R
for i in $(seq 1 40); do
  bash $B/avatar.sh baixar
  n=$(ls $B/avatar/*.id | wc -l); ok=$(ls $B/avatar/[0-9]-*.mp4 2>/dev/null | wc -l)
  [ "$ok" -ge "$n" ] && break
  log "avatar $ok/$n; tento de novo em 10 min"; sleep 600
done
[ "$(ls $B/avatar/[0-9]-*.mp4 2>/dev/null | wc -l)" -ge 6 ] || falha "avatar não chegou"
log "avatar ok"
[ -s $B/build/segmentos-a.json ] || systemd-run --user --scope --quiet -p MemoryMax=16G -p MemorySwapMax=0 python3 motor/monta_avatar.py ciencia a || falha "monta_avatar"
python3 ciencia/gera_ciencia.py > $B/build/gera.log 2>&1 || falha "gera_ciencia (âncora? ver build/gera.log)"
render $B/cena-a $B/build/ia-ciencia-r7exp.mp4 $B/build/render.log
log "completo ok $(ffprobe -v error -show_entries format=duration -of csv=p=0 $B/build/ia-ciencia-r7exp.mp4)s"
ffmpeg -loglevel error -y -i $B/build/ia-ciencia-r7exp.mp4 -vf scale=1280:720 -c:v libx264 -b:v 900k -c:a aac -b:a 96k -movflags +faststart $B/build/ia-ciencia-r7exp-720.mp4
python3 ciencia/gera_ciencia.py limpo > $B/build/gera-limpo.log 2>&1 || falha "gera_ciencia limpo"
mkdir -p $B/reels
render $B/cena-a-limpo $B/reels/limpo-a.mp4 $B/build/render-limpo.log
python3 ciencia/gera_reels_ciencia.py > $B/build/gera-reels.log 2>&1 || falha "gera_reels_ciencia (ver build/gera-reels.log)"
for d in $B/reels/indice-4-pecas $B/reels/peca-*; do
  s=$(basename $d); render $d $B/build/reel-$s.mp4 $B/build/render-reel-$s.log
  log "reel $s ok"
done
log "FIM_R7EXP"
