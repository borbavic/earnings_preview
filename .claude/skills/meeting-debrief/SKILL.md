---
name: meeting-debrief
description: Transforma as notas de uma reunião com empresa (Granola) em scorecard contra a tese, sentimento da reunião vs. sentimento da ação e post no Teams. Usar quando o analista disser "processa a reunião com X", "debrief", "scorecard da reunião", "manda pro Teams", ou ao sair de reuniões de conferência.
---

# Meeting debrief

Arquivos (relativos à raiz do repo):
- `meeting_notes/thesis_cards/{TICKER}.md` — tese, pilares e sentimento base da ação
- `meeting_notes/scorecard_rubric.md` — regras de pontuação (ler antes de pontuar)
- `meeting_notes/post_to_teams.py` — faz as contas, grava o registro .md e publica no Teams
- `meeting_notes/records/` — um JSON + um MD por reunião

## Passos

1. **Achar a reunião no Granola.** `search_meetings` por empresa/ticker e data, depois `get_meetings`
   para ler as notas. Se o plano permitir, usar `get_meeting_transcript` para tirar frases literais.
   No plano free não há transcrição pelo MCP: trabalhar só com as notas e dizer isso no registro.

2. **Carregar a ficha da empresa.** Se `thesis_cards/{TICKER}.md` não existir, parar e pedir ao
   analista a tese (ou propor um rascunho da Parte A para ele validar). Nunca inventar a tese.
   Se a Parte B (sentimento base) tiver mais de 7 dias, atualizar com busca na web, citando fonte e
   data de cada dado, e avisar que o dado pode estar desatualizado.

3. **Pontuar** seguindo `scorecard_rubric.md`:
   - Cada nota diferente de zero precisa de evidência literal ou de um número das notas. Sem
     evidência, a nota é `null` (pilar) ou 0 (dimensão).
   - Tom é medido contra a "última interação" registrada na ficha, não em termos absolutos.
   - Separar o que a empresa disse da nossa interpretação.
   - Marcar cada highlight como `Consenso` ou `Diferenciado`, comparando com a tabela "Nós vs.
     consenso" da ficha e com a narrativa da Parte B. Diferenciado = algo que o consenso não modela.
   - Marcar `bear_trigger_hit: true` se algum gatilho do caso bear apareceu.
   - Não calcular médias nem gap à mão: o script faz isso.

4. **Gravar** `meeting_notes/records/{AAAA-MM-DD}_{TICKER}_{formato}.json` no formato de
   `records/_example_debrief.json` e rodar:
   `python3 meeting_notes/post_to_teams.py <arquivo.json> --print-card`

5. **Mostrar ao analista** no chat: veredito, gap, ação sugerida, highlights e red flags. Pedir
   confirmação antes de publicar, a menos que ele já tenha dito para publicar direto.

6. **Publicar** com `--post` (precisa de `TEAMS_WEBHOOK_URL` no ambiente). Se o webhook não estiver
   disponível, entregar o texto do registro .md pronto para colar no Teams.

7. **Fechar o ciclo.** Propor a atualização da seção "Tom da gestão na última interação" da ficha
   com as frases desta reunião, para servir de referência na próxima.

## Modo conferência (várias reuniões no dia)

Ao final do dia, se pedido: listar as reuniões do dia no Granola, processar cada uma e montar um
resumo com uma linha por empresa (ticker, veredito, gap, ação), ordenado pelo |gap|.
