#!/usr/bin/env python3
"""r7exp completo 16:9 — "PHP2Shell: seu site está exposto?" (21/10/2026).

Reaproveita as peças do motor (motor/gera.py) e do musk/gera_musk.py sem editá-los; o mapa aqui é o quadro das
versões do PHP (todas com a falha → 8.2–8.5 corrigidas → ≤ 8.1 sem correção oficial) + "7 em cada 10 sites".
Uso: python3 php/gera_php.py [--falso]     (--falso = tempos inventados a partir das falas, só para testar o layout)
Precisa: imagens/*.png, tempos/<fala>.json, build/avatar-a.mp4 + build/segmentos-a.json (motor/monta_avatar.py php a).
Saída: cena-a/index.html
"""
import json, re, sys
from pathlib import Path
import yaml

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "motor"))
sys.path.insert(0, str(AQUI.parent / "musk"))
import gera as G  # noqa: E402
import gera_musk as M  # noqa: E402

V = "a"
GX, GY, GS = G.GX, G.GY, G.GS
VERS = [("5.4", "a 7.4", None), ("8.0", "", None), ("8.1", "", None),
        ("8.2", "", "8.2.35"), ("8.3", "", "8.3.36"), ("8.4", "", "8.4.27"), ("8.5", "", "8.5.12")]
TX0, TSTEP, TW, TY, TH = 390, 200, 184, 390, 400
VERDE, VERM, AMAR, AZUL, ROXO = "#4ade80", "#ff4d4d", "#FACC15", "#38bdf8", "#a78bfa"


def gy(y): return GY + y * GS


