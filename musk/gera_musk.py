#!/usr/bin/env python3
"""r7exp completo 16:9 — "Musk: dois caminhos da IA" (21/10/2026).

Reaproveita as peças do motor (motor/gera.py: Fala, Cena.foto/tags/cadeia/titulo_caminho/abre_meia/meia, estilo.css)
sem editá-lo; troca o mapa (escala log da economia: hoje → +20–30% → até ×1.000.000) e os blocos.
Uso: python3 musk/gera_musk.py [--falso]     (--falso = tempos inventados a partir das falas, só para testar o layout)
Precisa: imagens/*.png, tempos/<fala>.json, build/avatar-a.mp4 + build/segmentos-a.json (motor/monta_avatar.py musk a).
Saída: cena-a/index.html
"""
import json, re, sys, unicodedata
from pathlib import Path
import yaml

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "motor"))
import gera as G  # noqa: E402

V = "a"
GX, GY, GS = G.GX, G.GY, G.GS
Y1, DEC = 820, 100            # y de ×1 no mapa e altura de cada década (escala log)


def gx(x): return GX + x * GS
def gy(y): return GY + y * GS


def norm(s): return G.norm(s)


# ---------------------------------------------------------------- mapa
def mapa_svg(f):
    L = f["mapa"]["linhas"]
    grade = "".join(f'<path d="M220,{Y1 - k * DEC} H1700"/>' for k in range(7))
    marcas = ["×1", "×10", "×100", "×1.000", "×10.000", "×100.000", "×1.000.000"]
    ticks = "".join(f'<text class="tick" x="236" y="{Y1 - k * DEC - 10}">{m}</text>' for k, m in enumerate(marcas) if k)
    linhas, masks = "", ""
    for k, l in L.items():
        tr = f' stroke-dasharray="4 16" stroke-linecap="round" mask="url(#m{k})"' if l.get("pontilhada") else ""
        if l.get("pontilhada"):
            masks += f'<mask id="m{k}" maskUnits="userSpaceOnUse"><path id="mk{k}" d="{l["d"]}" stroke="#fff" stroke-width="40" fill="none"/></mask>'
        linhas += (f'<g id="g{k}" class="linha"><path id="l{k}" d="{l["d"]}" stroke="{l["cor"]}" stroke-width="7" fill="none" filter="url(#glow)"{tr}/>'
                   f'<text id="t{k}" class="lbl" x="1700" y="{l["y"]}" text-anchor="end" fill="{l["cor"]}" opacity="0">{l["nome"]}</text></g>')
    return f'''
<svg id="mapa" width="1920" height="1080" viewBox="0 0 1920 1080">
 <defs>
  <filter id="glow" filterUnits="userSpaceOnUse" x="-200" y="-200" width="2400" height="1600"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <marker id="ah" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#fff"/></marker>
  <marker id="ahy" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#FACC15"/></marker>
  {masks}
  <linearGradient id="nevoa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff4d4d" stop-opacity=".55"/><stop offset="1" stop-color="#ff4d4d" stop-opacity="0"/></linearGradient>
 </defs>
 <g transform="translate({GX},{GY}) scale({GS})">
  <g id="eixos" opacity="0">
   <g stroke="#1d1d26" stroke-width="2">{grade}</g>
   <path d="M220,900 V130" stroke="#fff" stroke-width="4" marker-end="url(#ah)"/>
   <path d="M220,900 H1720" stroke="#fff" stroke-width="4"/>
   <g id="ticks" fill="#c4c4cc" font-size="24">{ticks}</g>
   <text class="axis" transform="translate(170,520) rotate(-90)" text-anchor="middle">TAMANHO DA ECONOMIA (escala log)</text>
   <text class="axis" x="600" y="955" text-anchor="middle">HOJE</text>
   <text class="axis" x="1700" y="955" text-anchor="end">FUTURO · sem data</text>
  </g>
  <g id="nev" opacity="0"><rect x="980" y="120" width="740" height="330" fill="url(#nevoa)"/>
   <text x="1350" y="300" text-anchor="middle" fill="#fff" font-size="40">NINGUÉM CONTROLA</text>
   <text x="1350" y="350" text-anchor="middle" fill="#fff" font-size="40">O RESULTADO</text></g>
  {linhas}
  <g id="degrau" opacity="0"><path d="M1500,700 L1500,790" stroke="#38bdf8" stroke-width="5" marker-end="url(#ah)"/>
   <text x="1500" y="680" text-anchor="middle" fill="#fff" font-size="34">SÓ UM DEGRAU: +20% A 30%</text></g>
  <g id="aqui" opacity="0"><text x="470" y="640" text-anchor="middle" fill="#fff" font-size="40">ESTAMOS AQUI · ×1</text>
   <path d="M470,660 C470,720 520,790 578,812" stroke="#fff" stroke-width="5" fill="none" marker-end="url(#ah)"/></g>
  <circle id="dot" cx="600" cy="{Y1}" r="17" fill="#fff" filter="url(#glow)" opacity="0"/>
  <g id="qq" opacity="0" font-size="60" fill="#ddd"><text x="1660" y="560">?</text><text x="1660" y="790">?</text></g>
  <g id="empurra" opacity="0"><path id="pEmp" d="M1450,860 C1480,700 1500,520 1490,300" stroke="#FACC15" stroke-width="12" fill="none" stroke-linecap="round" marker-end="url(#ahy)"/>
   <text x="1450" y="890" text-anchor="middle" fill="#FACC15" font-size="32">VOCÊ DIRIGE</text></g>
 </g>
</svg>'''


