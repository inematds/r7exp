#!/usr/bin/env python3
"""Reels 9:16 do "Qual bot você vai usar?" tirados do completo (PADRAO §3): um por bot + o reel-índice.

Mesmo esquema do php/gera_reels_php.py (motor/gera_reels.monta: título · explicativo 16:9 limpo · avatar · imagem da Carla).
Precisa de: reels/limpo-a.mp4 (python3 bots/gera_bots.py limpo → render), build/n-<fala>.mp4, tempos/<fala>.json.
Uso: python3 bots/gera_reels_bots.py → bots/reels/<slug>/index.html; render com `npx hyperframes render`.
"""
import json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "motor"))
sys.path.insert(0, str(AQUI.parent / "php"))
import gera_reels as R  # noqa: E402
import gera_reels_php as RP  # noqa: E402

RP.AQUI = AQUI   # meias() lê a cena-a desta pasta
R.CORRIGE.update({"Cloud": "Claude", "cloud": "Claude", "Doué": "Duet", "Doué.": "Duet.", "Doué,": "Duet,"})
MARCA = "QUAL BOT?"

CASOS = [  # id, fala, nome curto (≤ 18), cor, banda [(palavra-âncora | 0, imagem, rótulo)]
    ("G", "1-grok", "GROK BOT", "#e5e7eb", [(0, "carla-2026.png", "A CARLA · CONSULTORA"), ("chefe", "grok-carla.png", "EQUIPE DE BOTS")]),
    ("M", "2-muse", "META MUSE", "#60a5fa", [(0, "carla-2026.png", "A CARLA · CONSULTORA"), ("marcou", "muse-carla.png", "ELE LIGA POR VOCÊ")]),
    ("D", "3-dots", "CHATGPT DOTS", "#2dd4bf", [(0, "carla-2026.png", "A CARLA · CONSULTORA"), ("carla", "dots-carla.png", "USA SUA MEMÓRIA")]),
    ("C", "4-duet", "CLAUDE DUET", "#fb923c", [(0, "carla-2026.png", "A CARLA · CONSULTORA"), ("monta", "duet-carla.png", "O MAIS PROATIVO")]),
]


def main():
    seg = {s["fala"]: s for s in json.loads((AQUI / "build" / "segmentos-a.json").read_text())["segmentos"]}
    jan = RP.meias()
    for n, (k, fala, nome, cor, itens) in enumerate(CASOS, 1):
        s = seg[fala]
        dur = round(s["dur"], 2)
        _, w = R.palavras(AQUI, fala, dur)
        outros = [c for c in CASOS if c[0] != k]
        cel = "".join(f'<div class="cel" id="c{j}"><img src="assets/{o[4][-1][1]}" style="height:240px"><span style="color:{o[3]}">{o[2]}</span></div>'
                      for j, o in enumerate(outros))
        fim_html = (f'<h2 style="top:200px;font-size:84px;color:#fff">EXISTEM OUTROS</h2>'
                    f'<h2 style="top:300px;font-size:124px;color:#FACC15;white-space:nowrap">3 BOTS</h2>'
                    f'<div class="grade">{cel}</div>'
                    f'<div class="sub" id="fsub" style="top:1260px">QUAL É O SEU?<br><span class="pill">vídeo completo no canal</span></div>')
        fim_js = [f'tl.to("#c{j}", {{opacity:1, duration:0.3}}, {dur + 0.1 + j * 0.25:.2f});' for j in range(3)]
        fim_js.append(f'tl.to("#fsub", {{opacity:1, duration:0.3}}, {dur + 1.0:.2f});')
        slug = f"bot-{n}-{fala.split('-', 1)[1]}"
        R.monta(AQUI, slug, marca=MARCA, chip=f"BOT {n} DE 4", nome=nome, cor=cor, fala=fala, exp="limpo-a.mp4",
                exp_ini=s["ini"], dur=dur, banda=RP.banda_de(w, itens), fim_html=fim_html, fim_js=fim_js,
                zooms=RP.zooms_rel(jan, s["ini"], dur))
        a = AQUI / "reels" / slug / "assets"
        for o in outros:
            R.link(AQUI / "imagens" / o[4][-1][1], a / o[4][-1][1])
    # reel-índice: a abertura até "Vamos ver como fica a vida dela…"
    fala = "0-intro"
    _, w = R.palavras(AQUI, fala, 999)
    t_fim = round(R.t_palavra(w, "vamos") - 0.15, 2)
    banda = RP.banda_de(w, [(0, "final-carla.png", "QUAL BOT É O SEU?"), ("mapa", "duet-carla.png", "4 AGENTES · 10 SEMANAS"),
                            ("carla", "carla-2026.png", "A CARLA · 41 ANOS · CONSULTORA")])
    lis = "".join(f'<div class="li" id="l{j}"><i style="background:{c[3]}"></i><span style="color:{c[3]}">{c[2]}</span></div>'
                  for j, c in enumerate(CASOS))
    fim_html = (f'<h2 style="top:240px;font-size:150px;color:#FACC15">QUAL É</h2><h2 style="top:390px;font-size:110px;color:#fff">O SEU BOT?</h2>'
                f'<div class="lista" style="top:600px">{lis}</div>'
                f'<div class="sub" id="fsub" style="top:1180px">um reel para cada bot<br><span class="pill">vídeo completo no canal</span></div>')
    fim_js = [f'tl.to("#l{j}", {{opacity:1, duration:0.25}}, {t_fim + 0.05 + j * 0.25:.2f});' for j in range(4)]
    fim_js.append(f'tl.to("#fsub", {{opacity:1, duration:0.3}}, {t_fim + 1.3:.2f});')
    R.monta(AQUI, "indice-4-bots", marca=MARCA, chip="4 AGENTES PESSOAIS", nome="QUAL BOT?", cor="#FACC15", fala=fala,
            exp="limpo-a.mp4", exp_ini=0.0, dur=t_fim, banda=banda, fim_html=fim_html, fim_js=fim_js,
            zooms=RP.zooms_rel(jan, 0.0, t_fim))


if __name__ == "__main__":
    main()