# ---------------------------------------------------------------- mapa: versões do PHP
def mapa_svg(f):
    sites = ""
    for i in range(10):
        x = 420 + i * 128
        cor = AMAR if i < 7 else "#3a3a46"
        sites += (f'<g class="site" id="st{i}"><rect x="{x}" y="215" width="104" height="82" rx="10" fill="{cor}22" stroke="{cor}" stroke-width="4"/>'
                  f'<path d="M{x},237 H{x + 104}" stroke="{cor}" stroke-width="3"/><circle cx="{x + 12}" cy="226" r="4" fill="{cor}"/>'
                  f'<circle cx="{x + 25}" cy="226" r="4" fill="{cor}"/></g>')
    tiles = ""
    for i, (v, v2, fix) in enumerate(VERS):
        x = TX0 + i * TSTEP; cx = x + TW / 2
        vt = (f'<text x="{cx}" y="{TY + 80}" text-anchor="middle" font-size="66" class="vv">{v}</text>'
              + (f'<text x="{cx}" y="{TY + 120}" text-anchor="middle" font-size="32" fill="#c9c9d2">{v2}</text>' if v2 else ""))
        est = (f'<g id="e0{i}"><text x="{cx}" y="{TY + 250}" text-anchor="middle" font-size="90" fill="#6b6b78">?</text></g>'
               f'<g id="e1{i}" opacity="0"><text x="{cx}" y="{TY + 270}" text-anchor="middle" font-size="110" fill="{VERM}" font-weight="800">✕</text>'
               f'<text x="{cx}" y="{TY + 350}" text-anchor="middle" font-size="34" fill="{VERM}" font-weight="800">FALHA</text></g>')
        if fix:
            est += (f'<g id="e2{i}" opacity="0"><text x="{cx}" y="{TY + 210}" text-anchor="middle" font-size="26" fill="#c9c9d2">corrigida na</text>'
                    f'<text x="{cx}" y="{TY + 262}" text-anchor="middle" font-size="44" fill="{AMAR}" font-weight="800">{fix}</text>'
                    f'<text x="{cx}" y="{TY + 350}" text-anchor="middle" font-size="32" fill="{AMAR}" font-weight="800">ATUALIZE</text></g>'
                    f'<g id="e3{i}" opacity="0"><text x="{cx}" y="{TY + 270}" text-anchor="middle" font-size="110" fill="{VERDE}" font-weight="800">✓</text>'
                    f'<text x="{cx}" y="{TY + 350}" text-anchor="middle" font-size="28" fill="{VERDE}" font-weight="800">PROTEGIDO</text></g>')
        else:
            est += (f'<g id="e2{i}" opacity="0"><text x="{cx}" y="{TY + 240}" text-anchor="middle" font-size="36" fill="{VERM}" font-weight="800">SEM</text>'
                    f'<text x="{cx}" y="{TY + 285}" text-anchor="middle" font-size="26" fill="{VERM}" font-weight="800">CORREÇÃO</text>'
                    f'<text x="{cx}" y="{TY + 320}" text-anchor="middle" font-size="26" fill="{VERM}" font-weight="800">OFICIAL</text></g>'
                    f'<g id="e3{i}" opacity="0"><text x="{cx}" y="{TY + 250}" text-anchor="middle" font-size="64" fill="{VERM}" font-weight="800">⇄</text>'
                    f'<text x="{cx}" y="{TY + 350}" text-anchor="middle" font-size="34" fill="{VERM}" font-weight="800">MUDE</text></g>')
        tiles += (f'<g class="tile" id="v{i}"><rect id="vr{i}" x="{x}" y="{TY}" width="{TW}" height="{TH}" rx="16" fill="#15151c" stroke="#3a3a46" stroke-width="5"/>'
                  f'{vt}{est}</g>')
    return f'''
<svg id="mapa" width="1920" height="1080" viewBox="0 0 1920 1080">
 <defs><filter id="glow" filterUnits="userSpaceOnUse" x="-200" y="-200" width="2400" height="1600"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
 <g transform="translate({GX},{GY}) scale({GS})">
  <g id="ticks" opacity="0">
   <text x="420" y="180" font-size="56" fill="#fff" font-weight="800" class="vv"><tspan fill="{AMAR}">7 EM CADA 10</tspan> SITES RODAM PHP</text>
   {sites}
   <text x="420" y="345" font-size="26" fill="#9a9aa6">estimativas da imprensa: 70% a 80% dos sites do mundo · inclusive WordPress</text>
  </g>
  <g id="eixos" opacity="0">
   {tiles}
   <text class="axis" x="420" y="{TY + TH + 60}">← MAIS ANTIGA (2012)</text>
   <text class="axis" x="{TX0 + 6 * TSTEP + TW}" y="{TY + TH + 60}" text-anchor="end">MAIS NOVA →</text>
  </g>
 </g>
</svg>'''


CSS_EXTRA = M.CSS_EXTRA + """
.vv { font-family:Sora; font-weight:800; fill:#fff; }
.tile text { font-family:Sora; }
.pain { position:absolute; left:80px; top:150px; width:800px; }
.pain .pt { font-family:Sora; font-weight:800; font-size:62px; line-height:1.1; margin-top:22px; }
.pain .mono { font-family:'JetBrains Mono',monospace; font-size:28px; color:#c9c9d2; margin-top:16px; padding:12px 18px; background:#15151c; border:2px solid #33333d; border-radius:10px; }
.pain .row27 { margin-top:22px; }
.res { display:flex; align-items:center; gap:22px; margin-top:26px; font-family:Sora; font-weight:700; font-size:36px; opacity:0; }
.res b { font-size:30px; padding:10px 18px; border-radius:10px; color:#0c0c10; flex:none; }
.res span { color:#e5e5ea; }
"""


