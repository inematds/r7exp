#!/usr/bin/env python3
"""Reels 9:16 do PHP2Shell tirados do completo (PADRAO §3): um por caso + o reel-índice.

Usa o monta() do motor/gera_reels.py (faixas: título · explicativo 16:9 limpo · avatar · imagem da Lúcia).
Precisa de: reels/limpo-a.mp4 (python3 php/gera_php.py limpo → render), build/n-<fala>.mp4, tempos/<fala>.json.
Uso: python3 php/gera_reels_php.py   → php/reels/<slug>/index.html; render com `npx hyperframes render`.
"""
import json, re, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "motor"))
import gera_reels as R  # noqa: E402

R.CORRIGE.update({"Php": "PHP", "php": "PHP", "Cloud": "Claude"})
MARCA = "PHP2SHELL"

CASOS = [  # id, fala, nome curto (≤ 18), cor, banda [(palavra-âncora | 0, imagem, rótulo)]
    ("P", "1-plataforma", "PLATAFORMA PRONTA", "#4ade80",
     [(0, "lucia-2026.png", "A LÚCIA · PADARIA"), ("lucia", "plataforma-lucia.png", "CASO 1 · SHOPIFY, WIX…")]),
    ("W", "2-wordpress", "WORDPRESS", "#FACC15",
     [(0, "lucia-2026.png", "A LÚCIA · PADARIA"), ("falha", "falha-servidor.png", "A FALHA ESTÁ NO PHP"),
      ("lucia", "wordpress-lucia.png", "CASO 2 · HOSPEDAGEM")]),
    ("S", "3-servidor", "SERVIDOR PRÓPRIO", "#ff4d4d",
     [(0, "servidor-ataque.png", "CASO 3 · VPS"), ("fazer", "servidor-tecnico.png", "ATUALIZE AGORA")]),
]


def meias():
    """janelas em que o 16:9 mostrava o avatar em meia tela (lado direito da faixa limpa fica vazio)."""
    js = (AQUI / "cena-a" / "index.html").read_text()
    ev = []
    for m in re.finditer(r'tl\.(?:to|set)\("#avw", \{([^}]*)\}, ([\d.]+)\)', js):
        corpo, t = m.group(1), float(m.group(2))
        ev.append(("fim" if corpo.replace(" ", "").startswith("x:0,y:0,scale:1,") else "ini", t))
    jan, aberta = [], None
    for tipo, t in sorted(ev, key=lambda e: e[1]):
        if tipo == "ini" and aberta is None:
            aberta = t
        elif tipo == "fim" and aberta is not None:
            jan.append((aberta, t + 0.7)); aberta = None
    return jan


def zooms_rel(jan, ini, dur):
    out = []
    for a, b in jan:
        a, b = a - ini, b - ini
        if b <= 0.8 or a >= dur - 0.8:
            continue
        a, b = max(0.0, a), min(dur, b)
        if b - a > 2.0:
            out.append((round(a, 2), round(b, 2), 1.2, "0% 35%"))
    return out


def banda_de(w, itens):
    out, depois = [], 0.0
    for anc, img, rot in itens:
        t = 0.0 if anc == 0 else R.t_palavra(w, anc, depois)
        depois = t
        out.append((round(t, 2), img, rot, "#ECECF1"))
    return out


def main():
    seg = {s["fala"]: s for s in json.loads((AQUI / "build" / "segmentos-a.json").read_text())["segmentos"]}
    jan = meias()
    for n, (k, fala, nome, cor, itens) in enumerate(CASOS, 1):
        s = seg[fala]
        dur = round(s["dur"], 2)
        _, w = R.palavras(AQUI, fala, dur)
        outros = [c for c in CASOS if c[0] != k]
        cel = "".join(f'<div class="cel" id="c{j}"><img src="assets/{o[4][-1][1]}"><span style="color:{o[3]}">{o[2]}</span></div>'
                      for j, o in enumerate(outros))
        fim_html = (f'<h2 style="top:200px;font-size:84px;color:#fff">EXISTEM OUTROS</h2>'
                    f'<h2 style="top:300px;font-size:124px;color:#FACC15;white-space:nowrap">2 CASOS</h2>'
                    f'<div class="grade">{cel}</div>'
                    f'<div class="sub" id="fsub" style="top:1000px">QUAL É O SEU?<br><span class="pill">vídeo completo no canal</span></div>')
        fim_js = [f'tl.to("#c{j}", {{opacity:1, duration:0.3}}, {dur + 0.1 + j * 0.25:.2f});' for j in range(2)]
        fim_js.append(f'tl.to("#fsub", {{opacity:1, duration:0.3}}, {dur + 0.9:.2f});')
        slug = f"caso-{n}-{fala.split('-', 1)[1]}"
        R.monta(AQUI, slug, marca=MARCA, chip=f"CASO {n} DE 3", nome=nome, cor=cor, fala=fala, exp="limpo-a.mp4",
                exp_ini=s["ini"], dur=dur, banda=banda_de(w, itens), fim_html=fim_html, fim_js=fim_js,
                zooms=zooms_rel(jan, s["ini"], dur))
        a = AQUI / "reels" / slug / "assets"
        for o in outros:
            R.link(AQUI / "imagens" / o[4][-1][1], a / o[4][-1][1])
    # reel-índice: a abertura até "vamos ver o que ela faz em cada caso"
    fala = "0-intro"
    _, w = R.palavras(AQUI, fala, 999)
    t_fim = round(R.t_palavra(w, "vamos") - 0.15, 2)
    banda = banda_de(w, [(0, "falha-servidor.png", "UMA FALHA NO PHP"), ("governos", "servidor-ataque.png", "GOVERNOS TIRARAM SITES DO AR"), ("lucia", "lucia-2026.png", "A LÚCIA · 54 ANOS · PADARIA")])
    lis = "".join(f'<div class="li" id="l{j}"><i style="background:{c[3]}"></i><span style="color:{c[3]}">{c[2]}</span></div>'
                  for j, c in enumerate(CASOS))
    fim_html = (f'<h2 style="top:240px;font-size:150px;color:#FACC15">QUAL É</h2><h2 style="top:390px;font-size:110px;color:#fff">O SEU CASO?</h2>'
                f'<div class="lista" style="top:600px">{lis}</div>'
                f'<div class="sub" id="fsub" style="top:1100px">um reel para cada caso<br><span class="pill">vídeo completo no canal</span></div>')
    fim_js = [f'tl.to("#l{j}", {{opacity:1, duration:0.25}}, {t_fim + 0.05 + j * 0.25:.2f});' for j in range(3)]
    fim_js.append(f'tl.to("#fsub", {{opacity:1, duration:0.3}}, {t_fim + 1.2:.2f});')
    R.monta(AQUI, "indice-3-casos", marca=MARCA, chip="21/10/2026 · URGENTE", nome="SITE EXPOSTO?", cor="#FACC15", fala=fala,
            exp="limpo-a.mp4", exp_ini=0.0, dur=t_fim, banda=banda, fim_html=fim_html, fim_js=fim_js,
            zooms=zooms_rel(jan, 0.0, t_fim))


if __name__ == "__main__":
    main()
