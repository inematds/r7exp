#!/usr/bin/env python3
"""Motor r7exp: ficha.yaml + tempos das falas do avatar → composição HyperFrames (index.html) de uma versão.

Uso: motor/gera.py <pasta-do-completo> <versao>        (ex.: completo a)
Precisa de: <pasta>/ficha.yaml, <pasta>/imagens/*.png, <pasta>/tempos/<fala>.json (palavras do whisper)
e <pasta>/build/avatar-<versao>.mp4 + segmentos.json (feito por motor/monta_avatar.py).
Saída: <pasta>/cena-<versao>/index.html (+ assets ligados).
"""
import json, re, sys, unicodedata, shutil
from pathlib import Path
import yaml

AQUI = Path(__file__).resolve().parent
W, H = 1920, 1080
GX, GY, GS = 40, -10, 0.88          # mapa: translate(GX,GY) scale(GS) no viewBox 0 0 1920 1080
PIP = dict(left=36, top=684, w=320, h=360)          # mesma proporção da meia tela (960x1080)     # avatar no canto inferior esquerdo
MEIA = dict(left=960, top=0, w=960, h=1080)    # avatar em meia tela (D8: nunca tela cheia)


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


class Fala:
    def __init__(self, nome, palavras, ini):
        self.nome, self.w, self.ini = nome, palavras, ini
        self.cur = 0.0

    def t(self, palavra, depois=None, obrig=True):
        """tempo absoluto da 1ª ocorrência de `palavra` depois de `depois` (absoluto) ou do cursor do bloco"""
        base = (depois - self.ini) if depois is not None else self.cur
        alvo = norm(palavra)
        for exato in (True, False):
            for x in self.w:
                if x["start"] + 1e-3 < base:
                    continue
                n = norm(x["word"])
                if (n == alvo) if exato else n.startswith(alvo):
                    self.cur = x["start"]
                    return round(self.ini + x["start"], 2)
        if obrig:
            raise SystemExit(f"âncora '{palavra}' não achada em {self.nome} depois de {base:.2f}s")
        return None

    @property
    def fim(self):
        return round(self.ini + self.w[-1]["end"], 2)


# ---------------------------------------------------------------- geometria do mapa
def gx(x): return GX + x * GS
def gy(y): return GY + y * GS


def mapa_svg(f):
    L = f["mapa"]["linhas"]
    grade = "".join(f'<path d="M220,{y} H1700"/>' for y in range(160, 900, 80)) + \
            "".join(f'<path d="M{x},160 V900"/>' for x in range(300, 1701, 100))
    linhas = ""
    for k, l in L.items():
        tr = ' stroke-dasharray="4 14" stroke-linecap="round" mask="url(#mU)"' if l.get("pontilhada") else ""
        linhas += (f'<g id="g{k}" class="linha"><path id="l{k}" d="{l["d"]}" stroke="{l["cor"]}" stroke-width="7" fill="none" filter="url(#glow)"{tr}/>'
                   f'<text id="t{k}" class="lbl" x="1700" y="{l["y"]}" text-anchor="end" fill="{l["cor"]}">{l["nome"]}</text></g>')
    U = L["U"]["d"]
    return f'''
<svg id="mapa" width="1920" height="1080" viewBox="0 0 1920 1080">
 <defs>
  <filter id="glow" filterUnits="userSpaceOnUse" x="-200" y="-200" width="2400" height="1600"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <mask id="mU" maskUnits="userSpaceOnUse"><path id="uMask" d="{U}" stroke="#fff" stroke-width="30" fill="none"/></mask>
  <marker id="ah" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#fff"/></marker>
  <marker id="ahy" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#FACC15"/></marker>
 </defs>
 <g transform="translate({GX},{GY}) scale({GS})">
  <g stroke="#1d1d26" stroke-width="2">{grade}</g>
  <path d="M220,900 V150" stroke="#fff" stroke-width="4" marker-end="url(#ah)"/>
  <path d="M220,900 H1720" stroke="#fff" stroke-width="4"/>
  <text class="axis" transform="translate(170,530) rotate(-90)" text-anchor="middle">LIBERDADE E SOBREVIVÊNCIA</text>
  <text class="axis" x="560" y="955" text-anchor="middle">PASSADO</text>
  <text class="axis" x="760" y="955" text-anchor="middle">2026</text><text class="axis" x="920" y="955" text-anchor="middle">2030</text>
  <text class="axis" x="1300" y="955" text-anchor="middle">2040</text><text class="axis" x="1700" y="955" text-anchor="middle">2050</text>
  <g id="hoje" opacity="0"><path d="M760,680 H1700" stroke="#9a9aa6" stroke-width="3" stroke-dasharray="10 10"/><text x="1700" y="712" text-anchor="end" fill="#9a9aa6" font-size="26">NÍVEL DE HOJE</text></g>
  <path id="lHist" d="M220,680 L760,680" stroke="#5ad1f0" stroke-width="7" fill="none" filter="url(#glow)"/>
  <text id="tHist" x="250" y="728" fill="#5ad1f0" class="lbl" opacity="0">200 MIL ANOS DE HISTÓRIA</text>
  <g id="marcos" font-size="44"><text id="m1" x="330" y="660" opacity="0">⚔️</text><text id="m2" x="480" y="660" opacity="0">🏛️</text><text id="m3" x="630" y="660" opacity="0">💡</text></g>
  {linhas}
  <g id="aqui" opacity="0"><text x="610" y="500" text-anchor="middle" fill="#fff" font-size="40">ESTAMOS AQUI</text>
   <path d="M600,520 C590,580 640,640 728,668" stroke="#fff" stroke-width="5" fill="none" marker-end="url(#ah)"/></g>
  <circle id="dot" cx="760" cy="680" r="17" fill="#fff" filter="url(#glow)" opacity="0"/>
  <g id="sobe" opacity="0"><path d="M900,600 L900,540" stroke="#e052e6" stroke-width="5" marker-end="url(#ah)"/><text x="900" y="520" text-anchor="middle" fill="#fff" font-size="30">SOBE: PARECE MELHOR</text></g>
  <g id="acomoda" opacity="0"><text x="1380" y="590" text-anchor="middle" fill="#fff" font-size="30">…E SE ACOMODA PERTO DE HOJE</text></g>
  <g id="empurra" opacity="0"><path id="pEmp" d="M1250,840 C1290,700 1300,520 1290,300" stroke="#FACC15" stroke-width="12" fill="none" stroke-linecap="round" marker-end="url(#ahy)"/></g>
 </g>
</svg>'''


