#!/usr/bin/env python3
"""r7exp completo 16:9 — "Qual bot você vai usar?" (22/10/2026). Par do refazvideo D-pz8L1orVI.

Mapa = os 4 agentes pessoais lado a lado (lançados ago–out 2026); cada bloco muda de estado:
0 "?" · 1 a força · 2 o ponto fraco · 3 para quem é. A Carla (consultora, 41) atravessa os 4 caminhos.
Reaproveita peças do motor (motor/gera.py) e do musk/gera_musk.py sem editá-los (mesmo esquema do php/gera_php.py).
Uso: python3 bots/gera_bots.py [--falso] [limpo]
Precisa: imagens/*.png, tempos/<fala>.json, build/avatar-a.mp4 + build/segmentos-a.json (motor/monta_avatar.py bots a).
Saída: cena-a/index.html (ou cena-a-limpo/ sem avatar e sem legenda, para os reels).
"""
import json, re, shutil, sys
from pathlib import Path
import yaml

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "motor"))
sys.path.insert(0, str(AQUI.parent / "musk"))
sys.path.insert(0, str(AQUI.parent / "php"))
import gera as G  # noqa: E402
import gera_musk as M  # noqa: E402
import gera_php as P  # noqa: E402

V = "a"
GX, GY, GS = G.GX, G.GY, G.GS
VERDE, VERM, AMAR = "#4ade80", "#ff4d4d", "#FACC15"
#        slug   nome            data      cor        força (2 linhas)                fraco (2 linhas)               para quem
BOTS = [("grok", "Grok Bot", "11 ago", "#e5e7eb", ("EQUIPE", "DE BOTS"), ("E-MAIL FALHA", "É PAGO"), "EQUIPE DIGITAL"),
        ("muse", "Meta Muse", "8 set", "#60a5fa", ("LIGA POR", "VOCÊ"), ("MODELO", "NÃO É DE PONTA"), "TELEFONE"),
        ("dots", "ChatGPT Dots", "29 set", "#2dd4bf", ("USA SUA", "MEMÓRIA"), ("BUGS", "E LENTO"), "MEMÓRIA"),
        ("duet", "Claude Duet", "21 out", "#fb923c", ("O MAIS", "PROATIVO"), ("NAVEGADOR", "FORA DO BRASIL"), "INICIATIVA")]
TX0, TSTEP, TW, TY, TH = 400, 345, 315, 300, 520


def gy(y): return GY + y * GS


