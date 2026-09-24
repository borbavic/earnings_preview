# Framework bottom-up: receita 2030 de OpenAI e Anthropic

Data: 24-set-2026. Dados de mercado até ago-2026 (run-rates, usuários, GW). Vários pontos vêm de imprensa que resume divulgações das empresas, não de filings. Antes de usar no deck, revalidar os números marcados como "secundário" na aba Sources do modelo.

Arquivos: modelo em `model/AI_labs_revenue_2030_bottomup.xlsx` (fórmulas vivas, coluna Custom editável) e a mesma lógica em `model/revenue_2030_model.py`.

---

## 1. Conclusão

**$350-400B por empresa em 2030 é o topo do range defensável, não o base.** Bate com os planos das próprias empresas (OpenAI >$280B, com relatos de até ~$350B; Anthropic $190-200B já em 2028) e com a trajetória do run-rate, mas exige 1,3-1,6x o que o nosso bottom-up base entrega.

| 2030, $B | Bear | Base | Bull | Plano da empresa | Momentum (run-rate) |
|---|---|---|---|---|---|
| OpenAI | 96 | 298 | 714 | >280 (fev-26), ~350 em relatos posteriores | 274 |
| Anthropic | 82 | 259 | 568 | 190-200 em 2028 (caso de IPO) | 346 |
| Combinado | 178 | 557 | 1.282 | ~500-550 | 620 |

Para contexto: a mediana de superforecasters para OpenAI+Anthropic combinados em 2030 é $300B (34% de chance de >$400B). Nosso base combinado ($557B) está acima disso e alinhado aos planos das empresas.

**Três pontos que precisam estar explícitos no deck:**

1. **A aritmética de GW não fecha como está.** 25 GW × $35B/GW = $875B, não $350-400B. $350-400B corresponde a 10-11 GW a $35B/GW, ou a 25 GW a $14-16B/GW. Precisamos escolher uma das duas teses, porque elas contam histórias diferentes (ver seção 5).
2. **$35B/GW é bull, não base.** OpenAI hoje realiza ~$10B por GW de capacidade total (0,2 GW → $2B em 2023; 1,9 GW → $20B em 2025). Anthropic realiza ~$18-20B/GW (~5 GW no fim de 2026 vs. run-rate de saída de ~$90B). Nosso base 2030 é $13,5B/GW. Chegar a $35B/GW exige ganho simultâneo nas quatro alavancas: share de inferência na frota, utilização, tokens/GW (Rubin) e preço realizado por token.
3. **O gargalo é compute, não demanda.** No base, o bottom-up da Anthropic ($259B) excede a capacidade de 16 GW a $13,5B/GW ($216B). Ou ela chega a ~19 GW, ou realiza ~$16B/GW. Para OpenAI, 22 GW a $13,5B/GW ($297B) fecha exatamente com o bottom-up ($298B).

**O que é consenso e o que é diferenciado:**

- Consenso (planos das empresas e sell-side que os replica): OpenAI ~$300B em 2030, mix consumer/enterprise 50/50, ads $100B; Anthropic ~$200B em 2028, ~80% API/enterprise.
- Diferenciado (nosso): a restrição é $/GW, não penetração. O debate certo com o time não é "quantos usuários" e sim "quanto de receita por GW e por que". E o motor que decide a Anthropic é gasto por desenvolvedor em agentes (base $9,75k/dev/ano vs. $1,8-3k hoje), não assentos de knowledge worker.

---

## 2. A identidade que a apresentação precisa fechar

A receita de 2030 tem que ser a mesma vista por três lentes independentes. Se uma não fecha, a projeção não está pronta.

```
DEMANDA (bottom-up)                    OFERTA (compute)                                  MOMENTUM
Σ usuários pagantes × gasto × share  =  GW × %inferência × utilização × tokens/GW × $/M tok  ≈  run-rate 2026 × Π(1+g)
```