CSS_EXTRA = """
.tick { font-family:Sora; font-weight:700; }
.bign { position:absolute; left:300px; top:150px; width:740px; padding:30px 36px; opacity:0; }
.bign .num { font-family:Sora; font-weight:800; font-size:120px; line-height:1; margin:14px 0 6px; }
.bign .sub { font-size:30px; color:#c9c9d2; line-height:1.3; }
.bign .alerta { margin-top:18px; font-family:Sora; font-weight:700; font-size:26px; color:#c9c9d2; border-top:2px solid #33333d; padding-top:14px; opacity:0; }
.cbar { display:flex; align-items:center; gap:14px; font-family:Sora; font-weight:700; font-size:26px; margin-top:16px; }
.cbar span { width:230px; flex:none; color:#c9c9d2; }
.cbar div { height:30px; border-radius:6px; width:0; }
.quote { position:absolute; left:80px; top:180px; width:800px; }
.quote .qt { font-family:Sora; font-weight:700; font-size:66px; line-height:1.15; margin-top:26px; }
.quote .qs { font-size:30px; color:#c9c9d2; margin-top:22px; }
.pills { position:absolute; left:300px; top:600px; display:flex; gap:18px; }
.pills div { font-family:Sora; font-weight:700; font-size:34px; padding:12px 24px; border-radius:14px; background:rgba(12,12,16,.9); border:2px solid #ff4d4d; opacity:0; }
.cc p { padding:0 12px 14px; font-size:24px; color:#c9c9d2; text-align:center; }
.mus { position:absolute; left:120px; top:170px; width:780px; }
"""