# ---------------------------------------------------------------- mapa: os 4 bots
def mapa_svg(f):
    tiles, dots = "", ""
    for i, (slug, nome, data, cor, forca, fraco, quem) in enumerate(BOTS):
        x = TX0 + i * TSTEP; cx = x + TW / 2
        est = (f'<g id="e0{i}"><text x="{cx}" y="{TY + 420}" text-anchor="middle" font-size="96" fill="#6b6b78">?</text></g>'
               f'<g id="e1{i}" opacity="0"><text x="{cx}" y="{TY + 380}" text-anchor="middle" font-size="40" fill="{cor}" font-weight="800">{forca[0]}</text>'
               f'<text x="{cx}" y="{TY + 430}" text-anchor="middle" font-size="40" fill="{cor}" font-weight="800">{forca[1]}</text></g>'
               f'<g id="e2{i}" opacity="0"><text x="{cx}" y="{TY + 350}" text-anchor="middle" font-size="64" fill="{VERM}" font-weight="800">✕</text>'
               f'<text x="{cx}" y="{TY + 410}" text-anchor="middle" font-size="31" fill="{VERM}" font-weight="800">{fraco[0]}</text>'
               f'<text x="{cx}" y="{TY + 450}" text-anchor="middle" font-size="31" fill="{VERM}" font-weight="800">{fraco[1]}</text></g>'
               f'<g id="e3{i}" opacity="0"><text x="{cx}" y="{TY + 365}" text-anchor="middle" font-size="64" fill="{VERDE}" font-weight="800">✓</text>'
               f'<text x="{cx}" y="{TY + 430}" text-anchor="middle" font-size="34" fill="{VERDE}" font-weight="800">{quem}</text></g>')
        tiles += (f'<g class="tile" id="v{i}"><rect id="vr{i}" x="{x}" y="{TY}" width="{TW}" height="{TH}" rx="22" fill="#15151c" stroke="#3a3a46" stroke-width="5"/>'
                  f'<image href="assets/logo-{slug}.png" x="{cx - 85}" y="{TY + 30}" width="170" height="160" preserveAspectRatio="xMidYMid meet"/>'
                  f'<text x="{cx}" y="{TY + 250}" text-anchor="middle" font-size="40" class="vv">{nome}</text>{est}</g>')
        dots += (f'<circle cx="{cx}" cy="{TY + TH + 70}" r="14" fill="{AMAR}"/>'
                 f'<text x="{cx}" y="{TY + TH + 125}" text-anchor="middle" font-size="30" fill="#c9c9d2">{data}</text>')
    br = (f'<g id="br" opacity="0"><rect x="{TX0 + 3 * TSTEP - 15}" y="{TY - 40}" width="{TW + 30}" height="58" rx="29" fill="{VERM}"/>'
          f'<text x="{TX0 + 3 * TSTEP + TW / 2}" y="{TY - 1}" text-anchor="middle" font-size="27" fill="#fff" font-weight="800">AINDA NÃO NO BRASIL</text></g>')
    return f'''
<svg id="mapa" width="1920" height="1080" viewBox="0 0 1920 1080">
 <g transform="translate({GX},{GY}) scale({GS})">
  <g id="ticks" opacity="0">
   <text x="400" y="190" font-size="58" fill="#fff" font-weight="800" class="vv"><tspan fill="{AMAR}">4 AGENTES</tspan> EM 10 SEMANAS</text>
   <text x="400" y="240" font-size="28" fill="#9a9aa6">cada um aposta numa força diferente</text>
  </g>
  <g id="eixos" opacity="0">
   {tiles}
   <path d="M{TX0},{TY + TH + 70} H{TX0 + 3 * TSTEP + TW}" stroke="#3a3a46" stroke-width="5"/>
   {dots}
   {br}
  </g>
 </g>
</svg>'''