| Lente | O que responde | Onde erra |
|---|---|---|
| Demanda | Quem paga, quanto e por quê | Multiplica muitas premissas; bear/bull explodem |
| Oferta | Quanto a frota consegue faturar | $/GW depende de preço por token, que cai 5-10x/ano por unidade de capacidade |
| Momentum | O que o run-rate atual já embute | Extrapola desaceleração sem dizer de onde vem a receita |
| Base rates | Se o número é plausível vs. folha salarial, software, ads | Só dá ordem de grandeza |

A ponte de $/GW é o slide central:

| Receita por GW de capacidade total | Valor | Como se chega |
|---|---|---|
| OpenAI 2023 | ~$10B | 0,2 GW → $2B run-rate |
| OpenAI 2025 | ~$10,5B | 1,9 GW → >$20B run-rate |
| Anthropic 2026 (est.) | ~$18-20B | ~5 GW fim-26 vs. ~$90B run-rate de saída |
| Base 2030 | $13,5B | 20q tokens/GW × $1,6/M × 68% util × 62% inferência |
| Bull 2030 | $47B | 32q × $2,6/M × 78% × 72% |
| Deck (atual) | $35B | Exige tudo do bull ao mesmo tempo |

Leitura: o preço realizado por token cai, mas tokens por GW sobem com Rubin e o share de inferência sobe quando a receita escala. $13,5B/GW assume que esses efeitos quase se cancelam. $35B/GW assume que capacidade vira receita quase 1:1 com margem de software madura (ver tabela de margem bruta na seção 5).

---

## 3. Motor enterprise (o que decide a Anthropic)

### 3.1 Árvore de drivers

```
Knowledge workers globais (~1,05B)
├─ Devs / engenheiros de dados e IA (38M) ─┐
├─ Profissionais de alta intensidade (220M) ├─ × penetração paga × (salário × % gasto em IA) = pool global por tier
└─ Knowledge workers gerais (790M) ─────────┘                                                  × share da empresa
Pool de trabalho automatizável ($8T de folha) × % automatizado por agentes × captura do vendor = pool "machine API"
                                                                                                × share da empresa
```

Quatro motores, cada um com pool global (todos os vendors) e share da empresa. O share captura receita direta (Claude Code, ChatGPT Enterprise) e a camada de modelo dentro de ferramentas de terceiros (Cursor, Copilot, Bedrock, Vertex, Foundry).

### 3.2 Premissas e âncoras 2026

| Driver | Bear | Base | Bull | Âncora 2026 |
|---|---|---|---|---|
| Devs (M) / penetração paga | 34 / 68% | 38 / 80% | 44 / 90% | ~30M devs; ~10-12M assentos pagos (Copilot 4,7M, Cursor, Claude Code, Codex) = 35-40% |
| Gasto por dev pago ($/ano) | 5.040 | 9.750 | 12.800 | Claude Code enterprise $150-250/mês = $1,8-3k; heavy users >$1k/mês |
| Profissionais (M) / penetração | 205 / 32% | 220 / 45% | 240 / 55% | ~35-40M assentos pagos no mundo (M365 Copilot 20M, ChatGPT biz 9M) = ~4% dos KW, ~10% dos profissionais |
| Gasto por profissional pago ($/ano) | 855 | 1.800 | 2.925 | Copilot $360; ChatGPT Enterprise ~$600-900 com uso; Atlanta Fed: $2.068/funcionário em IA (tudo incluso) |
| KW gerais (M) / penetração | 770 / 14% | 790 / 25% | 815 / 38% | Produtos de assento a $20-30/mês; bundling do Copilot |
| Gasto por KW geral ($/ano) | 203 | 360 | 640 | Copilot $360 |
| Pool automatizável ($T) × % automatizado × captura | 7 × 6% × 20% | 8 × 10% × 25% | 10 × 14% × 30% | Folha global ~$58T; knowledge work $35-50T; só suporte e coding têm agentes em escala |
| Share Anthropic: devs / pros / gerais / machine | 35/13/6/30% | 42/20/8/38% | 48/24/12/40% | Menlo: Anthropic ~54% do gasto em coding, ~32-40% da API enterprise |
| Share OpenAI: devs / pros / gerais / machine | 18/25/20/20% | 25/30/25/25% | 32/35/30/28% | 7M assentos enterprise; Codex 2M+ usuários semanais; API ~15-20% da receita |

