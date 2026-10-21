#!/usr/bin/env python3
"""r7exp vertical (9:16) — "Musk: os humanoides vão mudar tudo" (21/10/2026), lives6.

Molde: reels/thwaites/gera_v.py. Diferença: o avatar abre em MEIA TELA (1080x960, embaixo) até "desenho" e vai para o PiP.
Blocos: abertura (capa) · cérebro sem mãos → golfinho → curva de valor · escada log 1×…1.000.000× (palpite) ·
dinheiro → watts e toneladas · Marcos e os dois caminhos · plano em 3 passos · participante ou espectador + inema.club.
Uso: python3 gera_v.py [--falso]   Precisa: tempos/w/words.json, cena/assets/avatar.mp4, imagens. Saída: cena/index.html
"""
import json, re, sys, subprocess, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
W, H = 1080, 1920
STAGE = 1180
AV = dict(left=690, top=1300, w=354, h=500)
MEIA = dict(left=0, top=960, w=1080, h=960)
OUT = AQUI / "cena"

FONTE = "Elon Musk a Walter Isaacson (série The Builders, out/2026) · números = palpite dele · imagens ilustrativas"

TROCAS = [
    ("trinta por cento", "30%"), ("30 por cento", "30%"), ("um milhão de vezes", "1 milhão de vezes"),
    ("inema ponto club", "inema.club"), ("inema club", "inema.club"), ("inema.club", "inema.club"),
]
COR = {"cai": "#ff4d4d", "espectador": "#ff4d4d", "longe": "#ff4d4d", "barato": "#ff4d4d", "explode": "#FACC15"}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def palavras(falso):
    if falso:
        txt = (AQUI / "falas/musk.txt").read_text().split()
        t, out = 0.3, []
        for w in txt:
            d = max(0.18, len(w) / 14.5)
            out.append({"word": w, "start": round(t, 2), "end": round(t + d, 2)})
            t += d + (0.35 if re.search(r"[.?:]$", w) else 0.06)
        return out
    w = json.loads((AQUI / "tempos/w/words.json").read_text())
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

    def imagem(self, ini, fim, img, pos="50% 0%", z=1.08, extra="", fade_in=True):
        inner = self.id("im")
        corpo = f'<div class="in" id="{inner}"><img class="foto" id="{inner}f" src="assets/{img}" style="object-position:{pos}" alt=""/><div class="vin"></div>{extra}</div>'
        self.clip(ini, fim, corpo, 2)
        if fade_in:
            self.fade(f"#{inner}", ini, fim)
        else:
            self.a(f'tl.set("#{inner}", {{opacity:1}}, 0); tl.to("#{inner}", {{opacity:0, duration:0.4}}, {fim - 0.4:.2f});')
        self.a(f'tl.fromTo("#{inner}f", {{scale:1.0}}, {{scale:{z}, duration:{fim - ini + 0.4:.2f}, ease:"none"}}, {ini:.2f});')
        return inner

    def palco(self, ini, fim, corpo, track=3):
        inner = self.id("pl")
        self.clip(ini, fim, f'<div class="in" id="{inner}">{corpo}</div>', track)
        self.fade(f"#{inner}", ini, fim)
        return inner

    def painel(self, ini, fim, chip, linhas, cor="#FACC15", grande=None):
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


DEFS = '''<defs>
 <filter id="glow" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1300" height="1400"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <marker id="ahr" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#ff4d4d"/></marker>
 <marker id="ahy" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#FACC15"/></marker>
 <linearGradient id="gb" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#3a3a46"/><stop offset="1" stop-color="#5a5a68"/></linearGradient>
 <linearGradient id="gy" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#a16207"/><stop offset="1" stop-color="#FACC15"/></linearGradient>
</defs>'''


def svg(corpo):
    return f'<svg class="dg" width="{W}" height="{STAGE}" viewBox="0 0 {W} {STAGE}">{DEFS}{corpo}</svg>'


# ---------------------------------------------------------------- blocos
def bloco_abertura(c, F, fim):
    tDe = F.t("desenho")
    c.imagem(0.0, fim, "capa.png", pos="50% 0%", z=1.05, fade_in=False,
             extra='<div class="selo" id="selo">ELON MUSK · ENTREVISTA A WALTER ISAACSON</div>')
    c.entra("#selo", 0.4)
    return tDe + 0.6