def fim_linha(k, f):
    """ponto final (x,y) da linha no ecrã"""
    d = f["mapa"]["linhas"][k]["d"]
    nums = re.findall(r"-?\d+(?:\.\d+)?", d)
    return gx(float(nums[-2])), gy(float(nums[-1]))


def y_linha_meio(k, f):
    """y aproximado da linha em x≈1200 (para a câmera)"""
    return {"U": 360, "P": 350, "G": 520, "Z": 650, "E": 860}[k]


# ---------------------------------------------------------------- montagem
class Cena:
    def __init__(self, f, versao, pasta):
        self.f, self.v, self.p = f, versao, pasta
        self.html, self.js = [], []
        self.n = 0

    def id(self, pre):
        self.n += 1
        return f"{pre}{self.n}"

    def clip(self, ini, fim, corpo, track, cls="scene", extra=""):
        i = self.id("c")
        self.html.append(f'<div id="{i}" class="clip {cls}" data-start="{ini:.2f}" data-duration="{max(0.1, fim - ini):.2f}" data-track-index="{track}" {extra}>{corpo}</div>')
        return i

    def a(self, s):
        self.js.append(s)

    def entra(self, sel, t, d=0.45, dy=24, ease="back.out(2)"):
        self.a(f'tl.fromTo({json.dumps(sel)}, {{opacity:0, y:{dy}}}, {{opacity:1, y:0, duration:{d}, ease:"{ease}"}}, {t:.2f});')

    def cena_in_out(self, inner, ini, fim, fade=0.5):
        self.a(f'tl.fromTo("#{inner}", {{opacity:0}}, {{opacity:1, duration:{fade}}}, {ini:.2f});')
        self.a(f'tl.to("#{inner}", {{opacity:0, duration:{fade}}}, {max(ini + fade, fim - fade):.2f});')

    # --- câmera do mapa
    def foco(self, k, t, outras=0.15, z=1.16):
        f = self.f
        ks = [x for x in f["mapa"]["linhas"] if x != k]
        oy = gy(y_linha_meio(k, f))
        self.a(f'tl.to({json.dumps(["#g" + x for x in ks])}, {{opacity:{outras}, duration:0.6}}, {t:.2f});')
        self.a(f'tl.to("#g{k}", {{opacity:1, duration:0.6}}, {t:.2f});')
        self.a(f'tl.to("#l{k}", {{attr:{{"stroke-width":11}}, duration:0.6}}, {t:.2f});')
        self.a(f'tl.to({json.dumps(["#l" + x for x in ks])}, {{attr:{{"stroke-width":7}}, duration:0.6}}, {t:.2f});')
        self.a(f'tl.to("#cam", {{scale:{z}, transformOrigin:"1150px {oy:.0f}px", duration:1.6, ease:"power2.inOut"}}, {t:.2f});')

    def mapa_inteiro(self, t, outras=1.0):
        ks = list(self.f["mapa"]["linhas"])
        self.a(f'tl.to("#cam", {{scale:1, duration:1.2, ease:"power2.inOut"}}, {t:.2f});')
        self.a(f'tl.to({json.dumps(["#g" + x for x in ks])}, {{opacity:{outras}, duration:0.6}}, {t:.2f});')
        self.a(f'tl.to({json.dumps(["#l" + x for x in ks])}, {{attr:{{"stroke-width":7}}, duration:0.6}}, {t:.2f});')

    def esconde_mapa(self, ini, fim):
        """o mapa some enquanto uma cena opaca o cobre (evita texto oculto no check)"""
        self.a(f'tl.set("#cam", {{opacity:0}}, {ini + 0.6:.2f}); tl.set("#cam", {{opacity:1}}, {fim - 0.6:.2f});')

    # --- peças
    def foto(self, ini, fim, img, carimbo=None, sub=None, revela=False, img2=None, t2=None, track=3):
        inner = self.id("in")
        r = ' style="clip-path:circle(0% at 44% 38%);"' if revela else ""
        corpo = f'<div class="in" id="{inner}"><div class="full ovh" id="{inner}r"{r}><img class="foto" id="{inner}f" src="assets/{img}" alt=""/><div class="grad"></div></div>'
        if img2:
            corpo += f'<div class="full ovh" id="{inner}b" style="opacity:0"><img class="foto" id="{inner}f2" src="assets/{img2}" alt=""/><div class="grad"></div></div>'
        if carimbo:
            corpo += f'<div class="stamp"><small>{sub or "A MESMA ANA"}</small><span>{carimbo}</span></div>'
        corpo += "</div>"
        self.clip(ini, fim, corpo, track)
        self.cena_in_out(inner, ini, fim)
        self.esconde_mapa(ini, fim)
        if revela:
            self.a(f'tl.set("#{inner}", {{opacity:1}}, {ini:.2f});')
            self.a(f'tl.to("#{inner}r", {{clipPath:"circle(120% at 44% 38%)", duration:1.6, ease:"power2.inOut"}}, {ini:.2f});')
        fim2 = t2 if img2 and t2 else fim
        self.a(f'tl.fromTo("#{inner}f", {{scale:1.0}}, {{scale:1.07, duration:{fim2 - ini + 0.8:.2f}, ease:"none"}}, {ini:.2f});')
        if img2 and t2:
            self.a(f'tl.to("#{inner}b", {{opacity:1, duration:0.9}}, {t2:.2f});')
            self.a(f'tl.fromTo("#{inner}f2", {{scale:1.0}}, {{scale:1.06, duration:{fim - t2 + 0.5:.2f}, ease:"none"}}, {t2:.2f});')
        return inner

    def tags(self, F, itens, fim, track=4):
        """pílulas que entram na palavra, coluna à direita"""
        corpo = '<div class="tags">'
        ts = []
        for j, (pal, txt) in enumerate(itens):
            i = self.id("tg")
            cls = "tag bad" if txt.startswith(("✕", "⚠")) else ("tag gold" if txt.startswith("✓") else "tag")
            corpo += f'<div class="{cls}" id="{i}">{txt}</div>'
            ts.append((i, F.t(pal)))
        corpo += "</div>"
        self.clip(ts[0][1] - 0.2, fim, corpo, track, cls="full")
        for i, t in ts:
            self.entra("#" + i, t - 0.1, dy=0)
            self.a(f'tl.fromTo("#{i}", {{x:40}}, {{x:0, duration:0.45, ease:"back.out(2)"}}, {t - 0.1:.2f});')

    def lista(self, F, itens, fim, track=4):
        corpo = '<div class="strip">'
        ts = []
        for pal, kind, txt in itens:
            i = self.id("it")
            ic = {"ok": "✓", "nao": "—", "bad": "✕"}[kind]
            corpo += f'<div class="it {kind}" id="{i}"><i>{ic}</i>{txt}</div>'
            ts.append((i, F.t(pal), kind))
        corpo += "</div>"
        self.clip(ts[0][1] - 0.2, fim, corpo, track, cls="full")
        for i, t, k in ts:
            self.entra("#" + i, t - 0.1)
        bad = [t for _, t, k in ts if k == "bad"]
        if bad:
            self.a(f'tl.to({json.dumps(["#" + i for i, _, k in ts if k != "bad"])}, {{opacity:0.35, duration:0.4}}, {bad[0] + 0.6:.2f});')

    def card_oque(self, F, k, n, itens, ini, fim, track=4):
        L = self.f["mapa"]["linhas"][k]
        corpo = (f'<div class="card oque" style="border-color:{L["cor"]}55"><div class="chip" style="background:{L["cor"]}2e;color:{L["cor"]}">O QUE É</div>'
                 f'<div class="ctit">{L["nome"].capitalize()}</div>')
        ts = []
        for pal, ic, txt in itens:
            i = self.id("r")
            corpo += f'<div class="row" id="{i}"><div class="ic">{ic}</div><div>{txt}</div></div>'
            ts.append((i, F.t(pal)))
        corpo += "</div>"
        c = self.clip(ini, fim, corpo, track, cls="full")
        self.a(f'tl.to("#mapa .lbl", {{opacity:0, duration:0.3}}, {ini - 0.2:.2f}); tl.to("#mapa .lbl", {{opacity:1, duration:0.3}}, {fim:.2f});')
        self.a(f'tl.fromTo("#{c} .card", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:0.5}}, {ini:.2f});')
        self.a(f'tl.to("#{c} .card", {{opacity:0, duration:0.4}}, {fim - 0.4:.2f});')
        for i, t in ts:
            self.a(f'tl.fromTo("#{i}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {t - 0.1:.2f});')

    def cadeia(self, F, nos, img, ini, fim, cor="#FACC15", risco=None, track=5, nome=""):
        inner = self.id("in")
        n = len(nos); larg = 380 if n <= 3 else 330; gap = 70
        tot = n * larg + (n - 1) * gap; x0 = (W - tot) // 2 + 100
        corpo = (f'<div class="in opaque" id="{inner}"><img class="foto" src="assets/{img}" alt="" style="opacity:.2;filter:blur(6px)"/>'
                 f'<div class="chip" style="position:absolute;left:{x0}px;top:220px;background:rgba(250,204,21,.16);color:#FACC15">O QUE LEVA ATÉ LÁ{(" · " + nome) if nome else ""}</div>')
        ts = []
        for j, (pal, t1, t2) in enumerate(nos):
            i = self.id("no"); x = x0 + j * (larg + gap)
            corpo += f'<div class="node" id="{i}" style="left:{x}px;width:{larg}px"><div class="n">{"RESULTADO" if j == n - 1 else f"PASSO {j + 1}"}</div><div class="t">{t1}</div><div class="s">{t2}</div></div>'
            if j:
                corpo += f'<svg class="seta" id="{i}s" style="left:{x - gap + 6}px" viewBox="0 0 60 34"><path d="M0,17 H44 M34,5 L52,17 L34,29" stroke="#FACC15" stroke-width="5" fill="none"/></svg>'
            ts.append((i, F.t(pal), j))
        if risco:
            corpo += f'<div class="risco" id="{inner}rk">{risco["texto"]}</div>'
        corpo += "</div>"
        self.clip(ini, fim, corpo, track)
        self.cena_in_out(inner, ini, fim)
        self.esconde_mapa(ini, fim)
        for i, t, j in ts:
            if j:
                self.a(f'tl.fromTo("#{i}s", {{opacity:0.2, x:-10}}, {{opacity:1, x:0, duration:0.4}}, {t - 0.3:.2f});')
            self.a(f'tl.to("#{i}", {{opacity:1, borderColor:"{cor if j == len(ts) - 1 else "#FACC15"}", duration:0.4}}, {t - 0.1:.2f});')
            self.a(f'tl.fromTo("#{i}", {{y:16}}, {{y:0, duration:0.4, ease:"back.out(2)"}}, {t - 0.1:.2f});')
        if risco:
            self.entra(f"#{inner}rk", F.t(risco["de"]) - 0.1)

    def massa(self, F, itens, ini, fim, fecho=None, track=6, muitos=False, nome=""):
        """multidão de pontos cinza; um (ou muitos) sai amarelo e sobe; à direita os itens"""
        inner = self.id("in")
        pts = ""
        k = 0
        for r in range(9):
            for c in range(14):
                x, y = 140 + c * 48 + (24 if r % 2 else 0), 330 + r * 52
                cls = "pt"
                if (r, c) == (4, 7) or (muitos and (r * 14 + c) % 9 == 4):
                    cls = "pt sai"
                pts += f'<circle class="{cls}" cx="{x}" cy="{y}" r="13"/>'
                k += 1
        corpo = (f'<div class="in opaque" id="{inner}"><svg class="multi" width="900" height="1080" viewBox="0 0 900 1080">{pts}</svg>'
                 f'<div class="mtit"><span class="chip" style="background:rgba(74,222,128,.16);color:#4ade80">COMO NÃO SER A MASSA{(" · " + nome) if nome else ""}</span></div>')
        ts = []
        if itens:
            corpo += '<div class="mlist">'
            for j, (pal, txt) in enumerate(itens):
                i = self.id("m")
                corpo += f'<div class="mi" id="{i}"><b>{j + 1}</b><span>{txt}</span></div>'
                ts.append((i, F.t(pal)))
            corpo += "</div>"
        if fecho:
            corpo += f'<div class="mfecho" id="{inner}fx"><div>{fecho["a"]}</div><div style="color:#FACC15">{fecho["b"]}</div></div>'
        corpo += "</div>"
        self.clip(ini, fim, corpo, track)
        self.cena_in_out(inner, ini, fim)
        self.esconde_mapa(ini, fim)
        self.a(f'tl.fromTo("#{inner} .pt", {{opacity:0}}, {{opacity:1, duration:0.4, stagger:0.004}}, {ini:.2f});')
        self.a(f'tl.to("#{inner} .sai", {{fill:"#FACC15", y:-60, duration:0.8, ease:"back.out(2)", stagger:0.03}}, {ini + 0.9:.2f});')
        for i, t in ts:
            self.a(f'tl.fromTo("#{i}", {{opacity:0, x:50}}, {{opacity:1, x:0, duration:0.45, ease:"back.out(2)"}}, {t - 0.1:.2f});')
        if fecho:
            tf = F.t(fecho["de"]) - 1.2
            self.a(f'tl.to("#{inner} .mlist", {{opacity:0.25, duration:0.3}}, {tf:.2f});')
            self.entra(f"#{inner}fx", tf)

    def titulo_caminho(self, k, n, ini, fim, track=7):
        L = self.f["mapa"]["linhas"][k]
        corpo = (f'<div class="tcam" id="tc{k}"><span class="chip" style="background:{L["cor"]};color:#0c0c10">CAMINHO {n}</span>'
                 f'<div class="tnome" style="color:{L["cor"]}">{L["nome"]}</div></div>')
        c = self.clip(ini, fim, corpo, track, cls="full")
        self.a(f'tl.fromTo("#tc{k}", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.5}}, {ini:.2f});')
        self.a(f'tl.to("#tc{k} .tnome", {{scale:0.5, transformOrigin:"0 0", duration:0.6}}, {ini + 2.6:.2f});')
        self.a(f'tl.to("#tc{k}", {{opacity:0, duration:0.4}}, {fim - 0.4:.2f});')

    # ------------------------------------------------------------ blocos
    def abertura(self, F, ab):
        f = self.f
        t_capa = F.t(ab["capa_ate"]) - 0.15
        inner = self.id("in")
        self.clip(0, t_capa + 0.6, f'<div class="in" id="{inner}" style="opacity:1"><img class="foto" id="{inner}f" src="assets/{ab["capa"]}" alt="capa"/></div>', 3)
        self.a(f'tl.fromTo("#{inner}f", {{scale:1.0}}, {{scale:1.05, duration:{t_capa + 0.6:.2f}, ease:"none"}}, 0);')
        self.a(f'tl.to("#{inner}", {{opacity:0, duration:0.6}}, {t_capa:.2f});')
        self.esconde_mapa(-1, t_capa + 0.6)
        self.a(f'tl.set("#avw", {{opacity:0}}, 0); tl.to("#avw", {{opacity:1, duration:0.5}}, {min(3.2, t_capa):.2f});')
        m = ab["mapa"]
        cur = t_capa
        if "ai2027" in ab:                                   # versão b: AI 2027 + Stanford antes do mapa
            a7 = ab["ai2027"]; ts_ = F.t(ab["stanford"]["de"]); F.cur = t_capa - F.ini
            i2 = self.id("in")
            corpo = (f'<div class="in opaque" id="{i2}"><div class="a27"><div class="chip" style="background:rgba(250,204,21,.16);color:#FACC15">UM CENÁRIO</div>'
                     f'<div class="a27t">{a7["titulo"]}</div><div class="a27s">{a7["sub"]}</div>'
                     f'<div class="tl27"><div class="tlb"><div class="tlf" id="{i2}tf"></div></div><span style="left:0">2025</span><span style="left:47%">2026</span><span style="left:94%">2027</span></div>')
            its = []
            for pal, ic, txt in a7["itens"]:
                j = self.id("a"); corpo += f'<div class="row27" id="{j}"><div class="ic">{ic}</div><div>{txt}</div></div>'; its.append((j, F.t(pal)))
            corpo += f'<div class="ress" id="{i2}rs">⚠ {a7["ressalva"]["texto"]}</div></div></div>'
            self.clip(cur, ts_ + 0.3, corpo, 4)
            self.cena_in_out(i2, cur, ts_ + 0.3)
            self.esconde_mapa(cur, ts_)
            self.a(f'tl.fromTo("#{i2}tf", {{width:"0%"}}, {{width:"100%", duration:{max(1.0, its[0][1] - cur - 0.2):.2f}, ease:"power1.inOut"}}, {cur + 0.3:.2f});')
            for j, t in its:
                self.a(f'tl.fromTo("#{j}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {t - 0.1:.2f});')
            self.entra(f"#{i2}rs", F.t(a7["ressalva"]["de"]) - 0.1)
            self.meia(cur + 0.2, ts_)
            st = ab["stanford"]; ta = F.t(m["abre"])
            i3 = self.id("in")
            corpo = (f'<div class="in opaque" id="{i3}"><div class="stf"><div class="chip" style="background:rgba(255,77,77,.16);color:#ff6b6b">JÁ COMEÇOU</div>'
                     f'<div class="stn"><span><i id="{i3}n" style="font-style:normal">0</i>%</span>{st["unid"]}</div><div class="stl">{st["l"]}</div><div class="stfo">fonte: {st["fonte"]}</div></div></div>')
            self.clip(ts_, ta + 0.2, corpo, 4)
            self.cena_in_out(i3, ts_, ta + 0.2)
            self.esconde_mapa(ts_, ta)
            self.a(f'(()=>{{const o={{v:0}}; tl.to(o, {{v:{st["ate"]}, duration:1.4, ease:"power2.out", onUpdate:()=>{{document.getElementById("{i3}n").textContent=Math.round(o.v)}}}}, {ts_ + 0.3:.2f});}})();')
            # mapa: história rápida + 5 linhas na palavra "caminhos"
            self.desenha_hist(ta - 1.6, 1.4)
            self.a(f'tl.fromTo("#dot", {{opacity:0, attr:{{r:4}}}}, {{opacity:1, attr:{{r:17}}, duration:0.4}}, {ta - 0.3:.2f});')
            self.desenha_linhas(ta)
            cur = ta
        else:
            tg = F.t(m["agora"]); F.cur = t_capa - F.ini
            self.desenha_hist(t_capa + 0.4, tg - t_capa - 0.6)
            for j, pal in enumerate(["guerras", "imperios", "invencoes"]):
                t = F.t(pal, obrig=False)
                if t:
                    self.a(f'tl.fromTo("#m{j + 1}", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.4, ease:"back.out(3)"}}, {t:.2f});')
            self.a(f'tl.to("#marcos", {{opacity:0, duration:0.6}}, {tg + 0.8:.2f});')
            self.a(f'tl.fromTo("#dot", {{opacity:0, attr:{{r:4}}}}, {{opacity:1, attr:{{r:17}}, duration:0.5, ease:"back.out(3)"}}, {tg:.2f});')
            self.a(f'tl.fromTo("#aqui", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.6}}, {tg + 0.4:.2f});')
            F.cur = tg - F.ini
            self.desenha_linhas(F.t(m["abre"]))
            c = ab["card"]; tc = F.t(c["de"]) - 0.2; tan = F.t(ab["ana"]["de"], depois=tc)
            i2 = self.id("in")
            corpo = (f'<div class="in opaque" id="{i2}"><div class="tegm"><div class="chip" style="background:rgba(250,204,21,.16);color:#FACC15">{c["chip"]}</div>'
                     f'<div class="a27t" style="font-size:72px">{c["titulo"]}</div><div class="a27s">{c["sub"]}</div>'
                     f'<div class="mini5">' + "".join(f'<span style="background:{l["cor"]}"></span>' for l in f["mapa"]["linhas"].values()) + '</div></div></div>')
            self.clip(tc, tan + 0.3, corpo, 4)
            self.cena_in_out(i2, tc, tan + 0.3)
            self.esconde_mapa(tc, tan)
            self.meia(tc + 0.2, tan)
            F.cur = tan - F.ini - 0.05
            cur = tc
        # Ana 2026
        an = ab["ana"]; ta = F.t(an["de"]); tp = F.t(ab["pre"]["de"])
        self.foto(ta - 0.2, tp + 0.2, "ana-2026.png", carimbo="ANA · 2026", sub="A PERSONAGEM")
        F.cur = ta - F.ini
        self.tags(F, an["tags"], tp + 0.2)
        # prévia: mapa inteiro com "?" + Ana no ponto 2026
        tpi = F.t(ab["pior"], depois=tp)
        self.mapa_inteiro(tp, 0.55)
        corpo = '<div class="full">'
        for k in f["mapa"]["linhas"]:
            x, y = fim_linha(k, f)
            corpo += f'<div class="q" style="left:{x + 18:.0f}px;top:{y - 48:.0f}px">?</div>'
        corpo += f'<div class="ban" id="ban1">{ab["pre"]["texto"]}</div>'
        if "massa" in ab:
            corpo += f'<div class="ban" id="ban2" style="opacity:0">{ab["massa"]["texto"]}</div>'
        corpo += '</div>'
        c = self.clip(tp, tpi + 0.8, corpo, 5, cls="full")
        self.a(f'tl.fromTo("#{c} .q", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.4, stagger:0.12, ease:"back.out(2)"}}, {tp + 0.3:.2f});')
        self.entra("#ban1", tp + 0.2)
        if "massa" in ab:
            tm = F.t(ab["massa"]["de"], depois=tp)
            self.a(f'tl.to("#ban1", {{opacity:0, duration:0.3}}, {tm - 1.2:.2f});')
            self.entra("#ban2", tm - 1.0)
        self.a(f'tl.to("#{c}", {{opacity:0, duration:0.5}}, {tpi + 0.2:.2f});')
        self.foco("E", tpi, outras=0.15)

    def desenha_hist(self, t, d):
        self.a(f'(()=>{{const p=document.getElementById("lHist"),L=p.getTotalLength(); tl.fromTo(p,{{strokeDasharray:L,strokeDashoffset:L}},{{strokeDashoffset:0,duration:{max(0.8, d):.2f},ease:"power1.inOut"}},{t:.2f});}})();')
        self.a(f'tl.fromTo("#tHist", {{opacity:0}}, {{opacity:1, duration:0.5}}, {t + 0.6:.2f});')

    def desenha_linhas(self, t):
        for j, k in enumerate(["U", "P", "G", "Z", "E"]):
            alvo = "uMask" if k == "U" else "l" + k
            self.a(f'(()=>{{const p=document.getElementById("{alvo}"),L=p.getTotalLength(); tl.fromTo(p,{{strokeDasharray:L,strokeDashoffset:L}},{{strokeDashoffset:0,duration:1.5,ease:"power2.out"}},{t - 0.2 + j * 0.25:.2f});}})();')
            self.a(f'tl.fromTo("#t{k}", {{opacity:0, x:20}}, {{opacity:1, x:0, duration:0.5}}, {t + 0.6 + j * 0.25:.2f});')

    def meia(self, ini, fim):
        """avatar cresce para meia tela à direita e volta ao canto"""
        a, b = MEIA, PIP
        k = a["w"] / b["w"]
        self.a(f'tl.to("#avw", {{x:{a["left"] - b["left"]}, y:{a["top"] - b["top"]}, scale:{k:.3f}, transformOrigin:"0 0", duration:0.7, ease:"power2.inOut"}}, {ini:.2f});')
        self.a(f'tl.to("#avw", {{x:0, y:0, scale:1, duration:0.7, ease:"power2.inOut"}}, {fim - 0.7:.2f});')
        self.a(f'tl.to("#legenda", {{x:-480, duration:0.5}}, {ini:.2f}); tl.to("#legenda", {{x:0, duration:0.5}}, {fim - 0.5:.2f});')

    def caminho(self, F, c, prox):
        f = self.f; k = c["id"]
        t0 = F.ini
        tq = F.t(c["o_que_e"]["de"]) if c["o_que_e"]["de"] else t0
        self.foco(k, t0 - 0.4)
        tv = F.t(c["vive"]["de"], depois=tq)
        self.titulo_caminho(k, c["n"], t0, tv)
        F.cur = tq - F.ini
        self.card_oque(F, k, c["n"], c["o_que_e"]["itens"], tq + 0.3, tv - 0.1)
        v = c["vive"]
        # fim do "vive": nota no mapa (zoo) ou "leva"
        tn = F.t(c["nota_mapa"]["de"], depois=tv) if c.get("nota_mapa") else None
        tl_ = F.t(c["leva"]["de"], depois=tv)
        fim_v = tn or tl_
        F.cur = tv - F.ini
        if v.get("lista"):
            t2 = F.t(v["lista"][-1][0], depois=tv) + 1.6 if v.get("imagem2") else None
        else:
            t2 = (F.t(v["tags"][-1][0], depois=tv) + 1.4) if v.get("imagem2") else None
        F.cur = tv - F.ini
        self.foto(tv - 0.2, fim_v + 0.2, v["imagem"], carimbo=v["carimbo"], revela=v.get("revela"), img2=v.get("imagem2"), t2=t2)
        F.cur = tv - F.ini
        if v.get("lista"):
            self.lista(F, v["lista"], fim_v + 0.2)
        else:
            self.tags(F, v["tags"], fim_v + 0.2)
        if tn:
            nm = c["nota_mapa"]
            ts, ta_, tc = F.t(nm["sobe"], depois=tn), F.t(nm["acomoda"], depois=tn), F.t(nm["medidor"], depois=tn)
            self.a(f'tl.set(["#tHist","#aqui","#marcos"], {{opacity:0}}, {tn - 0.5:.2f});')
            self.a(f'tl.fromTo("#sobe", {{opacity:0}}, {{opacity:1, duration:0.4}}, {ts - 0.1:.2f});')
            self.a(f'tl.fromTo("#hoje", {{opacity:0}}, {{opacity:1, duration:0.5}}, {ta_ - 0.6:.2f});')
            self.a(f'tl.fromTo("#acomoda", {{opacity:0}}, {{opacity:1, duration:0.5}}, {ta_ - 0.1:.2f});')
            self.a(f'tl.to(["#acomoda","#sobe"], {{opacity:0, duration:0.3}}, {tc - 0.4:.2f});')
            corpo = ('<div class="card meter"><div class="blab"><span style="color:#4ade80">CONFORTO</span><span style="color:#4ade80">ALTO</span></div>'
                     '<div class="bar"><div class="bC" style="background:#4ade80"></div></div><div class="blab"><span style="color:#ff4d4d">LIBERDADE</span><span style="color:#ff4d4d">BAIXA</span></div>'
                     '<div class="bar"><div class="bL" style="background:#ff4d4d"></div></div><div class="neq">Conforto <span style="color:#FACC15">≠</span> liberdade</div></div>')
            cm = self.clip(tc - 0.2, tl_ + 0.1, corpo, 4, cls="full")
            self.a(f'tl.fromTo("#{cm} .meter", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.5}}, {tc - 0.2:.2f});')
            self.a(f'tl.fromTo("#{cm} .bC", {{width:"0%"}}, {{width:"92%", duration:0.8}}, {tc:.2f});')
            self.a(f'tl.fromTo("#{cm} .bL", {{width:"0%"}}, {{width:"18%", duration:0.8}}, {tc + 0.7:.2f});')
            self.a(f'tl.fromTo("#{cm} .neq", {{opacity:0}}, {{opacity:1, duration:0.4}}, {tc + 1.2:.2f});')
            self.a(f'tl.to(["#hoje"], {{opacity:0, duration:0.3}}, {tl_:.2f});')
        tm = F.t(c["massa"]["de"], depois=tl_)
        F.cur = tl_ - F.ini
        lv = c["leva"]
        self.cadeia(F, lv["nos"], lv["imagem"], tl_ - 0.2, tm + 0.1, cor=f["mapa"]["linhas"][k]["cor"], risco=lv.get("risco"), nome=f["mapa"]["linhas"][k]["nome"])
        F.cur = tm - F.ini
        ms = c["massa"]
        self.massa(F, ms["itens"], tm - 0.2, prox - 0.1, fecho=ms.get("fecho"), nome=f["mapa"]["linhas"][k]["nome"])

    def final(self, F, fn, fim_total):
        f = self.f
        t0 = F.ini
        self.mapa_inteiro(t0 - 0.5, 1.0)
        tf = F.t(fn["frase"]["de"])
        # comparação: 5 Anas lado a lado
        imgs = [("E", "extincao-casa.png"), ("Z", "ana-2040-zoo.png"), ("G", "governo-ana.png"), ("P", "paraiso-ana.png"), ("U", "utopia-ana.png")]
        inner = self.id("in")
        corpo = f'<div class="in opaque" id="{inner}"><div class="cmp">'
        for k, im in imgs:
            L = f["mapa"]["linhas"][k]
            corpo += f'<div class="cc" style="border-top:8px solid {L["cor"]}"><img src="assets/{im}" alt=""/><span style="color:{L["cor"]}">{L["nome"]}</span></div>'
        corpo += f'</div><div class="frase" id="{inner}fr"><div>{fn["frase"]["a"]}</div><div style="color:#FACC15">{fn["frase"]["b"]}</div></div></div>'
        tp = F.t(fn["passos"]["de"], depois=tf)
        self.clip(t0, tp + 0.2, corpo, 4)
        self.cena_in_out(inner, t0, tp + 0.2)
        self.esconde_mapa(t0, tp)
        self.a(f'tl.fromTo("#{inner} .cc", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.5, stagger:0.25, ease:"back.out(2)"}}, {t0 + 0.2:.2f});')
        self.a(f'tl.to("#{inner} .cmp", {{opacity:0.25, duration:0.5}}, {tf - 1.6:.2f});')
        self.entra(f"#{inner}fr", tf - 1.5)
        # passos
        tmz = F.t(fn["massa"]["de"], depois=tp)
        F.cur = tp - F.ini
        i2 = self.id("in")
        corpo = f'<div class="in opaque" id="{i2}"><div class="chip" style="position:absolute;left:120px;top:150px;background:rgba(74,222,128,.16);color:#4ade80">COMO SE PREPARAR, HOJE</div><div class="passos">'
        ts = []
        for pal, num, txt in fn["passos"]["itens"]:
            j = self.id("p"); corpo += f'<div class="ps" id="{j}"><b>{num}</b><span>{txt}</span></div>'; ts.append((j, F.t(pal)))
        corpo += "</div></div>"
        self.clip(tp, tmz + 0.2, corpo, 5)
        self.cena_in_out(i2, tp, tmz + 0.2)
        self.esconde_mapa(tp, tmz)
        for j, t in ts:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:0.45, ease:"back.out(2)"}}, {t - 0.15:.2f});')
            self.a(f'tl.to("#{j} b", {{backgroundColor:"#4ade80", duration:0.3}}, {t + 0.3:.2f});')
        # massa → desenhar a linha (mapa) → CTA
        td = F.t("desenhar", depois=tmz)
        F.cur = tmz - F.ini
        self.massa(F, [], tmz - 0.2, td + 0.1, fecho={"de": "desenhar", "a": fn["massa"]["a"], "b": fn["massa"]["b"]}, muitos=True)
        tq = F.t(fn["cta"]["de"], depois=td) if F.t(fn["cta"]["de"], depois=td, obrig=False) else td + 3
        self.mapa_inteiro(td - 0.2, 1.0)
        self.a(f'tl.fromTo("#empurra", {{opacity:0}}, {{opacity:1, duration:0.3}}, {td:.2f});')
        self.a(f'(()=>{{const p=document.getElementById("pEmp"),L=p.getTotalLength(); tl.fromTo(p,{{strokeDasharray:L,strokeDashoffset:L}},{{strokeDashoffset:0,duration:1.0,ease:"power2.out"}},{td + 0.1:.2f});}})();')
        self.a(f'tl.to(["#gE","#gZ"], {{opacity:0.25, duration:0.6}}, {td + 0.6:.2f});')
        tq0 = F.t("futuros", depois=td, obrig=False) or tq
        i3 = self.id("in")
        corpo = (f'<div class="in" id="{i3}"><div class="full" style="background:rgba(12,12,16,.88)"></div><div class="fim"><h2>{fn["cta"]["pergunta"]}</h2>'
                 f'<div class="sub">comenta aqui 👇</div><div class="pill" id="{i3}p">inema.club</div></div>'
                 f'<div class="printc" id="{i3}pr"><img src="assets/print-guia.png" alt="guia sobreviver-ia"/><span>kit aberto · inema.club</span></div></div>')
        tclub = F.t("inema", depois=td, obrig=False) or tq + 2
        self.clip(tq0 - 0.4, fim_total, corpo, 6)
        self.a(f'tl.fromTo("#{i3}", {{opacity:0}}, {{opacity:1, duration:0.6}}, {tq0 - 0.4:.2f});')
        self.entra(f"#{i3}p", tclub - 0.1)
        self.a(f'tl.fromTo("#{i3}pr", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.6, ease:"back.out(2)"}}, {tclub:.2f});')