# ---------------------------------------------------------------- cena
class Cena(M.Cena):
    def mapa_todo(self, t, d=1.0, ticks=True):
        self.a(f'tl.to("#cam", {{scale:1, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
        if ticks:
            self.a(f'tl.to("#ticks", {{opacity:1, duration:0.6}}, {t + 0.3:.2f});')

    def zoom_tiles(self, t, z=1.15):
        self.a(f'tl.to("#cam", {{scale:{z}, transformOrigin:"1000px {gy(TY + TH / 2):.0f}px", duration:1.4, ease:"power2.inOut"}}, {t:.2f});')
        self.a(f'tl.to("#ticks", {{opacity:0, duration:0.4}}, {t:.2f});')

    def estado(self, t, idxs, s, stroke, fill, stagger=0.12):
        """muda os blocos `idxs` para o estado s (0 ?, 1 falha, 2 corrigida/sem correção, 3 protegido/mude)"""
        for k, i in enumerate(idxs):
            tt = t + k * stagger
            for e in range(4):
                if e != s:
                    self.a(f'tl.to("#e{e}{i}", {{opacity:0, duration:0.25}}, {tt:.2f});')
            self.a(f'tl.fromTo("#e{s}{i}", {{opacity:0, scale:0.6, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:0.45, ease:"back.out(2)"}}, {tt:.2f});')
            self.a(f'tl.to("#vr{i}", {{attr:{{stroke:"{stroke}", fill:"{fill}"}}, duration:0.4}}, {tt:.2f});')

    def cadeia2(self, F, chip, nos, img, ini, fim, cor):
        """cadeia do motor com outro rótulo no chip"""
        n0 = len(self.html)
        self.cadeia(F, nos, img, ini, fim, cor=cor)
        self.html[n0] = self.html[n0].replace("O QUE LEVA ATÉ LÁ", chip)

    def painel(self, F, chip, cor, titulo, mono, itens, ini, fim, track=5):
        """texto à ESQUERDA, avatar em meia tela à direita; itens (palavra, ícone, texto) entram na palavra"""
        inner = self.id("in")
        corpo = (f'<div class="in opaque" id="{inner}"><div class="pain"><span class="chip" style="background:{cor}2e;color:{cor}">{chip}</span>'
                 f'<div class="pt">{titulo}</div>' + (f'<div class="mono">{mono}</div>' if mono else ""))
        ts = []
        for pal, ic, txt in itens:
            j = self.id("p"); corpo += f'<div class="row27" id="{j}"><div class="ic">{ic}</div><div>{txt}</div></div>'; ts.append((j, F.t(pal)))
        corpo += "</div></div>"
        self.clip(ini, fim, corpo, track)
        self.cena_in_out(inner, ini, fim)
        self.esconde_mapa(ini, fim)
        self.meia(ini + 0.1, fim)
        self.a(f'tl.to("#fonte", {{opacity:0, duration:0.3}}, {ini:.2f}); tl.to("#fonte", {{opacity:1, duration:0.4}}, {fim:.2f});')
        for j, t in ts:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {t - 0.1:.2f});')
        return inner

    def faixa(self, txt, ini, fim, cor=None, track=5):
        i = self.id("bn")
        st = f' style="border-color:{cor};color:{cor}"' if cor else ""
        self.clip(ini, fim, f'<div class="full"><div class="ban" id="{i}"{st}>{txt}</div></div>', track, cls="full")
        self.entra(f"#{i}", ini + 0.1)
        self.a(f'tl.to("#{i}", {{opacity:0, duration:0.3}}, {fim - 0.3:.2f});')
        self.a(f'tl.to("#ticks", {{opacity:0, duration:0.3}}, {ini - 0.2:.2f});')

    # ------------------------------------------------------------ abertura
    def abertura(self, F):
        t_capa = F.t("exagero") - 0.5                    # capa parada a 1ª frase inteira
        inner = self.id("in")
        self.clip(0, t_capa + 0.6, f'<div class="in" id="{inner}" style="opacity:1"><img class="foto" id="{inner}f" src="assets/capa.png" alt="capa"/></div>', 3)
        self.a(f'tl.fromTo("#{inner}f", {{scale:0.93, transformOrigin:"0% 0%"}}, {{scale:0.95, transformOrigin:"0% 0%", duration:{t_capa + 0.6:.2f}, ease:"none"}}, 0);')
        self.a(f'tl.to("#{inner}", {{opacity:0, duration:0.6}}, {t_capa:.2f});')
        self.esconde_mapa(-1, t_capa + 0.6)
        tg = F.t("grafico")
        self.abre_meia(tg)
        self.a(f'tl.set(["#marca","#fonte"], {{opacity:0}}, 0); tl.to("#marca", {{opacity:1, duration:0.5}}, {t_capa:.2f}); tl.to("#fonte", {{opacity:1, duration:0.5}}, {tg:.2f});')
        # governos que tiraram sites do ar (metade esquerda, avatar à direita)
        F.cur = t_capa - F.ini
        tm = F.t("motivo")
        F.cur = t_capa - F.ini
        i2 = self.id("in")
        corpo = (f'<div class="in opaque" id="{i2}"><div class="mus"><div class="chip" style="background:rgba(255,77,77,.16);color:#ff8a8a">ESTA SEMANA</div>'
                 f'<div class="a27t" style="font-size:80px">Governos tiraram sites do ar</div>')
        its = []
        for pal, txt in [("franca", "França"), ("dinamarca", "Dinamarca"), ("finlandia", "Finlândia"), ("holanda", "Holanda")]:
            j = self.id("a"); corpo += f'<div class="row27" id="{j}"><div class="ic">🏛️</div><div>{txt}</div></div>'; its.append((j, F.t(pal)))
        corpo += f'<div class="ress" id="{i2}rs" style="border-color:#ff4d4d;color:#ff8a8a;font-size:32px">⚠ por precaução, antes de corrigir</div></div></div>'
        self.clip(t_capa, tm + 0.3, corpo, 4)
        self.cena_in_out(i2, t_capa, tm + 0.3)
        self.esconde_mapa(t_capa, tm)
        for j, t in its:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {t - 0.1:.2f});')
        self.entra(f"#{i2}rs", F.t("semana") - 0.1)
        # o motivo: PHP, 7 em cada 10
        F.cur = tm - F.ini
        tsete = F.t("sete", obrig=False) or F.t("7")
        tp = F.t("pesquisadores"); t12 = F.t("2012")
        i3 = self.id("in")
        corpo = (f'<div class="in opaque" id="{i3}"><div class="mus"><div class="chip" style="background:rgba(250,204,21,.16);color:#FACC15">O MOTIVO</div>'
                 f'<div class="a27t" style="font-size:88px">Uma falha no PHP</div><div class="a27s">o motor por baixo do site</div>'
                 f'<div class="num" id="{i3}n" style="font-family:Sora;font-weight:800;font-size:120px;color:#FACC15;margin-top:18px;opacity:0">7 em 10</div>'
                 f'<div class="a27s" id="{i3}s" style="opacity:0">sites do mundo · inclusive WordPress</div>'
                 f'<div class="row27" id="{i3}a"><div class="ic">🤖</div><div>achada com ajuda de IA</div></div>'
                 f'<div class="row27" id="{i3}b"><div class="ic">📅</div><div>existe desde 2012 (PHP 5.4)</div></div></div></div>')
        self.clip(tm, tg + 0.3, corpo, 5)
        self.cena_in_out(i3, tm, tg + 0.3)
        self.esconde_mapa(tm, tg)
        self.entra(f"#{i3}n", tsete - 0.1); self.entra(f"#{i3}s", tsete + 0.5)
        self.a(f'tl.fromTo("#{i3}a", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {tp - 0.1:.2f});')
        self.a(f'tl.fromTo("#{i3}b", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:0.45}}, {t12 - 0.1:.2f});')
        # mapa: sites no "gráfico", blocos nas "versões", tudo vermelho no "todas"
        self.a(f'tl.fromTo("#ticks", {{opacity:0}}, {{opacity:1, duration:0.6}}, {tg:.2f});')
        self.a(f'tl.fromTo(".site", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.35, stagger:0.08}}, {tg + 0.1:.2f});')
        tv = F.t("versoes"); tt = F.t("todas")
        self.a(f'tl.fromTo("#eixos", {{opacity:0}}, {{opacity:1, duration:0.4}}, {tv - 0.2:.2f});')
        self.a(f'tl.fromTo(".tile", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4, stagger:0.09}}, {tv - 0.1:.2f});')
        self.estado(tt - 0.1, range(7), 1, VERM, "#2a0f12", stagger=0.08)
        # Lúcia hoje
        tl_ = F.t("lucia"); tc = F.t("caso", depois=tl_)
        self.foto(tl_ - 0.2, tc + 0.2, "lucia-2026.png", carimbo="LÚCIA · HOJE", sub="A PERSONAGEM")
        F.cur = tl_ - F.ini
        self.tags(F, [("padaria", "dona de padaria · 54 anos"), ("freelancer", "site feito por freelancer em 2018"),
                      ("ninguem", "✕ ninguém mais entrou lá")], tc + 0.2)
        self.faixa("O QUE ELA FAZ EM CADA CASO · E VOCÊ NO SEU", tc, F.fim + 0.5)

    # ------------------------------------------------------------ caso 1: plataforma pronta
    def plataforma(self, F, prox):
        t0 = F.ini
        tv = F.t("lucia")
        self.titulo("CASO 1", "PLATAFORMA PRONTA", AZUL, t0, tv)
        F.cur = 0
        ts = F.t("shopify")
        self.card(F, "O QUE É", AZUL, "Shopify, Wix, Squarespace",
                  [("aluga", "🏪", "você aluga a loja"), ("empresa", "🛡️", "a empresa cuida do servidor")], ts - 0.2, tv - 0.1)
        self.esconde_mapa(ts - 0.8, tv + 0.6)
        tf = F.t("fazer", depois=tv)
        F.cur = tv - F.ini
        self.foto(tv - 0.2, tf + 0.2, "plataforma-lucia.png", carimbo="LÚCIA · PLATAFORMA PRONTA", sub="A MESMA LÚCIA")
        F.cur = tv - F.ini
        self.tags(F, [("cardapio", "só troca cardápio e fotos"), ("responsabilidade", "o PHP é com a plataforma"),
                      ("rapido", "✓ costumam corrigir rápido")], tf + 0.2)
        F.cur = tf - F.ini
        self.lista_verde(F, "O QUE FAZER · PLATAFORMA PRONTA", [("aviso", "confira o aviso de segurança da plataforma"),
                                                               ("suporte", "não achou? pergunte ao suporte")],
                         tf - 0.1, prox - 0.1, fecho=[("mensagem", "Uma mensagem"), ("resolve", "resolve.")], cor=AZUL)

    # ------------------------------------------------------------ caso 2: WordPress em hospedagem
    def wordpress(self, F, prox):
        t0 = F.ini
        tfa = F.t("falha")
        self.titulo("CASO 2", "WORDPRESS NA HOSPEDAGEM", AMAR, t0, tfa)
        F.cur = 0
        self.faixa("O CASO DA MAIORIA DAS PEQUENAS EMPRESAS", F.t("maioria") - 0.2, tfa - 0.1, cor=AMAR)
        tlu = F.t("lucia", depois=tfa)
        F.cur = tfa - F.ini
        self.cadeia2(F, "POR QUE PREOCUPA", [("falha", "FALHA NO PHP", "não no WordPress"), ("acionada", "ANTES DO WORDPRESS", "a falha entra primeiro"),
                                             ("plugin", "PLUGIN DE SEGURANÇA", "✕ não segura")], "falha-servidor.png", tfa - 0.2, tlu - 0.2, VERM)
        tf = F.t("fazer", depois=tlu)
        F.cur = tlu - F.ini
        self.foto(tlu - 0.2, tf + 0.2, "wordpress-lucia.png", carimbo="LÚCIA · WORDPRESS", sub="A MESMA LÚCIA")
        F.cur = tlu - F.ini
        self.tags(F, [("ar", "site no ar"), ("funciona", "padaria funcionando"), ("versao", "✕ nem sabe a versão do PHP")], tf + 0.2)
        # passo 1: teste com o verificador da OpenAI
        tvul = F.t("vulneravel", depois=tf)
        F.cur = tf - F.ini
        self.painel(F, "PASSO 1 · TESTE", VERDE, "Verificador gratuito da OpenAI", "github.com/openai/php2shell-checker",
                    [("cloud", "🤖", "passe o link ao Claude, Codex ou Gemini"),
                     ("rode", "💬", "“rode só contra o meu site e explique em português”")], tf - 0.1, tvul - 0.3)
        # resultados
        tpa = F.t("painel", depois=tvul)
        F.cur = tvul - F.ini
        tde = F.t("desconhecido")
        i = self.id("in")
        corpo = (f'<div class="in opaque" id="{i}"><div class="pain"><span class="chip" style="background:{AMAR}2e;color:{AMAR}">O RESULTADO</span>'
                 f'<div class="res" id="{i}a"><b style="background:{VERM}">VULNERABLE</b><span>vulnerável → atualize</span></div>'
                 f'<div class="res" id="{i}b"><b style="background:{AMAR}">UNKNOWN</b><span>desconhecido → NÃO é sinal verde</span></div>'
                 f'<div class="res" id="{i}c" style="font-size:30px;color:#c9c9d2"><span>confira a versão no painel da hospedagem</span></div></div></div>')
        self.clip(tvul - 0.3, tpa + 0.1, corpo, 5)
        self.cena_in_out(i, tvul - 0.3, tpa + 0.1)
        self.esconde_mapa(tvul - 0.3, tpa)
        self.meia(tvul - 0.2, tpa + 0.1)
        self.a(f'tl.to("#fonte", {{opacity:0, duration:0.3}}, {tvul - 0.3:.2f}); tl.to("#fonte", {{opacity:1, duration:0.4}}, {tpa:.2f});')
        self.entra(f"#{i}a", tvul - 0.1); self.entra(f"#{i}b", tde - 0.1); self.entra(f"#{i}c", tde + 1.4)
        # no mapa: quais versões têm correção
        tof = F.t("oficial", depois=tpa); tpr = F.t("provedor", depois=tof)
        self.mapa_todo(tpa - 0.3, ticks=False)
        self.zoom_tiles(tpa + 0.2)
        self.estado(tpa + 0.4, [3, 4, 5, 6], 2, AMAR, "#2a2410")
        self.estado(tof - 0.6, [0, 1, 2], 2, VERM, "#2a0f12")
        self.faixa("8.1 OU MAIS VELHA: PEÇA AO PROVEDOR PARA MUDAR A VERSÃO HOJE", tpr - 1.2, prox + 0.1, cor=VERM)

    # ------------------------------------------------------------ caso 3: servidor próprio
    def servidor(self, F, prox):
        t0 = F.ini
        tu = F.t("urgente")
        self.mapa_todo(t0 - 0.4, ticks=False)
        self.titulo("CASO 3", "SERVIDOR PRÓPRIO (VPS)", ROXO, t0, tu)
        F.cur = 0
        self.faixa("NÃO TEM A QUEM PEDIR: É COM VOCÊ", F.t("pedir") - 0.2, tu - 0.1, cor=ROXO)
        tf = F.t("fazer", depois=tu)
        F.cur = tu - F.ini
        self.foto(tu - 0.2, tf + 0.2, "servidor-ataque.png", carimbo="ATAQUES JÁ COMEÇARAM", sub="CLOUDFLARE · 21/10, 07:43 UTC")
        F.cur = tu - F.ini
        self.tags(F, [("cloudflare", "⚠ a Cloudflare viu ataques"), ("antes", "⚠ antes de a correção sair")], tf + 0.2)
        th = F.t("hora", depois=tf)
        F.cur = tf - F.ini
        self.foto(tf - 0.2, th + 0.1, "servidor-tecnico.png", carimbo="LÚCIA · SERVIDOR PRÓPRIO", sub="O TÉCNICO DELA")
        F.cur = tf - F.ini
        self.tags(F, [("atualize", "✓ atualize o PHP agora"), ("corrigida", "8.2.35 · 8.3.36 · 8.4.27 · 8.5.12"),
                      ("reinicie", "reinicie o serviço")], th + 0.1)
        tex = F.t("exposto", depois=th)
        F.cur = th - F.ini
        ttot = F.t("totalmente")
        self.quote("AJUSTE TEMPORÁRIO NÃO BASTA", VERM, "Só a atualização resolve.",
                   "ajustes na configuração não protegem totalmente · time do PHP", th - 0.2, tex - 0.4, img="falha-servidor.png", tsub=ttot - 1.0)
        F.cur = tex - F.ini
        self.lista_verde(F, "SE O SERVIDOR FICOU EXPOSTO", [("arquivos", "procure arquivos novos"),
                                                            ("usuarios", "e usuários que você não criou")], tex - 0.4, prox - 0.1, cor=ROXO)

    # ------------------------------------------------------------ final
    def final(self, F, fim_total):
        t0 = F.ini
        tp = F.t("parar")
        cards = [("lucia-2026.png", "#9a9aa6", "HOJE", "site esquecido", None),
                 ("plataforma-lucia.png", AZUL, "PLATAFORMA", "confere com o suporte", "plataforma"),
                 ("wordpress-lucia.png", AMAR, "HOSPEDAGEM", "testa e pede a versão nova", "hospedagem"),
                 ("servidor-tecnico.png", ROXO, "SERVIDOR", "atualiza agora", "servidor")]
        inner = self.id("in")
        corpo = f'<div class="in opaque" id="{inner}"><div class="cmp">'
        ts = []
        F.cur = 0.0
        for im, cor, nome, sub, pal in cards:
            j = self.id("cc")
            corpo += f'<div class="cc" id="{j}" style="border-top:8px solid {cor}"><img src="assets/{im}" alt=""/><span style="color:{cor}">{nome}</span><p>{sub}</p></div>'
            ts.append((j, F.t(pal) if pal else t0 + 0.3))
        corpo += '</div><div class="frase" id="%sfr"><div>Três casos.</div><div style="color:#FACC15">A mesma Lúcia.</div></div></div>' % inner
        self.clip(t0, tp - 0.4, corpo, 4)
        self.cena_in_out(inner, t0, tp - 0.4)
        self.esconde_mapa(t0, tp - 0.4)
        for j, t in ts:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.5, ease:"back.out(2)"}}, {t - 0.15:.2f});')
        self.a(f'tl.set("#{inner}fr", {{opacity:0}}, 0);')
        # não vai parar
        F.cur = tp - F.ini
        th = F.t("hoje", depois=tp)
        self.quote("ISSO NÃO VAI PARAR", VERM, "A IA está achando falhas antigas cada vez mais rápido.", "e quem ataca também usa IA",
                   tp - 0.5, th - 0.1, img="servidor-ataque.png")
        # passos
        F.cur = th - F.ini
        tpr = F.t("proteger")
        F.cur = th - F.ini
        i2 = self.id("in")
        corpo = f'<div class="in opaque" id="{i2}"><div class="chip" style="position:absolute;left:420px;top:130px;background:rgba(74,222,128,.16);color:#4ade80">O QUE FAZER, HOJE</div><div class="passos">'
        ts = []
        for pal, num, txt in [("teste", "1", "teste o seu site: verificador gratuito da OpenAI"),
                              ("veja", "2", "veja a versão do PHP: 8.1 ou mais velha = mude"),
                              ("mande", "3", "mande este vídeo para quem tem site antigo e esquecido")]:
            j = self.id("p"); corpo += f'<div class="ps" id="{j}"><b>{num}</b><span>{txt}</span></div>'; ts.append((j, F.t(pal)))
        corpo += "</div></div>"
        self.clip(th - 0.1, tpr, corpo, 5)
        self.cena_in_out(i2, th - 0.1, tpr)
        self.esconde_mapa(th - 0.1, tpr)
        for j, t in ts:
            self.a(f'tl.fromTo("#{j}", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:0.45, ease:"back.out(2)"}}, {t - 0.15:.2f});')
            self.a(f'tl.to("#{j} b", {{backgroundColor:"#4ade80", duration:0.3}}, {t + 0.3:.2f});')
        # mapa: protegido
        tvo = F.t("voce", depois=tpr)
        self.mapa_todo(tpr - 0.5, ticks=False)
        self.zoom_tiles(tpr - 0.3, z=1.1)
        self.estado(tpr, [3, 4, 5, 6], 3, VERDE, "#0f2a17")
        self.estado(tpr + 0.6, [0, 1, 2], 3, VERM, "#2a0f12")
        self.faixa("PROTEGER LEVA 10 MINUTOS", tpr - 0.1, tvo + 1.0, cor=VERDE)
        tclub = F.t("inema", depois=tvo, obrig=False) or tvo + 4
        i3 = self.id("in")
        corpo = (f'<div class="in" id="{i3}"><img class="foto" src="assets/final-lucia.png" alt=""/><div class="full" style="background:rgba(12,12,16,.8)"></div><div class="fim"><h2>E você?</h2>'
                 f'<div class="sub">comenta: “eu protegi meu site” 👇</div><div class="pill" id="{i3}p">inema.club</div></div>'
                 f'<div class="printc" id="{i3}pr"><img src="assets/print-inema.png" alt="inema.club"/><span>aberto e gratuito · inema.club</span></div></div>')
        self.clip(tvo + 0.6, fim_total, corpo, 6)
        self.esconde_mapa(tvo + 0.6, fim_total + 2)
        self.a(f'tl.fromTo("#{i3}", {{opacity:0}}, {{opacity:1, duration:0.6}}, {tvo + 0.6:.2f});')
        self.entra(f"#{i3}p", tclub - 0.1)
        self.a(f'tl.fromTo("#{i3}pr", {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.6, ease:"back.out(2)"}}, {tclub:.2f});')


