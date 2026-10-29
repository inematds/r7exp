#!/usr/bin/env bash
cd "$(dirname "$0")"
export PATH="$HOME/.npm-global/bin:$PATH"
X="codex exec -s workspace-write --skip-git-repo-check"
[ -s rafael-hoje.png ] || $X - < pedido-ref.txt > codex-ref.log 2>&1
$X -i rafael-hoje.png - < pedido.txt > codex.log 2>&1 &
[ -s capa-r7.png ] || $X - < pedido-capa.txt > codex-capa.log 2>&1 &
wait; python3 $HOME/projetos/refazvideo/ferramentas/cor_neutra.py corrigir $(ls *.png | grep -v -e print-inema -e capa-r7 -e amarela) > /dev/null 2>&1; ls -la *.png; echo FIM_IMAGENS