Pools globais resultantes (todos os vendors, $B): devs 117 / 296 / 507; profissionais 56 / 178 / 386; gerais 22 / 71 / 198; machine API 84 / 200 / 420. Total enterprise 278 / 746 / 1.511. O base de $746B é ~30% do gasto global em software projetado para 2030 (~$2,4T) e ~1,1% da folha salarial global. Bain estima que a indústria de IA como um todo precisa de $2T de receita em 2030 para pagar o capex; nosso pool enterprise é ~37% disso.

### 3.3 Sobre a sua proposta (MAU × salário $100k × 20%)

A lógica de "% do salário" é a certa como teto de disposição a pagar, mas os números precisam de três ajustes:

- **20% do salário é bull para devs, não média.** $20k/funcionário/ano é 7-50x o observado hoje: Copilot $360 (0,3% de $100k), ChatGPT Enterprise ~$600-900 (0,6-0,9%), Claude Code enterprise $1,8-3k (1,2-2% de um dev americano; 2-4% do blend global), heavy users de agentes ~$12k (8%). Nosso base é 13% para devs (agentes paralelos), 3% para profissionais, 1,2% para gerais. Aplicar 20% a todos os MAU superestima por uma ordem de grandeza.
- **Use assentos pagos, não MAU.** MAU inclui free; no enterprise o que importa é assento licenciado mais consumo. E separe assento de tokens: o assento ($240-360/ano) é pequeno; o que escala é consumo de agentes.
- **Salário $100k é EUA.** O blend global é $30-75k por tier. Se o deck for US-only, o pool é ~100M knowledge workers e o salário sobe, mas a penetração global cai. Os dois caminhos chegam a números parecidos; o importante é não misturar salário americano com população global.

Teto lógico para o gasto: gasto ≤ ganho de produtividade × salário × captura do vendor. Exemplo: 30% de produtividade × $100k × 30% de captura = $9k/ano (9%). Esse é o argumento para defender o base de devs.

Cross-check em tokens: $9,75k/ano a $1,6/M tokens realizados = 6,1B tokens/ano = ~24M tokens por dia útil por dev. Um usuário pesado do Claude Code hoje roda 10-50M tokens/dia (com cache). Plausível para devs com agentes em paralelo; implausível para o knowledge worker médio.

---

## 4. Motor consumer (o que decide a OpenAI)

### 4.1 Árvore de drivers

```
MAU 2030 (2,0B base)
├─ pagantes: MAU × conversão (6%) × ARPU ($18/mês) × 12  = subs
├─ free: MAU × (1 − conversão) × ARPU de ads ($30/ano)  = ads
└─ GMV roteado via ChatGPT ($400B) × take rate (2,5%)   = commerce
```

### 4.2 Premissas e âncoras

| Driver | Bear | Base | Bull | Âncora 2026 |
|---|---|---|---|---|
| ChatGPT MAU (M) | 1.500 | 2.000 | 2.500 | 1B MAU (jun-26), ~1B WAU (jul-26); internet ~5,6B → 6B; Meta DAP 3,58B |
| Conversão paga | 4,5% | 6% | 9% | >50M subs consumer / ~1B = ~5%; Go grátis na Índia até dez-26 |
| ARPU pagante ($/mês) | 15 | 18 | 24 | Go $8 (EUA) / ₹399; Plus $20; Pro $200 (~0,5M); blend hoje ~$25-30 caindo com mix EM |
| ARPU de ads por free user ($/ano) | 15 | 30 | 55 | Meta 2025: $58 global, US&C ~$250+; Google Search ~$60-70/usuário; plano OpenAI $100B = ~$50/free user; hoje $1B run-rate em <200 dias |
| GMV via ChatGPT ($B) / take rate | 100 / 2% | 400 / 2,5% | 1.000 / 3% | Instant Checkout (set-25); e-commerce global ~$7T em 2030 |
| Claude MAU (M) / conversão / ARPU | 150 / 8% / $26 | 250 / 10% / $32 | 400 / 13% / $40 | Estimativas de terceiros 30-140M; consumer ~5-10% da receita |

