# Padrão r7exp — RASCUNHO (aguarda aprovação do protótipo)

## 1. Plano (antes da fala)
| Campo | Regra |
|---|---|
| tema | um assunto com **opções/cenários** (futuros, caminhos, tipos, escolhas) |
| mapa | o gráfico/diagrama que mostra todas as opções de uma vez (SVG próprio, em PT, com fonte) |
| personagem | uma pessoa fixa (nome, idade, roupa) que aparece em todas as opções |
| opções | 3–6; para cada uma: O QUE É · COMO VOCÊ VIVE · O QUE LEVA ATÉ LÁ (com fonte) |
| ação | o que a pessoa pode fazer, cada ação ligada a uma alavanca no mapa |
| destino | página do inema.club |

## 2. Estrutura do completo 16:9 (4–6 min)
1. **Gancho no mapa** (0–15 s): o gráfico se desenha; "estamos aqui"; a pergunta.
2. **Personagem hoje** (15–30 s): a pessoa em 2026.
3. **Uma parte por opção** (40–60 s cada): câmera entra na linha → painel de 3 linhas → a personagem transformada
   → como se chega lá (diagrama de causa) → volta ao mapa.
4. **Comparação**: todas as versões da personagem lado a lado.
5. **O que fazer**: ações empurrando a curva para cima, ao vivo.
6. **CTA** inema.club + pergunta.

## 3. Reels que saem do completo
- Um reel por opção (o bloco 3 em 9:16, 35–60 s), sempre terminando com "existem outros N caminhos".
- Um reel-índice: o mapa + as N versões da personagem em 2 s cada + "qual é o seu?".

## 4. Tela (linguagem visual)
- Mapa SVG animado: linhas desenhadas por `stroke-dashoffset`, a linha ativa acende, as outras ficam a 15%.
- Câmera no mapa ≤ 1,25× (tem texto); dissolve entre partes; troca de conteúdo a cada ≤ 4 s (16:9) / 1,5–3 s (9:16).
- Painel: O QUE É / COMO VOCÊ VIVE / O QUE LEVA ATÉ LÁ, ícones de traço, item entra na palavra falada.
- Personagem: mesma referência em todas as imagens (Codex com imagem de referência); transição por máscara/varredura.
- Diagrama de causa: nós que acendem em sequência (A → B → C).
- Cores: preto `#0c0c10`, amarelo `#FACC15` no destaque, cada opção com sua cor de linha do mapa; fonte Sora/Montserrat.
- Avatar do Nei: PiP, nunca tela cheia (D8). Sem efeitos sonoros (D7).
