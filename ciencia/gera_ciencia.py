#!/usr/bin/env python3
"""r7exp completo 16:9 — "A IA resolveu 100 anos de ciência?" (28/10/2026). Molde: bancos/gera_bancos.py.

Mapa = as 4 peças lado a lado (física 1954 · computação 1999 · matemática 1917 · você); cada bloco muda de estado:
0 "?" · 1 o fato · 2 o limite · 3 o que fazer. O Rafael (41, professor de matemática) atravessa as 4 peças.
Peça 4 tem o gráfico dos anos em que cada pergunta ficou aberta (109 · 72 · 27), palco cheio, fonte embaixo.
Reaproveita peças do motor/musk/php/bots sem editá-los (mesmo esquema do bots/gera_bots.py).
Uso: python3 ciencia/gera_ciencia.py [--falso] [limpo]
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
#        slug       nome                ícone      sub         cor        fato (2 linhas)                  risco (2 linhas)                o que fazer (2 linhas)
PECAS = [("fisica", "FÍSICA", "⚛️", "1954", "#60a5fa", ("A TEORIA", "EXISTE"), ("SÓ A", "METADE"), ("CONFERIR", "O RESTO")),
         ("computacao", "COMPUTAÇÃO", "💻", "1999", "#c084fc", ("A HIPÓTESE", "CAIU"), ("AINDA", "LENTO"), ("SEPARAR", "MEDO E FATO")),
         ("matematica", "MATEMÁTICA", "📐", "1917", "#fb923c", ("TODAS AS", "DIMENSÕES"), ("DIFÍCIL DE", "ENTENDER"), ("EXPLICAR", "A PROVA")),
         ("voce", "VOCÊ", "🧑", "2026", AMAR, ("CHEGA NO", "SEU TRABALHO"), ("SÓ", "ASSISTIR"), ("COORDENAR", "A MÁQUINA"))]
TX0, TSTEP, TW, TY, TH = 400, 345, 315, 300, 520

CSS_GRAF = """
.graf { position:absolute; left:400px; right:70px; top:120px; bottom:60px; }
.graf .gt { font-family:Sora; font-weight:700; font-size:52px; color:#fff; line-height:1.1; margin-top:16px; }
.graf .gs { font-size:28px; color:#9a9aa6; margin-top:10px; }
.gl { display:flex; align-items:center; gap:24px; margin-top:46px; opacity:0; }
.gl .gn { width:300px; font-family:Sora; font-weight:700; font-size:32px; line-height:1.15; color:#e5e7eb; }
.gl .gn small { display:block; font-family:Inter, sans-serif; font-weight:600; font-size:22px; color:#9a9aa6; }
.gl .gtr { flex:1; height:96px; background:#1c1c24; border-radius:14px; overflow:hidden; }
.gl .gb { height:100%; border-radius:14px; transform:scaleX(0); transform-origin:0 50%; }
.gl .gv { width:230px; font-family:Sora; font-weight:800; font-size:76px; text-align:right; opacity:0; }
.gfonte { margin-top:48px; font-size:26px; color:#9a9aa6; }
.pics { font-size:120px; }
"""


def gy(y): return GY + y * GS


# ---------------------------------------------------------------- mapa: as 4 peças
def mapa_svg(f):
    tiles, dots = "", ""
    for i, (slug, nome, ic, sub, cor, fato, risco, faz) in enumerate(PECAS):
        x = TX0 + i * TSTEP; cx = x + TW / 2
        def duas(e, linhas, c, y0, fs, sinal=None):
            s = f'<g id="e{e}{i}" opacity="0">'
            if sinal:
                s += f'<text x="{cx}" y="{TY + 345}" text-anchor="middle" font-size="60" fill="{c}" font-weight="800">{sinal}</text>'
            s += (f'<text x="{cx}" y="{TY + y0}" text-anchor="middle" font-size="{fs}" fill="{c}" font-weight="800">{linhas[0]}</text>'
                  f'<text x="{cx}" y="{TY + y0 + fs + 8}" text-anchor="middle" font-size="{fs}" fill="{c}" font-weight="800">{linhas[1]}</text></g>')
            return s
        est = (f'<g id="e0{i}"><text x="{cx}" y="{TY + 420}" text-anchor="middle" font-size="96" fill="#6b6b78">?</text></g>'
               + duas(1, fato, cor, 385, 38) + duas(2, risco, VERM, 410, 31, "✕") + duas(3, faz, VERDE, 410, 31, "✓"))
        if ic == "logo":
            icone = f'<image href="assets/logo-openai.png" x="{cx - 75}" y="{TY + 40}" width="150" height="140" preserveAspectRatio="xMidYMid meet"/>'
        else:
            icone = f'<text x="{cx}" y="{TY + 165}" text-anchor="middle" font-size="120">{ic}</text>'
        tiles += (f'<g class="tile" id="v{i}"><rect id="vr{i}" x="{x}" y="{TY}" width="{TW}" height="{TH}" rx="22" fill="#15151c" stroke="#3a3a46" stroke-width="5"/>'
                  f'{icone}<text x="{cx}" y="{TY + 250}" text-anchor="middle" font-size="{29 if len(nome) > 12 else 36}" class="vv">{nome}</text>{est}</g>')
        dots += (f'<circle cx="{cx}" cy="{TY + TH + 70}" r="14" fill="{AMAR}"/>'
                 f'<text x="{cx}" y="{TY + TH + 125}" text-anchor="middle" font-size="30" fill="#c9c9d2">{sub}</text>')
    return f'''
<svg id="mapa" width="1920" height="1080" viewBox="0 0 1920 1080">
 <g transform="translate({GX},{GY}) scale({GS})">
  <g id="ticks" opacity="0">
   <text x="400" y="190" font-size="58" fill="#fff" font-weight="800" class="vv"><tspan fill="{AMAR}">3 PERGUNTAS</tspan> + VOCÊ</text>
   <text x="400" y="240" font-size="28" fill="#9a9aa6">da física até o seu trabalho</text>
  </g>
  <g id="eixos" opacity="0">
   {tiles}
   <path d="M{TX0},{TY + TH + 70} H{TX0 + 3 * TSTEP + TW}" stroke="#3a3a46" stroke-width="5"/>
   {dots}
  </g>
 </g>
</svg>'''


class Cena(P.Cena):
    def zoom_tile(self, t, i, z=1.08):
        # origem presa à esquerda: o quadro cresce para a direita e não entra sob o PiP do avatar
        x0 = GX + TX0 * GS
        cx = min(GX + (TX0 + i * TSTEP + TW / 2) * GS, (x0 * z - 380) / (z - 1))
        self.a(f'tl.to("#cam", {{scale:{z}, transformOrigin:"{cx:.0f}px {gy(TY + TH / 2):.0f}px", duration:1.4, ease:"power2.inOut"}}, {t:.2f});')
        self.a(f'tl.to("#ticks", {{opacity:0, duration:0.4}}, {t:.2f});')

    def destaca(self, t, i):
        cor = PECAS[i][4]
        outros = [f"#v{j}" for j in range(4) if j != i]
        self.a(f'tl.to({json.dumps(outros)}, {{opacity:0.25, duration:0.5}}, {t:.2f}); tl.to("#v{i}", {{opacity:1, duration:0.5}}, {t:.2f});')
        self.a(f'tl.to("#vr{i}", {{attr:{{stroke:"{cor}"}}, duration:0.4}}, {t:.2f});')

    def todos(self, t):
        self.a(f'tl.to(".tile", {{opacity:1, duration:0.5}}, {t:.2f});')

    def risco(self, F, i, t, fim):
        """mapa volta, o bloco vira vermelho e a faixa diz o limite"""
        r = PECAS[i][6]
        self.mapa_todo(t - 0.3, ticks=False)
        self.todos(t - 0.3)
        self.zoom_tile(t - 0.2, i, z=1.06)
        self.estado(t + 0.2, [i], 2, VERM, "#2a0f12")
        self.faixa(f"LIMITE · {r[0]} {r[1]}", t - 0.1, fim, cor=VERM)

    def abre(self, F, i, tci):
        """entra na peça i: mapa inteiro, zoom no bloco, estado 1 e título"""
        t0 = F.ini
        cor = PECAS[i][4]
        self.mapa_todo(t0 - 0.4, ticks=False)
        self.todos(t0 - 0.4)
        self.zoom_tile(t0 + 0.1, i)
        self.destaca(t0 + 0.1, i)
        self.estado(t0 + 0.8, [i], 1, cor, "#1c1c24")
        self.titulo(f"PEÇA {i + 1} DE 4", PECAS[i][1], cor, t0, tci)

    def rafael(self, F, ini_pal, fim, img, carimbo, tags, depois=None):
        F.cur = (depois - F.ini - 0.02) if depois else F.cur
        tfo = F.t(ini_pal)
        self.foto(tfo - 0.2, fim + 0.2, img, carimbo=carimbo, sub="O MESMO RAFAEL")
        F.cur = tfo - F.ini - 0.02
        self.tags(F, tags, fim + 0.2)
        self.esconde_mapa(tfo - 0.2, fim + 0.2)
        return tfo

    # ------------------------------------------------------------ gráfico do teste (peça 2)
    def grafico(self, F, ini, fim):
        linhas = [("agulha", "Matemática", "a agulha · 1917", 109, "#fb923c"),
                  ("fisica", "Física", "a massa · 1954", 72, "#60a5fa"),
                  ("computacao", "Computação", "o atalho · 1999", 27, "#c084fc")]
        F.cur = ini - F.ini - 0.02
        inner = self.id("in")
        corpo = (f'<div class="in opaque" id="{inner}"><div class="graf">'
                 f'<span class="chip" style="background:rgba(250,204,21,.16);color:{AMAR}">ANOS SEM RESPOSTA</span>'
                 f'<div class="gt">Fechadas em <span style="color:{AMAR}">6 semanas</span></div>'
                 f'<div class="gs">anos que cada pergunta ficou aberta até a IA responder (set–out/2026)</div>')
        ts = []
        for pal, nome, sub, v, cor in linhas:
            j = self.id("g")
            corpo += (f'<div class="gl" id="{j}"><div class="gn">{nome}<small>{sub}</small></div>'
                      f'<div class="gtr"><div class="gb" id="{j}b" style="background:{cor}"></div></div>'
                      f'<div class="gv" id="{j}v" style="color:{cor}">{v}</div></div>')
            ts.append((j, F.t(pal), v))
        corpo += '<div class="gfonte">fonte: OpenAI, 26/10/2026 · física: só a 1ª metade · provas em revisão por cientistas de fora</div></div></div>'
        self.clip(ini, fim, corpo, 5)
        self.cena_in_out(inner, ini, fim)
        self.esconde_mapa(ini, fim + 0.5)
        for j, t, v in ts:
            self.a(f'tl.to("#{j}", {{opacity:1, duration:0.3}}, {t - 0.35:.2f});')
            self.a(f'tl.fromTo("#{j}b", {{scaleX:0}}, {{scaleX:{v / 120:.3f}, duration:1.1, ease:"power2.out"}}, {t - 0.25:.2f});')
            self.a(f'tl.to("#{j}v", {{opacity:1, duration:0.4}}, {t + 0.6:.2f});')

    # ------------------------------------------------------------ abertura
    def abertura(self, F):
        t_capa = F.t("calma") - 0.2                      # capa parada a 1ª frase inteira
        inner = self.id("in")
        self.clip(0, t_capa + 0.6, f'<div class="in" id="{inner}" style="opacity:1"><img class="foto" id="{inner}f" src="assets/capa-quadro0.png" alt="capa"/></div>', 3)
        self.a(f'tl.fromTo("#{inner}f", {{scale:0.93, transformOrigin:"0% 0%"}}, {{scale:0.95, transformOrigin:"0% 0%", duration:{t_capa + 0.6:.2f}, ease:"none"}}, 0);')
        self.a(f'tl.to("#{inner}", {{opacity:0, duration:0.6}}, {t_capa:.2f});')
        self.esconde_mapa(-1, t_capa + 0.6)
        tg = F.t("mapa")
        self.abre_meia(tg)
        self.a(f'tl.set(["#marca","#fonte"], {{opacity:0}}, 0); tl.to("#marca", {{opacity:1, duration:0.5}}, {t_capa:.2f}); tl.to("#fonte", {{opacity:1, duration:0.5}}, {tg:.2f});')
        F.cur = t_capa - F.ini - 0.02
        i2 = self.id("in")
        corpo = (f'<div class="in opaque" id="{i2}"><div class="mus"><div class="chip" style="background:rgba(250,204,21,.16);color:{AMAR}">O QUE ACONTECEU</div>'
                 f'<div class="a27t" style="font-size:76px">Não é mágica</div>')
        its = []
        for pal, ic, txt, cor in [("magica", "✕", "não é mágica", VERM), ("tudo", "✕", "não resolveu tudo", VERM),
                                  ("ramos", "✓", "mexeu em 3 ramos da ciência", VERDE), ("vez", "⚡", "tudo de uma vez, em semanas", AMAR)]:
            j = self.id("a")
            corpo += f'<div class="row27" id="{j}"><div class="ic" style="color:{cor}">{ic}</div><div style="color:{cor}">{txt}</div></div>'
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
        self.a(f'tl.fromTo("#ticks", {{opacity:0}}, {{opacity:1, duration:0.6}}, {tg:.2f});')
        self.a(f'tl.fromTo("#eixos", {{opacity:0}}, {{opacity:1, duration:0.4}}, {tg:.2f});')
        self.a(f'tl.fromTo(".tile", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.45, stagger:0.15}}, {tg + 0.1:.2f});')
        tc = F.t("rafael", depois=tg); tv = F.t("vamos", depois=tc)
        self.foto(tc - 0.2, tv + 0.2, "rafael-hoje.png", carimbo="RAFAEL · HOJE", sub="O PERSONAGEM")
        F.cur = tc - F.ini - 0.02
        self.tags(F, [("professor", "professor de matemática · 41 anos"), ("perguntas", "✕ “certas perguntas não têm resposta”")], tv + 0.2)
        self.faixa("O QUE MUDA PARA ELE · E PARA VOCÊ", tv, F.fim + 0.5)

    # ------------------------------------------------------------ as 4 peças
    def fisica(self, F, prox):
        F.cur = 0; tci = F.t("fisico")
        self.abre(F, 0, tci)
        F.cur = tci - F.ini - 0.02; tfo = F.t("rafael", depois=tci)
        F.cur = tci - F.ini - 0.02
        self.card(F, "O QUE É", PECAS[0][4], "Yang-Mills · desde 1954",
                  [("pauli", "❓", "Pauli: de onde vem a massa?"), ("quarks", "⚛️", "explica os quarks dentro de você"),
                   ("nobel", "🏅", "a IA provou · um Nobel confere")], tci - 0.2, tfo - 0.1)
        self.esconde_mapa(tci - 0.8, tfo + 0.6)
        F.cur = tfo - F.ini - 0.02; tfr = F.t("atencao", depois=tfo)
        self.rafael(F, "rafael", tfr, "fisica-rafael.png", "RAFAEL · A FÍSICA", [("lugar", "✓ a pergunta do livro mudou de lugar")], depois=tci)
        self.risco(F, 0, tfr, prox + 0.1)

    def computacao(self, F, prox):
        F.cur = 0; tci = F.t("imagine")
        self.abre(F, 1, tci)
        F.cur = tci - F.ini - 0.02; tia = F.t("achou", depois=tci)
        F.cur = tci - F.ini - 0.02
        self.card(F, "O PROBLEMA", PECAS[1][4], "Não existe atalho?",
                  [("jantar", "🍽️", "jantar com 100 convidados e regras"), ("conferir", "✓", "conferir é fácil · achar é difícil"),
                   ("centenas", "📚", "centenas de artigos em cima disso")], tci - 0.2, tia - 0.3)
        self.esconde_mapa(tci - 0.8, tia)
        F.cur = tia - F.ini - 0.02; tfo = F.t("rafael", depois=tia)
        F.cur = tia - F.ini - 0.02
        self.card(F, "A IA", VERDE, "Achou o atalho",
                  [("achou", "⚡", "algoritmo novo, verificado"), ("caiu", "✕", "a hipótese caiu"),
                   ("autores", "🔍", "os próprios autores revisam")], tia - 0.2, tfo - 0.1)
        self.esconde_mapa(tia - 0.4, tfo + 0.6)
        F.cur = tfo - F.ini - 0.02; tfr = F.t("atencao", depois=tfo)
        self.rafael(F, "rafael", tfr, "computacao-rafael.png", "RAFAEL · A COMPUTAÇÃO", [("aula", "✓ vira uma aula incrível")], depois=tia)
        self.risco(F, 1, tfr, prox + 0.1)

    def matematica(self, F, prox):
        F.cur = 0; tci = F.t("japao")
        self.abre(F, 2, tci)
        F.cur = tci - F.ini - 0.02; teq = F.t("equacao", depois=tci)
        F.cur = tci - F.ini - 0.02
        self.card(F, "O ENIGMA", PECAS[2][4], "A agulha de 1917",
                  [("agulha", "🪡", "girar uma agulha: qual a menor área?"), ("seculo", "⏳", "um enigma que atravessou o século"),
                   ("fields", "🏅", "3D só em 2025 · Medalha Fields")], tci - 0.2, teq - 0.3)
        self.esconde_mapa(tci - 0.8, teq)
        F.cur = teq - F.ini - 0.02; tfo = F.t("rafael", depois=teq)
        F.cur = teq - F.ini - 0.02
        self.card(F, "A IA", VERDE, "Uma equação nova",
                  [("equacao", "∞", "uma equação que ninguém tinha usado"), ("todas", "✓", "todas as dimensões de uma vez")], teq - 0.2, tfo - 0.1)
        self.esconde_mapa(teq - 0.4, tfo + 0.6)
        F.cur = tfo - F.ini - 0.02; tfr = F.t("atencao", depois=tfo)
        self.rafael(F, "rafael", tfr, "matematica-rafael.png", "RAFAEL · A MATEMÁTICA", [("cruza", "✓ a máquina cruza ideias de um jeito novo")], depois=teq)
        self.risco(F, 2, tfr, prox + 0.1)

    def voce(self, F, prox):
        F.cur = 0; tci = F.t("padrao")
        self.abre(F, 3, tci)
        F.cur = tci - F.ini - 0.02; tre = F.t("remedios", depois=tci)
        self.grafico(F, tci - 0.2, tre - 0.2)
        F.cur = tre - F.ini - 0.02; tme = F.t("merito", depois=tre)
        F.cur = tre - F.ini - 0.02
        self.card(F, "CHEGA EM", PECAS[3][4], "Muito além da matemática",
                  [("remedios", "💊", "remédios"), ("energia", "⚡", "energia"), ("trabalho", "💼", "no seu trabalho")], tre - 0.2, tme - 0.1)
        F.cur = tme - F.ini - 0.02; tfo = F.t("rafael", depois=tme)
        F.cur = tme - F.ini - 0.02
        self.card(F, "O MÉRITO MUDOU", VERDE, "Ter critério",
                  [("pedra", "✕", "quebrar pedra"), ("pedir", "🗣️", "pedir"), ("conferir", "🔍", "conferir"), ("explicar", "💡", "explicar")], tme - 0.2, tfo - 0.1)
        self.esconde_mapa(tre - 0.4, tfo)
        self.rafael(F, "rafael", F.fim, "voce-rafael.png", "RAFAEL · NA SALA DE AULA",
                    [("aulas", "✓ prepara as aulas com IA"), ("resposta", "✓ ensina a conferir cada resposta")], depois=tme)
        self.estado(tfo + 0.2, [3], 1, AMAR, "#1c1c24")

    # ------------------------------------------------------------ final
    def final(self, F, fim_total):
        t0 = F.ini
        cards = [("fisica-rafael.png", PECAS[0][4], "FÍSICA", "conferir a metade aberta", "metade"),
                 ("computacao-rafael.png", PECAS[1][4], "COMPUTAÇÃO", "separar medo e verdade", "medo"),
                 ("matematica-rafael.png", PECAS[2][4], "MATEMÁTICA", "explicar a prova", "explicar"),
                 ("voce-rafael.png", PECAS[3][4], "VOCÊ", "coordenar a máquina", "coordenar")]
        inner = self.id("in")
        corpo = f'<div class="in opaque" id="{inner}"><div class="cmp">'
        ts = []
        F.cur = 0.0
        for im, cor, nome, sub, pal in cards:
            j = self.id("cc")
            corpo += f'<div class="cc" id="{j}" style="border-top:8px solid {cor}"><img src="assets/{im}" alt=""/><span style="color:{cor}">{nome}</span><p>{sub}</p></div>'
            ts.append((j, F.t(pal)))
        corpo += "</div></div>"
        F.cur = ts[-1][1] - F.ini; tr = F.t("entender")
        self.clip(t0, tr - 0.3, corpo, 4)
        self.cena_in_out(inner, t0, tr - 0.3)
        self.esconde_mapa(t0, tr - 0.3)
        for j, t in ts:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.5, ease:"back.out(2)"}}, {t - 0.15:.2f});')
        ti = F.t("isso", depois=tr)
        self.mapa_todo(tr - 0.4, ticks=False)
        self.todos(tr - 0.4)
        self.a(f'tl.to("#cam", {{scale:1.06, transformOrigin:"1000px {gy(TY + TH / 2):.0f}px", duration:1.2, ease:"power2.inOut"}}, {tr - 0.2:.2f});')
        for i in range(4):
            self.estado(tr + i * 0.2, [i], 3, VERDE, "#0f2a17", stagger=0)
        self.faixa("A MÁQUINA DESCOBRE · ENTENDER É COM A GENTE", tr, ti + 0.2, cor=VERDE)
        tclub = F.t("inema", depois=ti, obrig=False) or ti + 2
        i3 = self.id("in")
        corpo = (f'<div class="in" id="{i3}"><img class="foto" src="assets/final-rafael.png" alt=""/><div class="full" style="background:rgba(12,12,16,.8)"></div><div class="fim"><h2>E você?</h2>'
                 f'<div class="sub">comenta: “eu vou coordenar” 👇</div><div class="pill" id="{i3}p">inema.club</div></div>'
                 f'<div class="printc" id="{i3}pr"><img src="assets/print-inema.png" alt="inema.club"/><span>aberto e gratuito · inema.club</span></div></div>')
        self.clip(ti - 0.1, fim_total, corpo, 6)
        self.esconde_mapa(ti - 0.1, fim_total + 2)
        self.a(f'tl.fromTo("#{i3}", {{opacity:0}}, {{opacity:1, duration:0.6}}, {ti - 0.1:.2f});')
        self.entra(f"#{i3}p", tclub - 0.1)
        self.a(f'tl.fromTo("#{i3}pr", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.6, ease:"back.out(2)"}}, {tclub:.2f});')


CORRIGE = {"ia": "IA", "Ia": "IA", "Open": "Open", "inema": "inema", "Yang,": "Yang,", "Kakeia": "Kakeya"}


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
    cena.fisica(falas[ordem[1]], ini[2])
    cena.computacao(falas[ordem[2]], ini[3])
    cena.matematica(falas[ordem[3]], ini[4])
    cena.voce(falas[ordem[4]], ini[5])
    cena.final(falas[ordem[5]], total)
    pal = []
    for s in seg["segmentos"]:
        for x in falas[s["fala"]].w:
            wd = CORRIGE.get(x["word"].strip(), x["word"].strip())
            if pal and wd[:1] in "-." and len(wd) > 1:
                pal[-1]["word"] += wd; continue
            pal.append({"word": wd, "t": round(s["ini"] + x["start"], 2)})
    leg = P._legenda(cena, pal, total, {"atencao": VERM, "metade": VERM, "caiu": VERM, "fisica": "#60a5fa", "computacao": "#c084fc",
                                         "matematica": "#fb923c", "nobel": AMAR, "openai": AMAR, "voce": AMAR, "criterio": VERDE,
                                         "conferir": VERDE, "explicar": VERDE, "coordenar": VERDE, "entender": VERDE})
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
<style>{G.CSS}{P.CSS_EXTRA}{CSS_GRAF}</style></head>
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