CSS = (AQUI / "estilo.css").read_text() if (AQUI / "estilo.css").exists() else ""


def legenda(cena, palavras, fim_total):
    KEY = {"extincao": "#ff4d4d", "zoologico": "#e052e6", "governo": "#facc15", "paraiso": "#4ade80", "utopia": "#a78bfa",
           "massa": "#FACC15", "decide": "#FACC15", "escolha": "#ff4d4d", "liberdade": "#ff4d4d"}
    grupos, g = [], []
    for i, w in enumerate(palavras):
        g.append(w); nx = palavras[i + 1] if i + 1 < len(palavras) else None
        if len(g) == 3 or re.search(r"[.,:?!]$", w["word"].strip()) or not nx or nx["t"] - w["t"] > 0.9:
            grupos.append(g); g = []
    html = []
    for k, gr in enumerate(grupos):
        ini = gr[0]["t"] - 0.05
        prox = grupos[k + 1][0]["t"] - 0.05 if k + 1 < len(grupos) else fim_total
        fim = min(prox, gr[-1]["t"] + 1.4)
        spans = " ".join(f'<b data-t="{w["t"]:.2f}">{re.sub(r"[.,:]$", "", w["word"].strip())}</b>' for w in gr)
        i = f"cap{k}"
        html.append(f'<div class="cap" id="{i}">{spans}</div>')
        cena.a(f'tl.set("#{i}", {{opacity:1}}, {ini:.2f}); tl.set("#{i}", {{opacity:0}}, {fim:.2f});')
        for j, w in enumerate(gr):
            cor = KEY.get(norm(w["word"]), "#FACC15")
            cena.a(f'tl.set("#{i} b:nth-child({j + 1})", {{color:"{cor}"}}, {w["t"]:.2f}); tl.set("#{i} b:nth-child({j + 1})", {{color:"#fff"}}, {min(fim, w["t"] + 0.45):.2f});')
    return "".join(html)


