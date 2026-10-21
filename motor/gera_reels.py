#!/usr/bin/env python3
"""Reels 9:16 tirados do completo (PADRAO §3): um por caminho + o reel-índice.

Faixas (1080x1920): título (0-170) · explicativo 16:9 limpo (170-778) · avatar (778-1338, legenda no peito)
· a Ana naquele futuro (1338-1920). No fim, cartão "existem outros 4 caminhos" (caminho) ou "qual é o seu?" (índice).

Uso: python3 motor/gera_reels.py completo [--so E,Z]
Precisa de: reels/limpo-a.mp4 e reels/limpo-b.mp4 (gera.py <pasta> a|b limpo), build/n-<fala>.mp4, tempos/<fala>.json.
Saída: <pasta>/reels/<slug>/index.html (+ assets por hardlink); render com `npx hyperframes render`.
"""
import json, os, re, shutil, sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from gera import legenda, CORRIGE, norm  # noqa: E402

W, H = 1080, 1920
Y_EXP, H_EXP = 170, 608
Y_AV, H_AV = 778, 560
Y_IMG = Y_AV + H_AV
FIM = 3.5          # cartão final (sem fala)

# imagens da Ana em 2040 por caminho (a de 2026 abre todos)
FOTOS = {"E": ["extincao-casa.png", "extincao-corrida.png"], "Z": ["ana-2040-zoo.png", "ana-2040-vidro.png"],
         "G": ["governo-ana.png", "governo-rua.png"], "P": ["paraiso-ana.png", "paraiso-cidade.png"],
         "U": ["utopia-ana.png", "utopia-familia.png"]}
SLUG = {"E": "1-extincao", "Z": "2-zoologico", "G": "3-governo", "P": "4-paraiso", "U": "5-utopia"}

CSS = """
@font-face { font-family:"Sora"; src:url("assets/fonts/sora-latin-700-normal.woff2") format("woff2"); font-weight:700; }
@font-face { font-family:"Inter"; src:url("assets/fonts/Inter-700.woff2") format("woff2"); font-weight:700; }
@font-face { font-family:"Montserrat"; src:url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight:900; }
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:1080px; height:1920px; overflow:hidden; background:#0c0c10; }
#root { width:100%; height:100%; position:relative; background:#0c0c10; color:#fff; font-family:Inter, sans-serif; }
.clip { position:absolute; }
.full { inset:0; }
#hdr { left:0; top:0; width:1080px; height:170px; padding:22px 40px 0; }
.chip { display:inline-block; font-family:Sora; font-weight:700; font-size:26px; letter-spacing:.14em; padding:7px 16px; border-radius:999px; background:#FACC15; color:#14110a; }
.marca { position:absolute; right:40px; top:28px; font-family:Sora; font-weight:700; font-size:28px; letter-spacing:.14em; color:#FACC15; }
.marca span { color:#ECECF1; }
.nome { font-family:Montserrat; font-weight:900; font-size:76px; line-height:1; margin-top:12px; white-space:nowrap; text-transform:uppercase; }
#expw { position:absolute; left:0; top:170px; width:1080px; height:608px; overflow:hidden; }
#exp { position:absolute; left:0; top:0; width:1080px; height:608px; object-fit:cover; }
#avw { position:absolute; left:0; top:778px; width:1080px; height:560px; overflow:hidden; border-top:4px solid #FACC15; border-bottom:4px solid #FACC15; }
#av { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; object-position:50% 22%; }
#banda { left:0; top:1338px; width:1080px; height:582px; overflow:hidden; }
#banda img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; transform-origin:50% 40%; }
#banda .sombra { position:absolute; inset:0; background:linear-gradient(180deg, rgba(12,12,16,.55) 0%, rgba(12,12,16,0) 30%); }
.rot { position:absolute; left:40px; top:26px; font-family:Sora; font-weight:700; font-size:30px; letter-spacing:.06em; padding:8px 18px; border-radius:12px; background:rgba(12,12,16,.85); opacity:0; }
#legenda { left:0; top:0; width:1080px; height:1920px; }
.cap { position:absolute; left:30px; right:30px; top:1196px; text-align:center; font-family:Montserrat; font-weight:900; font-size:68px; line-height:1.05; text-transform:uppercase; opacity:0;
       color:#fff; -webkit-text-stroke:10px #000; paint-order:stroke fill; }
.cap b { font-weight:900; }
#capa img { width:100%; height:100%; object-fit:cover; }
.fim { background:#0c0c10; opacity:0; }
.fim h2 { position:absolute; left:40px; right:40px; text-align:center; font-family:Montserrat; font-weight:900; text-transform:uppercase; line-height:1; }
.grade { position:absolute; left:40px; right:40px; top:480px; display:grid; grid-template-columns:1fr 1fr; gap:22px; }
.cel { border-radius:16px; overflow:hidden; background:#16161e; opacity:0; }
.cel img { width:100%; height:300px; object-fit:cover; display:block; }
.cel span { display:block; padding:12px 10px; font-family:Sora; font-weight:700; font-size:28px; text-align:center; }
.lista { position:absolute; left:90px; right:90px; top:520px; }
.li { display:flex; align-items:center; gap:24px; margin-bottom:34px; font-family:Sora; font-weight:700; font-size:50px; opacity:0; }
.li i { flex:none; width:30px; height:30px; border-radius:50%; }
.sub { position:absolute; left:40px; right:40px; text-align:center; font-family:Sora; font-weight:700; font-size:40px; color:#c9c9d2; line-height:1.3; opacity:0; }
.pill { display:inline-block; margin-top:22px; font-family:Sora; font-weight:700; font-size:44px; padding:14px 40px; border-radius:999px; background:#FACC15; color:#1a1206; }
"""