# ---------------------------------------------------------------- cena
class Cena(G.Cena):
    def foco_d(self, t):
        ks = ["F"]
        self.a(f'tl.to("#gF", {{opacity:0.15, duration:0.6}}, {t:.2f}); tl.to("#gD", {{opacity:1, duration:0.6}}, {t:.2f});')
        self.a(f'tl.to("#cam", {{scale:1.2, transformOrigin:"1150px {gy(812):.0f}px", duration:1.6, ease:"power2.inOut"}}, {t:.2f});')
        self.a(f'tl.to("#ticks", {{opacity:0, duration:0.4}}, {t:.2f});')

    def mapa_todo(self, t, d=1.2, ticks=True):
        self.a(f'tl.to("#cam", {{scale:1, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
        self.a(f'tl.to(["#gD","#gF"], {{opacity:1, duration:0.6}}, {t:.2f});')
        if ticks:
            self.a(f'tl.to("#ticks", {{opacity:1, duration:0.6}}, {t + 0.4:.2f});')

    def desenha(self, k, t, d=1.6):
        self.a(f'(()=>{{const p=document.getElementById("l{k}"),L=p.getTotalLength(); tl.fromTo(p,{{strokeDasharray:"0 "+L}},{{strokeDasharray:L+" 0",duration:{d},ease:"power2.out"}},{t:.2f});}})();'
               if k == "D" else
               f'(()=>{{const p=document.getElementById("l{k}"); tl.fromTo(p,{{opacity:0}},{{opacity:1,duration:0.3}},{t:.2f}); '
               f'const m=document.getElementById("mkF"),L=m.getTotalLength(); tl.fromTo(m,{{strokeDasharray:L,strokeDashoffset:L}},{{strokeDashoffset:0,duration:{d},ease:"power2.in"}},{t:.2f});}})();')
        self.a(f'tl.fromTo("#t{k}", {{opacity:0, x:20}}, {{opacity:1, x:0, duration:0.5}}, {t + d - 0.3:.2f});')

    def card(self, F, chip, cor, titulo, itens, ini, fim, track=4, left=1000):
        corpo = (f'<div class="card oque" style="left:{left}px;border-color:{cor}55"><div class="chip" style="background:{cor}2e;color:{cor}">{chip}</div>'
                 f'<div class="ctit">{titulo}</div>')
        ts = []
        for pal, ic, txt in itens:
            i = self.id("r")
            corpo += f'<div class="row" id="{i}"><div class="ic">{ic}</div><div>{txt}</div></div>'
            ts.append((i, F.t(pal)))
        corpo += "</div>"
        c = self.clip(ini, fim, corpo, track, cls="full")
        self.a(f'tl.fromTo("#{c} .card", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:0.5}}, {ini:.2f});')
        self.a(f'tl.to("#{c} .card", {{opacity:0, duration:0.4}}, {fim - 0.4:.2f});')
        for i, t in ts:
            self.a(f'tl.fromTo("#{i}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {t - 0.1:.2f});')
        return c

    def titulo(self, chip, nome, cor, ini, fim, track=7):
        i = self.id("tc")
        corpo = (f'<div class="tcam" id="{i}"><span class="chip" style="background:{cor};color:#0c0c10">{chip}</span>'
                 f'<div class="tnome" style="color:{cor}">{nome}</div></div>')
        self.clip(ini, fim, corpo, track, cls="full")
        self.a(f'tl.fromTo("#{i}", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.5}}, {ini:.2f});')
        self.a(f'tl.to("#ticks", {{opacity:0, duration:0.3}}, {ini - 0.3:.2f});')
        self.a(f'tl.to("#{i} .tnome", {{scale:0.5, transformOrigin:"0 0", duration:0.6}}, {ini + 2.6:.2f});')
        self.a(f'tl.to("#{i}", {{opacity:0, duration:0.4}}, {fim - 0.4:.2f});')

    def lista_verde(self, F, chip, itens, ini, fim, fecho=None, track=6, cor="#4ade80"):
        """multidão de pontos cinza; um sai amarelo; à direita os itens; fecho em 2 linhas, cada uma na sua palavra"""
        inner = self.id("in")
        pts = ""
        for r in range(9):
            for c in range(14):
                x, y = 140 + c * 48 + (24 if r % 2 else 0), 330 + r * 52
                pts += f'<circle class="{"pt sai" if (r, c) == (4, 7) else "pt"}" cx="{x}" cy="{y}" r="13"/>'
        corpo = (f'<div class="in opaque" id="{inner}"><svg class="multi" width="900" height="1080" viewBox="0 0 900 1080">{pts}</svg>'
                 f'<div class="mtit"><span class="chip" style="background:{cor}2a;color:{cor}">{chip}</span></div><div class="mlist">')
        ts = []
        for j, (pal, txt) in enumerate(itens):
            i = self.id("m")
            corpo += f'<div class="mi" id="{i}"><b>{j + 1}</b><span>{txt}</span></div>'
            ts.append((i, F.t(pal)))
        corpo += "</div>"
        if fecho:
            corpo += f'<div class="mfecho"><div id="{inner}fa" style="opacity:0">{fecho[0][1]}</div><div id="{inner}fb" style="color:#FACC15;opacity:0">{fecho[1][1]}</div></div>'
        corpo += "</div>"
        self.clip(ini, fim, corpo, track)
        self.cena_in_out(inner, ini, fim)
        self.esconde_mapa(ini, fim)
        self.a(f'tl.fromTo("#{inner} .pt", {{opacity:0}}, {{opacity:1, duration:0.4, stagger:0.004}}, {ini:.2f});')
        self.a(f'tl.to("#{inner} .sai", {{fill:"#FACC15", y:-60, duration:0.8, ease:"back.out(2)"}}, {ini + 0.9:.2f});')
        for i, t in ts:
            self.a(f'tl.fromTo("#{i}", {{opacity:0, x:50}}, {{opacity:1, x:0, duration:0.45, ease:"back.out(2)"}}, {t - 0.1:.2f});')
        if fecho:
            ta, tb = F.t(fecho[0][0]), F.t(fecho[1][0])
            self.a(f'tl.to("#{inner} .mlist", {{opacity:0.3, duration:0.3}}, {ta - 0.3:.2f});')
            self.entra(f"#{inner}fa", ta - 0.15, dy=16)
            self.entra(f"#{inner}fb", tb - 0.15, dy=16)
        self.a(f'tl.set(".mfecho", {{opacity:1}}, 0);')

    def quote(self, chip, cor, texto, sub, ini, fim, img=None, track=5, tsub=None):
        """frase grande na metade ESQUERDA com o avatar em meia tela à direita"""
        inner = self.id("in")
        fundo = f'<img class="foto" src="assets/{img}" alt="" style="opacity:.28;filter:blur(4px)"/>' if img else ""
        corpo = (f'<div class="in opaque" id="{inner}">{fundo}<div class="quote"><span class="chip" style="background:{cor}2e;color:{cor}">{chip}</span>'
                 f'<div class="qt">{texto}</div><div class="qs" id="{inner}s">{sub}</div></div></div>')
        self.clip(ini, fim, corpo, track)
        self.cena_in_out(inner, ini, fim)
        self.esconde_mapa(ini, fim)
        if tsub:
            self.entra(f"#{inner}s", tsub - 0.1, dy=14)
        self.meia(ini + 0.1, fim)
        self.a(f'tl.to("#fonte", {{opacity:0, duration:0.3}}, {ini:.2f}); tl.to("#fonte", {{opacity:1, duration:0.4}}, {fim:.2f});')
        return inner

    # ------------------------------------------------------------ abertura
    def abertura(self, F):
        t_capa = F.t("sou") - 0.4                        # capa parada a 1ª frase inteira (até "Não sou eu")
        inner = self.id("in")
        self.clip(0, t_capa + 0.6, f'<div class="in" id="{inner}" style="opacity:1"><img class="foto" id="{inner}f" src="assets/capa.png" alt="capa"/></div>', 3)
        self.a(f'tl.fromTo("#{inner}f", {{scale:0.93, transformOrigin:"0% 0%"}}, {{scale:0.95, transformOrigin:"0% 0%", duration:{t_capa + 0.6:.2f}, ease:"none"}}, 0);')
        self.a(f'tl.to("#{inner}", {{opacity:0, duration:0.6}}, {t_capa:.2f});')
        self.esconde_mapa(-1, t_capa + 0.6)
        tg = F.t("grafico")
        self.abre_meia(tg)                               # avatar em meia tela da capa até o gráfico
        self.a(f'tl.set(["#marca","#fonte"], {{opacity:0}}, 0); tl.to("#marca", {{opacity:1, duration:0.5}}, {t_capa:.2f}); tl.to("#fonte", {{opacity:1, duration:0.5}}, {tg:.2f});')
        # cartão da entrevista (metade esquerda, avatar à direita)
        F.cur = t_capa - F.ini
        i2 = self.id("in")
        corpo = (f'<div class="in opaque" id="{i2}"><div class="mus"><div class="chip" style="background:rgba(250,204,21,.16);color:#FACC15">A ENTREVISTA</div>'
                 f'<div class="a27t" style="font-size:96px">Elon Musk</div><div class="a27s">a Walter Isaacson, o biógrafo dele</div>')
        its = []
        for pal, ic, txt in [("digital", "💻", "caminho 1: IA digital"), ("robos", "🦾", "caminho 2: robôs")]:
            j = self.id("a"); corpo += f'<div class="row27" id="{j}"><div class="ic">{ic}</div><div>{txt}</div></div>'; its.append((j, F.t(pal)))
        tn = F.t("ninguem")
        corpo += f'<div class="ress" id="{i2}rs" style="border-color:#ff4d4d;color:#ff8a8a;font-size:34px">⚠ ninguém controla o resultado</div></div></div>'
        self.clip(t_capa, tg + 0.3, corpo, 4)
        self.cena_in_out(i2, t_capa, tg + 0.3)
        self.esconde_mapa(t_capa, tg)
        for j, t in its:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {t - 0.1:.2f});')
        self.entra(f"#{i2}rs", tn - 0.1)
        # mapa: eixos no "gráfico", ponto no "estamos"
        self.a(f'tl.fromTo("#eixos", {{opacity:0}}, {{opacity:1, duration:0.8}}, {tg:.2f});')
        te = F.t("estamos")
        self.a(f'tl.fromTo("#dot", {{opacity:0, attr:{{r:4}}}}, {{opacity:1, attr:{{r:17}}, duration:0.5, ease:"back.out(3)"}}, {te:.2f});')
        self.a(f'tl.fromTo("#aqui", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.6}}, {te + 0.3:.2f});')
        self.a(f'tl.fromTo("#qq", {{opacity:0}}, {{opacity:1, duration:0.5}}, {te + 1.0:.2f});')
        # Marcos hoje
        tm = F.t("marcos"); tc = F.t("caminho", depois=tm)
        self.a(f'tl.to("#qq", {{opacity:0, duration:0.3}}, {tm - 0.5:.2f}); tl.to("#qq", {{opacity:1, duration:0.4}}, {tc + 0.2:.2f});')
        self.foto(tm - 0.2, tc + 0.2, "marcos-2026.png", carimbo="MARCOS · HOJE", sub="O PERSONAGEM")
        F.cur = tm - F.ini
        self.tags(F, [("40", "40 anos"), ("oficina", "dono de oficina mecânica"), ("sol", "trabalha de sol a sol")], tc + 0.2)
        # prévia: mapa com "?" e a faixa
        tf = F.fim
        corpo = '<div class="full"><div class="ban" id="banM">O MESMO DIA DELE EM CADA CAMINHO</div></div>'
        self.clip(tc, tf + 0.5, corpo, 5, cls="full")
        self.entra("#banM", tc + 0.2)
        self.a(f'tl.to("#aqui", {{opacity:0, duration:0.4}}, {tc:.2f});')

    # ------------------------------------------------------------ caminho 1: IA digital
    def digital(self, F, prox):
        t0 = F.ini
        self.a(f'tl.to("#qq", {{opacity:0, duration:0.4}}, {t0 - 0.4:.2f});')
        self.desenha("D", t0 - 0.2)
        self.foco_d(t0 + 0.4)
        tq = F.t("que"); tv = F.t("marcos")
        self.titulo("CAMINHO 1", "IA DIGITAL", "#38bdf8", t0, tv)
        F.cur = tq - F.ini
        self.card(F, "O QUE É", "#38bdf8", "Programas que pensam",
                  [("agentes", "🤖", "agentes de IA"), ("pesquisam", "🔎", "pesquisam e programam"), ("analisam", "📊", "analisam e atendem")], tq + 0.3, tv - 0.1)
        tqt = F.t("quanto", depois=tv)
        F.cur = tv - F.ini
        self.foto(tv - 0.2, tqt + 0.2, "digital-marcos.png", carimbo="MARCOS · IA DIGITAL", sub="O MESMO MARCOS")
        F.cur = tv - F.ini
        self.tags(F, [("telefone", "📞 agente atende o telefone"), ("orcamento", "orçamento sai sozinho"), ("agenda", "agenda se organiza"),
                      ("horas", "✓ ganha horas no dia"), ("conserta", "o carro ainda é com ele")], tqt + 0.2)
        # quanto muda: barras + degrau no mapa
        tl_ = F.t("leva", depois=tqt)
        F.cur = tqt - F.ini
        tv2 = F.t("20"); tdg = F.t("degrau")
        i = self.id("bn")
        corpo = (f'<div class="card bign" id="{i}" style="border-color:#38bdf855"><span class="chip" style="background:#38bdf82e;color:#38bdf8">ESTIMATIVA DO MUSK</span>'
                 f'<div class="num" style="color:#38bdf8;font-size:96px">+20% a 30%</div><div class="sub">na produção da economia</div>'
                 f'<div class="cbar"><span>HOJE</span><div class="b1" style="background:#9a9aa6"></div></div>'
                 f'<div class="cbar"><span>COM IA DIGITAL</span><div class="b2" style="background:#38bdf8"></div></div>'
                 f'<div class="alerta" id="{i}a">sem cronograma verificável</div></div>')
        self.clip(tqt, tl_ + 0.1, corpo, 4, cls="full")
        self.a(f'tl.fromTo("#{i}", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.5}}, {tqt:.2f});')
        self.a(f'tl.fromTo("#{i} .b1", {{width:0}}, {{width:250, duration:0.6}}, {tqt + 0.4:.2f});')
        self.a(f'tl.fromTo("#{i} .b2", {{width:0}}, {{width:310, duration:0.9}}, {tv2:.2f});')
        self.a(f'tl.fromTo("#{i}a", {{opacity:0}}, {{opacity:1, duration:0.4}}, {tv2 + 1.2:.2f});')
        self.a(f'tl.to("#{i}", {{opacity:0, duration:0.4}}, {tl_ - 0.3:.2f});')
        self.a(f'tl.fromTo("#degrau", {{opacity:0}}, {{opacity:1, duration:0.5}}, {tdg - 0.6:.2f});')
        # o que leva até lá
        tm = F.t("tras", depois=tl_)
        F.cur = tl_ - F.ini
        self.cadeia(F, [("modelos", "MODELOS MELHORES", "cada vez mais capazes"), ("agentes", "AGENTES", "ligados às ferramentas"),
                        ("empresas", "EMPRESAS QUE APRENDEM", "→ +20% a 30%")], "digital-agentes.png", tl_ - 0.2, tm - 1.0, cor="#38bdf8", nome="IA DIGITAL")
        self.a(f'tl.to("#degrau", {{opacity:0, duration:0.3}}, {tl_:.2f});')
        F.cur = tm - F.ini - 1.5
        self.lista_verde(F, "COMO NÃO FICAR PARA TRÁS · IA DIGITAL", [("agentes", "aprenda agora a montar agentes para o seu trabalho")],
                         tm - 1.2, prox - 0.1, fecho=[("espera", "Quem espera vira cliente."), ("aprende", "Quem aprende vira dono.")])

    # ------------------------------------------------------------ caminho 2: robôs
    def robos(self, F, prox):
        t0 = F.ini
        tmaior = F.t("maior")
        self.mapa_todo(t0 - 0.4, ticks=False)
        self.a(f'tl.to("#gD", {{opacity:0.35, duration:0.6}}, {t0:.2f});')
        self.desenha("F", tmaior - 0.3, d=2.2)
        tq = F.t("que"); tv = F.t("marcos")
        self.titulo("CAMINHO 2", "ROBÔS", "#FACC15", t0, tv)
        F.cur = tq - F.ini
        self.card(F, "O QUE É", "#FACC15", "Inteligência com mãos",
                  [("montam", "🦾", "montam, constroem, carregam, consertam"), ("fabricas", "🏭", "fábricas, laboratórios e obras")], tq + 0.3, tv - 0.1)
        tvi = F.t("visao", depois=tv)
        F.cur = tv - F.ini
        self.foto(tv - 0.2, tvi + 0.2, "robos-oficina.png", carimbo="MARCOS · ROBÔS", sub="O MESMO MARCOS")
        F.cur = tv - F.ini
        self.tags(F, [("oleo", "robô troca o óleo"), ("motor", "desmonta o motor"), ("noite", "trabalha a noite inteira"),
                      ("melhor", "✕ ele já não é o melhor")], tvi + 0.2)
        # a previsão (frase à esquerda, avatar em meia tela)
        tqt = F.t("quanto", depois=tvi)
        tp = F.t("previsao", depois=tvi)
        self.quote("A PREVISÃO DO MUSK", "#FACC15", "Humanos deixam de ser os melhores em qualquer trabalho.",
                   "até nos criativos · é uma previsão, não um fato", tvi - 0.2, tqt + 0.2, img="robos-oficina.png", tsub=tp)
        # quanto muda: contador até ×1.000.000 no mapa inteiro
        tl_ = F.t("leva", depois=tqt)
        F.cur = tqt - F.ini
        tmi = F.t("milhao"); tdi = F.t("dinheiro")
        i = self.id("bn")
        corpo = (f'<div class="card bign" id="{i}" style="border-color:#FACC1555"><span class="chip" style="background:#FACC152e;color:#FACC15">ESTIMATIVA DO MUSK</span>'
                 f'<div class="num" style="color:#FACC15">×<i id="{i}n" style="font-style:normal">1</i></div><div class="sub">até um milhão de vezes a economia de hoje, com robôs + espaço</div>'
                 f'<div class="alerta" id="{i}a">se hoje fosse 1 cm, isso seria 10 km · especulativo, sem cronograma</div></div>'
                 f'<div class="pills" id="{i}p"><div>💰 dinheiro perde peso</div><div>💼 emprego perde peso</div></div>')
        self.clip(tqt, tl_ + 0.1, corpo, 4, cls="full")
        self.mapa_todo(tqt)
        self.a(f'tl.to("#gF", {{opacity:1, duration:0.4}}, {tqt:.2f}); tl.to("#lF", {{attr:{{"stroke-width":11}}, duration:0.6}}, {tqt:.2f});')
        self.a(f'tl.fromTo("#{i}", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.5}}, {tqt:.2f});')
        self.a(f'(()=>{{const o={{v:0}}; tl.to(o, {{v:6, duration:2.2, ease:"power2.in", onUpdate:()=>{{document.getElementById("{i}n").textContent=Math.round(Math.pow(10,o.v)).toLocaleString("pt-BR")}}}}, {tmi - 1.6:.2f});}})();')
        self.a(f'tl.fromTo("#{i}a", {{opacity:0}}, {{opacity:1, duration:0.4}}, {tmi + 1.0:.2f});')
        self.a(f'tl.fromTo("#{i}p div", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.4, stagger:0.5}}, {tdi - 0.1:.2f});')
        self.a(f'tl.to("#{i}", {{opacity:0, duration:0.4}}, {tl_ - 0.3:.2f});')
        # o que leva até lá
        tm = F.t("tras", depois=tl_)
        F.cur = tl_ - F.ini
        self.cadeia(F, [("producao", "PRODUÇÃO AUTOMATIZADA", "robôs que fazem robôs"), ("energia", "ENERGIA DO SOL", "captada no espaço"),
                        ("recursos", "RECURSOS DE FORA DA TERRA", "→ até ×1.000.000")], "robos-espaco.png", tl_ - 0.2, tm - 1.0, cor="#FACC15", nome="NA VISÃO DELE")
        F.cur = tm - F.ini - 1.5
        self.lista_verde(F, "COMO NÃO FICAR PARA TRÁS · ROBÔS", [("aprende", "entenda como um robô aprende"),
                                                                  ("simulador", "do real para o simulador, e de volta (Real2Sim)")],
                         tm - 1.2, prox - 0.1, fecho=[("entende", "Quem entende o robô"), ("dirige", "dirige o robô.")])

    # ------------------------------------------------------------ 3: o risco
    def risco(self, F, prox):
        t0 = F.ini
        self.mapa_todo(t0 - 0.4, ticks=False)
        self.a(f'tl.fromTo("#nev", {{opacity:0}}, {{opacity:1, duration:1.2}}, {t0 + 0.4:.2f});')
        tc = F.t("corrida")
        self.titulo("O RISCO", "ELE MESMO ADMITE", "#ff4d4d", t0, tc)
        ta = F.t("aposta", depois=tc)
        F.cur = tc - F.ini - 0.2
        self.cadeia(F, [("corrida", "A CORRIDA NÃO PARA", "ele não conseguiria pará-la"), ("influenciar", "ELE ENTROU", "para tentar influenciar"),
                        ("controlar", "CONTROLAR?", "inteligências milhares ou milhões de vezes maiores: improvável")],
                    "risco-corrida.png", tc - 0.2, ta - 0.4, cor="#ff4d4d", nome="O RISCO")
        tl_ = F.t("laboratorios", depois=ta)
        F.cur = ta - F.ini
        self.a(f'tl.to("#nev", {{opacity:0, duration:0.5}}, {ta - 0.6:.2f});')
        self.card(F, "A APOSTA DELE", "#4ade80", "IA que busca a verdade",
                  [("verdade", "🔍", "busca a verdade"), ("contradicoes", "⚖️", "evita contradições"), ("curiosidade", "✨", "tem curiosidade pela humanidade")],
                  ta - 0.2, tl_ - 0.1)
        te = F.t("erro", depois=tl_)
        F.cur = tl_ - F.ini
        self.foto(tl_ - 0.2, te + 0.2, "aposta-labs.png", carimbo="FISCALIZAÇÃO MÚTUA", sub="A PROPOSTA DELE")
        F.cur = tl_ - F.ini
        self.tags(F, [("laboratorios", "laboratórios fiscalizando uns aos outros"), ("semana", "reuniões toda semana"),
                      ("antecipado", "acesso antecipado aos modelos rivais"), ("perigo", "✓ achar o perigo antes do lançamento")], te + 0.2)
        tm = F.t("marcos", depois=te)
        F.cur = te - F.ini
        tg = F.t("garantia")
        self.quote("ELE RECONHECE UM ERRO", "#ff4d4d", "Ficou tempo demais na política, longe das empresas.",
                   "É uma aposta, não uma garantia.", te - 0.2, tm, tsub=tg - 1.0)
        F.cur = tm - F.ini
        self.lista_verde(F, "E O MARCOS?", [("decide", "não decide essa corrida"), ("assistir", "vai só assistir?"),
                                           ("supervisionar", "ou aprender a supervisionar a máquina")], tm - 0.2, prox - 0.1)
        self.a(f'tl.to("#nev", {{opacity:0, duration:0.4}}, {prox - 0.3:.2f});')

    # ------------------------------------------------------------ final
    def final(self, F, fim_total):
        t0 = F.ini
        tf = F.t("fazer")
        cards = [("marcos-2026.png", "#9a9aa6", "HOJE", "corre de sol a sol", None),
                 ("digital-marcos.png", "#38bdf8", "IA DIGITAL", "ganha tempo", "digital"),
                 ("robos-oficina.png", "#FACC15", "ROBÔS", "perde o posto de melhor", "robos"),
                 ("risco-corrida.png", "#ff4d4d", "O RISCO", "ninguém garante o controle", "controle")]
        inner = self.id("in")
        corpo = f'<div class="in opaque" id="{inner}"><div class="cmp">'
        ts = []
        F.cur = 0.0
        for im, cor, nome, sub, pal in cards:
            j = self.id("cc")
            corpo += f'<div class="cc" id="{j}" style="border-top:8px solid {cor}"><img src="assets/{im}" alt=""/><span style="color:{cor}">{nome}</span><p>{sub}</p></div>'
            ts.append((j, F.t(pal) if pal else t0 + 0.3))
        corpo += '</div><div class="frase" id="%sfr"><div>Dois caminhos.</div><div style="color:#FACC15">O mesmo Marcos.</div></div></div>' % inner
        self.clip(t0, tf + 0.2, corpo, 4)
        self.cena_in_out(inner, t0, tf + 0.2)
        self.esconde_mapa(t0, tf)
        for j, t in ts:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.5, ease:"back.out(2)"}}, {t - 0.15:.2f});')
        self.a(f'tl.set("#{inner}fr", {{opacity:0}}, 0);')
        # passos
        F.cur = tf - F.ini
        tb = F.t("basta")
        F.cur = tf - F.ini
        i2 = self.id("in")
        corpo = f'<div class="in opaque" id="{i2}"><div class="chip" style="position:absolute;left:420px;top:130px;background:rgba(74,222,128,.16);color:#4ade80">O QUE FAZER, HOJE</div><div class="passos">'
        ts = []
        for pal, num, txt in [("agentes", "1", "crie agentes agora: atendimento, vendas, processos"),
                              ("robos", "2", "prepare-se para os robôs: simulação e Real2Sim"),
                              ("dirigir", "3", "dirija sistemas: intenção, contexto, agentes, validação, supervisão")]:
            j = self.id("p"); corpo += f'<div class="ps" id="{j}"><b>{num}</b><span>{txt}</span></div>'; ts.append((j, F.t(pal)))
        corpo += "</div></div>"
        self.clip(tf, tb + 0.2, corpo, 5)
        self.cena_in_out(i2, tf, tb + 0.2)
        self.esconde_mapa(tf, tb)
        for j, t in ts:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:0.45, ease:"back.out(2)"}}, {t - 0.15:.2f});')
            self.a(f'tl.to("#{j} b", {{backgroundColor:"#4ade80", duration:0.3}}, {t + 0.3:.2f});')
        # não basta usar (frase à esquerda + avatar em meia tela)
        F.cur = tb - F.ini
        tc = F.t("construir"); tes = F.t("escolher"); tla = F.t("lado")
        self.quote("NÃO BASTA USAR A IA", "#FACC15", "Construir, coordenar e controlar.", "enquanto ainda dá para escolher",
                   tb - 0.2, tla - 0.3, img="final-marcos.png", tsub=tes)
        # CTA no mapa: você dirige
        self.mapa_todo(tla - 0.6)
        self.a(f'tl.fromTo("#empurra", {{opacity:0}}, {{opacity:1, duration:0.3}}, {tla:.2f});')
        self.a(f'(()=>{{const p=document.getElementById("pEmp"),L=p.getTotalLength(); tl.fromTo(p,{{strokeDasharray:L,strokeDashoffset:L}},{{strokeDashoffset:0,duration:1.0,ease:"power2.out"}},{tla + 0.1:.2f});}})();')
        tclub = F.t("inema", depois=tla, obrig=False) or tla + 4
        i3 = self.id("in")
        corpo = (f'<div class="in" id="{i3}"><div class="full" style="background:rgba(12,12,16,.86)"></div><div class="fim"><h2>De que lado você quer estar?</h2>'
                 f'<div class="sub">comenta: “eu vou aprender a dirigir” 👇</div><div class="pill" id="{i3}p">inema.club</div></div>'
                 f'<div class="printc" id="{i3}pr"><img src="assets/print-inema.png" alt="inema.club"/><span>aberto e gratuito · inema.club</span></div></div>')
        self.clip(tla + 1.2, fim_total, corpo, 6)
        self.a(f'tl.fromTo("#{i3}", {{opacity:0}}, {{opacity:1, duration:0.6}}, {tla + 1.2:.2f});')
        self.entra(f"#{i3}p", tclub - 0.1)
        self.a(f'tl.fromTo("#{i3}pr", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.6, ease:"back.out(2)"}}, {tclub:.2f});')


