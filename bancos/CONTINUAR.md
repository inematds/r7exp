# CONTINUAR — r7exp "A IA da OpenAI vai quebrar os sistemas dos bancos?" (22/10/2026)

Pasta: `~/projetos/r7exp/bancos`. Par do r7ex `~/projetos/r7ex/edicoes/2026-10-22-openai-bancos` (esse vai sozinho pela
produção r7ex → fila do lives8; não mexer nele aqui, só citar no tópico se já tiver link).

Fase 1 feita: ficha, 6 falas (`falas/`), avatar enviado ao estúdio HeyGen (`avatar/*.id`), imagens do Marcos pelo Codex
(`imagens/`), capa `imagens/capa-r7.png` (texto da thumb do Nei), gerador `gera_bancos.py` testado com `--falso`
(snapshot `build/snapF/`), gráfico do teste da OpenAI (5,4 → 86,6 → 97,9) na peça 2, reels `gera_reels_bancos.py`.
A cadeia `cadeia.sh` (unidade `r7exp-bancos-cadeia-*`) baixa o avatar, junta e transcreve (`motor/monta_avatar.py bancos a`),
renderiza o completo `build/openai-bancos-r7exp.mp4` (+ `-720.mp4`), o limpo e os 5 reels `build/reel-indice-4-pecas.mp4`,
`build/reel-peca-{1-antigo,2-salto,3-centavo,4-empresa}.mp4`, e escreve `FIM_R7EXP`.

## Ordem do Nei (citada)
- "quero criar um video r7exp [texto-gatilho: A IA da OPENAI Vai QUEBRAR os Sistemas dos BANCOS e das Empresas Gigantes!]
  ... e faz outro tambem r7ex, coloque os dois videos no lives8 inema.dev"
- r7exp = completo 16:9 + reels 9:16 na mesma entrega (regra de 22/10).
- Título que o Nei deu: "A IA da OPENAI Vai QUEBRAR os Sistemas dos BANCOS e das Empresas Gigantes!"
- Thumb que o Nei deu: "OPENAI VAI QUEBRAR / OS SISTEMAS DOS BANCOS! / EMPRESAS GIGANTES SÃO AS PRÓXIMAS?" (já é a capa-r7.png).

## Se o cadeia.log tiver ERRO
- "gera_bancos (âncora…)": o Whisper escreveu a palavra diferente. Ler `tempos/<fala>.json`, trocar a âncora em
  `bancos/gera_bancos.py` (atenção: "COBOL" pode vir "Cobol"/"Cobalt"; "OpenAI" pode vir "Open AI"; número pode vir em algarismo)
  e rodar `bash bancos/cadeia.sh` de novo (avatar baixado e `build/segmentos-a.json` são reaproveitados).
- render: ler o log indicado, corrigir o mínimo, rodar de novo. Registrar a falha em `~/projetos/r7exp/FALHAS.md` (1 linha).

## O que falta (fase 2)
1. Conferir quadros: `env -u GEMINI_API_KEY npx --yes hyperframes@0.8.181 snapshot bancos/cena-a --frames 20 --describe false -o bancos/build/snapR`
   e uma folha de cada reel. Reprovar: texto cortado/sobreposto, tela vazia, avatar em tela cheia, painel atrás do avatar,
   gráfico da peça 2 sem as 3 barras ou com a linha de fonte coberta pela legenda.
2. Mandar ao **bot v3** (só arquivos, legenda sem link): `build/openai-bancos-r7exp-720.mp4` e os 5 reels, com
   `node ~/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs` (cada envio imprime "msg N").
3. Publicar no **lives8** (Inema Vibe, público), sem citar o autor do vídeo em inglês que serviu de base:
   - completo: `cd ~/projetos/yt-pubx && ./yt-pubx publicar ~/projetos/r7exp/bancos/build/openai-bancos-r7exp.mp4 --canal lives8 --contexto-arquivo ~/projetos/r7exp/bancos/falas/0-intro.txt --contexto "r7exp (Nei Maldaner, INEMA.CLUB). Título sugerido pelo Nei: 'A IA da OPENAI Vai QUEBRAR os Sistemas dos BANCOS e das Empresas Gigantes!'. A OpenAI (pesquisa de 19/10/2026) mostrou o GPT 6.1 Soul reescrevendo programas em COBOL — linguagem de mais de 60 anos por trás de 95% das transações em caixa eletrônico e 80% das compras com cartão — com resultado idêntico: 5,4% no modelo anterior, 86,6% no novo e 97,9% pensando mais. Quebrar não é derrubar banco: é quebrar a dependência de tecnologia antiga. O perigo do centavo (COBOL corta, o moderno arredonda) e por que um especialista ainda confere. O Marcos, dono de distribuidora, atravessa as 4 peças. Para a sua empresa: entender o que existe, identificar riscos, testar com IA e mudar aos poucos. Teste da própria OpenAI, ainda privado. CTA inema.club, comente 'eu vou modernizar'." --dry-run`,
     olhar a thumb (deve sair da capa-r7.png com o texto do Nei; se o yt-pubx fizer outra, usar a capa-r7.png), publicar com `--plano`.
   - os 5 reels (9:16, sem thumb): mesmo comando com cada `build/reel-*.mp4`, `--canal lives8`, contexto da peça daquele reel.
4. **INEMA.DEV** (Telegram): tópico novo no grupo INEMA.DEV com a skill `postar-telegram` (mesmo formato do tópico 7527 do
   PHP2Shell): título, texto em blocos curtos, links do completo e dos reels, e título + link no MENU do grupo.
5. Links: mandar todos os links ao **inemaytbot** dizendo "Publicado no lives8 (Inema Vibe)" (token TELEGRAM_NOTIFY_BOT_TOKEN
   em `~/projetos/yt-pub-livesx-master/config/.env`, chat em `~/.config/aventurasinemavideo/telegram_chat`).
6. `ESTADO.md` na pasta (modelo `bots/ESTADO.md`), commit + push no repo r7exp (autor inematds), e gravar
   `CONTINUAR.resultado` com "FEITO: <urls> · v3 msgs N… · tópico INEMA.DEV N" ou "FALHOU: <passo> — <motivo>".

## Travas
- Nada de nova gravação HeyGen nem API paga. Só o canal lives8. Não apagar nada no Telegram/YouTube.
- `hyperframes snapshot` sempre com `--describe false` e sem GEMINI_API_KEY (senão chama o Gemini por API).
- Não mexer na produção do r7ex (`producao.py`); ele publica sozinho pela fila do lives8.