def bloco_cerebro(c, F, ini, fim):
    tCe, tGo, tQu = F.t("cérebro"), F.t("golfinho"), F.t("Quando")
    tCo, tHu, tEx = F.t("corpo"), F.t("humanoide"), F.t("explode")
    c.imagem(ini, tGo + 0.3, "cerebro.png", pos="50% 50%", z=1.08,
             extra='<div class="lbl1" id="lCe">🧠 IA de hoje:<br><b style="color:#FACC15">CÉREBRO SEM MÃOS</b></div>')
    c.entra("#lCe", tCe - 0.1)
    c.imagem(tGo - 0.1, tQu + 0.3, "golfinho.png", pos="50% 50%", z=1.08,
             extra='<div class="lbl1" id="lGo">🐬 muito inteligente,<br><b style="color:#ff4d4d">MAS NÃO PEGA NADA</b></div>')
    c.entra("#lGo", tGo + 0.2)
    # curva de valor: plana sem mãos, explode com corpo
    X = lambda k: 120 + k * 8.6          # k 0..100
    pts_plana = " L".join(f"{X(k):.0f},{900 - k * 0.6:.0f}" for k in range(0, 101, 5))
    pts_exp = " L".join(f"{X(k):.0f},{900 - 30 - (2.718 ** (k / 100 * 6.3) - 1) * 1.15:.0f}" for k in range(0, 101, 4))
    corpo = svg(f'''
 <text class="t1" x="540" y="150" text-anchor="middle">CÉREBRO + MÃOS</text>
 <text class="t3" x="540" y="205" text-anchor="middle" fill="#c9c9d2">o valor da inteligência, na conta do Musk</text>
 <path d="M120,260 V900 H1000" stroke="#55555f" stroke-width="4" fill="none"/>
 <text x="100" y="300" class="t4" fill="#9a9aa6" text-anchor="end" transform="rotate(-90 100 300)">VALOR</text>
 <path id="cvP" d="M{pts_plana}" stroke="#7cc4ff" stroke-width="8" fill="none" stroke-dasharray="1100" stroke-dashoffset="1100"/>
 <text id="cvPt" x="1000" y="880" class="t3" fill="#7cc4ff" text-anchor="end" opacity="0">🧠 só cérebro</text>
 <path id="cvE" d="M{pts_exp}" stroke="#FACC15" stroke-width="12" fill="none" filter="url(#glow)" stroke-dasharray="1500" stroke-dashoffset="1500"/>
 <g id="cvEt" opacity="0"><rect x="520" y="250" width="470" height="120" rx="16" fill="#0c0c10" stroke="#FACC15" stroke-width="4"/>
   <text x="755" y="305" class="t2" fill="#FACC15" text-anchor="middle">🤖 COM CORPO</text><text x="755" y="350" class="t3" fill="#fff" text-anchor="middle">o valor explode</text></g>
 <g id="cvH" opacity="0"><text x="300" y="1030" class="t2" fill="#fff" text-anchor="middle">pega</text><text x="540" y="1030" class="t2" fill="#fff" text-anchor="middle">monta</text><text x="800" y="1030" class="t2" fill="#fff" text-anchor="middle">constrói</text></g>
''')
    c.palco(tQu - 0.1, fim, corpo)
    c.a(f'tl.to("#cvP", {{strokeDashoffset:0, duration:1.0, ease:"none"}}, {tQu:.2f});')
    c.mostra("#cvPt", tQu + 0.6)
    c.mostra("#cvH", tHu)
    c.a(f'tl.to("#cvE", {{strokeDashoffset:0, duration:1.4, ease:"power2.in"}}, {max(tCo, tEx - 1.4):.2f});')
    c.entra("#cvEt", tEx)
    c.painel(ini, fim, "A IMAGEM DO MUSK", [(tCe, "🧠 IA de hoje: sem mãos"), (tGo, "🐬 golfinho: igual"),
                                            (tHu, "🤖 com corpo, o valor <b style='color:#FACC15'>explode</b>")])