class Cena(P.Cena):
    def zoom_tile(self, t, i, z=1.08):
        # origem presa à esquerda: o quadro cresce para a direita e não entra sob o PiP do avatar (canto inferior esquerdo)
        x0 = GX + TX0 * GS
        cx = min(GX + (TX0 + i * TSTEP + TW / 2) * GS, (x0 * z - 380) / (z - 1))
        self.a(f'tl.to("#cam", {{scale:{z}, transformOrigin:"{cx:.0f}px {gy(TY + TH / 2):.0f}px", duration:1.4, ease:"power2.inOut"}}, {t:.2f});')
        self.a(f'tl.to("#ticks", {{opacity:0, duration:0.4}}, {t:.2f});')

    def destaca(self, t, i):
        cor = BOTS[i][3]
        outros = [f"#v{j}" for j in range(4) if j != i]
        self.a(f'tl.to({json.dumps(outros)}, {{opacity:0.25, duration:0.5}}, {t:.2f}); tl.to("#v{i}", {{opacity:1, duration:0.5}}, {t:.2f});')
        self.a(f'tl.to("#vr{i}", {{attr:{{stroke:"{cor}"}}, duration:0.4}}, {t:.2f});')

    def todos(self, t):
        self.a(f'tl.to(".tile", {{opacity:1, duration:0.5}}, {t:.2f});')

    # ------------------------------------------------------------ abertura
    def abertura(self, F):
        t_capa = F.t("semanas") - 0.9                    # capa parada a 1ª frase inteira
        inner = self.id("in")
        self.clip(0, t_capa + 0.6, f'<div class="in" id="{inner}" style="opacity:1"><img class="foto" id="{inner}f" src="assets/capa-r7.png" alt="capa"/></div>', 3)
        self.a(f'tl.fromTo("#{inner}f", {{scale:0.93, transformOrigin:"0% 0%"}}, {{scale:0.95, transformOrigin:"0% 0%", duration:{t_capa + 0.6:.2f}, ease:"none"}}, 0);')
        self.a(f'tl.to("#{inner}", {{opacity:0, duration:0.6}}, {t_capa:.2f});')
        self.esconde_mapa(-1, t_capa + 0.6)
        tg = F.t("mapa")
        self.abre_meia(tg)
        self.a(f'tl.set(["#marca","#fonte"], {{opacity:0}}, 0); tl.to("#marca", {{opacity:1, duration:0.5}}, {t_capa:.2f}); tl.to("#fonte", {{opacity:1, duration:0.5}}, {tg:.2f});')
        # quatro gigantes (metade esquerda, avatar à direita)
        F.cur = t_capa - F.ini - 0.02
        i2 = self.id("in")
        corpo = (f'<div class="in opaque" id="{i2}"><div class="mus"><div class="chip" style="background:rgba(250,204,21,.16);color:#FACC15">EM 10 SEMANAS</div>'
                 f'<div class="a27t" style="font-size:76px">4 gigantes, 4 agentes pessoais</div>')
        its = []
        for pal, (slug, nome, data, cor, *_) in zip(["grok", "muse", "dots", "duet"], BOTS):
            j = self.id("a")
            corpo += (f'<div class="row27" id="{j}"><img src="assets/logo-{slug}.png" alt="" style="width:64px;height:60px;object-fit:contain;border-radius:12px">'
                      f'<div><b style="color:{cor}">{nome}</b> <span style="color:#9a9aa6">· {data}</span></div></div>')
            its.append((j, F.t(pal, obrig=False)))
        corpo += "</div></div>"
        self.clip(t_capa, tg + 0.3, corpo, 4)
        self.cena_in_out(i2, t_capa, tg + 0.3)
        self.esconde_mapa(t_capa, tg)
        tprev = t_capa + 0.4
        for j, t in its:
            t = t or tprev + 1.0
            self.a(f'tl.fromTo("#{j}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {t - 0.1:.2f});')
            tprev = t
        # mapa: os 4 blocos; o Duet ganha a etiqueta "ainda não no Brasil"
        self.a(f'tl.fromTo("#ticks", {{opacity:0}}, {{opacity:1, duration:0.6}}, {tg:.2f});')
        self.a(f'tl.fromTo("#eixos", {{opacity:0}}, {{opacity:1, duration:0.4}}, {tg:.2f});')
        self.a(f'tl.fromTo(".tile", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.45, stagger:0.15}}, {tg + 0.1:.2f});')
        tb = F.t("brasil")
        self.a(f'tl.fromTo("#br", {{opacity:0, scale:0.6, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.45, ease:"back.out(2)"}}, {tb - 0.2:.2f});')
        # Carla hoje
        tc = F.t("carla", depois=tb); tv = F.t("vamos", depois=tc)
        self.foto(tc - 0.2, tv + 0.2, "carla-2026.png", carimbo="CARLA · HOJE", sub="A PERSONAGEM")
        F.cur = tc - F.ini - 0.02
        self.tags(F, [("consultora", "consultora · 41 anos"), ("dia", "✕ cem e-mails por dia"),
                      ("estourando", "✕ agenda estourando")], tv + 0.2)
        self.faixa("COMO FICA A VIDA DELA COM CADA BOT", tv, F.fim + 0.5)

    # ------------------------------------------------------------ um caminho por bot
    def bot(self, F, i, prox, card_ini, card_tit, card_itens, foto_ini, img, carimbo, tags, fraco_ini):
        slug, nome, data, cor, forca, fraco, quem = BOTS[i]
        t0 = F.ini
        self.a(f'tl.set("#br", {{opacity:{1 if i == 3 else 0}}}, {t0:.2f});')
        self.mapa_todo(t0 - 0.4, ticks=False)
        self.todos(t0 - 0.4)
        self.zoom_tile(t0 + 0.1, i)
        self.destaca(t0 + 0.1, i)
        self.estado(t0 + 0.8, [i], 1, cor, "#1c1c24")
        F.cur = 0
        tci = F.t(card_ini)
        self.titulo(f"BOT {i + 1} DE 4", nome.upper(), cor, t0, tci)
        F.cur = tci - F.ini - 0.02
        tfo = F.t(foto_ini, depois=tci)
        F.cur = tci - F.ini - 0.02
        self.card(F, "O QUE É", cor, card_tit, card_itens, tci - 0.2, tfo - 0.1)
        self.esconde_mapa(tci - 0.8, tfo + 0.6)
        tfr = F.t(fraco_ini, depois=tfo)
        F.cur = tfo - F.ini - 0.02
        self.foto(tfo - 0.2, tfr + 0.2, img, carimbo=carimbo, sub="A MESMA CARLA")
        F.cur = tfo - F.ini - 0.02
        self.tags(F, tags, tfr + 0.2)
        # ponto fraco no mapa
        self.mapa_todo(tfr - 0.3, ticks=False)
        self.zoom_tile(tfr - 0.2, i, z=1.06)
        self.estado(tfr + 0.2, [i], 2, VERM, "#2a0f12")
        self.faixa(f"PONTO FRACO · {fraco[0]} · {fraco[1]}", tfr - 0.1, prox + 0.1, cor=VERM)

    # ------------------------------------------------------------ final
    def final(self, F, fim_total):
        t0 = F.ini
        tm = F.t("melhor")
        cards = [("grok-carla.png", BOTS[0][3], "GROK", "equipe digital", "equipe"),
                 ("muse-carla.png", BOTS[1][3], "MUSE", "liga por você", "ligue"),
                 ("dots-carla.png", BOTS[2][3], "DOTS", "usa sua memória", "vive"),
                 ("duet-carla.png", BOTS[3][3], "DUET", "organiza seu dia", "organize")]
        inner = self.id("in")
        corpo = f'<div class="in opaque" id="{inner}"><div class="cmp">'
        ts = []
        F.cur = 0.0
        for im, cor, nome, sub, pal in cards:
            j = self.id("cc")
            corpo += f'<div class="cc" id="{j}" style="border-top:8px solid {cor}"><img src="assets/{im}" alt=""/><span style="color:{cor}">{nome}</span><p>{sub}</p></div>'
            ts.append((j, F.t(pal)))
        corpo += '</div><div class="frase" id="%sfr"><div>Quatro bots.</div><div style="color:#FACC15">A mesma Carla.</div></div></div>' % inner
        self.clip(t0, tm - 0.4, corpo, 4)
        self.cena_in_out(inner, t0, tm - 0.4)
        self.esconde_mapa(t0, tm - 0.4)
        for j, t in ts:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.5, ease:"back.out(2)"}}, {t - 0.15:.2f});')
        self.a(f'tl.set("#{inner}fr", {{opacity:0}}, 0);')
        # mapa: para quem é cada um
        F.cur = tm - F.ini - 0.02
        ti = F.t("isso", depois=tm)
        self.a(f'tl.set("#br", {{opacity:0}}, {tm - 0.5:.2f});')
        self.mapa_todo(tm - 0.5, ticks=False)
        self.todos(tm - 0.5)
        self.a(f'tl.to("#cam", {{scale:1.06, transformOrigin:"1000px {gy(TY + TH / 2):.0f}px", duration:1.2, ease:"power2.inOut"}}, {tm - 0.3:.2f});')
        for i in range(4):
            self.estado(tm + i * 0.2, [i], 3, VERDE, "#0f2a17", stagger=0)
        self.faixa("O MELHOR AGENTE JUNTARIA OS 4", tm - 0.1, ti + 0.2, cor=VERDE)
        tclub = F.t("inema", depois=ti, obrig=False) or ti + 2
        i3 = self.id("in")
        corpo = (f'<div class="in" id="{i3}"><img class="foto" src="assets/final-carla.png" alt=""/><div class="full" style="background:rgba(12,12,16,.8)"></div><div class="fim"><h2>E você?</h2>'
                 f'<div class="sub">comenta: “eu escolho o …” 👇</div><div class="pill" id="{i3}p">inema.club</div></div>'
                 f'<div class="printc" id="{i3}pr"><img src="assets/print-inema.png" alt="inema.club"/><span>aberto e gratuito · inema.club</span></div></div>')
        self.clip(ti - 0.1, fim_total, corpo, 6)
        self.esconde_mapa(ti - 0.1, fim_total + 2)
        self.a(f'tl.fromTo("#{i3}", {{opacity:0}}, {{opacity:1, duration:0.6}}, {ti - 0.1:.2f});')
        self.entra(f"#{i3}p", tclub - 0.1)
        self.a(f'tl.fromTo("#{i3}pr", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.6, ease:"back.out(2)"}}, {tclub:.2f});')


