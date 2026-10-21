"""Imagens do reel r7exp 9:16 "Musk: os humanoides vão mudar tudo" pelo Codex image_gen (assinatura, sem API).
Uso: python3 gerar.py [id ...]. Marcos: marcos.png primeiro; marcos-vazio e marcos-robo usam ele como referência (-i).
Robô = humanoide realista estilo Optimus, visor preto liso, nunca cartoon. Nenhuma pessoa famosa."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = ("Use a ferramenta de geração de imagem (image_gen) para criar UMA imagem VERTICAL em RETRATO 9:16 (o maior tamanho "
        "vertical disponível, 1024x1536 ou próximo). Estilo: fotografia cinematográfica fotorrealista, dramática, luz NEUTRA, "
        "balanço de branco neutro: pele natural, NUNCA amarelado, dourado ou sépia, sem cara de CGI nem de desenho. Robô, "
        "quando houver: humanoide realista no estilo do Tesla Optimus, corpo branco e grafite, juntas pretas, cabeça lisa com "
        "visor PRETO brilhante sem rosto, calmo, nada de olho vermelho nem ameaça, nada de cartoon. Todo texto na imagem em "
        "PORTUGUÊS DO BRASIL, com acentos corretos, sem erros de grafia; nenhum outro texto além do pedido. Nenhum logotipo, "
        "nenhuma marca d'água, nenhuma pessoa famosa ou reconhecível. Um assunto principal só, forte, com contraste. "
        "Salve o arquivo final exatamente como ./arte.png neste diretório e responda só 'ok'.\n\nCena: {cena}")
MARCOS = ("Marcos, homem brasileiro de uns 45 anos, pele morena clara, cabelo curto escuro com fios grisalhos nas têmporas, "
          "barba curta por fazer, camisa de trabalho cinza-azulada de manga curta com a gola aberta e um pano de oficina no "
          "bolso de trás")
REF = (" A imagem anexada é a REFERÊNCIA do personagem: é o MESMO homem (mesmo rosto, mesmo cabelo, mesma barba, mesma "
       "camisa cinza-azulada) e a MESMA pequena oficina; mude só o que a cena pede.")
ITENS = {
    "capa": ("Capa de reel viral. Close emocional, de frente, da cabeça e dos ombros de um robô humanoide estilo Optimus, visor "
             "preto liso refletindo luzes frias, olhando direto para o espectador, fundo escuro de galpão com bokeh. O robô ocupa "
             "a faixa do MEIO-ALTO da imagem (entre 22% e 50% da altura). A METADE DE BAIXO (50% a 100%) é quase preta #0c0c10, "
             "lisa, escurecendo naturalmente, sem texto e sem objetos. Tipografia essencial, no TOPO (entre 4% e 22% da altura), "
             "extra-negrito sem serifa condensado, centralizado, com margem lateral de 8%: em branco enorme 'VAI MUDAR' e logo "
             "abaixo, ainda maior, em amarelo #FACC15, 'TUDO'. Grafia exata, só essas três palavras.", None),
    "marcos": (f"{MARCOS}, de pé dentro da própria pequena oficina mecânica de bairro no Brasil, olhando para a câmera com "
               "expressão séria e pensativa, mãos um pouco sujas de graxa, um carro popular com o capô aberto atrás dele, "
               "ferramentas na parede, luz branca de oficina, natural. Enquadramento da cintura para cima, o homem na metade "
               "de cima da imagem; o terço de baixo mais escuro. Sem texto.", None),
    "marcos-vazio": (f"{MARCOS}, sozinho na oficina VAZIA, sem nenhum carro, sem clientes, sentado num banquinho com os "
                     "cotovelos nos joelhos, olhando preocupado para o celular, portão aberto mostrando a rua vazia; luz fria "
                     "e azulada, sensação de desânimo. O homem na metade de cima da imagem; o terço de baixo mais escuro. "
                     "Sem texto." + REF, "marcos.png"),
    "marcos-robo": (f"{MARCOS}, confiante e sorridente, braços cruzados, na mesma oficina agora CHEIA: atrás dele um robô "
                    "humanoide estilo Optimus trabalha no motor de um carro com o capô aberto, e um cliente conversa com o "
                    "Marcos com um aperto de mão; luz branca neutra, clara, sensação de prosperidade. O homem na metade de cima "
                    "da imagem; o terço de baixo mais escuro. Sem texto." + REF, "marcos.png"),
}


def gera(k):
    cena, ref = ITENS[k]
    out = os.path.join(AQUI, f"{k}.png")
    if os.path.exists(out):
        return k, "já existe"
    d = os.path.join(AQUI, "work", k)
    os.makedirs(d, exist_ok=True)
    cmd = ["codex", "exec", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox", "-"]
    if ref:  # -i aceita vários arquivos: fica no fim, depois do "-"
        cmd += ["-i", os.path.join(AQUI, ref)]
    r = subprocess.run(cmd, input=BASE.format(cena=cena), cwd=d, capture_output=True, text=True, timeout=1500)
    open(os.path.join(d, "codex.log"), "w").write((r.stdout or "") + "\n" + (r.stderr or ""))
    if os.path.exists(os.path.join(d, "arte.png")):
        os.replace(os.path.join(d, "arte.png"), out)
        return k, "OK"
    return k, "FALHOU " + (r.stderr or r.stdout)[-300:]


pedidos = sys.argv[1:] or ["capa", "marcos", "marcos-vazio", "marcos-robo"]
primeiro = [k for k in pedidos if k in ("capa", "marcos")]
depois = [k for k in pedidos if k not in primeiro]
with ThreadPoolExecutor(2) as ex:
    for lote in (primeiro, depois):
        for k, st in ex.map(gera, lote):
            print(k, st, flush=True)
print("FIM_GERAR")