Resultado OpenAI consumer ($B): subs 12 / 26 / 65; ads 22 / 56 / 125; commerce 2 / 10 / 30.

### 4.3 Sobre a sua proposta (1B × 5% × $20; ads a 50% da Meta)

- **1B × 5% × $20 × 12 = $12B é o ChatGPT de hoje, não o de 2030.** 1B MAU é jun-26 e 5% é a conversão atual; o resultado fica abaixo dos ~$17B que estimamos de subs consumer no run-rate atual. Para 2030 o driver é MAU (2B base) e mix de tiers, não conversão. O base de $26B já assume ARPU caindo para $18 com o peso de Go em mercados emergentes.
- **Ads a 50% do ARPU da Meta dá $75B, perto do plano da OpenAI.** Meta 2025 = $58/pessoa global; a ~7%/ano chega a ~$80 em 2030; 50% = $40 × 1,9B free = $75B. Nosso base é $30 ($56B); o plano da OpenAI ($100B) implica ~$50/free user, que é o ARPU do Google Search hoje. A build regional ajuda a defender $30-45: US&C (20% dos usuários, $150), Europa (20%, $45), resto (60%, $8) = $44. ChatGPT tem 31% dos usuários nos EUA vs. ~10% do DAP da Meta, o que sustenta ARPU acima do que o mix global sugere.
- **Base rate contra:** o ChatGPT hoje realiza ~$4/free user/ano nos EUA ($1B run-rate sobre ~250M free/Go). Chegar a $30-50 em quatro anos é 8-12x. A Meta levou seis anos (2012-2018) para ir de ~$5 para ~$25 de ARPU global. A OpenAI parte de CPM mais alto ($60) e intenção de busca, mas o ramp é agressivo.

---

## 5. Reconciliação com GW

### 5.1 Receita = GW × $/GW

| GW \ $/GW | $8B | $10,5B | $14B | $20B | $28B | $35B |
|---|---|---|---|---|---|---|
| 10 GW | 80 | 105 | 140 | 200 | 280 | 350 |
| 15 GW | 120 | 158 | 210 | 300 | 420 | 525 |
| 20 GW | 160 | 210 | 280 | 400 | 560 | 700 |
| 25 GW | 200 | 262 | 350 | 500 | 700 | 875 |
| 30 GW | 240 | 315 | 420 | 600 | 840 | 1.050 |

Duas teses possíveis para $350-400B: (a) 10-11 GW a $35B/GW, "poucos GW muito rentáveis"; (b) 25-28 GW a $14B/GW, "muitos GW com economics de hoje". A tese (b) é consistente com os planos de capacidade anunciados (OpenAI 30 GW em 2030; Anthropic ~10 GW já em 2027) e com o $/GW realizado. A tese (a) contradiz os anúncios de capacidade, a menos que grande parte dos GW seja treino.

### 5.2 O que constrói o $/GW

$/GW de capacidade total = tokens/GW-ano × preço realizado × utilização × share de inferência. Na tabela abaixo, utilização e share de inferência estão no base (68% × 62% = 0,42):

| tokens/GW-ano \ $/M tokens | $0,8 | $1,2 | $1,6 | $2,2 | $3,0 |
|---|---|---|---|---|---|
| 12 quadrilhões | 4,0 | 6,1 | 8,1 | 11,1 | 15,2 |
| 16 | 5,4 | 8,1 | 10,8 | 14,8 | 20,2 |
| 20 | 6,7 | 10,1 | 13,5 | 18,6 | 25,3 |
| 24 | 8,1 | 12,1 | 16,2 | 22,3 | 30,4 |
| 32 | 10,8 | 16,2 | 21,6 | 29,7 | 40,5 |