def bloco_conta(c, F, ini, fim):
    tCo, tCh, tCr = F.t("conta"), F.t("chat"), F.t("cresce")
    tRo, tAp, tVe = F.t("robôs"), F.t("aposta"), F.t("vezes")
    base, dec = 1000, 105
    y = lambda d: base - 40 - d * dec            # d = log10(v)
    grade = ""
    for d, lab in enumerate(["1×", "10×", "100×", "1 mil×", "10 mil×", "100 mil×", "1 milhão×"]):
        grade += (f'<path d="M190,{y(d):.0f} H1040" stroke="#22222c" stroke-width="2"/>'
                  f'<text x="180" y="{y(d) + 9:.0f}" class="t4" fill="#9a9aa6" text-anchor="end">{lab}</text>')
    def barra(nome, x, cor):
        return f'<rect id="{nome}" x="{x}" y="{base}" width="230" height="0" rx="10" fill="url(#{cor})"/>'
    corpo = svg(f'''
 <text class="t1" x="540" y="150" text-anchor="middle">A CONTA DELE</text>
 <text class="t3" x="540" y="205" text-anchor="middle" fill="#c9c9d2">tamanho da economia · escala que pula de 10 em 10</text>
 {grade}<path d="M190,{base} H1040" stroke="#9a9aa6" stroke-width="3"/>
 {barra("b1", 220, "gb")}{barra("b2", 500, "gb")}{barra("b3", 780, "gy")}
 <g id="l1" opacity="0"><text x="335" y="1045" class="t3" fill="#fff" text-anchor="middle">HOJE</text><text x="335" y="{y(0) - 20:.0f}" class="t3" fill="#c9c9d2" text-anchor="middle">1×</text></g>
 <g id="l2" opacity="0"><text x="615" y="1045" class="t3" fill="#fff" text-anchor="middle">IA DO CHAT</text><text x="615" y="{y(0.12) - 20:.0f}" class="t2" fill="#7cc4ff" text-anchor="middle">+30%</text></g>
 <g id="l3" opacity="0"><text x="895" y="1045" class="t3" fill="#FACC15" text-anchor="middle">ROBÔS +</text><text x="895" y="1085" class="t3" fill="#FACC15" text-anchor="middle">ESPAÇO</text></g>
 <g id="l3v" opacity="0"><text x="895" y="{y(6) - 22:.0f}" class="t2" fill="#FACC15" text-anchor="middle">1 milhão×</text></g>
 <g id="crb" opacity="0" transform="rotate(-12 560 560)"><rect x="300" y="500" width="520" height="120" rx="12" fill="none" stroke="#ff4d4d" stroke-width="8"/>
   <text x="560" y="582" class="t2" fill="#ff4d4d" text-anchor="middle" style="font-size:54px">PALPITE DO MUSK</text></g>
''')
    c.palco(ini, fim, corpo)
    c.a(f'tl.to("#b1", {{attr:{{y:{y(0):.0f}, height:{base - y(0):.0f}}}, duration:0.6}}, {tCo:.2f});')
    c.mostra("#l1", tCo)
    c.a(f'tl.to("#b2", {{attr:{{y:{y(0.12):.0f}, height:{base - y(0.12):.0f}}}, duration:0.6}}, {tCh:.2f});')
    c.mostra("#l2", tCr - 0.1)
    c.mostra("#l3", tRo - 0.1)
    c.a(f'tl.to("#b3", {{attr:{{y:{y(6):.0f}, height:{base - y(6):.0f}}}, duration:{max(0.8, tVe - tAp + 0.3):.2f}, ease:"power2.in"}}, {tAp - 0.1:.2f});')
    c.mostra("#l3v", tAp + 0.3)
    c.a(f'tl.fromTo("#crb", {{opacity:0, scale:1.6, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)"}}, {tAp + 0.7:.2f});')
    c.painel(ini, fim, "A CONTA · PALPITE DELE", [(tCh, "💬 só a IA do chat: <b style='color:#7cc4ff'>+30%</b>"),
                                                  (tRo, "🦾 com robôs e o espaço…")],
             grande=(tAp + 0.2, "ATÉ 1 MILHÃO×"))


