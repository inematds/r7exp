#!/usr/bin/env python3
"""r7exp vertical (9:16) — "O mar vai subir? Faça a conta comigo" (Thwaites, 21/10/2026).

Primeiro reel r7exp em 1080x1920: diagramas que evoluem na palavra falada (corte da geleira, copos, conta,
escada da praia com a mesma pessoa, curva do mar), painel embaixo à esquerda e avatar do Nei no canto (D8).
Uso: python3 gera_v.py [--falso]      (--falso = tempos inventados a 14 car/s, só para testar o layout)
Precisa: tempos/thwaites.json (whisper, palavras), avatar/avatar.mp4, imagens/*.png. Saída: cena/index.html
"""
import json, re, sys, shutil, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MOTOR = Path.home() / "projetos/r7exp/motor"
W, H = 1080, 1920
STAGE = 1180                        # altura do palco dos diagramas
AV = dict(left=690, top=1300, w=354, h=500)
PAINEL = dict(left=36, top=1300, w=630, h=500)
OUT = AQUI / "cena"

FONTE = "Poinelli et al., Nature Communications (out/2026) · NOAA · BedMachine · IBGE · IPCC/PBMC · foto: Nei Maldaner · ilustrativo"

TROCAS = [
    ("trezentos e sessenta quilômetros cúbicos", "360 km³"), ("sessenta e cinco centímetros", "65 cm"),
    ("cinquenta e oito metros", "58 m"), ("mil oitocentos e oitenta", "1880"), ("dois mil e quatro", "2004"),
    ("dois mil e seis", "2006"), ("dois mil e cem", "2100"), ("dois quilômetros", "2 km"), ("um milímetro", "1 mm"),
    ("três centímetros", "3 cm"), ("vinte centímetros", "20 cm"), ("três metros", "3 m"), ("um metro", "1 metro"),
    ("vinte andares", "20 andares"), ("inema ponto club", "inema.club"), ("inema club", "inema.club"),
    ("360 quilômetros cúbicos", "360 km³"), ("65 centímetros", "65 cm"), ("58 metros", "58 m"), ("3 centímetros", "3 cm"),
    ("20 centímetros", "20 cm"), ("3 metros", "3 m"),
]
COR = {"juizo": "#ff4d4d", "dobrou": "#ff4d4d", "morna": "#ff4d4d", "derrete": "#ff4d4d", "nova": "#ff4d4d",
       "exagero": "#ff4d4d", "comecou": "#ff4d4d", "cidade": "#ff4d4d"}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


# ---------------------------------------------------------------- tempos
def palavras(falso):
    if falso:
        txt = (AQUI / "falas/thwaites.txt").read_text().split()
        t, out = 0.3, []
        for w in txt:
            d = max(0.18, len(w) / 14.5)
            out.append({"word": w, "start": round(t, 2), "end": round(t + d, 2)})
            t += d + (0.35 if re.search(r"[.?:]$", w) else 0.06)
        return out
    w = json.loads((AQUI / "tempos/thwaites.json").read_text())
    return w["words"] if isinstance(w, dict) else w


class Fala:
    def __init__(self, w):
        self.w, self.cur = w, 0.0

    def t(self, pal, obrig=True):
        alvo = norm(pal)
        for exato in (True, False):
            for x in self.w:
                if x["start"] + 1e-3 < self.cur:
                    continue
                n = norm(x["word"])
                if (n == alvo) if exato else n.startswith(alvo):
                    self.cur = x["start"]
                    return round(x["start"], 2)
        if obrig:
            raise SystemExit(f"âncora '{pal}' não achada depois de {self.cur:.2f}s")

    @property
    def fim(self):
        return round(self.w[-1]["end"], 2)


