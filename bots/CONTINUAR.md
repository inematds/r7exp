# CONTINUAR — r7exp "Qual bot você vai usar?" (22/10/2026)

Pasta: `~/projetos/r7exp/bots`. Par do refazvideo `~/projetos/output/explica-D-pz8L1orVI` (mesmo tema).
Fase 1 feita: ficha, 6 falas (`falas/`), avatar enviado ao estúdio HeyGen (`avatar/*.id`), imagens da Carla pelo Codex
(`imagens/`, folha `build/folha-imagens.jpg`), capa `imagens/capa-r7.png`, gerador `gera_bots.py` testado com `--falso`
(snapshot `build/snapF/`), reels `gera_reels_bots.py`. A cadeia `cadeia.sh` (unidade `r7exp-bots-cadeia-*`) baixa o avatar,
junta e transcreve (`motor/monta_avatar.py bots a`), renderiza o completo `build/qual-bot-r7exp.mp4` (+ `-720.mp4`),
o limpo e os 5 reels `build/reel-indice-4-bots.mp4`, `build/reel-bot-{1-grok,2-muse,3-dots,4-duet}.mp4`, e escreve `FIM_R7EXP`.

## Ordem do Nei (citada)
- "no final faz um r7exp do conteúdo e manda para mim e no lives1" (o conteúdo = comparação Grok Bot, Meta Muse,
  ChatGPT Dots, Claude Duet; o Duet ainda não está no Brasil; vantagem de cada um).
- r7exp = completo 16:9 + reels 9:16 na mesma entrega (regra de 22/10).

## Se o cadeia.log tiver ERRO
- "gera_bots (âncora…)": o Whisper escreveu a palavra diferente. Ler `tempos/<fala>.json`, trocar a âncora em
  `bots/gera_bots.py` (ex.: número em algarismo "41", "3"; "Claude" pode vir "Cloud") e rodar `bash bots/cadeia.sh` de novo
  (o avatar já baixado e o `build/segmentos-a.json` são reaproveitados).
- render: ler o log indicado, corrigir o mínimo, rodar de novo. Registrar a falha em `~/projetos/r7exp/FALHAS.md` (1 linha).

## O que falta (fase 2)
1. Conferir quadros: `env -u GEMINI_API_KEY npx hyperframes snapshot bots/cena-a --frames 16 --describe false -o bots/build/snapR`
   e uma folha de cada reel. Reprovar: texto cortado/sobreposto, tela vazia, avatar em tela cheia, painel atrás do avatar.
2. Mandar ao **bot v3** (só arquivos, legenda sem link): `build/qual-bot-r7exp-720.mp4` e os 5 reels, com
   `node ~/projetos/refazvideo/ferramentas/enviar_bot_v3.mjs` (cada envio imprime "msg N").
3. Publicar no **lives1** (público), sem citar o autor do vídeo original:
   - completo: `cd ~/projetos/yt-pubx && ./yt-pubx publicar ~/projetos/r7exp/bots/build/qual-bot-r7exp.mp4 --canal lives1 --contexto-arquivo ~/projetos/r7exp/bots/falas/0-intro.txt --contexto "r7exp: a Carla, consultora, testa os 4 agentes pessoais (Grok Bot, Meta Muse, ChatGPT Dots, Claude Duet); a força e o ponto fraco de cada um; Duet ainda não está no Brasil. CTA inema.club." --dry-run`, olhar a thumb, publicar com `--plano`.
   - os 5 reels (9:16, sem thumb): mesmo comando com cada `build/reel-*.mp4` e contexto do bot daquele reel.
4. Links: mandar todos os links ao **inemaytbot** dizendo "Publicado no lives1 (INEMA TDS)" (token TELEGRAM_NOTIFY_BOT_TOKEN
   em `~/projetos/yt-pub-livesx-master/config/.env`, chat em `~/.config/aventurasinemavideo/telegram_chat`).
5. `ESTADO.md` na pasta (modelo `php/ESTADO.md`), commit + push no repo r7exp (autor inematds), e gravar
   `CONTINUAR.resultado` com "FEITO: <urls> · v3 msgs N…" ou "FALHOU: <passo> — <motivo>".

## Travas
- Nada de nova gravação HeyGen nem API paga. Só o canal lives1. Não apagar nada no Telegram/YouTube.
- `hyperframes snapshot` sempre com `--describe false` e sem GEMINI_API_KEY (senão chama o Gemini por API).