def bloco_dinheiro(c, F, ini, fim):
    tDi, tEn, tWa, tTo = F.t("dinheiro"), F.t("energia"), F.t("watts"), F.t("toneladas")
    corpo = '''<div class="din">
 <div class="t1h">O DINHEIRO VIRA…</div>
 <div class="coin" id="coin"><span>R$</span><span>US$</span><span>€</span></div>
 <div class="seta" id="dset">⬇</div>
 <div class="duo"><div class="dbox" id="dw"><em>⚡</em><b>WATTS</b><i>energia</i></div>
 <div class="dbox" id="dt"><em>⚖️</em><b>TONELADAS</b><i>matéria</i></div></div>
</div>'''
    c.palco(ini, fim, corpo)
    c.entra("#coin", tDi - 0.1)
    c.a(f'tl.to("#coin", {{opacity:0.25, scale:0.8, filter:"grayscale(1)", duration:0.5}}, {tEn:.2f});')
    c.mostra("#dset", tEn)
    c.entra("#dw", tWa - 0.1); c.entra("#dt", tTo - 0.1)
    c.painel(ini, fim, "A MOEDA DO FUTURO", [(tWa, "⚡ quantos watts"), (tTo, "⚖️ quantas toneladas")], grande=(tEn, "ENERGIA"))


def bloco_marcos(c, F, ini, fim):
    tMa, tMe, tCa = F.t("Marcos"), F.t("Mesmo"), F.t("caminhos")
    tAs, tBa, tCai = F.t("assiste"), F.t("barato"), F.t("cai")
    tPa, tAg, tCl, tCr = F.t("participa"), F.t("agentes"), F.t("cliente"), F.t("cresce")
    c.imagem(ini, tMe + 0.3, "marcos.png", pos="50% 20%", z=1.06,
             extra='<div class="lbl1" id="lMa" style="top:900px"><b style="color:#FACC15">MARCOS</b>, 45<br>dono de uma oficina</div>')
    c.entra("#lMa", tMa + 0.2)
    corpo = svg('''
 <text class="t1" x="540" y="180" text-anchor="middle">MESMO PONTO, DOIS CAMINHOS</text>
 <circle id="mp0" cx="100" cy="400" r="18" fill="#fff" opacity="0"/>
 <path id="mR" d="M100,400 C260,410 380,480 500,585" stroke="#ff4d4d" stroke-width="12" fill="none" marker-end="url(#ahr)" stroke-dasharray="600" stroke-dashoffset="600"/>
 <path id="mY" d="M100,400 C360,390 760,350 1010,260" stroke="#FACC15" stroke-width="12" fill="none" marker-end="url(#ahy)" filter="url(#glow)" stroke-dasharray="1000" stroke-dashoffset="1000"/>
 <path id="mG1" d="M100,400 C260,410 380,480 500,585" stroke="#55555f" stroke-width="5" fill="none" stroke-dasharray="12 10" opacity="0"/>
 <path id="mG2" d="M100,400 C360,390 760,350 1010,260" stroke="#55555f" stroke-width="5" fill="none" stroke-dasharray="12 10" opacity="0"/>
 <text id="mRt" x="560" y="520" class="t2" fill="#ff4d4d" opacity="0">CAI ↓</text>
 <text id="mYt" x="1000" y="345" class="t2" fill="#FACC15" text-anchor="end" opacity="0">CRESCE ↑</text>
''') + '''<div class="card cR" id="kR"><img src="assets/marcos-vazio.png" alt=""/><div class="ktag" style="background:#c81e1e">ESPECTADOR<br><small>assiste de longe</small></div></div>
<div class="card cY" id="kY"><img src="assets/marcos-robo.png" alt=""/><div class="ktag" style="background:#FACC15;color:#1a1206">PARTICIPANTE<br><small>usa o robô</small></div></div>'''
    c.palco(tMe - 0.1, fim, corpo)
    c.mostra("#mp0", tMe)
    c.mostra("#mG1", tCa - 0.1); c.mostra("#mG2", tCa - 0.1)
    c.a(f'tl.to("#mR", {{strokeDashoffset:0, duration:{max(0.8, tCai - tAs):.2f}, ease:"power1.in"}}, {tAs:.2f});')
    c.entra("#kR", tAs)
    c.mostra("#mRt", tCai - 0.1)
    c.a(f'tl.to("#mY", {{strokeDashoffset:0, duration:{max(0.8, tCr - tPa):.2f}, ease:"power1.in"}}, {tPa:.2f});')
    c.entra("#kY", tPa)
    c.mostra("#mYt", tCr - 0.1)
    c.painel(ini, fim, "MARCOS · DOIS CAMINHOS", grande=(tMa, "MESMA<br>OFICINA"), linhas=[(tAs, "<b style='color:#ff4d4d'>assiste</b>: o robô faz mais barato"),
                                                   (tPa, "<b style='color:#FACC15'>participa</b>: robô + agentes"),
                                                   (tCl, "e cuida do cliente → <b style='color:#FACC15'>cresce</b>")])