Âncoras: OpenAI processa ~15B tokens/min na API (mar-26), ~8 quadrilhões/ano, mais o consumo do ChatGPT; Google processa 3,2 quadrilhões/mês (mai-26). Preço realizado hoje: OpenAI ~$2-2,5/M (subs incluídas), Anthropic ~$5/M (API, output pesado de coding). Lista set-26: Opus 5.5 $4/$20, GPT-6 Sol $2/$10, Gemini Flash $0,75/$3,75. Para $35B/GW com o mix base de utilização e inferência, precisa de 32 quadrilhões a $2,6/M ou equivalente.

### 5.3 Margem bruta implícita

Custo de compute alugado: Oracle-OpenAI $300B / 5 anos / 4,5 GW = ~$13,3B por GW-ano. TCO de data center próprio: ~$38B de capex + ~$0,9B/ano de opex por GW (Epoch AI), ~$8-9B por GW-ano anualizado. Só a parte de inferência entra em COGS; treino é P&D.

| Receita/GW \ custo/GW-ano | $6B | $8B | $10B | $13,3B |
|---|---|---|---|---|
| $10,5B | 43% | 24% | 5% | -27% |
| $13,5B | 56% | 41% | 26% | 1% |
| $20B | 70% | 60% | 50% | 34% |
| $28B | 79% | 71% | 64% | 53% |
| $35B | 83% | 77% | 71% | 62% |

Leitura: $13,5B/GW só funciona com compute próprio ou chips customizados (TPU, Trainium) a $6-8B por GW-ano. Com compute alugado a preço Oracle, $13,5B/GW dá margem zero. Anthropic guiou margem bruta de 63% em 2026 e 70% em 2027; isso é consistente com ~$18-20B/GW realizados e custo blended de $6-8B. A tese de $35B/GW é a tese de "margem de software madura" (75-80%).

---

## 6. Cenários por empresa

### 6.1 OpenAI 2030 ($B)

| Segmento | Bear | Base | Bull | RR 2026 (est.) | Múltiplo base | CAGR base |
|---|---|---|---|---|---|---|
| Devs / coding agents | 21 | 74 | 162 | 4 | 18,5x | 96% |
| Assentos profissionais | 14 | 54 | 135 | 8 | 6,7x | 55% |
| Assentos KW gerais | 4 | 18 | 60 | 2 | 8,9x | 66% |
| Machine / agent API | 17 | 50 | 118 | 6 | 8,3x | 63% |
| Subs consumer | 12 | 26 | 65 | 17 | 1,5x | 10% |
| Ads | 22 | 56 | 125 | 1 | 56x | 154% |
| Commerce | 2 | 10 | 30 | 0,5 | 20x | 100% |
| Outros | 4 | 10 | 20 | 1,5 | 6,7x | 55% |
| **Total** | **96** | **298** | **714** | **40** | **7,4x** | **59%** |

Base: enterprise 66% da receita, consumer 31%. A empresa fala em 50/50. A diferença é a nossa premissa de subs consumer (crescem só 1,5x) e de ads ($56B vs. $100B do plano).

Supply check: 22 GW × $13,5B = $297B, fecha com o bottom-up. Momentum: $50B saída-26 × 1,75 × 1,60 × 1,45 × 1,35 = $274B.

O que $350B implica (estrutura base): $15,9B/GW em 22 GW, ou 26 GW a $13,5B; uplift de 1,27x nos motores enterprise; se só o gasto por dev mover, 22% do salário ($16,6k/dev); se só a automação machine mover, 20% do pool automatizável. $400B: $18,2B/GW ou 30 GW; uplift 1,52x; 31% do salário de devs ou 30% do pool.

### 6.2 Anthropic 2030 ($B)

