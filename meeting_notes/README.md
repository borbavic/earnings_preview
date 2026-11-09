# Notas de reunião: tese, sentimento e Teams

Sistema para sair de uma reunião com empresa e ter, em poucos minutos, um scorecard contra a nossa
tese, o sentimento da reunião comparado ao sentimento da ação e um post no Teams.

## Decisão: Notion não é necessário

| Peça | Ferramenta | Por quê |
|---|---|---|
| Captura e resumo factual | **Granola** (template próprio) | Grava e resume; app de iPhone para reuniões presenciais |
| Cérebro: tese, scorecard, sentimento | **Claude** + fichas em `thesis_cards/` | Precisa da tese e da linha de base de cada empresa, que o Granola não tem |
| Contas (médias, gap, veredito) | `post_to_teams.py` | Determinístico: o LLM dá as notas com evidência, o script faz a conta |
| Distribuição | **Teams** (Workflows webhook) | Já faz parte do Microsoft 365; sem custo extra |
| Arquivo histórico | `records/` neste repo (ou SharePoint) | Um .json + um .md por reunião; o Claude consegue consultar o histórico |

O Notion só acrescentaria uma interface de banco de dados (filtrar por ticker, ver o sentimento ao
longo do tempo). Se o chefe quiser isso depois, basta conectar o Notion ao Claude e trocar o destino
do registro: o template não muda.

**Onde vale gastar:** Granola Business (~US$14/usuário/mês). No plano free o Claude não acessa a
transcrição pelo conector, só as notas resumidas, e o histórico fica limitado a 30 dias. A transcrição
é onde estão as frases literais e o hedging, que alimentam a nota de tom.

## Fluxo depois de cada reunião

1. Granola grava com o template "Equity: Reunião com Empresa" (`granola_template.md`).
2. No Claude: "processa a reunião com {TICKER}" (skill `.claude/skills/meeting-debrief`).
3. O Claude lê as notas no Granola, carrega `thesis_cards/{TICKER}.md`, pontua pela
   `scorecard_rubric.md` e grava `records/{data}_{TICKER}_{formato}.json`.
4. `post_to_teams.py` calcula score de tese, sentimento da reunião, gap e ação sugerida, grava o .md
   e publica o card no canal (depois da sua confirmação).

Exemplo fictício de entrada e saída: `records/_example_debrief.json` e `records/_example_debrief.md`.
Ele mostra o ponto central do método: reunião levemente positiva (+0,20) numa ação com sentimento
base esticado (+1,20) dá gap de -1,00, ou seja, o que ouvimos é pior do que o preço já desconta.

## Checklist antes da conferência

- [ ] **Compliance:** confirmar que o uso do Granola (gravação/transcrição por IA) está aprovado e qual
      é a regra de consentimento nas reuniões com empresas. Isso vem antes de tudo.
- [ ] Criar o template no Granola (`granola_template.md`) e testar numa reunião interna.
- [ ] Decidir sobre o Granola Business (transcrição + histórico).
- [ ] Criar uma ficha em `thesis_cards/` por empresa com reunião marcada (copiar `_TEMPLATE.md`).
      Parte A com o time; Parte B (sentimento base) até 48h antes da reunião.
- [ ] Teams: no canal desejado → `...` → **Workflows** → "Post to a channel when a webhook request is
      received". Copiar a URL gerada e guardá-la como segredo (não commitar).
- [ ] Teste de ponta a ponta: `python3 post_to_teams.py records/_example_debrief.json --post`.

## Comandos

```bash
python3 post_to_teams.py records/_example_debrief.json --print-card
```

```bash
TEAMS_WEBHOOK_URL='<url do Workflow>' python3 post_to_teams.py records/<arquivo>.json --post
```