CORRIGE = {"ia": "IA", "Ia": "IA", "inema.club": "inema.club"}


def main():
    pasta, versao = Path(sys.argv[1]).resolve(), sys.argv[2]
    f = yaml.safe_load((pasta / "ficha.yaml").read_text())
    seg = json.loads((pasta / "build" / f"segmentos-{versao}.json").read_text())
    falas = {}
    for s in seg["segmentos"]:
        w = json.loads((pasta / "tempos" / f"{s['fala']}.json").read_text())
        falas[s["fala"]] = Fala(s["fala"], w, s["ini"])
    total = round(seg["total"] + 0.6, 2)
    cena = Cena(f, versao, pasta)
    ab = f["aberturas"][versao]
    cena.abertura(falas[ab["fala"]], ab)
    cams = f["caminhos"]
    for j, c in enumerate(cams):
        prox = falas[cams[j + 1]["fala"]].ini if j + 1 < len(cams) else falas[f["final"]["fala"]].ini
        cena.caminho(falas[c["fala"]], c, prox)
    cena.final(falas[f["final"]["fala"]], f["final"], total)
    # legenda (todas as falas)
    pal = []
    for s in seg["segmentos"]:
        for x in falas[s["fala"]].w:
            pal.append({"word": CORRIGE.get(x["word"].strip(), x["word"].strip()), "t": round(s["ini"] + x["start"], 2)})
    leg = legenda(cena, pal, total)
    pip = PIP
    av = (f'<div id="avw" style="left:{pip["left"]}px;top:{pip["top"]}px;width:{pip["w"]}px;height:{pip["h"]}px;">'
          f'<video id="av" src="assets/avatar-{versao}.mp4" data-start="0" data-duration="{seg["total"]:.2f}" data-track-index="9" data-has-audio="true" data-volume="1" playsinline></video>'
          f'<div class="avtag">Nei Maldaner · INEMA</div></div>')
    html = f'''<!doctype html>
<html lang="pt-BR" data-resolution="landscape">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
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
    out = pasta / f"cena-{versao}"
    (out / "assets").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"ok {out/'index.html'} · {total:.1f} s · {len(cena.js)} eventos")


if __name__ == "__main__":
    main()