| Segmento | Bear | Base | Bull | RR 2026 (est.) | Múltiplo base | CAGR base |
|---|---|---|---|---|---|---|
| Devs / coding agents | 41 | 124 | 243 | 25 | 5,0x | 45% |
| Assentos profissionais | 7 | 36 | 93 | 10 | 3,6x | 34% |
| Assentos KW gerais | 1 | 6 | 24 | 1 | 5,7x | 49% |
| Machine / agent API | 25 | 76 | 168 | 20 | 3,8x | 36% |
| Subs consumer | 4 | 10 | 25 | 6 | 1,6x | 11% |
| Ads | 0 | 0 | 0 | 0 | n/a | n/a |
| Outros | 4 | 8 | 15 | 3 | 2,7x | 25% |
| **Total** | **82** | **259** | **568** | **65** | **4,0x** | **38%** |

Base: coding é 48% da receita, machine API 29%, assentos 16%, consumer 4%. O mix de 2026 é estimativa nossa a partir do run-rate divulgado ($65B) e do Claude Code ($8B em maio, mais o Claude dentro de Cursor e Copilot).

Supply check: 16 GW × $13,5B = $216B, abaixo do bottom-up ($259B). Fecha com 19 GW ou com $16,2B/GW. Momentum: $90B saída-26 × 1,70 × 1,45 × 1,30 × 1,20 = $346B, ou seja, o run-rate atual já "embute" o número do deck se a desaceleração for gradual.

O que $350B implica: $21,9B/GW em 16 GW, ou 26 GW a $13,5B; uplift de 1,37x nos motores enterprise; se só o gasto por dev mover, 22% do salário ($16,8k/dev); se só a automação mover, 22% do pool. $400B: $25B/GW ou 30 GW; uplift 1,58x; 28% do salário de devs ou 28% do pool. Só penetração de profissionais não resolve (precisaria de >100%).

---

## 7. Bull e bear

### Anthropic

Bull ($550B+):
- Devs: 44M × 90% × $12,8k × 48% share = $243B. Agentes rodando em paralelo viram a norma; Claude mantém a liderança em coding.
- Machine API: pool de $420B (14% de $10T automatizado, 30% de captura), 40% de share = $168B. Suporte, back-office, legal e financeiro automatizados via Bedrock/Vertex/Foundry.
- Compute: 22 GW a $26B/GW, com TPU/Trainium baratos e utilização de 78%.

Bear ($80-100B, run-rate estagna):
- Open-source e modelos chineses comoditizam coding; preço realizado cai para $1,2/M mais rápido do que o volume cresce.
- Share em devs cai para 35% (OpenAI, Google e Cursor com modelos próprios); gasto por dev fica em $5k.
- Compute: 10 GW a $6B/GW; margem bruta não passa de 40%; o IPO precifica $190-200B em 2028 e o número não vem.

### OpenAI

Bull ($700B):
- 2,5B MAU com 9% pagantes a $24 ($65B) e ads a $55/free user ($125B), Google Search-like.
- Enterprise: 32% do pool de devs e 35% dos assentos profissionais via ChatGPT Enterprise e Frontier; $300B+.
- 30 GW a $47B/GW.

Bear ($100B):
- Consumer satura em 1,5B MAU; conversão 4,5%; ads em $15/free user (regulação, resistência do usuário, CPM cai com inventário).
- Enterprise perde para Microsoft/Anthropic em assentos e coding; API 20% de share.
- 15 GW a $6B/GW; compute contratado ($750B até 2030) vira passivo.

---

## 8. Como montar no deck (5 slides)