def bloco_plano(c, F, ini, fim):
    tPl, tMq, tCo, tFo = F.t("planeje"), F.t("Marque"), F.t("Comece"), F.t("fortaleça")
    tCf, tCu, tCr = F.t("confiança"), F.t("cuidado"), F.t("criatividade")
    corpo = '''<div class="plano">
 <div class="t1h">PARE E PLANEJE</div>
 <div class="pas" id="p1"><span class="ck" id="k1">✓</span><div><b>MARQUE O REPETITIVO</b><i>o que um robô faria</i></div></div>
 <div class="pas" id="p2"><span class="ck" id="k2">✓</span><div><b>USE IA HOJE</b><i>seja quem dirige a máquina</i></div></div>
 <div class="pas" id="p3"><span class="ck" id="k3">✓</span><div><b>FORTALEÇA O HUMANO</b><i>isso não se compra no mercado</i></div></div>
 <div class="hum"><span id="h1">🤝 confiança</span><span id="h2">❤️ cuidado</span><span id="h3">💡 criatividade</span></div>
</div>'''
    c.palco(ini, fim, corpo)
    for n, t in ((1, tMq), (2, tCo), (3, tFo)):
        c.entra(f"#p{n}", t - 0.1)
        c.a(f'tl.fromTo("#k{n}", {{opacity:0, scale:0.3}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(3)"}}, {t + 0.5:.2f});')
    c.entra("#h1", tCf - 0.1); c.entra("#h2", tCu - 0.1); c.entra("#h3", tCr - 0.1)
    c.painel(ini, fim, "SEU PLANO · 3 PASSOS", [(tMq, "① marque o repetitivo"), (tCo, "② use IA hoje"), (tFo, "③ fortaleça o humano")])