# ---------------------------------------------------------------- composição
class Cena:
    def __init__(self):
        self.html, self.js, self.n = [], [], 0

    def id(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def a(self, s):
        self.js.append(s)

    def clip(self, ini, fim, corpo, track, cls="stage"):
        i = self.id("c")
        self.html.append(f'<div id="{i}" class="clip {cls}" data-start="{ini:.2f}" data-duration="{max(0.1, fim - ini):.2f}" data-track-index="{track}">{corpo}</div>')
        return i

    def fade(self, sel, ini, fim, d=0.4):
        self.a(f'tl.fromTo("{sel}", {{opacity:0}}, {{opacity:1, duration:{d}}}, {ini:.2f});')
        self.a(f'tl.to("{sel}", {{opacity:0, duration:{d}}}, {max(ini + d, fim - d):.2f});')

    def entra(self, sel, t, dy=26, d=0.45):
        self.a(f'tl.fromTo("{sel}", {{opacity:0, y:{dy}}}, {{opacity:1, y:0, duration:{d}, ease:"back.out(2)"}}, {t:.2f});')

    def mostra(self, sel, t, d=0.4):
        self.a(f'tl.fromTo("{sel}", {{opacity:0}}, {{opacity:1, duration:{d}}}, {t:.2f});')

    # --- palco: imagem com movimento lento
    def imagem(self, ini, fim, img, pos="50% 0%", z=1.08, extra=""):
        inner = self.id("im")
        corpo = f'<div class="in" id="{inner}"><img class="foto" id="{inner}f" src="assets/{img}" style="object-position:{pos}" alt=""/><div class="vin"></div>{extra}</div>'
        self.clip(ini, fim, corpo, 2)
        self.fade(f"#{inner}", ini, fim)
        self.a(f'tl.fromTo("#{inner}f", {{scale:1.0}}, {{scale:{z}, duration:{fim - ini + 0.4:.2f}, ease:"none"}}, {ini:.2f});')
        return inner

    def palco(self, ini, fim, corpo, track=2):
        inner = self.id("pl")
        self.clip(ini, fim, f'<div class="in" id="{inner}">{corpo}</div>', track)
        self.fade(f"#{inner}", ini, fim)
        return inner

    # --- painel embaixo à esquerda
    def painel(self, ini, fim, chip, linhas, cor="#FACC15", grande=None):
        """linhas: [(t, html)], grande: (t, html) número grande"""
        inner = self.id("pn")
        corpo = f'<div class="painel" id="{inner}" style="border-color:{cor}66"><div class="chip" style="background:{cor}2e;color:{cor}">{chip}</div>'
        ev = []
        if grande:
            gi = self.id("g")
            corpo += f'<div class="pgr" id="{gi}" style="color:{cor}">{grande[1]}</div>'
            ev.append((gi, grande[0]))
        for t, txt in linhas:
            li = self.id("r")
            corpo += f'<div class="prow" id="{li}">{txt}</div>'
            ev.append((li, t))
        corpo += "</div>"
        fim = fim - 0.3
        self.clip(ini, fim, corpo, 5, cls="full")
        self.a(f'tl.fromTo("#{inner}", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:0.45}}, {ini:.2f});')
        self.a(f'tl.to("#{inner}", {{opacity:0, duration:0.35}}, {fim - 0.35:.2f});')
        for i, t in ev:
            self.entra("#" + i, max(ini + 0.1, t - 0.1))
        return inner


def svg(corpo, vb=f"0 0 {W} {STAGE}"):
    return f'<svg class="dg" width="{W}" height="{STAGE}" viewBox="{vb}">{DEFS}{corpo}</svg>'


DEFS = '''<defs>
 <filter id="glow" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1300" height="1400"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <marker id="ah" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#fff"/></marker>
 <marker id="ahr" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#ff4d4d"/></marker>
 <marker id="ahy" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#FACC15"/></marker>
 <linearGradient id="agua" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b6ea8"/><stop offset="1" stop-color="#0a2740"/></linearGradient>
 <linearGradient id="gelo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f2f8ff"/><stop offset="1" stop-color="#a9cdea"/></linearGradient>
</defs>'''


# ---------------------------------------------------------------- blocos
def bloco_abertura(c, F, fim):
    ini = 0.0
    tD, tC = F.t("desenho"), F.t("conta")
    extra = (f'<div class="chips"><span class="ch" id="chD">✏️ DESENHO</span><span class="ch" id="chC">🧮 CONTA</span></div>')
    c.imagem(ini, fim, "abertura.png", z=1.06, extra=extra)
    c.entra("#chD", tD - 0.1); c.entra("#chC", tC - 0.1)
    tX = F.t("exagero", obrig=False)
    c.painel(ini + 0.2, fim, "A PERGUNTA", [(tD, "✏️ com desenho"), (tC, "🧮 e com conta")],
             cor="#ff4d4d", grande=(ini + 0.3, "É EXAGERO?"))


def bloco_mapa(c, F, ini, fim):
    tT, tP, tD = F.t("Thwaites"), F.t("Paraná"), F.t("dobrou")
    extra = ('<div class="lbl1" id="mT"><b style="color:#ff4d4d">THWAITES</b><br>192 mil km²</div>'
             '<div class="lbl2" id="mP">≈ o <b style="color:#FACC15">PARANÁ</b> inteiro<br><small>199 mil km² · IBGE · mesma escala</small></div>')
    c.imagem(ini, fim, "map-ant-parana-v.png", pos="50% 0%", z=1.05, extra=extra)
    c.entra("#mT", tT); c.entra("#mP", tP)
    c.painel(ini, fim, "ESTUDO NOVO · OUT/2026", [(tD, "contribuição da Thwaites ao mar até 2100"), (tD + 0.6, "<small>Nature Communications · UC Irvine + NASA</small>")],
             cor="#ff4d4d", grande=(tD - 0.2, "1,5 → 3 cm"))


def bloco_corte(c, F, ini, fim):
    tAp, tKm = F.t("apoiada"), F.t("quilômetros")
    tMa, tDe, tSo, tOc = F.t("maré"), F.t("derrete"), F.t("soltando"), F.t("oceano")
    rocha = "M0,960 C120,950 260,880 420,770 C520,820 700,940 1080,1080 L1080,1180 L0,1180 Z"
    gelo = "M420,770 C520,820 700,940 1080,1080 L1200,1130 L1200,180 L1080,200 C860,230 640,280 420,330 Z"
    plataforma = "M300,392 L420,330 L420,770 C390,640 350,520 300,455 Z"
    corpo = svg(f'''
 <text class="t1" x="540" y="150" text-anchor="middle">CORTE DA GELEIRA</text>
 <rect x="0" y="420" width="1080" height="760" fill="url(#agua)"/>
 <g id="nivel"><path d="M0,420 H1080" stroke="#7cc4ff" stroke-width="4" stroke-dasharray="14 10"/><text x="24" y="405" class="t3" fill="#7cc4ff">NÍVEL DO MAR</text></g>
 <path d="{rocha}" fill="#3a2f2a" stroke="#6b5a50" stroke-width="3"/>
 <g id="gl"><path d="{gelo}" fill="url(#gelo)"/><path id="plat" d="{plataforma}" fill="#d8ebfa" opacity=".92"/></g>
 <g id="cApo" opacity="0"><rect x="600" y="515" width="360" height="110" rx="12" fill="#ffffff" opacity=".9"/><text x="780" y="560" class="t2" fill="#0c0c10" text-anchor="middle">GELO APOIADO</text><text x="780" y="605" class="t2" fill="#0c0c10" text-anchor="middle">NA ROCHA</text></g>
 <g id="cPla" opacity="0"><text x="380" y="300" class="t4" fill="#fff" text-anchor="middle">BOIA ↓</text></g>
 <g id="cKm" opacity="0"><path d="M960,430 V1020" stroke="#FACC15" stroke-width="5" marker-end="url(#ahy)" marker-start="url(#ahy)"/>
   <rect x="610" y="900" width="330" height="96" rx="12" fill="#0c0c10" opacity=".85"/><text x="775" y="940" class="t3" fill="#FACC15" text-anchor="middle">LEITO ATÉ</text><text x="775" y="982" class="t3" fill="#FACC15" text-anchor="middle">≈ 2 KM ABAIXO</text></g>
 <g id="cMa" opacity="0"><path id="seta" d="M30,880 C180,870 320,820 430,790 C520,830 600,870 700,905" stroke="#ff4d4d" stroke-width="10" fill="none" stroke-dasharray="26 18" marker-end="url(#ahr)" filter="url(#glow)"/>
   <text x="60" y="840" class="t2" fill="#ff4d4d">ÁGUA MORNA</text><text x="60" y="1080" class="t3" fill="#ffb3b3">a maré bombeia por baixo</text></g>
 <path id="cDe" d="M425,782 C520,832 640,900 760,948" stroke="#ff4d4d" stroke-width="16" fill="none" opacity="0" filter="url(#glow)"/>
 <g id="cPt"><circle id="pt" cx="420" cy="770" r="16" fill="#FACC15" filter="url(#glow)" opacity="0"/></g>
 <g id="cSo" opacity="0"><text x="300" y="1140" class="t3" fill="#FACC15">← o ponto de apoio recua</text></g>
 <g id="cOc" opacity="0"><path d="M120,300 V230" stroke="#7cc4ff" stroke-width="8" marker-end="url(#ah)"/><text x="160" y="270" class="t2" fill="#fff">MAR SOBE</text></g>
''')
    p = c.palco(ini, fim, corpo)
    c.mostra("#cApo", tAp); c.mostra("#cPla", tAp + 0.3); c.mostra("#pt", tAp + 0.3)
    c.mostra("#cKm", tKm - 0.1)
    c.a(f'tl.to("#cKm", {{opacity:0, duration:0.3}}, {tMa - 0.2:.2f});')
    c.mostra("#cMa", tMa - 0.1)
    c.a(f'tl.fromTo("#seta", {{strokeDashoffset:0}}, {{strokeDashoffset:-440, duration:{fim - tMa:.2f}, ease:"none"}}, {tMa:.2f});')
    c.mostra("#cDe", tDe - 0.1)
    c.a(f'tl.to("#cDe", {{opacity:0.35, duration:0.5, repeat:3, yoyo:true}}, {tDe + 0.4:.2f});')
    c.mostra("#cSo", tSo - 0.1)
    c.a(f'tl.to("#pt", {{attr:{{cx:700, cy:905}}, duration:1.8, ease:"power2.inOut"}}, {tSo:.2f});')
    c.a(f'tl.to("#gl", {{x:-70, duration:2.2, ease:"power1.inOut"}}, {tSo + 0.2:.2f});')
    c.mostra("#cOc", tOc - 0.2)
    c.a(f'tl.to("#nivel", {{y:-22, duration:1.0}}, {tOc - 0.2:.2f});')
    c.painel(ini, fim, "COMO ELA DERRETE", [(tMa, "① a maré empurra água morna"), (tDe, "② derrete a base, por baixo"), (tSo, "③ solta da rocha e escorrega")], cor="#ff4d4d")


def copo(x, nome, pedra):
    """copo de 300 x 520 em x; água no y 560"""
    r = (f'<path d="M{x+40},1000 L{x+360},1000 L{x+330},500 L{x+70},500 Z" fill="#3a2f2a" stroke="#6b5a50" stroke-width="3"/>' if pedra else "")
    gelo_y = 410 if pedra else 520
    return f'''
 <g id="{nome}">
  <rect id="{nome}a" x="{x+12}" y="560" width="376" height="440" fill="url(#agua)" opacity=".9"/>
  <path d="M{x+12},560 H{x+388}" stroke="#7cc4ff" stroke-width="3" stroke-dasharray="10 8"/>
  {r}
  <rect id="{nome}g" x="{x+120}" y="{gelo_y}" width="160" height="{90 if pedra else 110}" rx="14" fill="url(#gelo)" stroke="#fff" stroke-width="2"/>
  <path d="M{x},300 L{x+12},1010 L{x+388},1010 L{x+400},300" stroke="#e7eef7" stroke-width="7" fill="none" opacity=".85"/>
 </g>'''


def bloco_copos(c, F, ini, fim):
    tCo, tBo, tRo, tCa, tNo = F.t("copo"), F.t("boia"), F.t("rocha"), F.t("cai"), F.t("nova")
    corpo = svg(f'''
 <text class="t1" x="540" y="150" text-anchor="middle">O QUE SOBE O MAR?</text>
 <g id="k1">{copo(60, "cA", False)}<text x="260" y="1090" class="t2" fill="#7cc4ff" text-anchor="middle">GELO QUE BOIA</text></g>
 <g id="k2" opacity="0">{copo(620, "cB", True)}<text x="820" y="1090" class="t2" fill="#FACC15" text-anchor="middle">GELO EM TERRA</text></g>
 <g id="rA" opacity="0"><rect x="70" y="200" width="380" height="80" rx="12" fill="#0c0c10"/><text x="260" y="254" class="t2" fill="#7cc4ff" text-anchor="middle">QUASE NADA</text></g>
 <g id="rB" opacity="0"><rect x="630" y="200" width="380" height="80" rx="12" fill="#3b0d0d"/><text x="820" y="254" class="t2" fill="#ff4d4d" text-anchor="middle">↑ ÁGUA NOVA</text></g>
''')
    c.palco(ini, fim, corpo)
    c.a(f'tl.to("#cAg", {{opacity:0, scale:0.2, transformOrigin:"50% 50%", duration:1.6}}, {tBo:.2f});')
    c.mostra("#rA", tBo + 0.3)
    c.mostra("#k2", tRo - 0.3)
    c.a(f'tl.to("#cBg", {{y:170, rotation:20, transformOrigin:"50% 50%", duration:0.9, ease:"power2.in"}}, {tCa:.2f});')
    c.a(f'tl.to("#cBg", {{opacity:0, duration:1.0}}, {tCa + 1.0:.2f});')
    c.a(f'tl.to("#cBa", {{attr:{{y:490, height:510}}, duration:1.2}}, {tNo - 0.2:.2f});')
    c.mostra("#rB", tNo - 0.1)
    c.painel(ini, fim, "A DIFERENÇA", [(tBo, "🧊 gelo que boia: quase nada"), (tRo, "🏔️ gelo em cima da rocha…"), (tNo, "…vira <b style='color:#ff4d4d'>água nova</b> no mar")], cor="#FACC15")


def bloco_conta(c, F, ini, fim):
    tPl, tMm, tCu, tSo, tIn = F.t("planeta"), F.t("milímetro"), F.t("cúbicos"), F.t("sozinha"), F.t("inteira")
    corpo = f'''<div class="conta">
 <div class="t1h">A CONTA</div>
 <div class="eq" id="e1">🌊 oceanos: <b>361,8 milhões de km²</b></div>
 <div class="eq" id="e2">× <b>1 mm</b> de altura</div>
 <div class="eq big" id="e3">= <b>≈ 360 km³</b> de água</div>
 <div class="cnts"><div class="cnt" id="n1"><small>SÓ A THWAITES</small><span id="v1">0</span><i>cm de mar</i></div>
 <div class="cnt" id="n2"><small>A ANTÁRTICA TODA</small><span id="v2">0</span><i>metros de mar</i></div></div>
</div>'''
    c.palco(ini, fim, corpo)
    c.entra("#e1", tPl - 0.2); c.entra("#e2", tMm - 0.1); c.entra("#e3", tCu - 0.2)
    c.entra("#n1", tSo - 0.1); c.entra("#n2", tIn - 0.1)
    c.a(f'tl.fromTo("#v1", {{innerText:0}}, {{innerText:65, duration:1.4, snap:{{innerText:1}}}}, {tSo:.2f});')
    c.a(f'tl.fromTo("#v2", {{innerText:0}}, {{innerText:58, duration:1.4, snap:{{innerText:1}}}}, {tIn:.2f});')
    c.painel(ini, fim, "FAÇA A CONTA", [(tMm, "1 mm no planeta inteiro"), (tCu, "= ≈ 360 km³ de água"), (tIn, "<small>BedMachine (Morlighem) · antarcticglaciers.org</small>")], cor="#FACC15")


def pessoa(x, chao, pxcm, cor="#FACC15"):
    """silhueta de 1,70 m com os pés em (x, chao)"""
    h = 170 * pxcm
    s = h / 170.0
    return (f'<g transform="translate({x},{chao}) scale({s})" fill="{cor}">'
            '<circle cx="0" cy="-158" r="12"/><rect x="-16" y="-144" width="32" height="62" rx="10"/>'
            '<rect x="-27" y="-140" width="10" height="56" rx="5"/><rect x="17" y="-140" width="10" height="56" rx="5"/>'
            '<rect x="-15" y="-86" width="13" height="86" rx="5"/><rect x="2" y="-86" width="13" height="86" rx="5"/></g>')


def degrau(nome, pxcm, nivel_cm, titulo, sub, extra="", regua=None, frente=""):
    chao = 1040
    agua = nivel_cm * pxcm
    ticks = ""
    if regua:
        passo, maxv, un, mult = regua
        v = 0
        while v <= maxv + 1e-6:
            y = chao - v * mult * pxcm
            if y > 150:
                ticks += f'<path d="M60,{y:.0f} H90" stroke="#9a9aa6" stroke-width="3"/><text x="100" y="{y + 9:.0f}" class="t4" fill="#d4d4dc">{v:g} {un}</text>'
            v += passo
    return f'''<g id="{nome}" opacity="0">
 <rect x="0" y="0" width="{W}" height="{STAGE}" fill="#0c0c10"/>
 <rect x="0" y="{chao}" width="{W}" height="{STAGE - chao}" fill="#3b3226"/>
 {extra}
 <path d="M60,{chao} V160" stroke="#9a9aa6" stroke-width="3"/>{ticks}
 <rect id="{nome}a" x="0" y="{chao}" width="{W}" height="0" fill="#1b6ea8" opacity=".72"/>
 {frente}
 <text class="t1" x="1040" y="150" text-anchor="end" fill="#7cc4ff" id="{nome}t">{titulo}</text>
 <text class="t3" x="1040" y="200" text-anchor="end" fill="#c9c9d2">{sub}</text>
</g>''', (nome, chao - agua, agua)


def bloco_escada(c, F, ini, fim):
    tPr = F.t("praia")
    tD = F.t("2100")
    tSom, tCi = F.t("Somando"), F.t("cintura")
    tOc, tTe = F.t("Ocidental"), F.t("térreo")
    tTo, tAn = F.t("toda"), F.t("andares")
    c.a('')  # imagem da praia (a mesma pessoa vai para a escada)
    c.imagem(ini, tD + 0.4, "praia.png", pos="50% 0%", z=1.06,
             extra='<div class="lbl1" id="voce" style="top:860px"><b style="color:#FACC15">VOCÊ</b>, NA PRAIA</div>')
    c.entra("#voce", tPr - 0.1)
    casa = '<rect x="560" y="{y}" width="420" height="{h}" fill="#26262f" stroke="#55555f" stroke-width="3"/>'
    pr = ""
    for k in range(20):
        pr += f'<rect x="600" y="{1040 - (k + 1) * 2.9 * 100 * 0.14:.1f}" width="300" height="{2.9 * 100 * 0.14 - 4:.1f}" fill="#26262f" stroke="#55555f" stroke-width="2"/>'
    d1, a1 = degrau("d1", 4.6, 3, "3 cm", "até 2100 · só a Thwaites", pessoa(540, 1040, 4.6) + '<path d="M760,960 L620,1025" stroke="#FACC15" stroke-width="5" marker-end="url(#ahy)"/><text x="770" y="950" class="t2" fill="#FACC15">3 cm: no pé</text>', regua=(50, 200, "cm", 1))
    d2, a2 = degrau("d2", 4.6, 98, "≈ 1 m", "até 2100 · tudo somado (IPCC: 26–98 cm)", pessoa(540, 1040, 4.6), regua=(50, 200, "cm", 1))
    d3, a3 = degrau("d3", 1.7, 330, "3,3 m", "Antártica Ocidental · séculos", casa.format(y=1040 - 300 * 1.7, h=300 * 1.7, ty=1040 - 300 * 1.7 + 50) + pessoa(330, 1040, 1.7), regua=(1, 6, "m", 100),
                    frente=f'<text x="770" y="{1040 - 300 * 1.7 + 60:.0f}" class="t2" fill="#fff" text-anchor="middle">TÉRREO · 3 m</text>')
    d4, a4 = degrau("d4", 0.14, 5800, "58 m", "a Antártica toda · prédio de ~20 andares", pr + pessoa(330, 1040, 0.14), regua=(10, 60, "m", 100),
                    frente=pr.replace('fill="#26262f" stroke="#55555f"', 'fill="none" stroke="#e6e6ee"') + pessoa(330, 1040, 0.14)
                    + '<circle cx="330" cy="1024" r="30" fill="none" stroke="#FACC15" stroke-width="5"/><path d="M330,930 V982" stroke="#FACC15" stroke-width="6" marker-end="url(#ahy)"/><text x="330" y="910" class="t2" fill="#FACC15" text-anchor="middle">VOCÊ</text>')
    corpo = svg(d1 + d2 + d3 + d4)
    c.palco(tD - 0.2, fim, corpo)
    tempos = [(a1, tD, tSom), (a2, tSom, tOc), (a3, tOc, tTo), (a4, tTo, fim)]
    for (nome, y, h), t0, t1 in tempos:
        c.a(f'tl.to("#{nome}", {{opacity:1, duration:0.35}}, {t0:.2f});')
        c.a(f'tl.to("#{nome}a", {{attr:{{y:{y:.0f}, height:{h:.0f}}}, duration:1.6, ease:"power2.out"}}, {t0 + 0.2:.2f});')
        if t1 < fim:
            c.a(f'tl.to("#{nome}", {{opacity:0, duration:0.35}}, {t1:.2f});')
    c.painel(tD - 0.2, fim, "A MESMA PRAIA", [(tD, "<b>3 cm</b> · só a Thwaites · 2100"), (tCi, "<b>≈ 1 m</b> · tudo somado · 2100"),
                                              (tTe, "<b>3,3 m</b> · Antártica Ocidental"), (tAn, "<b>58 m</b> · a Antártica toda")], cor="#7cc4ff")
    return tPr


def bloco_curva(c, F, ini, fim):
    tCo, tVi, tRi = F.t("começou"), F.t("20"), F.t("ritmo")
    pts = [(1880, 0), (1900, 2), (1920, 4.5), (1940, 8), (1960, 11), (1980, 14), (1993, 16), (2000, 17.5), (2010, 20.5), (2020, 23)]
    X = lambda a: 140 + (a - 1880) / 140 * 860
    Y = lambda v: 960 - v / 25 * 700
    d = "M" + " L".join(f"{X(a):.0f},{Y(v):.0f}" for a, v in pts)
    grade = "".join(f'<path d="M140,{Y(v):.0f} H1000" stroke="#22222c" stroke-width="2"/><text x="120" y="{Y(v) + 9:.0f}" class="t4" fill="#9a9aa6" text-anchor="end">{v}</text>' for v in (0, 5, 10, 15, 20, 25))
    anos = "".join(f'<text x="{X(a):.0f}" y="1010" class="t4" fill="#c9c9d2" text-anchor="middle">{a}</text>' for a in (1880, 1920, 1960, 2000, 2020))
    corpo = svg(f'''
 <text class="t1" x="540" y="150" text-anchor="middle">O MAR JÁ SUBIU</text>
 <text class="t3" x="540" y="200" text-anchor="middle" fill="#c9c9d2">nível médio do mar, em cm (curva ilustrativa · NOAA)</text>
 {grade}{anos}
 <path id="crv" d="{d}" stroke="#7cc4ff" stroke-width="9" fill="none" filter="url(#glow)" stroke-dasharray="1400" stroke-dashoffset="1400"/>
 <g id="kV" opacity="0"><rect x="560" y="300" width="440" height="92" rx="14" fill="#0c0c10" stroke="#7cc4ff" stroke-width="3"/><text x="780" y="360" class="t2" fill="#fff" text-anchor="middle">+21 a 24 cm</text></g>
 <g id="kR" opacity="0"><rect x="180" y="430" width="560" height="150" rx="14" fill="#3b0d0d" stroke="#ff4d4d" stroke-width="3"/>
   <text x="460" y="490" class="t3" fill="#fff" text-anchor="middle">século XX: 1,4 mm/ano</text><text x="460" y="550" class="t2" fill="#ff4d4d" text-anchor="middle">2006–2015: 3,6 mm/ano</text></g>
''')
    c.palco(ini, fim, corpo)
    c.a(f'tl.to("#crv", {{strokeDashoffset:0, duration:2.4, ease:"power1.inOut"}}, {tCo - 0.2:.2f});')
    c.mostra("#kV", tVi - 0.1); c.mostra("#kR", tRi - 0.1)
    c.painel(ini, fim, "JÁ COMEÇOU · NOAA", [(tRi, "o ritmo <b style='color:#ff4d4d'>mais que dobrou</b>")], cor="#ff4d4d", grande=(tVi - 0.1, "+21–24 cm"))


def bloco_nei(c, F, ini, fim):
    tAn = F.t("Antártica")
    tVi = F.t("vi")
    c.imagem(ini, fim, "nei-antartica.png", pos="50% 30%", z=1.06)
    c.painel(ini, fim, "FOTO: NEI MALDANER", [(tVi, "eu vi esse gelo de perto")], cor="#FACC15", grande=(tAn, "ANTÁRTICA<br>2004 · 2006"))


def bloco_cta(c, F, ini, fim):
    tMa, tCo, tCi, tIn = F.t("mapa"), F.t("completo"), F.t("cidade"), F.t("inema")
    corpo = f'''<div class="ctas">
 <div class="cbox" id="q1"><small>VEJA SE A ÁGUA CHEGA NA SUA RUA</small><b>coastal.climatecentral.org</b><i>mapa de risco do mar subindo</i></div>
 <div class="cbox vid" id="q2"><img src="assets/thumb16.jpg" alt=""/><div><small>▶ VÍDEO COMPLETO NO CANAL</small><b>Geleira do Juízo Final</b></div></div>
 <div class="club" id="q3"><b>inema.club</b><i>aprenda inteligência artificial</i></div>
</div>'''
    c.palco(ini, fim, corpo)
    c.entra("#q1", tMa - 0.1); c.entra("#q2", tCo - 0.1); c.entra("#q3", tIn - 0.1)
    inner = c.id("pn")
    c.clip(tCi - 0.2, fim, f'<div class="painel red" id="{inner}"><div class="ptg">DE QUE CIDADE<br>VOCÊ É? 👇</div><div class="psub">o mar chega até aí?</div></div>', 5, cls="full")
    c.a(f'tl.fromTo("#{inner}", {{opacity:0, scale:0.9}}, {{opacity:1, scale:1, duration:0.45, ease:"back.out(2)"}}, {tCi - 0.2:.2f});')


# ---------------------------------------------------------------- legenda
def legenda(c, pal, fim_total):
    toks, i = [], 0
    while i < len(pal):
        for chave, troca in TROCAS:
            ks = chave.split()
            if [norm(x["word"]) for x in pal[i:i + len(ks)]] == [norm(k) for k in ks]:
                pont = re.search(r"[.,:?!]$", pal[i + len(ks) - 1]["word"].strip())
                toks.append({"word": troca + (pont.group(0) if pont else ""), "t": pal[i]["start"], "num": True})
                i += len(ks)
                break
        else:
            toks.append({"word": pal[i]["word"].strip(), "t": pal[i]["start"], "num": False})
            i += 1
    grupos, g = [], []
    for k, w in enumerate(toks):
        g.append(w)
        nx = toks[k + 1] if k + 1 < len(toks) else None
        if len(g) == 3 or re.search(r"[.,:?!]$", w["word"]) or not nx or nx["t"] - w["t"] > 0.9:
            grupos.append(g); g = []
    html = []
    for k, gr in enumerate(grupos):
        ini = gr[0]["t"] - 0.05
        prox = grupos[k + 1][0]["t"] - 0.05 if k + 1 < len(grupos) else fim_total
        fim = min(prox, gr[-1]["t"] + 1.4)
        spans = " ".join(f'<b>{re.sub(r"[.,:]$", "", w["word"])}</b>' for w in gr)
        cid = f"cap{k}"
        html.append(f'<div class="cap" id="{cid}">{spans}</div>')
        c.a(f'tl.set("#{cid}", {{opacity:1}}, {ini:.2f}); tl.set("#{cid}", {{opacity:0}}, {fim:.2f});')
        for j, w in enumerate(gr):
            cor = "#FACC15" if w["num"] else COR.get(norm(w["word"]), "#FACC15")
            c.a(f'tl.set("#{cid} b:nth-child({j + 1})", {{color:"{cor}"}}, {w["t"]:.2f}); tl.set("#{cid} b:nth-child({j + 1})", {{color:"#fff"}}, {min(fim, w["t"] + 0.45):.2f});')
    return "".join(html)


CSS = '''
@font-face { font-family:"Sora"; src:url("assets/fonts/sora-latin-700-normal.woff2") format("woff2"); font-weight:700; }
@font-face { font-family:"Sora"; src:url("assets/fonts/sora-latin-400-normal.woff2") format("woff2"); font-weight:400; }
@font-face { font-family:"Inter"; src:url("assets/fonts/Inter-500.woff2") format("woff2"); font-weight:500; }
@font-face { font-family:"Inter"; src:url("assets/fonts/Inter-700.woff2") format("woff2"); font-weight:700; }
@font-face { font-family:"Montserrat"; src:url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight:900; }
:root { --bg:#0c0c10; --am:#FACC15; --tx:#ECECF1; --mu:#a3a3ae; --red:#ff4d4d; }
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:1080px; height:1920px; overflow:hidden; background:var(--bg); }
#root { width:100%; height:100%; position:relative; font-family:Inter, sans-serif; color:var(--tx); background:var(--bg); }
.full { position:absolute; inset:0; }
.stage { position:absolute; left:0; top:0; width:1080px; height:1180px; overflow:hidden; }
.in { position:absolute; inset:0; opacity:0; overflow:hidden; }
.foto { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.vin { position:absolute; inset:0; background:linear-gradient(180deg, rgba(12,12,16,.0) 60%, rgba(12,12,16,.95) 100%); }
.dg { position:absolute; left:0; top:0; }
.dg text { font-family:Sora, sans-serif; font-weight:700; }
.t1 { font-size:52px; fill:#fff; letter-spacing:.02em; } .t2 { font-size:40px; } .t3 { font-size:30px; } .t4 { font-size:26px; }
.chip { display:inline-block; font-family:Sora; font-weight:700; font-size:22px; letter-spacing:.14em; padding:8px 16px; border-radius:999px; }
#marca { position:absolute; left:30px; top:28px; padding:8px 16px; border-radius:10px; background:rgba(12,12,16,.85); font-family:Sora; font-weight:700; font-size:24px; letter-spacing:.14em; color:var(--am); z-index:5; }
#marca span { color:var(--tx); }
#fonte { position:absolute; left:36px; right:36px; top:1836px; font-size:19px; line-height:1.35; color:#9a9aa6; }
.chips { position:absolute; left:0; right:0; top:1000px; display:flex; justify-content:center; gap:24px; }
.ch { opacity:0; font-family:Sora; font-weight:700; font-size:40px; padding:14px 28px; border-radius:16px; background:rgba(12,12,16,.88); border:3px solid var(--am); color:#fff; }
.lbl1, .lbl2 { position:absolute; left:50px; opacity:0; font-family:Sora; font-weight:700; font-size:44px; line-height:1.2; padding:16px 24px; border-radius:16px; background:rgba(12,12,16,.88); }
.lbl1 { top:120px; } .lbl2 { top:940px; } .lbl2 small { font-size:26px; color:#c9c9d2; font-weight:400; }
/* painel */
.painel { position:absolute; left:36px; top:1300px; width:630px; height:500px; padding:28px 30px; border-radius:20px; background:#14141c; border:3px solid #2c2c38; opacity:0; }
.pgr { font-family:Sora; font-weight:700; font-size:78px; line-height:1.05; margin:18px 0 10px; opacity:0; }
.prow { font-family:Sora; font-weight:700; font-size:34px; line-height:1.25; margin-top:18px; opacity:0; }
.prow small { font-size:22px; color:#9a9aa6; font-weight:400; }
.painel.red { background:#c81e1e; border-color:#ff6b6b; display:flex; flex-direction:column; justify-content:center; }
.ptg { font-family:Sora; font-weight:700; font-size:64px; line-height:1.1; color:#fff; }
.psub { font-size:36px; color:#ffe4e4; margin-top:18px; font-weight:700; }
/* avatar */
#avw { position:absolute; overflow:hidden; border-radius:18px; border:3px solid var(--am); background:#000; }
#av { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; object-position:58% 30%; }
.avtag { position:absolute; left:0; right:0; bottom:0; padding:6px 10px; font-family:Sora; font-weight:700; font-size:18px; background:rgba(12,12,16,.85); color:#fff; }
/* legenda */
.cap { position:absolute; left:20px; right:20px; top:1196px; text-align:center; font-family:Montserrat; font-weight:900; font-size:64px; text-transform:uppercase; opacity:0;
       color:#fff; -webkit-text-stroke:8px #000; paint-order:stroke fill; }
/* conta */
.conta { position:absolute; inset:0; padding:90px 60px; background:radial-gradient(ellipse at 50% 30%, #0f2a40 0%, #0c0c10 70%); }
.t1h { font-family:Sora; font-weight:700; font-size:56px; text-align:center; margin-bottom:40px; }
.eq { font-family:Sora; font-weight:700; font-size:46px; line-height:1.2; margin:22px 0; opacity:0; } .eq b { color:#7cc4ff; }
.eq.big { font-size:62px; } .eq.big b { color:var(--am); }
.cnts { display:flex; gap:30px; margin-top:60px; }
.cnt { flex:1; padding:26px; border-radius:18px; background:#1a1014; border:3px solid var(--red); opacity:0; text-align:center; }
.cnt small { display:block; font-family:Sora; font-weight:700; font-size:26px; letter-spacing:.1em; color:#ffb3b3; }
.cnt span { display:block; font-family:Sora; font-weight:700; font-size:150px; line-height:1.05; color:var(--red); }
.cnt i { font-style:normal; font-size:30px; font-weight:700; }
/* cta */
.ctas { position:absolute; inset:0; padding:140px 50px 0; background:radial-gradient(ellipse at 50% 20%, #10283a 0%, #0c0c10 70%); }
.cbox { padding:30px; border-radius:20px; background:#14141c; border:3px solid #7cc4ff; margin-bottom:34px; opacity:0; }
.cbox small { display:block; font-family:Sora; font-weight:700; font-size:26px; letter-spacing:.08em; color:#7cc4ff; }
.cbox b { display:block; font-family:Sora; font-weight:700; font-size:52px; margin-top:10px; color:#fff; }
.cbox i { display:block; font-style:normal; font-size:30px; color:#c9c9d2; margin-top:8px; }
.cbox.vid { display:flex; gap:24px; align-items:center; border-color:var(--am); } .cbox.vid img { width:380px; border-radius:12px; }
.cbox.vid small { color:var(--am); } .cbox.vid b { font-size:40px; }
.club { display:inline-block; padding:22px 40px; border-radius:999px; background:var(--am); color:#1a1206; opacity:0; }
.club b { font-family:Sora; font-weight:700; font-size:56px; } .club i { font-style:normal; font-size:28px; font-weight:700; margin-left:16px; }
'''


def main():
    falso = "--falso" in sys.argv
    pal = palavras(falso)
    F = Fala(pal)
    total = round(F.fim + 0.8, 2)
    c = Cena()
    # cortes do roteiro (cada bloco começa na 1ª palavra da frase)
    marcos = {}
    for k, p in [("mapa", "Esta"), ("corte", "Olha"), ("copos", "Mas"), ("conta", "Agora"), ("escada", "imagina"),
                 ("curva", "Isso"), ("nei", "estive"), ("cta", "Quer")]:
        marcos[k] = F.t(p)
    marcos["nei"] = marcos["nei"] - 0.3          # "Eu estive…"
    F.cur = 0.0
    seq = ["abertura", "mapa", "corte", "copos", "conta", "escada", "curva", "nei", "cta"]
    ini = {"abertura": 0.0, **{k: marcos[k] - 0.15 for k in seq[1:]}}
    fim = {k: (ini[seq[j + 1]] + 0.3 if j + 1 < len(seq) else total) for j, k in enumerate(seq)}
    bloco_abertura(c, F, fim["abertura"])
    c.a(f'tl.set("#marca", {{opacity:0}}, 0); tl.to("#marca", {{opacity:1, duration:0.4}}, {fim["abertura"] - 0.3:.2f});')
    for k in seq[1:]:
        F.cur = marcos[k] - 0.01
        globals()["bloco_" + k](c, F, ini[k], fim[k])
    leg = legenda(c, pal, total)
    av = (f'<div id="avw" style="left:{AV["left"]}px;top:{AV["top"]}px;width:{AV["w"]}px;height:{AV["h"]}px;">'
          f'<video id="av" src="assets/avatar.mp4" data-start="0" data-duration="{total:.2f}" data-track-index="9" data-has-audio="true" data-volume="1" playsinline></video>'
          f'<div class="avtag">NEI MALDANER · INEMA</div></div>')
    html = f'''<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1080" data-height="1920">
 {"".join(c.html)}
 <div id="topo" class="clip full" data-start="0" data-duration="{total:.2f}" data-track-index="8"><div id="marca">INEMA <span>· EVENTOS EXTREMOS</span></div><div id="fonte">{FONTE}</div></div>
 {av}
 <div id="legenda" class="clip full" data-start="0" data-duration="{total:.2f}" data-track-index="10">{leg}</div>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(c.js)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>'''
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(html)
    json.dump({k: [ini[k], fim[k]] for k in seq}, open(AQUI / "build/blocos.json", "w"), indent=1)
    print(f"ok {OUT/'index.html'} · {total:.1f} s · {len(c.js)} eventos · {'FALSO' if falso else 'whisper'}")


if __name__ == "__main__":
    main()