CORRIGE = {"ia": "IA", "Ia": "IA", "Cloud": "Claude", "cloud": "Claude", "Duet.": "Duet.", "Doué": "Duet", "Doué.": "Duet.", "Doué,": "Duet,", "inema": "inema"}


def falso(ordem):
    segs, tempos, t = [], {}, 0.0
    for fala in ordem:
        txt = (AQUI / "falas" / f"{fala}.txt").read_text().split()
        tt, out = 0.2, []
        for w in txt:
            d = max(0.18, len(w) / 14.5)
            out.append({"word": w, "start": round(tt, 2), "end": round(tt + d, 2)})
            tt += d + (0.35 if re.search(r"[.?:]$", w) else 0.06)
        tempos[fala] = out
        segs.append({"fala": fala, "ini": round(t, 3), "dur": round(tt + 0.5, 3)})
        t += tt + 0.5
    return {"segmentos": segs, "total": round(t, 3)}, tempos


def main():
    f = yaml.safe_load((AQUI / "ficha.yaml").read_text())
    ordem = [f["aberturas"][V]["fala"]] + [c["fala"] for c in f["caminhos"]] + [f["final"]["fala"]]
    if "--falso" in sys.argv:
        seg, tempos = falso(ordem)
    else:
        seg = json.loads((AQUI / "build" / f"segmentos-{V}.json").read_text())
        tempos = {s["fala"]: json.loads((AQUI / "tempos" / f"{s['fala']}.json").read_text()) for s in seg["segmentos"]}
    falas = {s["fala"]: G.Fala(s["fala"], tempos[s["fala"]], s["ini"]) for s in seg["segmentos"]}
    total = round(seg["total"] + 0.6, 2)
    cena = Cena(f, V, AQUI)
    cena.abertura(falas[ordem[0]])
    ini = [falas[o].ini for o in ordem]
    cena.bot(falas[ordem[1]], 0, ini[2], "trata", "Uma equipe de bots",
             [("funcionario", "👥", "cada bot é um funcionário"), ("pesquisa", "🔎", "um pesquisa, outro escreve"),
              ("real", "⚡", "lê o X em tempo real")],
             "grok", "grok-carla.png", "CARLA · COM O GROK", [("chefe", "✓ chefe de uma equipe digital")], "atencao")
    cena.bot(falas[ordem[2]], 1, ini[3], "gratuito", "Liga para empresas",
             [("gratuito", "🆓", "gratuito"), ("visual", "✨", "o visual mais caprichado"), ("liga", "📞", "liga para empresas de verdade")],
             "marcou", "muse-carla.png", "CARLA · COM O MUSE",
             [("poda", "✓ marcou a poda de árvore"), ("negociou", "✓ negociou a conta de TV"), ("linha", "✓ não espera mais na linha")], "ponto")
    cena.bot(falas[ordem[3]], 2, ini[4], "mora", "Mora no ChatGPT",
             [("mora", "🏠", "dentro do ChatGPT"), ("memoria", "🧠", "já conhece a sua memória"), ("ensinar", "📚", "nada de novo para ensinar")],
             "carla", "dots-carla.png", "CARLA · COM O DOTS", [("clientes", "✓ já sabe quem são os clientes")], "problema")
    cena.bot(falas[ordem[4]], 3, ini[5], "proativo", "O mais proativo",
             [("proativo", "⚡", "busca trabalho sozinho"), ("horas", "⏰", "olha e-mail e agenda a cada 3 h"), ("traz", "📥", "traz o trabalho até você")],
             "monta", "duet-carla.png", "CARLA · COM O DUET",
             [("resumo", "✓ resumo da manhã"), ("escreve", "✓ aprende como ela escreve"), ("organizado", "✓ acorda com o dia organizado")], "trava")
    cena.final(falas[ordem[5]], total)
    pal = []
    for s in seg["segmentos"]:
        for x in falas[s["fala"]].w:
            wd = CORRIGE.get(x["word"].strip(), x["word"].strip())
            if pal and wd[:1] in "-." and len(wd) > 1:
                pal[-1]["word"] += wd; continue
            pal.append({"word": wd, "t": round(s["ini"] + x["start"], 2)})
    leg = P._legenda(cena, pal, total, {"grok": "#e5e7eb", "muse": "#60a5fa", "dots": "#2dd4bf", "duet": "#fb923c",
                                         "falha": "#ff4d4d", "erra": "#ff4d4d", "bugs": "#ff4d4d", "lento": "#ff4d4d", "trava": "#ff4d4d",
                                         "proativo": "#4ade80", "gratuito": "#4ade80", "memoria": "#4ade80"})
    limpo = "limpo" in sys.argv
    if limpo:
        leg = ""
    pip = G.PIP
    av = (f'<div id="avw" style="left:{pip["left"]}px;top:{pip["top"]}px;width:{pip["w"]}px;height:{pip["h"]}px;">'
          f'<video id="av" src="assets/avatar-{V}.mp4" data-start="0" data-duration="{seg["total"]:.2f}" data-track-index="9" data-has-audio="true" data-volume="1" playsinline></video>'
          f'<div class="avtag">Nei Maldaner · INEMA</div></div>')
    if limpo:
        av = ""
        cena.js = [l for l in cena.js if '"#avw"' not in l and '"#legenda"' not in l]
    html = f'''<!doctype html>
<html lang="pt-BR" data-resolution="landscape">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{G.CSS}{P.CSS_EXTRA}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1920" data-height="1080">
 <div id="mapaClip" class="clip full" data-start="0" data-duration="{total:.2f}" data-track-index="0"><div id="cam">{mapa_svg(f)}</div></div>
 {"".join(cena.html)}
 <div id="topo" class="clip full" data-start="0" data-duration="{total:.2f}" data-track-index="8"><div id="marca">INEMA <span>· {f["marca"].split("·")[-1].strip()}</span></div><div id="fonte">{f["fonte"]}</div></div>
 {av}
 <div id="legenda" class="clip full" data-start="0" data-duration="{total:.2f}" data-track-index="10">{leg}</div>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(cena.js)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>'''
    out = AQUI / (f"cena-{V}-limpo" if limpo else f"cena-{V}")
    a = out / "assets"; a.mkdir(parents=True, exist_ok=True)
    for p in (AQUI / "imagens").glob("*.png"):
        shutil.copy2(p, a / p.name)
    fontes = AQUI.parent / "php" / "cena-a" / "assets" / "fonts"
    if fontes.exists() and not (a / "fonts").exists():
        shutil.copytree(fontes, a / "fonts")
    av_src = AQUI / "build" / f"avatar-{V}.mp4"
    if av_src.exists() and not limpo:
        shutil.copy2(av_src, a / f"avatar-{V}.mp4")
    (out / "index.html").write_text(html)
    print(f"ok {out/'index.html'} · {total:.1f} s · {len(cena.js)} eventos")


if __name__ == "__main__":
    main()