class Js:
    def __init__(self):
        self.js = []

    def a(self, s):
        self.js.append(s)


def palavras(pasta, fala, ate):
    w = json.loads((pasta / "tempos" / f"{fala}.json").read_text())
    pal = []
    for x in w:
        if x["start"] >= ate - 0.05:
            break
        wd = CORRIGE.get(x["word"].strip(), x["word"].strip())
        if pal and wd[:1] in "-." and len(wd) > 1:
            pal[-1]["word"] += wd; continue
        pal.append({"word": wd, "t": round(x["start"], 2)})
    return pal, w


def link(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def monta(pasta, slug, *, chip, nome, cor, fala, exp, exp_ini, dur, banda, fim_html, fim_js, capa=None, capa_ate=0.0, zooms=()):
    """banda = [(t_ini, img, rotulo, cor_rotulo)]; troca com dissolve e zoom lento (≤1,08)."""
    out = pasta / "reels" / slug
    a = out / "assets"
    (a / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (pasta / "cena-a" / "assets" / "fonts").iterdir():
        link(f, a / "fonts" / f.name)
    link(pasta / "reels" / exp, a / "exp.mp4")
    link(pasta / "build" / f"n-{fala}.mp4", a / "av.mp4")
    imgs = sorted({b[1] for b in banda} | ({capa} if capa else set()))
    for im in imgs:
        src = pasta / "imagens" / im if (pasta / "imagens" / im).exists() else pasta / "build" / im
        link(src, a / im)
    total = round(dur + FIM, 2)
    J = Js()
    pal, _ = palavras(pasta, fala, dur)
    leg = legenda(J, pal, dur)
    # banda: imagens
    bh, rh = [], []
    for k, (t0, im, rot, rc) in enumerate(banda):
        t1 = banda[k + 1][0] if k + 1 < len(banda) else dur
        bh.append(f'<img id="bi{k}" src="assets/{im}">')
        rh.append(f'<div class="rot" id="br{k}" style="color:{rc}">{rot}</div>')
        if k:
            J.a(f'tl.to("#bi{k}", {{opacity:1, duration:0.6}}, {max(0, t0 - 0.3):.2f});')
        else:
            J.a('tl.set("#bi0", {opacity:1}, 0);')
        J.a(f'tl.fromTo("#bi{k}", {{scale:1}}, {{scale:1.08, duration:{t1 - t0 + 0.6:.2f}, ease:"none", immediateRender:false}}, '
            f'{max(0, t0 - 0.3):.2f});')
        if k:
            J.a(f'tl.to("#bi{k - 1}", {{opacity:0, duration:0.6}}, {t0 + 0.3:.2f});')
        J.a(f'tl.set("#br{k}", {{opacity:1}}, {t0:.2f}); tl.set("#br{k}", {{opacity:0}}, {t1 - 0.02:.2f});')
    capa_html = ""
    if capa:
        capa_html = (f'<div id="capa" class="clip full" data-start="0" data-duration="{capa_ate + 0.5:.2f}" data-track-index="12">'
                     f'<img src="assets/{capa}"></div>')
        J.a(f'tl.to("#capa", {{opacity:0, duration:0.45}}, {capa_ate:.2f});')
    for z0, z1, k, orig in zooms:      # enquadra um painel do 16:9 (o resto da faixa estaria vazio)
        J.a(f'tl.to("#exp", {{scale:{k}, transformOrigin:"{orig}", duration:0.6, ease:"power2.inOut"}}, {z0:.2f});')
        J.a(f'tl.to("#exp", {{scale:1, duration:0.6, ease:"power2.inOut"}}, {z1 - 0.6:.2f});')
    J.js.extend(fim_js)
    html = f'''<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1080" data-height="1920">
 <div id="hdr" class="clip" data-start="0" data-duration="{dur:.2f}" data-track-index="1"><span class="chip">{chip}</span>
  <div class="marca">INEMA <span>· 5 FUTUROS</span></div><div class="nome" style="color:{cor};font-size:{76 if len(nome) <= 18 else 66}px">{nome}</div></div>
 <div id="expw"><video id="exp" class="clip" src="assets/exp.mp4" data-start="0" data-duration="{dur:.2f}" data-media-start="{exp_ini:.3f}" data-track-index="2" data-volume="0" muted playsinline></video></div>
 <div id="avw">
  <video id="av" src="assets/av.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="4" data-has-audio="true" data-volume="1" playsinline></video></div>
 <div id="banda" class="clip" data-start="0" data-duration="{dur:.2f}" data-track-index="5">{"".join(bh)}<div class="sombra"></div>{"".join(rh)}</div>
 <div id="legenda" class="clip" data-start="0" data-duration="{dur:.2f}" data-track-index="10">{leg}</div>
 <div id="fim" class="clip full fim" data-start="{dur - 0.4:.2f}" data-duration="{FIM + 0.4:.2f}" data-track-index="11">{fim_html}</div>
 {capa_html}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.to("#fim", {{opacity:1, duration:0.4}}, {dur - 0.4:.2f});
{chr(10).join(J.js)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>'''
    (out / "index.html").write_text(html)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy2(pasta / "cena-a" / f, out / f)
    print(f"ok {slug} · {total:.1f} s")


def t_palavra(w, alvo, depois=0.0):
    for x in w:
        if x["start"] >= depois and norm(x["word"]).startswith(alvo):
            return x["start"]
    raise SystemExit(f"palavra não achada: {alvo}")


def main():
    pasta = Path(sys.argv[1]).resolve()
    so = sys.argv[sys.argv.index("--so") + 1].split(",") if "--so" in sys.argv else None
    f = yaml.safe_load((pasta / "ficha.yaml").read_text())
    L = f["mapa"]["linhas"]
    seg = {s["fala"]: s for s in json.loads((pasta / "build" / "segmentos-a.json").read_text())["segmentos"]}
    ordem = [c["id"] for c in f["caminhos"]]
    for n, c in enumerate(f["caminhos"], 1):
        k = c["id"]
        if so and k not in so:
            continue
        s = seg[c["fala"]]
        dur = round(s["dur"], 2)
        _, w = palavras(pasta, c["fala"], dur)
        nome = L[k]["nome"].replace(" ia", " IA")
        f1, f2 = FOTOS[k]
        t2040 = t_palavra(w, "vive") if any(norm(x["word"]).startswith("vive") for x in w) else 6.0
        tmeio = t2040 + (dur - t2040) / 2
        banda = [(0, "ana-2026.png", "A ANA · 2026", "#ECECF1"),
                 (t2040, f1, f"A ANA · 2040 · {nome}", L[k]["cor"]),
                 (tmeio, f2, f"2040 · {nome}", L[k]["cor"])]
        outros = [o for o in ordem if o != k]
        cel = "".join(f'<div class="cel" id="c{j}"><img src="assets/{FOTOS[o][0]}"><span style="color:{L[o]["cor"]}">'
                      f'{L[o]["nome"].replace(" ia", " IA")}</span></div>' for j, o in enumerate(outros))
        fim_html = (f'<h2 style="top:200px;font-size:84px;color:#fff">EXISTEM OUTROS</h2>'
                    f'<h2 style="top:300px;font-size:124px;color:#FACC15;white-space:nowrap">4 CAMINHOS</h2>'
                    f'<div class="grade">{cel}</div>'
                    f'<div class="sub" id="fsub" style="top:1240px">QUAL É O SEU?<br><span class="pill">vídeo completo no canal</span></div>')
        fim_js = [f'tl.to("#c{j}", {{opacity:1, duration:0.3}}, {dur + 0.1 + j * 0.25:.2f});' for j in range(4)]
        fim_js.append(f'tl.to("#fsub", {{opacity:1, duration:0.3}}, {dur + 1.2:.2f});')
        imgs_fim = [(dur + 9, FOTOS[o][0], "", "#fff") for o in outros]   # só para copiar os arquivos
        monta(pasta, f"caminho-{n}-{SLUG[k].split('-', 1)[1]}", chip=f"CAMINHO {n} DE 5", nome=nome, cor=L[k]["cor"],
              fala=c["fala"], exp="limpo-a.mp4", exp_ini=s["ini"], dur=dur, banda=banda, fim_html=fim_html, fim_js=fim_js)
        a = pasta / "reels" / f"caminho-{n}-{SLUG[k].split('-', 1)[1]}" / "assets"
        for _, im, _, _ in imgs_fim:
            link(pasta / "imagens" / im, a / im)
    if so and "I" not in so:
        return
    # reel-índice: abertura B
    fala = f["aberturas"]["b"]["fala"]
    _, w = palavras(pasta, fala, 999)
    t_fim = t_palavra(w, "comecando") - 0.15
    capa_ate = t_palavra(w, "junto") + 0.35
    t5 = t_palavra(w, "caminhos")
    banda = [(0, "ana-2026.png", "A ANA · 2026", "#ECECF1")]
    t, j = t5, 0
    while t < t_fim - 0.5:
        o = ordem[j % 5]
        banda.append((round(t, 2), FOTOS[o][0], f"2040 · {L[o]['nome'].replace(' ia', ' IA')}", L[o]["cor"]))
        t += 2.2; j += 1
    lis = "".join(f'<div class="li" id="l{j}"><i style="background:{L[o]["cor"]}"></i><span style="color:{L[o]["cor"]}">'
                  f'{L[o]["nome"].replace(" ia", " IA")}</span></div>' for j, o in enumerate(ordem))
    fim_html = (f'<h2 style="top:240px;font-size:150px;color:#FACC15">QUAL É</h2><h2 style="top:390px;font-size:110px;color:#fff">O SEU?</h2>'
                f'<div class="lista" style="top:600px">{lis}</div>'
                f'<div class="sub" id="fsub" style="top:1300px">um reel para cada caminho<br><span class="pill">vídeo completo no canal</span></div>')
    fim_js = [f'tl.to("#l{j}", {{opacity:1, duration:0.25}}, {t_fim + 0.05 + j * 0.25:.2f});' for j in range(5)]
    fim_js.append(f'tl.to("#fsub", {{opacity:1, duration:0.3}}, {t_fim + 1.4:.2f});')
    monta(pasta, "indice-5-caminhos", chip="A PARTIR DE 2027", nome="5 CAMINHOS", cor="#FACC15", fala=fala,
          exp="limpo-b.mp4", exp_ini=0.0, dur=round(t_fim, 2), banda=banda, fim_html=fim_html, fim_js=fim_js,
          capa="B-capa-9x16-3-empilhadas.jpg", capa_ate=capa_ate,
          zooms=[(t_palavra(w, "grupo") + 0.3, t_palavra(w, "stanford") - 0.2, 1.2, "5% 16%")])


if __name__ == "__main__":
    main()
