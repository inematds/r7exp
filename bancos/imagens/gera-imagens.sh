#!/usr/bin/env bash
cd "$(dirname "$0")"
X="codex exec -m gpt-6-astra -s workspace-write --skip-git-repo-check"
[ -s marcos-hoje.png ] || $X - < pedido-ref.txt > codex-ref.log 2>&1
$X -i marcos-hoje.png - < pedido.txt > codex.log 2>&1 &
$X - < pedido-capa.txt > codex-capa.log 2>&1 &
wait; ls -la *.png