def legenda(cena, palavras, fim_total):
    KEY = {"robos": "#FACC15", "robo": "#FACC15", "digital": "#38bdf8", "controla": "#ff4d4d", "controle": "#ff4d4d",
           "milhao": "#FACC15", "dirigir": "#FACC15", "dirige": "#FACC15", "corrida": "#ff4d4d", "erro": "#ff4d4d"}
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
        spans = " ".join(f'<b>{re.sub(r"[.,:]$", "", w["word"].strip())}</b>' for w in gr)
        i = f"cap{k}"
        html.append(f'<div class="cap" id="{i}">{spans}</div>')
        cena.a(f'tl.set("#{i}", {{opacity:1}}, {ini:.2f}); tl.set("#{i}", {{opacity:0}}, {fim:.2f});')
        for j, w in enumerate(gr):
            cor = KEY.get(norm(w["word"]), "#FACC15")
            cena.a(f'tl.set("#{i} b:nth-child({j + 1})", {{color:"{cor}"}}, {w["t"]:.2f}); tl.set("#{i} b:nth-child({j + 1})", {{color:"#fff"}}, {min(fim, w["t"] + 0.45):.2f});')
    return "".join(html)


CORRIGE = {"ia": "IA", "Ia": "IA", "IA.": "IA."}