1. **A identidade.** Demanda = oferta ≈ momentum, com os três números lado a lado (OpenAI 298 / 297 / 274; Anthropic 259 / 216 / 346). Mensagem: "o número que defendemos tem que fechar nas três lentes".
2. **Motor enterprise.** Waterfall de 1,05B knowledge workers → tiers → penetração → gasto → share, com a tabela de âncoras 2026 (Copilot $360, Claude Code $1,8-3k, Atlanta Fed $2.068). Mensagem: "o que decide a Anthropic é gasto por dev em agentes".
3. **Motor consumer.** MAU → pagantes / free / commerce, com a comparação de ARPU (Meta $58, Google Search $60-70, ChatGPT hoje ~$4). Mensagem: "o plano de ads da OpenAI ($100B) é Google-like; nosso base é metade".
4. **Ponte de $/GW.** Tabela da seção 2 (de $10B hoje a $13,5B base e $35B bull) com as quatro alavancas e a tabela de margem bruta. Mensagem: "$35B/GW é a tese de margem de software; $14B/GW é a tese de capacidade".
5. **Cenários e o que precisa ser verdade.** Bear/base/bull por empresa e a tabela "para $350-400B precisa de X". Mensagem: "o número do deck é o topo do range; aqui está o que tem que acontecer".

---

## 9. Riscos do framework

- **Compounding de premissas.** Bear e bull são todos-mínimos e todos-máximos; o intervalo real é mais estreito. Use o bear como "run-rate estagna" e o bull como "planos das empresas batem com folga".
- **Dupla contagem entre pools.** Claude dentro do Cursor está no pool de devs; Claude via Bedrock em um bot de suporte está no machine API. A fronteira é por caso de uso, não por canal. Ao atualizar o mix de 2026, manter essa regra.
- **Share da camada de modelo.** Quando o Copilot usa Claude, quanto do $30/assento chega à Anthropic é desconhecido. Assumimos que o share já é líquido disso.
- **Preço por token.** É a premissa mais frágil: cai 5-10x por ano por unidade de capacidade, mas o mix migra para modelos maiores e reasoning. O $1,6/M realizado no base é uma queda de ~35%/ano vs. os $2,5-5/M de hoje, compensada por mix.
- **Dados de 2026 de terceiros.** MAU do Claude, mix de receita e share de mercado vêm de estimativas; só run-rates, GW contratados, preços de lista e os planos vazados vêm de fontes primárias ou de imprensa financeira.

---

## 10. Fontes principais

- OpenAI: run-rate >$40B e enterprise >50% (imprensa, ago-26); plano 2030 >$280B (Bloomberg, 20-fev-26); plano de ads $2,5B → $100B (Axios, 9-abr-26); 15B tokens/min e Codex 2M+ (OpenAI, mar-26); 0,2 GW → 1,9 GW vs. $2B → $20B (MBI Deep Dives citando OpenAI); 30 GW em 2030 e compute $600-750B (WSJ/DCD); Nvidia 10 GW, AMD 6 GW, Broadcom 10 GW, Stargate (OpenAI); Oracle $300B / 4,5 GW (The Register).
- Anthropic: run-rate $65B (Bloomberg/Axios/TechCrunch, 17-ago-26); $30B e 1.000+ clientes >$1M (Anthropic, abr-26); $190-200B em 2028 (Reuters, 14-ago-26); ~5 GW fim-26 e ~10 GW 2027, 3,5 GW TPU, AWS até 5 GW (imprensa); margem bruta 40% → 63% → 70% (The Information via imprensa); Claude Code $8B ARR (imprensa, mai-26); custo por dev (docs Claude Code).
- Benchmarks: Meta FY25 $200,1B, DAP 3,58B, ARPP Q4 $16,56 (Meta IR); Google Search ads 2025 $175,8B (Alphabet); 3,2 quadrilhões de tokens/mês (Google I/O 2026); M365 Copilot 20M assentos, GitHub Copilot 4,7M (Microsoft via imprensa); Cursor $2B+ ARR; Atlanta Fed $2.068/funcionário (mai-26); Gartner IT $6,37T, software $1,47T, IA $2,59T (jul-26); Bain $2T e 200 GW (set-25); Epoch AI TCO de 1 GW; preços de lista (benchlm, set-26); superforecasters $300B combinado (Forecasting Research Institute).

URLs completas na aba Sources do modelo.
