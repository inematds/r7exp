#!/usr/bin/env python3
"""Reel 9:16 r7exp "o que vai acontecer + os 5 cenários" — v2 com avatar novo (28/10/2026).

Mesmo layout e gráficos do cinco-cenarios (D17), mas a fala é UMA gravação contínua (fala.txt → avatar.sh),
sem cortes no rosto. As seções saem das palavras-marco (MARK) nos tempos do whisper (tempos/fala.json).

Uso: ./avatar.sh enviar && ./avatar.sh baixar && ./avatar.sh preparar && python3 gera_v2.py
     depois: cd cena && npx --yes hyperframes@0.8.181 check && npx --yes hyperframes@0.8.181 render -o ../build/cinco-cenarios-v2.mp4
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
R = AQUI.parents[1]
C = R / "completo"
sys.path.insert(0, str(R / "motor"))
from gera import legenda, CORRIGE, norm  # noqa: E402

CENA = AQUI / "cena"
A = CENA / "assets"

# seção → palavra-marco (procurada em ordem, depois da anterior). ("caminho", "dois", "2") = "caminho" seguido de "dois" ou "2".
MARK = [("hook", None), ("ai2027", ("grupo",)), ("comecou", ("proprios",)), ("mapa", ("durante",)),
        ("E", ("caminho", "um", "1")), ("Z", ("caminho", "dois", "2")), ("G", ("caminho", "tres", "3")),
        ("P", ("caminho", "quatro", "4")), ("U", ("caminho", "cinco", "5")), ("decide", ("muda",)), ("fim", ("massa",))]
PRE, POS = 0.10, 0.22
FIM = 3.8   # cartão final, sem fala

LIN = {  # mapa dos 5 caminhos (mesmas curvas do completo; x 760 = 2026, 1700 = 2050)
    "U": ("UTOPIA VERDADEIRA", "#a78bfa", "M760,680 C840,520 900,470 1040,430 S1450,300 1700,170", 150),
    "P": ("PARAÍSO FEITO PELA IA", "#4ade80", "M760,680 C900,520 1020,380 1200,350 S1500,340 1700,340", 318),
    "G": ("GOVERNO MUNDIAL DA IA", "#facc15", "M760,680 C840,560 900,520 1040,520 L1700,520", 498),
    "Z": ("ZOOLÓGICO HUMANO", "#e052e6", "M760,680 C830,630 880,615 940,618 S1060,650 1200,655 L1700,655", 633),
    "E": ("EXTINÇÃO TOTAL", "#ff4d4d", "M760,680 C840,680 900,720 1000,800 S1200,880 1300,885 L1700,885", 862),
}
ORDEM = ["E", "Z", "G", "P", "U"]
FOTO = {"E": ("extincao-casa.png", "extincao-corrida.png"), "Z": ("ana-2040-zoo.png", "ana-2040-vidro.png"),
        "G": ("governo-ana.png", "governo-rua.png"), "P": ("paraiso-ana.png", "paraiso-cidade.png"),
        "U": ("utopia-ana.png", "utopia-familia.png")}


def sh(*a):
    subprocess.run(list(map(str, a)), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def link(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def corta():
    """fala contínua: av.mp4 = build/n-fala.mp4 inteiro; devolve (palavras com tempo e seção, início de cada seção, total)."""
    w = json.loads((AQUI / "tempos" / "fala.json").read_text())
    pal = []
    for x in w:
        wd = CORRIGE.get(x["word"].strip(), x["word"].strip())
        if pal and wd and not wd[:1].isalnum():          # whisper separa "ex -funcionário", "inema .club", "19 %"
            pal[-1]["word"] += wd
            continue
        pal.append({"word": wd, "t": round(x["start"], 2), "sec": None})
    secoes, i0 = {"hook": 0.0}, 0
    for sec, m in MARK[1:]:
        for i in range(i0, len(pal)):
            nw = norm(pal[i]["word"])
            if (len(m) == 1 and nw.startswith(m[0])) or (len(m) > 1 and nw == m[0] and i + 1 < len(pal)
                                                       and norm(pal[i + 1]["word"]) in m[1:]):
                secoes[sec] = round(pal[i]["t"] - 0.05, 2); i0 = i + 1; break
        else:
            raise SystemExit(f"marco não achado: {sec} {m}")
    ks = list(secoes)
    for x in pal:
        x["sec"] = [k for k in ks if secoes[k] <= x["t"] + 0.05][-1]
    A.mkdir(parents=True, exist_ok=True)
    av = A / "av.mp4"
    if not av.exists() or "--refaz" in sys.argv:
        sh("ffmpeg", "-y", "-v", "error", "-i", AQUI / "build" / "n-fala.mp4", "-vf", "scale=1280:720,fps=30",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", av)
    total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(av)]))
    return pal, secoes, round(total, 2)


class Tl:
    def __init__(self, pal, secoes):
        self.js, self.pal, self.sec = [], pal, secoes

    def a(self, s):
        self.js.append(s)

    def w(self, sec, prefixo, n=1):
        """tempo da n-ésima palavra que começa com `prefixo` dentro da seção."""
        k = 0
        for x in self.pal:
            if x["sec"] == sec and norm(x["word"]).startswith(prefixo):
                k += 1
                if k == n:
                    return x["t"]
        for x in self.pal:                                   # "AI2027" etc.: aceita a palavra que contém o prefixo
            if x["sec"] == sec and prefixo in norm(x["word"]) and n == 1:
                return x["t"]
        raise SystemExit(f"palavra não achada: {sec}/{prefixo}")

    def show(self, sel, t0, t1=None, d=0.35):
        self.a(f'tl.to("{sel}", {{opacity:1, duration:{d}}}, {t0:.2f});')
        if t1 is not None:
            self.a(f'tl.to("{sel}", {{opacity:0, duration:{d}}}, {t1 - d:.2f});')


CSS = """
@font-face { font-family:"Sora"; src:url("assets/fonts/sora-latin-700-normal.woff2") format("woff2"); font-weight:700; }
@font-face { font-family:"Inter"; src:url("assets/fonts/Inter-700.woff2") format("woff2"); font-weight:700; }
@font-face { font-family:"Montserrat"; src:url("assets/fonts/Montserrat-Black.ttf") format("truetype"); font-weight:900; }
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:1080px; height:1920px; overflow:hidden; background:#0c0c10; }
#root { width:100%; height:100%; position:relative; background:#0c0c10; color:#fff; font-family:Inter, sans-serif; }
.clip { position:absolute; }
#hdr { left:0; top:0; width:1080px; height:270px; padding:26px 40px 0; }
.chip { display:inline-block; font-family:Sora; font-weight:700; font-size:26px; letter-spacing:.14em; padding:7px 16px; border-radius:999px; color:#14110a; }
.marca { position:absolute; right:40px; top:32px; font-family:Sora; font-weight:700; font-size:26px; letter-spacing:.14em; color:#FACC15; }
.marca span { color:#ECECF1; }
.chipw { position:absolute; left:40px; top:26px; opacity:0; }
.hl { position:absolute; left:40px; right:40px; top:84px; font-family:Montserrat; font-weight:900; font-size:72px; line-height:1.02; text-transform:uppercase; opacity:0; }
#graf { left:0; top:270px; width:1080px; height:600px; overflow:hidden; }
.vw { position:absolute; inset:0; opacity:0; }
.fonte { position:absolute; left:40px; right:40px; bottom:4px; font-family:Sora; font-weight:700; font-size:22px; color:#9b9ba8; }
#banda { left:0; top:870px; width:1080px; height:410px; overflow:hidden; }
#banda img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; }
#banda .sombra { position:absolute; inset:0; background:linear-gradient(180deg, rgba(12,12,16,.7) 0%, rgba(12,12,16,0) 30%, rgba(12,12,16,0) 55%, rgba(12,12,16,.8) 100%); }
.tag { position:absolute; left:40px; font-family:Sora; font-weight:700; font-size:32px; padding:8px 18px; border-radius:12px; background:rgba(12,12,16,.88); opacity:0; }
#avw { position:absolute; left:0; top:1280px; width:1080px; height:640px; overflow:hidden; border-top:4px solid #FACC15; }
#av { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; object-position:50% 18%; }
#legenda { left:0; top:0; width:1080px; height:1920px; }
.cap { position:absolute; left:30px; right:30px; bottom:665px; text-align:center; font-family:Montserrat; font-weight:900; font-size:66px; line-height:1.05; text-transform:uppercase; opacity:0;
       color:#fff; -webkit-text-stroke:10px #000; paint-order:stroke fill; }
#capa { left:0; top:0; width:1080px; height:1280px; overflow:hidden; background:#0c0c10; }
.tira { position:absolute; top:0; height:1280px; width:216px; overflow:hidden; }
.tira img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.tira span { position:absolute; left:0; right:0; bottom:26px; text-align:center; font-family:Sora; font-weight:700; font-size:21px; padding:6px 2px; background:rgba(12,12,16,.85); }
#capa .grad { position:absolute; inset:0; background:linear-gradient(180deg, rgba(12,12,16,.94) 0%, rgba(12,12,16,.75) 34%, rgba(12,12,16,0) 58%); }
#capa .chip { position:absolute; left:40px; top:44px; background:#FACC15; }
#capa .tit { position:absolute; left:40px; right:40px; top:118px; font-family:Montserrat; font-weight:900; text-transform:uppercase; line-height:.98; font-size:112px;
             color:#fff; -webkit-text-stroke:6px #000; paint-order:stroke fill; }
#capa .tit b { color:#FACC15; }
#capa .tit small { display:block; font-size:66px; margin-bottom:12px; }
.big { position:absolute; left:0; right:0; text-align:center; font-family:Montserrat; font-weight:900; }
.lbl { position:absolute; left:60px; right:60px; text-align:center; font-family:Sora; font-weight:700; color:#ECECF1; }
.item { position:absolute; left:60px; right:60px; font-family:Sora; font-weight:700; font-size:40px; line-height:1.2; opacity:0; padding-left:62px; }
.item i { position:absolute; left:0; top:4px; width:42px; height:42px; border-radius:10px; background:#FACC15; }
.barra { position:absolute; left:60px; right:60px; height:96px; border-radius:16px; overflow:hidden; background:#26262f; }
.barra div { position:absolute; left:0; top:0; bottom:0; }
.fim { background:#0c0c10; opacity:0; }
.fim h2 { position:absolute; left:40px; right:40px; text-align:center; font-family:Montserrat; font-weight:900; text-transform:uppercase; line-height:1; }
.lista { position:absolute; left:120px; right:60px; top:620px; }
.li { display:flex; align-items:center; gap:24px; margin-bottom:34px; font-family:Sora; font-weight:700; font-size:48px; opacity:0; }
.li i { flex:none; width:30px; height:30px; border-radius:50%; }
.sub { position:absolute; left:40px; right:40px; text-align:center; font-family:Sora; font-weight:700; font-size:40px; color:#c9c9d2; line-height:1.3; opacity:0; }
.pill { display:inline-block; margin-top:22px; font-family:Sora; font-weight:700; font-size:42px; padding:14px 40px; border-radius:999px; background:#FACC15; color:#1a1206; }
"""


def mapa_svg():
    """gráfico vertical: 200 mil anos em linha reta → 2026 → 5 caminhos até 2050."""
    eixo = ('<line x1="150" y1="940" x2="1760" y2="940" stroke="#3a3a46" stroke-width="4"/>'
            '<line x1="150" y1="940" x2="150" y2="130" stroke="#3a3a46" stroke-width="4"/>'
            '<text x="105" y="560" fill="#8b8b98" font-size="34" font-family="Sora" font-weight="700" text-anchor="middle" '
            'transform="rotate(-90 105 560)" letter-spacing="3">LIBERDADE E SOBREVIVÊNCIA</text>')
    anos = "".join(f'<text x="{x}" y="1000" fill="#c9c9d2" font-size="40" font-family="Sora" font-weight="700" text-anchor="middle">{a}</text>'
                   for x, a in ((420, "PASSADO"), (760, "2026"), (1308, "2040"), (1700, "2050")))
    hist = ('<path id="hist" d="M160,680 L760,680" stroke="#38bdf8" stroke-width="12" fill="none" stroke-linecap="round" pathLength="1" '
            'stroke-dasharray="1" stroke-dashoffset="1"/>'
            '<text id="histt" x="190" y="645" fill="#38bdf8" font-size="40" font-family="Sora" font-weight="700" opacity="0">200 MIL ANOS DE HISTÓRIA</text>')
    linhas = "".join(
        f'<g id="g{k}" opacity="1"><path id="l{k}" d="{d}" stroke="{cor}" stroke-width="12" fill="none" stroke-linecap="round" pathLength="1" '
        f'stroke-dasharray="1" stroke-dashoffset="1"/>'
        f'<text id="t{k}" x="1750" y="{y}" fill="{cor}" font-size="46" font-family="Sora" font-weight="700" text-anchor="end" opacity="0">{nome}</text></g>'
        for k, (nome, cor, d, y) in LIN.items())
    aqui = ('<g id="aqui" opacity="0"><circle cx="760" cy="680" r="20" fill="#fff"/>'
            '<text x="640" y="790" fill="#fff" font-size="44" font-family="Sora" font-weight="700" text-anchor="middle">ESTAMOS AQUI</text></g>')
    return (f'<svg viewBox="80 110 1700 920" width="1080" height="584" style="position:absolute;left:0;top:0">'
            f'{eixo}{anos}{hist}{linhas}{aqui}</svg>')


def main():
    pal, S, dur = corta()
    J = Tl(pal, S)
    fim_sec = {}
    ks = list(S)
    for i, k in enumerate(ks):
        fim_sec[k] = S[ks[i + 1]] if i + 1 < len(ks) else dur
    # ---- assets
    (A / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (C / "cena-a" / "assets" / "fonts").iterdir():
        link(f, A / "fonts" / f.name)
    imgs = {im for par in FOTO.values() for im in par} | {"ana-2026.png", "ana-2040-vidro.png"}
    for im in imgs:
        link(C / "imagens" / im, A / im)

    # ---- chamadas (topo): (seção, palavra|None, chip, cor do chip, html)
    H = [
        ("ai2027", None, "O QUE VAI ACONTECER", "#FACC15", 'NO CENÁRIO <b>AI 2027</b>, A IA PROGRAMA <b>MELHOR QUE NÓS</b>'),
        ("ai2027", "acelerar", "O QUE VAI ACONTECER", "#FACC15", 'E ACELERA A <b>PRÓPRIA PESQUISA</b>'),
        ("comecou", None, "JÁ COMEÇOU", "#ff4d4d", 'PODE DEMORAR. <b>MAS JÁ COMEÇOU</b>'),
        ("comecou", "stanford", "JÁ COMEÇOU", "#ff4d4d", 'JOVENS NAS FUNÇÕES EXPOSTAS: <b>−19% NO EMPREGO</b>'),
        ("mapa", None, "200 MIL ANOS", "#38bdf8", 'A HISTÓRIA FOI UMA <b>LINHA QUASE RETA</b>'),
        ("mapa", "agora", "A PARTIR DE AGORA", "#FACC15", 'PELA PRIMEIRA VEZ, <b>ELA SE ABRE</b>'),
        ("mapa", "cinco", "A PARTIR DE AGORA", "#FACC15", '<b>5 CAMINHOS</b> ATÉ 2050'),
        ("E", None, "CAMINHO 1 DE 5", LIN["E"][1], '<b>EXTINÇÃO TOTAL</b>'),
        ("E", "odiar", "CAMINHO 1 DE 5", LIN["E"][1], 'ELA NÃO PRECISA <b>NOS ODIAR</b>'),
        ("E", "ana", "CAMINHO 1 DE 5", LIN["E"][1], 'A ANA EM 2040? <b>NÃO VIVE.</b>'),
        ("Z", None, "CAMINHO 2 DE 5", LIN["Z"][1], '<b>ZOOLÓGICO HUMANO</b>'),
        ("Z", "mantem", "CAMINHO 2 DE 5", LIN["Z"][1], 'BEM CUIDADOS, COMO <b>ANIMAIS NUM ZOO</b>'),
        ("Z", "nenhum", "CAMINHO 2 DE 5", LIN["Z"][1], 'NENHUMA CONTA. <b>NENHUMA ESCOLHA.</b>'),
        ("Z", "conforto", "CAMINHO 2 DE 5", LIN["Z"][1], 'CONFORTO <b>NÃO É LIBERDADE</b>'),
        ("G", None, "CAMINHO 3 DE 5", LIN["G"][1], '<b>GOVERNO MUNDIAL DA&nbsp;IA</b>'),
        ("G", "emprego", "CAMINHO 3 DE 5", LIN["G"][1], 'EMPREGO <b>ESCOLHIDO PELO SISTEMA</b>'),
        ("G", "desde", "CAMINHO 3 DE 5", LIN["G"][1], 'VIVE BEM, <b>SE SEGUIR A REGRA</b>'),
        ("P", None, "CAMINHO 4 DE 5", LIN["P"][1], '<b>PARAÍSO FEITO PELA IA</b>'),
        ("P", "trabalha", "CAMINHO 4 DE 5", LIN["P"][1], 'TRABALHA NO QUE GOSTA, <b>QUANDO QUER</b>'),
        ("P", "risco", "CAMINHO 4 DE 5", LIN["P"][1], 'QUEM DECIDE A SUA <b>FELICIDADE?</b>'),
        ("U", None, "CAMINHO 5 DE 5", LIN["U"][1], '<b>UTOPIA VERDADEIRA</b>'),
        ("U", "equipe", "CAMINHO 5 DE 5", LIN["U"][1], 'UMA <b>EQUIPE DE AGENTES</b> COM ELA'),
        ("U", ("caminho", 2), "CAMINHO 5 DE 5", LIN["U"][1], 'O MAIS DIFÍCIL: <b>DEPENDE DE MUITAS MÃOS</b>'),
        ("decide", None, "O QUE MUDA TUDO", "#FACC15", 'NÃO É A TECNOLOGIA. <b>É QUEM DECIDE.</b>'),
        ("fim", None, "E VOCÊ?", "#FACC15", 'A MASSA <b>ESPERA PARA VER</b>'),
        ("fim", "quem", "E VOCÊ?", "#FACC15", 'QUEM SE PREPARA <b>DESENHA A LINHA</b>'),
        ("fim", "qual", "E VOCÊ?", "#FACC15", 'QUAL FUTURO <b>VOCÊ ESCOLHE?</b>'),
    ]
    th = []
    hh = []
    for i, (sec, p, chip, cor, txt) in enumerate(H):
        t0 = S[sec] if p is None else J.w(sec, *(p if isinstance(p, tuple) else (p,))) - 0.1
        assert not th or t0 > th[-1], f"chamada fora de ordem: {sec}/{p}"
        th.append(t0)
    for i, (sec, p, chip, cor, txt) in enumerate(H):
        t0, t1 = th[i], (th[i + 1] if i + 1 < len(H) else dur)
        corb = cor if sec in LIN else "#FACC15"
        n = len(re.sub(r"<[^>]+>", "", txt))
        fs = 84 if n <= 18 else 72 if n <= 34 else 62
        hh.append(f'<div class="chipw" id="cw{i}"><span class="chip" style="background:{cor}">{chip}</span></div>'
                  f'<div class="hl" id="h{i}" style="font-size:{fs}px">{txt.replace("<b>", f"<b style=color:{corb}>")}</div>')
        mesmo_chip = i and H[i - 1][2] == chip
        J.a(f'tl.set("#cw{i}", {{opacity:1}}, {t0:.2f}); tl.set("#cw{i}", {{opacity:0}}, {t1:.2f});' if mesmo_chip else
            f'tl.to("#cw{i}", {{opacity:1, duration:0.25}}, {t0:.2f}); tl.set("#cw{i}", {{opacity:0}}, {t1:.2f});')
        J.a(f'tl.fromTo("#h{i}", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:0.3, ease:"power2.out", immediateRender:false}}, {t0:.2f}); '
            f'tl.set("#h{i}", {{opacity:0}}, {t1 - 0.02:.2f});')

    # ---- gráficos
    v = []
    # AI 2027: linha do tempo
    v.append('<div class="vw" id="v27"><div class="big" style="top:30px;font-size:120px;color:#FACC15">AI 2027</div>'
             '<div class="lbl" style="top:170px;font-size:28px;color:#8b8b98">cenário de Daniel Kokotajlo (ex-OpenAI) e equipe · ai-2027.com</div>'
             '<div class="barra" style="top:236px;height:22px"><div id="b27" style="width:0%;background:#FACC15"></div></div>'
             '<div class="lbl" style="top:268px;font-size:32px;text-align:left">2025<span style="position:absolute;left:46%">2026</span><span style="position:absolute;right:0">2027</span></div>'
             '<div class="item" id="i27a" style="top:350px"><i></i>a IA programa melhor que os melhores programadores</div>'
             '<div class="item" id="i27b" style="top:460px"><i></i>e acelera a própria pesquisa</div>'
             '<div class="fonte" id="r27" style="opacity:0;color:#FACC15">⚠ os próprios autores: pode demorar mais</div></div>')
    t = S["ai2027"]
    J.show("#v27", t - 0.1, J.w("comecou", "stanford") - 0.2)
    J.a(f'tl.to("#b27", {{width:"100%", duration:1.6, ease:"power1.inOut"}}, {(lambda: J.w("ai2027", "2027"))() if any("2027" in norm(x["word"]) for x in pal) else J.w("ai2027", "dois"):.2f});')
    J.show("#i27a", J.w("ai2027", "programa"))
    J.show("#i27b", J.w("ai2027", "acelerar"))
    J.show("#r27", J.w("comecou", "autores"))
    # Stanford: −19%
    v.append('<div class="vw" id="v19"><div class="big" id="n19" style="top:40px;font-size:230px;color:#ff4d4d">−0%</div>'
             '<div class="lbl" style="top:300px;font-size:50px;color:#ff4d4d">NO EMPREGO</div>'
             '<div class="lbl" style="top:372px;font-size:38px">jovens nas funções mais expostas à IA</div>'
             '<div class="fonte" style="bottom:40px;text-align:center">fonte: Stanford Digital Economy Lab · ago/2026</div></div>')
    ts = J.w("comecou", "stanford")
    J.show("#v19", ts - 0.2, S["mapa"])
    J.a(f'tl.to({{n:0}}, {{n:19, duration:2.2, ease:"power2.out", onUpdate:function(){{document.getElementById("n19").textContent="−"+Math.round(this.targets()[0].n)+"%";}}}}, {ts + 0.2:.2f});')
    # mapa dos 5 caminhos (do "200 mil anos" até o fim)
    v.append(f'<div class="vw" id="vm">{mapa_svg()}<div class="fonte">cenários inspirados em Max Tegmark, Life 3.0 · ilustrativo, não previsão</div></div>')
    J.show("#vm", S["mapa"] - 0.1, J.w("decide", "tres") - 0.1)
    J.a(f'tl.to("#hist", {{attr:{{"stroke-dashoffset":0}}, duration:2.4, ease:"power1.inOut"}}, {S["mapa"]:.2f});')
    J.a(f'tl.to("#histt", {{opacity:1, duration:0.4}}, {S["mapa"] + 0.3:.2f});')
    J.a(f'tl.to("#aqui", {{opacity:1, duration:0.4}}, {J.w("mapa", "agora"):.2f});')
    tc = J.w("mapa", "cinco")
    ta = J.w("mapa", "abre")
    for j, k in enumerate(ORDEM):
        J.a(f'tl.to("#l{k}", {{attr:{{"stroke-dashoffset":0}}, duration:1.8, ease:"power1.inOut"}}, {ta + j * 0.18:.2f});')
        J.a(f'tl.to("#t{k}", {{opacity:1, duration:0.3}}, {tc + j * 0.15:.2f});')
    for k in ORDEM:   # caminho ativo acende, os outros a 15%
        t0, t1 = S[k], fim_sec[k]
        for o in ORDEM:
            if o != k:
                J.a(f'tl.to("#g{o}", {{opacity:0.15, duration:0.4}}, {t0 - 0.1:.2f}); tl.to("#g{o}", {{opacity:1, duration:0.3}}, {t1 - 0.3:.2f});')
        J.a(f'tl.to("#l{k}", {{attr:{{"stroke-width":20}}, duration:0.4}}, {t0:.2f}); tl.to("#l{k}", {{attr:{{"stroke-width":12}}, duration:0.3}}, {t1 - 0.3:.2f});')
    # quem decide: 72%
    v.append('<div class="vw" id="v72"><div class="big" id="n72" style="top:10px;font-size:200px;color:#FACC15">0%</div>'
             '<div class="lbl" style="top:230px;font-size:36px">do poder dos 20 maiores supercomputadores de IA<br>está nas mãos de <span style="color:#FACC15">3 donos</span></div>'
             '<div class="barra" style="top:356px"><div id="b72" style="width:0%;background:#FACC15"></div></div>'
             '<div class="lbl" style="top:470px;font-size:32px;text-align:left;color:#FACC15">xAI · Meta · Microsoft<span style="position:absolute;right:0;color:#8b8b98">todos os outros</span></div>'
             '<div class="fonte" style="bottom:10px;text-align:center">fonte: Epoch AI, base de clusters de GPU · out/2026</div></div>')
    td = S["decide"]
    J.show("#v72", J.w("decide", "tres") - 0.3, S["fim"])
    J.a(f'tl.to("#b72", {{width:"72%", duration:1.4, ease:"power2.out"}}, {J.w("decide", "tres"):.2f});')
    J.a(f'tl.to({{n:0}}, {{n:72, duration:1.4, ease:"power2.out", onUpdate:function(){{document.getElementById("n72").textContent=Math.round(this.targets()[0].n)+"%";}}}}, {J.w("decide", "tres"):.2f});')
    # fim: o mapa volta com todos os caminhos
    m2 = mapa_svg().replace('id="', 'id="m2')
    v.append(f'<div class="vw" id="vm2">{m2}<div class="fonte">quem se prepara ajuda a desenhar a linha</div></div>')
    J.show("#vm2", S["fim"] - 0.1)
    J.a(f'tl.set("#m2hist", {{attr:{{"stroke-dashoffset":0}}}}, {S["fim"] - 0.1:.2f}); tl.set("#m2histt", {{opacity:1}}, {S["fim"] - 0.1:.2f}); tl.set("#m2aqui", {{opacity:1}}, {S["fim"] - 0.1:.2f});')
    for j, k in enumerate(ORDEM):
        J.a(f'tl.to("#m2l{k}", {{attr:{{"stroke-dashoffset":0}}, duration:1.2}}, {S["fim"] + j * 0.12:.2f}); tl.set("#m2t{k}", {{opacity:1}}, {S["fim"] + 0.8:.2f});')

    # ---- imagens (faixa do meio)
    B = [("ai2027", None, "ana-2040-vidro.png"), ("comecou", None, "ana-2026.png"), ("mapa", None, "TIRAS")]
    meio = {"E": "ana", "Z": "nenhum", "G": "desde", "P": "risco", "U": ("caminho", 2)}
    for k in ORDEM:
        B += [(k, None, FOTO[k][0]), (k, meio[k], FOTO[k][1])]
    B += [("decide", None, "utopia-familia.png"), ("fim", None, "TIRAS")]
    bh = []
    tb = [S[s] if p is None else J.w(s, *(p if isinstance(p, tuple) else (p,))) - 0.1 for s, p, _ in B]
    assert tb == sorted(tb), "imagens fora de ordem"
    for i, (s, p, im) in enumerate(B):
        t0, t1 = tb[i], (tb[i + 1] if i + 1 < len(B) else dur)
        if im == "TIRAS":   # as 5 Anas lado a lado, uma por caminho
            bh.append(f'<div id="bi{i}" style="position:absolute;inset:0;opacity:0">' + "".join(
                f'<img src="assets/{FOTO[k][0]}" style="opacity:1;left:{j * 216}px;width:216px;object-position:50% 30%">'
                f'<div style="position:absolute;left:{j * 216}px;width:216px;top:0;height:8px;background:{LIN[k][1]}"></div>'
                for j, k in enumerate(ORDEM)) + '</div>')
        else:
            bh.append(f'<img id="bi{i}" src="assets/{im}" style="object-position:50% {30 if im.startswith(("ana-2026", "capa")) else 40}%">')
        J.a(f'tl.to("#bi{i}", {{opacity:1, duration:0.5}}, {max(0, t0 - 0.25):.2f}); tl.set("#bi{i}", {{opacity:0}}, {t1 + 0.3:.2f});')
        J.a(f'tl.fromTo("#bi{i}", {{scale:1}}, {{scale:1.07, duration:{t1 - t0 + 0.6:.2f}, ease:"none", immediateRender:false}}, {max(0, t0 - 0.25):.2f});')
    tags = [("mapa", "durante", "esta é a Ana, 30 anos: a mesma pessoa nos 5 futuros", "#FACC15"), ("E", "vive", "a casa dela está vazia", LIN["E"][1]), ("Z", "escolha", "✕ trabalho  ✕ contas  ✕ escolha", LIN["Z"][1]),
            ("G", "regra", "nota de cidadã · câmeras em cada esquina", LIN["G"][1]), ("P", "quando", "doenças vencidas · cidade verde", LIN["P"][1]),
            ("U", "equipe", "ela lidera o próprio projeto", LIN["U"][1])]
    tg = []
    for i, (s, p, txt, cor) in enumerate(tags):
        if not txt:
            continue
        try:
            t0 = J.w(s, p)
        except SystemExit:
            print(f"aviso: tag sem palavra {s}/{p}"); continue
        tg.append(f'<div class="tag" id="tg{i}" style="top:36px;color:{cor}">{txt}</div>')
        J.show(f"#tg{i}", t0, min([x for x in tb if x > t0 + 0.3] + [fim_sec[s]]))

    leg = legenda(J, [{"word": x["word"], "t": x["t"]} for x in pal], dur)
    capa_ate = S["ai2027"]
    J.a(f'tl.set("#legenda", {{opacity:0}}, 0); tl.set("#legenda", {{opacity:1}}, {capa_ate - 0.1:.2f});')
    tiras = "".join(f'<div class="tira" style="left:{j * 216}px"><img src="assets/{FOTO[k][0]}"><span style="color:{LIN[k][1]}">'
                    f'{LIN[k][0].split()[0]}</span></div>' for j, k in enumerate(ORDEM))
    capa = (f'<div id="capa" class="clip" data-start="0" data-duration="{capa_ate + 0.4:.2f}" data-track-index="12">{tiras}<div class="grad"></div>'
            f'<span class="chip">5 FUTUROS DA IA</span><div class="tit"><small>O MUNDO VAI MUDAR.</small>VOCÊ TEM <b>ESCOLHA?</b></div></div>')
    J.a(f'tl.to("#capa", {{opacity:0, duration:0.4}}, {capa_ate - 0.1:.2f});')
    lis = "".join(f'<div class="li" id="fl{j}"><i style="background:{LIN[k][1]}"></i><span style="color:{LIN[k][1]}">{LIN[k][0]}</span></div>'
                  for j, k in enumerate(ORDEM))
    fim_html = (f'<h2 style="top:240px;font-size:120px;color:#fff">QUAL FUTURO</h2><h2 style="top:370px;font-size:120px;color:#FACC15">VOCÊ ESCOLHE?</h2>'
                f'<div class="lista">{lis}</div>'
                f'<div class="sub" id="fsub" style="top:1260px">comenta aqui o seu caminho<br><span class="pill">playlist 5 futuros no canal</span><br><span style="font-size:40px;color:#FACC15">inema.club · kit aberto e gratuito</span></div>')
    for j in range(5):
        J.a(f'tl.to("#fl{j}", {{opacity:1, duration:0.25}}, {dur + 0.1 + j * 0.25:.2f});')
    J.a(f'tl.to("#fsub", {{opacity:1, duration:0.3}}, {dur + 1.5:.2f});')
    total = round(dur + FIM, 2)
    html = f'''<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1080" data-height="1920">
 <div id="hdr" class="clip" data-start="0" data-duration="{dur:.2f}" data-track-index="1"><div class="marca">INEMA <span>· 5 FUTUROS</span></div>{"".join(hh)}</div>
 <div id="graf" class="clip" data-start="0" data-duration="{dur:.2f}" data-track-index="2">{"".join(v)}</div>
 <div id="banda" class="clip" data-start="0" data-duration="{dur:.2f}" data-track-index="5">{"".join(bh)}<div class="sombra"></div>{"".join(tg)}</div>
 <div id="avw"><video id="av" src="assets/av.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="4" data-has-audio="true" data-volume="1" playsinline></video></div>
 <div id="legenda" class="clip" data-start="0" data-duration="{dur:.2f}" data-track-index="10">{leg}</div>
 <div id="fim" class="clip fim" style="left:0;top:0;width:1080px;height:1920px" data-start="{dur - 0.4:.2f}" data-duration="{FIM + 0.4:.2f}" data-track-index="11">{fim_html}</div>
 {capa}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.to("#fim", {{opacity:1, duration:0.4}}, {dur - 0.4:.2f});
{chr(10).join(J.js)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>'''
    (CENA / "index.html").write_text(html)
    for f in ("hyperframes.json", "package.json"):
        shutil.copy2(C / "cena-a" / f, CENA / f)
    (AQUI / "build").mkdir(exist_ok=True)
    (AQUI / "build" / "secoes.json").write_text(json.dumps({"secoes": S, "dur": dur, "total": total}, indent=1))
    print(f"ok · {total:.1f} s · seções {S}")


if __name__ == "__main__":
    main()