def falso(ordem):
    """tempos inventados (14,5 car/s) para testar o layout antes do avatar"""
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
    cena.digital(falas[ordem[1]], ini[2])
    cena.robos(falas[ordem[2]], ini[3])
    cena.risco(falas[ordem[3]], ini[4])
    cena.final(falas[ordem[4]], total)
    pal = []
    for s in seg["segmentos"]:
        for x in falas[s["fala"]].w:
            wd = CORRIGE.get(x["word"].strip(), x["word"].strip())
            if pal and wd[:1] in "-." and len(wd) > 1:
                pal[-1]["word"] += wd; continue
            pal.append({"word": wd, "t": round(s["ini"] + x["start"], 2)})
    leg = legenda(cena, pal, total)
    pip = G.PIP
    av = (f'<div id="avw" style="left:{pip["left"]}px;top:{pip["top"]}px;width:{pip["w"]}px;height:{pip["h"]}px;">'
          f'<video id="av" src="assets/avatar-{V}.mp4" data-start="0" data-duration="{seg["total"]:.2f}" data-track-index="9" data-has-audio="true" data-volume="1" playsinline></video>'
          f'<div class="avtag">Nei Maldaner · INEMA</div></div>')
    html = f'''<!doctype html>
<html lang="pt-BR" data-resolution="landscape">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{G.CSS}{CSS_EXTRA}</style></head>
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
    out = AQUI / f"cena-{V}"
    (out / "assets").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"ok {out/'index.html'} · {total:.1f} s · {len(cena.js)} eventos")


if __name__ == "__main__":
    main()