def _legenda(cena, palavras, fim_total, KEY):
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
            cor = KEY.get(G.norm(w["word"]), "#FACC15")
            cena.a(f'tl.set("#{i} b:nth-child({j + 1})", {{color:"{cor}"}}, {w["t"]:.2f}); tl.set("#{i} b:nth-child({j + 1})", {{color:"#fff"}}, {min(fim, w["t"] + 0.45):.2f});')
    return "".join(html)


CORRIGE = {"ia": "IA", "Ia": "IA", "IA.": "IA.", "Php": "PHP", "php": "PHP", "Cloud": "Claude", "8": "8", "inema": "inema"}


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
    cena.plataforma(falas[ordem[1]], ini[2])
    cena.wordpress(falas[ordem[2]], ini[3])
    cena.servidor(falas[ordem[3]], ini[4])
    cena.final(falas[ordem[4]], total)
    pal = []
    for s in seg["segmentos"]:
        for x in falas[s["fala"]].w:
            wd = CORRIGE.get(x["word"].strip(), x["word"].strip())
            if pal and wd[:1] in "-." and len(wd) > 1:
                pal[-1]["word"] += wd; continue
            pal.append({"word": wd, "t": round(s["ini"] + x["start"], 2)})
    leg = _legenda(cena, pal, total, {"php": "#FACC15", "falha": "#ff4d4d", "invadido": "#ff4d4d", "vulneravel": "#ff4d4d",
                                      "urgente": "#ff4d4d", "protegi": "#4ade80", "atualize": "#4ade80", "teste": "#4ade80", "resolve": "#4ade80"})
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
    out = AQUI / (f"cena-{V}-limpo" if limpo else f"cena-{V}")
    (out / "assets").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"ok {out/'index.html'} · {total:.1f} s · {len(cena.js)} eventos")


if __name__ == "__main__":
    main()