def bloco_cta(c, F, ini, fim):
    tPt, tEs, tEsc, tPa, tIn = F.t("Participante"), F.t("espectador"), F.t("escreve"), F.t("participar"), F.t("inema")
    corpo = '''<div class="ctas">
 <div class="esc">
  <div class="op opY" id="oP"><em>🙋</em><b>PARTICIPANTE</b></div>
  <div class="ou">ou</div>
  <div class="op opG" id="oE"><em>🍿</em><b>ESPECTADOR</b></div>
 </div>
 <div class="bal" id="bal">💬 “eu escolho participar”</div>
 <div class="club" id="club"><b>inema.club</b><i>IA e robótica</i></div>
</div>'''
    c.palco(ini, fim, corpo)
    c.entra("#oP", tPt - 0.1); c.entra("#oE", tEs - 0.1)
    c.entra("#bal", tEsc)
    c.a(f'tl.to("#oP", {{scale:1.06, boxShadow:"0 0 60px #FACC15", duration:0.4}}, {tPa:.2f}); tl.to("#oE", {{opacity:0.35, duration:0.4}}, {tPa:.2f});')
    c.entra("#club", tIn - 0.1)
    c.painel(ini, tEsc, "A ESCOLHA", [], grande=(ini + 0.2, "E VOCÊ?"))
    inner = c.id("pn")
    c.clip(tEsc - 0.2, fim, f'<div class="painel red" id="{inner}"><div class="ptg">ME ESCREVE<br>AQUI 👇</div><div class="psub">“eu escolho participar”</div></div>', 5, cls="full")
    c.a(f'tl.fromTo("#{inner}", {{opacity:0, scale:0.9}}, {{opacity:1, scale:1, duration:0.45, ease:"back.out(2)"}}, {tEsc - 0.2:.2f});')


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
            toks.append({"word": pal[i]["word"].strip(), "t": pal[i]["start"], "num": bool(re.search(r"\d", pal[i]["word"]))})
            i += 1
    grupos, g = [], []
    for k, w in enumerate(toks):
        if g and len(" ".join(x["word"] for x in g + [w])) > 20:   # uma linha só, sem encostar no painel
            grupos.append(g); g = []
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
.in { position:absolute; inset:0; opacity:0; overflow:hidden; background:var(--bg); }
.foto { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.vin { position:absolute; inset:0; background:linear-gradient(180deg, rgba(12,12,16,.0) 60%, rgba(12,12,16,.95) 100%); }
.dg { position:absolute; left:0; top:0; }
.dg text { font-family:Sora, sans-serif; font-weight:700; }
.t1 { font-size:52px; fill:#fff; letter-spacing:.02em; } .t2 { font-size:40px; } .t3 { font-size:30px; } .t4 { font-size:26px; }
.chip { display:inline-block; font-family:Sora; font-weight:700; font-size:22px; letter-spacing:.14em; padding:8px 16px; border-radius:999px; }
#marca { position:absolute; left:30px; top:28px; padding:8px 16px; border-radius:10px; background:rgba(12,12,16,.85); font-family:Sora; font-weight:700; font-size:24px; letter-spacing:.14em; color:var(--am); z-index:5; }
#marca span { color:var(--tx); }
#fonte { position:absolute; left:36px; right:36px; top:1836px; font-size:19px; line-height:1.35; color:#9a9aa6; }
.selo { position:absolute; left:50%; top:880px; transform:translateX(-50%); white-space:nowrap; opacity:0; font-family:Sora; font-weight:700; font-size:30px; letter-spacing:.06em; padding:10px 22px; border-radius:10px; background:#c81e1e; color:#fff; }
.lbl1 { position:absolute; left:50px; top:120px; opacity:0; font-family:Sora; font-weight:700; font-size:46px; line-height:1.2; padding:18px 26px; border-radius:16px; background:rgba(12,12,16,.88); }
.painel { position:absolute; left:36px; top:1300px; width:630px; height:500px; padding:28px 30px; border-radius:20px; background:#14141c; border:3px solid #2c2c38; opacity:0; }
.pgr { font-family:Sora; font-weight:700; font-size:72px; line-height:1.05; margin:18px 0 10px; opacity:0; }
.prow { font-family:Sora; font-weight:700; font-size:34px; line-height:1.25; margin-top:18px; opacity:0; }
.painel.red { background:#c81e1e; border-color:#ff6b6b; display:flex; flex-direction:column; justify-content:center; }
.ptg { font-family:Sora; font-weight:700; font-size:64px; line-height:1.1; color:#fff; }
.psub { font-size:36px; color:#ffe4e4; margin-top:18px; font-weight:700; }
#avw { position:absolute; overflow:hidden; background:#000; }
#avb { position:absolute; border-radius:18px; border:3px solid var(--am); overflow:hidden; pointer-events:none; }
#av { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; object-position:50% 30%; transform-origin:50% 50%; }
.avtag { position:absolute; left:0; right:0; bottom:0; padding:6px 10px; font-family:Sora; font-weight:700; font-size:18px; background:rgba(12,12,16,.85); color:#fff; }
.cap { position:absolute; left:20px; right:20px; top:1196px; text-align:center; font-family:Montserrat; font-weight:900; font-size:64px; text-transform:uppercase; opacity:0;
       color:#fff; -webkit-text-stroke:8px #000; paint-order:stroke fill; }
.t1h { font-family:Sora; font-weight:700; font-size:56px; text-align:center; margin-bottom:40px; }
/* dinheiro */
.din { position:absolute; inset:0; padding:110px 60px; background:radial-gradient(ellipse at 50% 30%, #2a230a 0%, #0c0c10 70%); text-align:center; }
.coin { width:330px; height:330px; margin:0 auto; border-radius:50%; background:radial-gradient(circle at 35% 30%, #fde68a, #a16207); border:10px solid #ca8a04;
        display:flex; flex-direction:column; justify-content:center; font-family:Sora; font-weight:700; font-size:64px; color:#422006; line-height:1.05; opacity:0; }
.coin span:nth-child(2) { font-size:52px; } .coin span:nth-child(3) { font-size:58px; }
.seta { font-size:90px; margin:20px 0; color:#fff; opacity:0; }
.duo { display:flex; gap:30px; }
.dbox { flex:1; padding:30px 20px; border-radius:20px; background:#14141c; border:4px solid var(--am); opacity:0; }
.dbox em { display:block; font-style:normal; font-size:110px; line-height:1.1; }
.dbox b { display:block; font-family:Sora; font-weight:700; font-size:54px; color:var(--am); }
.dbox i { display:block; font-style:normal; font-size:32px; color:#c9c9d2; font-weight:700; margin-top:6px; }
/* marcos */
.card { position:absolute; top:610px; width:490px; height:540px; border-radius:20px; overflow:hidden; opacity:0; border:5px solid; }
.card img { width:100%; height:100%; object-fit:cover; object-position:50% 25%; }
.cR { left:30px; border-color:#ff4d4d; } .cY { left:560px; border-color:var(--am); }
.ktag { position:absolute; left:0; right:0; bottom:0; padding:12px 16px; font-family:Sora; font-weight:700; font-size:36px; line-height:1.1; color:#fff; text-align:center; }
.ktag small { font-size:24px; font-weight:400; }
/* plano */
.plano { position:absolute; inset:0; padding:110px 60px; background:radial-gradient(ellipse at 50% 25%, #10283a 0%, #0c0c10 70%); }
.pas { display:flex; gap:28px; align-items:center; padding:28px 30px; border-radius:20px; background:#14141c; border:3px solid #2c2c38; margin-bottom:28px; opacity:0; }
.ck { flex:none; width:96px; height:96px; border-radius:18px; background:var(--am); color:#1a1206; font-size:70px; font-weight:700; display:flex; align-items:center; justify-content:center; opacity:0; }
.pas b { display:block; font-family:Sora; font-weight:700; font-size:46px; color:#fff; }
.pas i { display:block; font-style:normal; font-size:30px; color:#c9c9d2; font-weight:700; margin-top:6px; }
.hum { display:flex; justify-content:center; gap:18px; margin-top:20px; }
.hum span { opacity:0; font-family:Sora; font-weight:700; font-size:34px; padding:14px 22px; border-radius:999px; background:#1f1a08; border:3px solid var(--am); }
/* cta */
.ctas { position:absolute; inset:0; padding:130px 50px 0; background:radial-gradient(ellipse at 50% 20%, #2a230a 0%, #0c0c10 70%); text-align:center; }
.esc { display:flex; align-items:center; gap:22px; }
.op { flex:1; padding:40px 10px; border-radius:24px; opacity:0; }
.op em { display:block; font-style:normal; font-size:120px; }
.op b { display:block; font-family:Sora; font-weight:700; font-size:44px; margin-top:12px; }
.opY { background:var(--am); color:#1a1206; } .opG { background:#26262f; color:#c9c9d2; border:3px solid #55555f; }
.ou { font-family:Sora; font-weight:700; font-size:40px; color:#9a9aa6; }
.bal { display:inline-block; margin-top:60px; padding:26px 36px; border-radius:28px 28px 28px 6px; background:#fff; color:#0c0c10; font-family:Sora; font-weight:700; font-size:46px; opacity:0; }
.club { display:inline-block; margin-top:60px; padding:22px 40px; border-radius:999px; background:var(--am); color:#1a1206; opacity:0; }
.club b { font-family:Sora; font-weight:700; font-size:56px; } .club i { font-style:normal; font-size:28px; font-weight:700; margin-left:16px; }
'''


def duracao_avatar():
    p = OUT / "assets/avatar.mp4"
    try:
        return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).strip())
    except Exception:
        return 0.0


def main():
    falso = "--falso" in sys.argv
    pal = palavras(falso)
    F = Fala(pal)
    total = round(max(F.fim + 0.8, duracao_avatar() if not falso else 0), 2)
    c = Cena()
    marcos = {}
    for k, p in [("cerebro", "Hoje"), ("conta", "Olha"), ("dinheiro", "dinheiro"), ("marcos", "Agora"),
                 ("plano", "Então"), ("cta", "Participante")]:
        marcos[k] = F.t(p)
    marcos["dinheiro"] -= 0.3                    # "E o dinheiro…"
    F.cur = 0.0
    seq = ["abertura", "cerebro", "conta", "dinheiro", "marcos", "plano", "cta"]
    ini = {"abertura": 0.0, **{k: marcos[k] - 0.15 for k in seq[1:]}}
    fim = {k: (ini[seq[j + 1]] + 0.3 if j + 1 < len(seq) else total) for j, k in enumerate(seq)}
    fim_meia = bloco_abertura(c, F, fim["abertura"])
    fim_meia = min(fim_meia, ini["cerebro"])
    # avatar: meia tela embaixo no quadro 0 → PiP; legenda, marca e fonte só depois
    # quadro = meia tela; o clip-path recorta até o PiP e o vídeo encolhe (só transform, sem left/top)
    cT, cR, cB, cL = AV["top"] - MEIA["top"], W - AV["left"] - AV["w"], H - AV["top"] - AV["h"], AV["left"]
    k = AV["h"] / MEIA["h"]
    dx, dy = AV["left"] + AV["w"] / 2 - MEIA["w"] / 2, AV["top"] - MEIA["top"] + AV["h"] / 2 - MEIA["h"] / 2
    c.a(f'tl.fromTo("#avw", {{clipPath:"inset(0px 0px 0px 0px round 0px)"}}, {{clipPath:"inset({cT}px {cR}px {cB}px {cL}px round 18px)", duration:0.7, ease:"power2.inOut"}}, {fim_meia - 0.7:.2f});')
    c.a(f'tl.fromTo("#av", {{x:0, y:0, scale:1}}, {{x:{dx:.0f}, y:{dy:.0f}, scale:{k:.4f}, duration:0.7, ease:"power2.inOut"}}, {fim_meia - 0.7:.2f});')
    c.a(f'tl.set("#avb", {{opacity:0}}, 0); tl.to("#avb", {{opacity:1, duration:0.3}}, {fim_meia - 0.1:.2f});')
    c.a(f'tl.set(["#marca","#fonte","#legenda"], {{opacity:0}}, 0); tl.to(["#marca","#fonte","#legenda"], {{opacity:1, duration:0.4}}, {fim_meia:.2f});')
    for k in seq[1:]:
        F.cur = marcos[k] - 0.01
        globals()["bloco_" + k](c, F, ini[k], fim[k])
    leg = legenda(c, pal, total)
    av = (f'<div id="avw" style="left:{MEIA["left"]}px;top:{MEIA["top"]}px;width:{MEIA["w"]}px;height:{MEIA["h"]}px;">'
          f'<video id="av" src="assets/avatar.mp4" data-start="0" data-duration="{total:.2f}" data-track-index="9" data-has-audio="true" data-volume="1" playsinline></video></div>'
          f'<div id="avb" style="left:{AV["left"]}px;top:{AV["top"]}px;width:{AV["w"]}px;height:{AV["h"]}px;"><div class="avtag">NEI MALDANER · INEMA</div></div>')
    html = f'''<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1080" data-height="1920">
 {"".join(c.html)}
 <div id="topo" class="clip full" data-start="0" data-duration="{total:.2f}" data-track-index="8"><div id="marca">INEMA <span>· ROBÔS E IA</span></div><div id="fonte">{FONTE}</div></div>
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
    (AQUI / "build").mkdir(exist_ok=True)
    json.dump({k: [ini[k], fim[k]] for k in seq} | {"fim_meia": fim_meia}, open(AQUI / "build/blocos.json", "w"), indent=1)
    print(f"ok {OUT/'index.html'} · {total:.1f} s · {len(c.js)} eventos · {'FALSO' if falso else 'whisper'}")


if __name__ == "__main__":
    main()
