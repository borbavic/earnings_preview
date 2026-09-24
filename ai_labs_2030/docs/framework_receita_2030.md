# Framework bottom-up: receita 2030 de OpenAI e Anthropic

Data: 24-set-2026. **Base = modelos MBI vBTG v3** (`OpenAI_breakeven_model_MBI_vBTG_v3.xlsx` e `Anthropic_model_MBI_vBTG_v3.xlsx`, pasta `trabalho/equityresearch/raw/empresas/ai labs`; os arquivos não estão no repo, só os valores extraídos em `model/v3_reference.json`). Dados de mercado até ago-2026, parte via imprensa financeira; revalidar os itens marcados "secundário" na aba Sources antes de usar no deck.

Arquivos: modelo em `model/AI_labs_revenue_2030_bottomup.xlsx` (fórmulas vivas, coluna Custom editável, reconciliação com o v3 na aba Summary) e a mesma lógica em `model/revenue_2030_model.py`.

---

## 1. Conclusão

**O base 2030 é o v3: OpenAI $338,1B (breakeven de EBIT GAAP) e Anthropic $425,6B (capacidade declarada × yield), $763,7B combinados.** O bottom-up reproduz esses totais exatamente e mostra o que eles exigem em usuários, gasto e share. Bear e bull são sensibilizações em torno do base, para crítica posterior.

| 2030, $B | Bear | Base (= v3) | Bull | Momentum (calendar, base) | Plano da empresa |
|---|---|---|---|---|---|
| OpenAI | 150 | 338 | 484 | 338 | >280 (fev-26), relatos de ~350 |
| Anthropic | 200 | 426 | 584 | 426 | 190-200 em 2028 (caso de IPO) |
| Combinado | 350 | 764 | 1.068 | 764 | ~500-550 |

Bear = o run-rate desacelera de ~60%/ano em 2027 para ~10% em 2030, sem cair (OpenAI $58B → $159B de run-rate de saída; Anthropic $100B → $211B); yield por GW de inferência cai para $20-24B e a frota fica em 15-16 GW médios. Bull = trajetória de capacidade declarada sem haircut (27,5 e 25 GW médios), yield flat em 2026E para a Anthropic ($40B) e $30B para a OpenAI, ~1,4x o base. Nenhum dos dois é catastrófico nem "moonshot"; os três lentes fecham com ±3% em cada cenário.

Referências externas: mediana de superforecasters para OpenAI+Anthropic combinados em 2030 é $300B (34% de chance de >$400B). O base combinado ($764B) é 2,5x essa mediana e ~40% acima dos planos das empresas. Bain estima que a indústria inteira precisa de $2T de receita em 2030 para pagar o capex; as duas empresas seriam 38% disso.

**O que o base v3 exige, na linguagem do bottom-up:**

1. **Um pool global de gasto enterprise em IA de ~$1,15T em 2030** (todos os vendors): devs $450B, profissionais $297B, knowledge workers gerais $100B, workloads de máquina/agentes via API $300B. É 48% do gasto global em software projetado para 2030 (~$2,4T) e 1,8% da folha salarial global (~$65T). As duas empresas ficam com 53% desse pool.
2. **Gasto por desenvolvedor de $12,6k/ano** (16,8% de um salário médio global de $75k) em 85% de 42M devs, contra $1,8-3k hoje no Claude Code enterprise. Anthropic com 46% desse pool ($205B) e OpenAI com 17% ($78B).
3. **Anthropic com 44% do pool de machine/agent API** ($131B de $300B). Esse share é a variável resolvida para fechar o total; o 2026 anchor é 32-40% (Menlo).
4. **OpenAI com $75B de ads** ($40 por usuário free, ~50% do ARPU da Meta em 2030) mais $32B de subs (2B MAU × 6,5% × $20,5) e $12B de commerce. Consumer = 35% da receita; a empresa fala em ~50/50.
5. **Yield por GW de inferência ~flat vs. 2026:** OpenAI $30,9B em 2030 vs. $27,1B em 2026E; Anthropic $35,0B vs. $40,2B (-6%/ano). O v3 assume que tokens por GW sobem na mesma velocidade em que o preço por token cai. Com 20 quadrilhões de tokens/GW e 68% de utilização, o preço realizado implícito é $2,3/M (OpenAI) e $2,6/M (Anthropic), contra ~$2-2,5/M e ~$5/M hoje.
6. **Compute:** OpenAI 20,2 GW médios em 2030 (22,1 GW no fim do ano, após haircut de 26,4% sobre os 30 GW declarados para caber nos $750B de compute); Anthropic 22,5 GW médios (25 GW no fim do ano, sem haircut). 54,1% da capacidade média em inferência nas duas (55% no fim do ano).

**Consenso vs. diferenciado.** Consenso (planos das empresas): OpenAI ~$300B em 2030 com ads $100B; Anthropic ~$200B em 2028 e ~80% API/enterprise. O base v3 está acima do consenso nas duas, sobretudo na Anthropic. O que é nosso: a restrição é GW × yield por GW de inferência, não penetração, e o motor de demanda que decide a Anthropic é gasto por dev em agentes (48% da receita base) mais automação via API (31%).

---

## 2. Como o base está amarrado ao v3

O v3 é um modelo de capacidade × yield: receita = GW médios de inferência × receita por GW de inferência. O bottom-up é um modelo de demanda: usuários × penetração × gasto × share. Os dois têm que dar o mesmo número, e o momentum (run-rate) também.

| Linha (2030) | v3 OpenAI | Modelo base | v3 Anthropic | Modelo base |
|---|---|---|---|---|
| Receita calendário ($B) | 338,10 | 338,10 | 425,62 | 425,62 |
| Run-rate de saída ($B) | 372,54 | 372,54 | 471,93 | 471,93 |
| GW médios no ano | 20,24 | 20,24 | 22,50 | 22,50 |
| Share de inferência (média) | 54,1% | 54,1% | 54,1% | 54,1% |
| GW médios de inferência | 10,95 | 10,95 | 12,18 | 12,18 |
| Receita por GW de inferência ($B) | 30,89 | 30,89 | 34,96 | 34,96 |
| Receita por GW total ($B) | 16,71 | 16,71 | 18,92 | 18,92 |
| Custo de inferência por GW-ano ($B) | 11,70 | 11,70 | 12,00 | 12,00 |
| Margem bruta | 59,1% | 59,1% | 62,7% | 62,7% |
| EBIT ($B) | 0,0 | – | 48,0 | – |

Como fecha: (i) os inputs de supply (GW médios, share de inferência, yield, custo por GW, outros CoR de 3%) são os do v3; (ii) o momentum usa o run-rate de saída de 2026 do v3 ($60B / $100B) e os crescimentos que reproduzem a trajetória do v3, com receita calendário = média dos run-rates de abertura e fechamento, como no v3; (iii) no bottom-up, o share de machine/agent API de cada empresa é uma fórmula na aba Inputs: (receita v3 − demais segmentos) ÷ pool de machine API. Todos os outros segmentos são escolhas explícitas. A aba Summary tem 20 linhas de reconciliação que precisam ficar em zero.

O que é do v3 e o que é nosso: totais, GW, share de inferência, yield, custo e margem são v3. A abertura por segmento, os pools globais, as penetrações e os gastos por assento são nossos e servem para testar a plausibilidade do total.

---

## 3. A identidade que a apresentação precisa fechar

```
DEMANDA (bottom-up)                    OFERTA (compute, v3)                      MOMENTUM
Σ usuários pagantes × gasto × share  =  GW médios × %inferência × yield/GW-inf  ≈  run-rate 2026 × Π(1+g)
```

| Lente | O que responde | Onde erra |
|---|---|---|
| Demanda | Quem paga, quanto e por quê | Multiplica muitas premissas; bear/bull explodem |
| Oferta | Quanto a frota consegue faturar | Yield depende de preço por token, que cai 5-10x/ano por unidade de capacidade |
| Momentum | O que o run-rate atual já embute | Extrapola desaceleração sem dizer de onde vem a receita |
| Base rates | Se o número é plausível vs. folha salarial, software, ads | Só dá ordem de grandeza |

A ponte de yield por GW de inferência é o slide central:

| | Yield ($B por GW de inferência) | Share de inferência | $/GW total | Como se chega |
|---|---|---|---|---|
| OpenAI 2025 | ~$24 | 46% (fim de ano) | ~$10,5 | 1,9 GW, $13,1B calendário / $20B run-rate |
| OpenAI 2026E (v3) | $27,1 | 45% | $12,3 | 4,05 GW no fim do ano, $36,5B |
| OpenAI 2030 base (v3) | $30,9 | 54,1% | $16,7 | 20,2 GW médios → $338B; breakeven |
| Anthropic 2025 | ~$12 | 42% | ~$4,7 | 1,4 GW, $4,5B |
| Anthropic 2026E (v3) | $40,2 | 45% | $17,8 | 5 GW no fim do ano, $57B |
| Anthropic 2030 base (v3) | $35,0 | 54,1% | $18,9 | 22,5 GW médios → $426B |
| Deck | $30 | 50-55% | $15-16,5 | 25 GW → $375-410B |
| Bear / bull (nosso) | $20-24 / $30-40 | 50-52% / 58% | $10-12,5 / $17,4-23,2 | 15-16 GW / 25-27,5 GW médios |

Leitura: o preço realizado por token cai, mas tokens por GW sobem com Rubin e o mix migra para modelos maiores e agentes. O v3 assume que os efeitos quase se cancelam (OpenAI +3% acumulado no yield 2026→2030; Anthropic -13%). O deck ($30B) fica 3% abaixo do yield da OpenAI e 14% abaixo do da Anthropic no v3.

---

## 4. Motor enterprise (o que decide a Anthropic)

### 4.1 Árvore de drivers

```
Knowledge workers globais (~1,05B)
├─ Devs / engenheiros de dados e IA (42M) ─┐
├─ Profissionais de alta intensidade (220M) ├─ × penetração paga × (salário × % gasto em IA) = pool global por tier
└─ Knowledge workers gerais (790M) ─────────┘                                                  × share da empresa
Pool de trabalho automatizável ($8T de folha) × % automatizado por agentes × captura do vendor = pool "machine API"
                                                                                                × share da empresa
```

Quatro motores, cada um com pool global (todos os vendors) e share da empresa. O share captura receita direta (Claude Code, ChatGPT Enterprise) e a camada de modelo dentro de ferramentas de terceiros (Cursor, Copilot, Bedrock, Vertex, Foundry).

### 4.2 Premissas e âncoras 2026

| Driver | Bear | Base | Bull | Âncora 2026 |
|---|---|---|---|---|
| Devs (M) / penetração paga | 38 / 78% | 42 / 85% | 44 / 90% | ~30M devs; ~10-12M assentos pagos (Copilot 4,7M, Cursor, Claude Code, Codex) = 35-40% |
| Gasto por dev pago ($/ano) | 7.920 | 12.600 | 14.820 | Claude Code enterprise $150-250/mês = $1,8-3k; heavy users >$1k/mês |
| Profissionais (M) / penetração | 210 / 42% | 220 / 50% | 230 / 55% | ~35-40M assentos pagos no mundo (M365 Copilot 20M, ChatGPT biz 9M) = ~4% dos KW, ~10% dos profissionais |
| Gasto por profissional pago ($/ano) | 1.482 | 2.700 | 3.276 | Copilot $360; ChatGPT Enterprise ~$600-900 com uso; Atlanta Fed: $2.068/funcionário em IA (tudo incluso) |
| KW gerais (M) / penetração | 775 / 20% | 790 / 30% | 800 / 36% | Produtos de assento a $20-30/mês; bundling do Copilot |
| Gasto por KW geral ($/ano) | 261 | 420 | 527 | Copilot $360 |
| Pool automatizável ($T) × % automatizado × captura | 7 × 9% × 24% | 8 × 12,5% × 30% | 9 × 14% × 32% | Folha global ~$58T; knowledge work $35-50T; só suporte e coding têm agentes em escala |
| Share Anthropic: devs / pros / gerais / machine | 42/16/6/40% | 45,6/18,5/8,0/43,7% | 46/21/10/43% | Menlo: Anthropic ~54% do gasto em coding, ~32-40% da API enterprise; machine base é resolvido |
| Share OpenAI: devs / pros / gerais / machine | 15/22/16/14% | 17,3/22,9/18,1/15,8% | 19/25/20/18% | 7M assentos enterprise; Codex 2M+ usuários semanais; API ~15-20% da receita; machine base é resolvido |

Pools globais resultantes ($B): devs 235 / 450 / 587; profissionais 131 / 297 / 414; gerais 40 / 100 / 152; machine API 151 / 300 / 403. Total enterprise 557 / 1.146 / 1.556.

### 4.3 Sobre a proposta original (MAU × salário $100k × 20%)

A lógica de "% do salário" é a certa como teto de disposição a pagar, e o base v3 já exige 16,8% para devs. Três ajustes:

- **20% do salário é a premissa de devs com agentes, não a média.** Hoje: Copilot $360 (0,3% de $100k), ChatGPT Enterprise ~$600-900 (0,6-0,9%), Claude Code enterprise $1,8-3k (1,2-2% de um dev americano; 2-4% do blend global), heavy users ~$12k (8%). O base usa 16,8% para devs, 4,5% para profissionais e 1,4% para gerais. Aplicar 20% a todos os MAU superestima por uma ordem de grandeza.
- **Use assentos pagos, não MAU.** MAU inclui free; no enterprise o que importa é assento licenciado mais consumo. O assento ($240-360/ano) é pequeno; o que escala é consumo de agentes.
- **Salário $100k é EUA.** O blend global é $30-75k por tier. Se o deck for US-only, o pool é ~100M knowledge workers e o salário sobe, mas a penetração global cai.

Teto lógico: gasto ≤ ganho de produtividade × salário × captura do vendor. Para $12,6k em $75k (16,8%): 40% de produtividade × 42% de captura, ou 50% × 34%. É o argumento que precisa estar no slide de devs.

Cross-check em tokens: $12,6k/ano a $2,3-2,6/M realizados = 4,8-5,5B tokens/ano = ~20M tokens por dia útil por dev. Um usuário pesado do Claude Code hoje roda 10-50M tokens/dia (com cache). Plausível para devs com agentes em paralelo; implausível para o knowledge worker médio.

---

## 5. Motor consumer (o que decide a OpenAI)

### 5.1 Árvore de drivers

```
MAU 2030 (2,0B base)
├─ pagantes: MAU × conversão (6,5%) × ARPU ($20,5/mês) × 12  = subs $32B
├─ free: MAU × (1 − conversão) × ARPU de ads ($40/ano)       = ads $75B
└─ GMV roteado via ChatGPT ($480B) × take rate (2,5%)        = commerce $12B
```

### 5.2 Premissas e âncoras

| Driver | Bear | Base | Bull | Âncora 2026 |
|---|---|---|---|---|
| ChatGPT MAU (M) | 1.600 | 2.000 | 2.300 | 1B MAU (jun-26), ~1B WAU (jul-26); internet ~5,6B → 6B; Meta DAP 3,58B |
| Conversão paga | 5,2% | 6,5% | 7,5% | >50M subs consumer / ~1B = ~5%; Go grátis na Índia até dez-26 |
| ARPU pagante ($/mês) | 16 | 20,5 | 22 | Go $8 (EUA) / ₹399; Plus $20; Pro $200 (~0,5M); blend hoje ~$25-30 caindo com mix EM |
| ARPU de ads por free user ($/ano) | 22 | 40 | 42 | Meta 2025: $58 global, US&C ~$250+; Google Search ~$60-70/usuário; plano OpenAI $100B = ~$50/free user; hoje $1B run-rate em <200 dias |
| GMV via ChatGPT ($B) / take rate | 150 / 2% | 480 / 2,5% | 700 / 2,7% | Instant Checkout (set-25); e-commerce global ~$7T em 2030 |
| Claude MAU (M) / conversão / ARPU | 200 / 10% / $30 | 250 / 12% / $40 | 350 / 13% / $42 | Estimativas de terceiros 30-140M; consumer ~5-10% da receita |

Resultado OpenAI consumer ($B): subs 16 / 32 / 46; ads 33 / 75 / 89; commerce 3 / 12 / 19. Consumer = 35% da receita base; a empresa projeta ~50/50, o que exigiria ads no plano dela ($100B) e subs ~$50B.

### 5.3 Sobre a proposta original (1B × 5% × $20; ads a 50% da Meta)

- **1B × 5% × $20 × 12 = $12B é o ChatGPT de hoje.** 1B MAU é jun-26 e 5% é a conversão atual; fica abaixo dos ~$15-17B de subs consumer no run-rate atual. Para 2030 o driver é MAU (2B) e mix de tiers; o base de $32B assume ARPU em $20,5 com o peso de Go em mercados emergentes.
- **Ads a 50% do ARPU da Meta é exatamente o base.** Meta 2025 = $58/pessoa global; a ~7%/ano chega a ~$80 em 2030; 50% = $40 × 1,87B free = $75B. A build regional dá o mesmo: US&C (20% dos usuários, $150), Europa (20%, $45), resto (60%, $8) = $44. ChatGPT tem 31% dos usuários nos EUA vs. ~10% do DAP da Meta.
- **Base rate contra:** o ChatGPT realiza ~$4/free user/ano nos EUA hoje ($1B run-rate sobre ~250M free/Go). $40 em quatro anos é 10x. A Meta levou seis anos (2012-2018) para ir de ~$5 para ~$25 de ARPU global; a OpenAI parte de CPM mais alto ($60) e intenção de busca.

---

## 6. Reconciliação com GW

### 6.1 Receita = GW médios × share de inferência × yield por GW de inferência

Com 54,1% da capacidade média em inferência (v3), $B:

| GW médios \ yield | $20B | $24B | $30B | $31B | $35B | $40B |
|---|---|---|---|---|---|---|
| 15 GW | 162 | 195 | 243 | 252 | 284 | 325 |
| 20 GW | 216 | 260 | 325 | 335 | 379 | 433 |
| 22,5 GW | 243 | 292 | 365 | 377 | 426 | 487 |
| 25 GW | 271 | 325 | 406 | 419 | 473 | 541 |
| 30 GW | 325 | 390 | 487 | 503 | 568 | 649 |

Com 22,5 GW médios ($B):

| Share de inferência \ yield | $20B | $24B | $30B | $31B | $35B | $40B |
|---|---|---|---|---|---|---|
| 45% | 203 | 243 | 304 | 314 | 354 | 405 |
| 50% | 225 | 270 | 338 | 349 | 394 | 450 |
| 54% | 243 | 292 | 364 | 377 | 425 | 486 |
| 60% | 270 | 324 | 405 | 418 | 472 | 540 |
| 65% | 293 | 351 | 439 | 453 | 512 | 585 |

Leitura: OpenAI base é a célula 20 GW × $31B ($338B); Anthropic base é 22,5 GW × $35B ($426B). Bear: OpenAI 15 GW × 50% × $20B = $150B, Anthropic 16 GW × 52% × $24B = $200B. Bull: 27,5 GW × 58% × $30B = $478B e 25 GW × 58% × $40B = $580B. O deck (25 GW × 52,5% × $30B = $394B) fica entre os dois v3: 1,17x o da OpenAI e 0,93x o da Anthropic. Se o deck quiser um número só para as duas, $394B é uma média razoável; se quiser o v3, são $338B e $426B.

### 6.2 O que constrói o yield

Yield por GW de inferência = tokens por GW-ano × preço realizado por token × utilização. Com 68% de utilização, $B por GW de inferência:

| tokens/GW-ano \ $/M tokens | $1,2 | $1,6 | $2,0 | $2,3 | $2,6 | $3,0 |
|---|---|---|---|---|---|---|
| 12 quadrilhões | 9,8 | 13,1 | 16,3 | 18,8 | 21,2 | 24,5 |
| 16 | 13,1 | 17,4 | 21,8 | 25,0 | 28,3 | 32,6 |
| 20 | 16,3 | 21,8 | 27,2 | 31,3 | 35,4 | 40,8 |
| 24 | 19,6 | 26,1 | 32,6 | 37,5 | 42,4 | 49,0 |
| 28 | 22,8 | 30,5 | 38,1 | 43,8 | 49,5 | 57,1 |
| 32 | 26,1 | 34,8 | 43,5 | 50,0 | 56,6 | 65,3 |

Âncoras: OpenAI processa ~15B tokens/min na API (mar-26), ~8 quadrilhões/ano, mais o consumo do ChatGPT; Google processa 3,2 quadrilhões/mês (mai-26). Preço realizado hoje: OpenAI ~$2-2,5/M (subs incluídas), Anthropic ~$5/M (API, output pesado de coding). Lista set-26: Opus 5.5 $4/$20, GPT-6 Sol $2/$10, Gemini Flash $0,75/$3,75. O yield da OpenAI no v3 ($30,9B) sai de 20 quadrilhões a $2,3/M; o da Anthropic ($35,0B), de 20 quadrilhões a $2,6/M ou de 28 a $1,85/M. O risco central é o preço realizado cair mais rápido do que tokens por GW sobem.

### 6.3 Margem bruta implícita

Custo de inferência por GW-ano no v3: OpenAI $11,7B (blend de Azure $12B, Oracle $13,3B, AWS $8-10B, chips próprios ~$10,5B); Anthropic $12B (fixado a partir de 2027; stack contratado ~$10B). O custo se aplica ao GW de inferência (COGS); o GW de treino é P&D.

| Yield por GW de inferência \ custo por GW-ano | $8B | $10B | $11,7B | $12B | $13,3B |
|---|---|---|---|---|---|
| $20B (bear OpenAI) | 60% | 50% | 42% | 40% | 34% |
| $24B (bear Anthropic) | 67% | 58% | 51% | 50% | 45% |
| $30,9B (OpenAI v3) | 74% | 68% | 62% | 61% | 57% |
| $35B (Anthropic v3) | 77% | 71% | 67% | 66% | 62% |
| $40B (bull Anthropic) | 80% | 75% | 71% | 70% | 67% |

Com os 3% de outros CoR, a margem bruta do v3 é 59,1% (OpenAI) e 62,7% (Anthropic), coerente com o guidance da Anthropic (63% em 2026, 70% em 2027). No bear ($20-24B de yield a $12,5B de custo e 4% de outros CoR), a margem bruta cai para 34-44% e o breakeven de EBIT da OpenAI não acontece em 2030. No bull (custo $10,5B), 63% e 71%.

---

## 7. Cenários por empresa

### 7.1 OpenAI 2030 ($B)

| Segmento | Bear | Base (v3) | Bull | 2026E | Múltiplo base | CAGR base |
|---|---|---|---|---|---|---|
| Devs / coding agents | 35 | 78 | 112 | 3,5 | 22,3x | 117% |
| Assentos profissionais | 29 | 68 | 104 | 7,5 | 9,1x | 74% |
| Assentos KW gerais | 6 | 18 | 30 | 1,8 | 10,0x | 78% |
| Machine / agent API | 21 | 47 | 73 | 5,5 | 8,6x | 71% |
| Subs consumer | 16 | 32 | 46 | 15,5 | 2,1x | 20% |
| Ads | 33 | 75 | 89 | 1,0 | 74,8x | 194% |
| Commerce | 3 | 12 | 19 | 0,4 | 30,0x | 134% |
| Outros | 6 | 8 | 12 | 1,3 | 6,2x | 58% |
| **Total** | **150** | **338** | **484** | **36,5** | **9,3x** | **74%** |

2026E = receita calendário do v3 ($36,5B); a abertura é nossa. Base: enterprise 62,5%, consumer 35%, outros 2,4%.

Supply e momentum base são idênticos ao v3 ($338,1B). Bear: 15 GW × 50% × $20B = $150B de capacidade e momentum de $152B (run-rate $58B → $159B); bull: 27,5 GW × 58% × $30B = $478B e momentum de $472B (run-rate $65B → $537B). Margem bruta 34% / 59% / 63%.

O que $280B (plano da empresa) implica: 0,83x o v3; yield de $25,6B em 20,2 GW, ou 16,8 GW no yield do v3. O que $394B (deck) implica: 1,17x; yield de $36,0B, ou 23,6 GW; uplift de 1,26x nos motores enterprise, o que sozinho em devs seria 29% do salário ($21,6k/dev) ou, só em automação, 27% do pool automatizável.

### 7.2 Anthropic 2030 ($B)

| Segmento | Bear | Base (v3) | Bull | 2026E | Múltiplo base | CAGR base |
|---|---|---|---|---|---|---|
| Devs / coding agents | 99 | 205 | 270 | 22,0 | 9,3x | 75% |
| Assentos profissionais | 21 | 55 | 87 | 8,5 | 6,5x | 59% |
| Assentos KW gerais | 2 | 8 | 15 | 0,8 | 10,0x | 78% |
| Machine / agent API | 61 | 131 | 173 | 17,5 | 7,5x | 65% |
| Subs consumer | 7 | 14 | 23 | 5,5 | 2,6x | 27% |
| Outros | 10 | 12 | 16 | 2,7 | 4,4x | 45% |
| **Total** | **200** | **426** | **584** | **57,0** | **7,5x** | **65%** |

Base: coding 48% da receita, machine API 31%, assentos 15%, consumer 3%, outros 3%. O machine API é a linha resolvida ($131B = 43,7% do pool).

Supply e momentum base idênticos ao v3 ($425,6B; run-rate de saída $471,9B). Bear: 16 GW × 52% × $24B = $200B de capacidade e momentum de $203B (run-rate $100B → $211B); bull: 25 GW × 58% × $40B = $580B e momentum de $568B (run-rate $110B → $637B). Margem bruta 44% / 63% / 71%.

O que $394B (deck) implica: 0,93x o v3; yield de $32,4B em 22,5 GW, ou 20,8 GW no yield do v3. O que $280B implica: 0,66x; yield de $23,0B, ou 14,8 GW.

---

## 8. Bull e bear

Critério: bear = o run-rate desacelera forte mas não cai (a Anthropic sai de 2026 com ~$100B e a OpenAI chega a ~$100B em 2027 mesmo no bear); bull = os planos de capacidade batem sem haircut e o yield não cai, ~1,4x o base. Os três lentes fecham com ±3% em cada cenário.

### Anthropic

Bull ($584B, run-rate de saída ~$637B):
- Devs: 44M × 90% × $14,8k × 46% share = $270B. Agentes em paralelo viram a norma; Claude mantém a liderança em coding.
- Machine API: pool de $403B (14% de $9T automatizado, 32% de captura), 43% de share = $173B.
- Compute: 25 GW médios × 58% inferência × $40B de yield (flat em 2026E) = $580B; margem bruta 71%.

Bear ($200B, run-rate de saída ~$211B, crescendo 8% em 2030):
- Yield cai 12%/ano para $24B por GW de inferência (open-source e modelos chineses comoditizam coding); custo de $12,5B → margem bruta 44%.
- Share em devs 42%, gasto por dev $7,9k, penetração de profissionais 42%; machine API 40% de um pool de $151B.
- Compute: 16 GW médios; o caso de IPO ($190-200B em 2028) só chega em 2030.

### OpenAI

Bull ($484B, run-rate de saída ~$537B):
- 2,3B MAU com 7,5% pagantes a $22 ($46B) e ads a $42/free user ($89B); commerce $19B.
- Enterprise: 19% do pool de devs, 25% dos assentos profissionais, 18% do machine API; $318B.
- 27,5 GW médios (path de 30 GW sem haircut) × 58% × $30B (deck) = $478B; margem bruta 63%.

Bear ($150B, run-rate de saída ~$159B, crescendo 10% em 2030):
- Consumer: 1,6B MAU, conversão 5,2%, ads em $22/free user ($33B).
- Enterprise perde para Microsoft/Anthropic em assentos e coding: 15% do pool de devs, 14% do machine API; $92B.
- 15 GW médios × 50% × $20B = $150B; margem bruta 34%; o breakeven de EBIT de 2030 não vem e o compute contratado ($750B) pesa.

---

## 9. Como montar no deck (5 slides)

1. **A identidade.** Demanda = oferta = momentum, com os três números lado a lado (OpenAI 338 / 338 / 338; Anthropic 426 / 426 / 426, todos v3). Mensagem: "o base é o v3; o bottom-up mostra o que ele exige".
2. **Motor enterprise.** Waterfall de 1,05B knowledge workers → tiers → penetração → gasto → share, com a tabela de âncoras 2026 (Copilot $360, Claude Code $1,8-3k, Atlanta Fed $2.068). Mensagem: "o v3 exige $12,6k por dev e 46% do pool de devs para a Anthropic".
3. **Motor consumer.** MAU → pagantes / free / commerce, com a comparação de ARPU (Meta $58, Google Search $60-70, ChatGPT hoje ~$4). Mensagem: "ads a 50% da Meta dá $75B; o plano da OpenAI é $100B".
4. **Ponte de yield.** Tabela da seção 3 (OpenAI $27,1B → $30,9B; Anthropic $40,2B → $35,0B) com as três alavancas (tokens/GW, preço realizado, utilização), o share de inferência e a tabela de margem bruta. Mensagem: "o v3 assume yield ~flat; o risco é preço por token cair mais rápido do que tokens por GW sobem".
5. **Cenários.** Bear/base/bull por empresa, o deck check ($394B entre os dois v3) e "o que precisa ser verdade". Mensagem: "o base combinado é $764B, 2,5x a mediana dos superforecasters".

---

## 10. Riscos do framework

- **Compounding de premissas.** Bear e bull movem todos os drivers na mesma direção, mas com amplitude moderada: bear é "run-rate desacelera para ~10%/ano em 2030" ($150B / $200B) e bull é "capacidade declarada sem haircut com yield flat" (~1,4x o base). Os três lentes fecham em cada cenário; cenários mais extremos são sensibilidade, não caso.
- **Linha resolvida.** O share de machine API no base é a variável de fechamento. Se as outras premissas mudarem, ela muda junto; se sair de um intervalo plausível (30-50%), o total v3 é que está pedindo demais.
- **Dupla contagem entre pools.** Claude dentro do Cursor está no pool de devs; Claude via Bedrock em um bot de suporte está no machine API. A fronteira é por caso de uso, não por canal.
- **Yield.** É a premissa mais frágil: preço por token cai 5-10x por ano por unidade de capacidade, mas o mix migra para modelos maiores e reasoning. O v3 assume compensação quase total.
- **Dados de 2026 de terceiros.** MAU do Claude, mix de receita e share de mercado vêm de estimativas; só run-rates, GW contratados, preços de lista, planos vazados e o v3 vêm de fontes primárias ou de imprensa financeira.

---

## 11. Fontes principais

- v3: `OpenAI_breakeven_model_MBI_vBTG_v3.xlsx` (Model!I100 receita, I29/I26 GW, I101 yield, I62 custo, I119 margem, I94 haircut, E100/E105 2026E) e `Anthropic_model_MBI_vBTG_v3.xlsx` (Model!I89, I29/I26, I88, I62, I107, I116 EBIT, E89/E90). Valores extraídos em `model/v3_reference.json`.
- OpenAI: run-rate >$40B e enterprise >50% (imprensa, ago-26); plano 2030 >$280B (Bloomberg, 20-fev-26); plano de ads $2,5B → $100B (Axios, 9-abr-26); 15B tokens/min e Codex 2M+ (OpenAI, mar-26); 30 GW em 2030 e compute $600-750B (WSJ/DCD); Oracle $300B / 4,5 GW (The Register).
- Anthropic: run-rate $65B (Bloomberg/Axios/TechCrunch, 17-ago-26); $30B e 1.000+ clientes >$1M (Anthropic, abr-26); $190-200B em 2028 (Reuters, 14-ago-26); margem bruta 40% → 63% → 70% (The Information via imprensa); Claude Code $8B ARR (imprensa, mai-26); custo por dev (docs Claude Code).
- Benchmarks: Meta FY25 $200,1B, DAP 3,58B, ARPP Q4 $16,56 (Meta IR); Google Search ads 2025 $175,8B (Alphabet); 3,2 quadrilhões de tokens/mês (Google I/O 2026); M365 Copilot 20M assentos, GitHub Copilot 4,7M (Microsoft via imprensa); Cursor $2B+ ARR; Atlanta Fed $2.068/funcionário (mai-26); Gartner IT $6,37T, software $1,47T, IA $2,59T (jul-26); Bain $2T e 200 GW (set-25); Epoch AI TCO de 1 GW; preços de lista (benchlm, set-26); superforecasters $300B combinado (Forecasting Research Institute).

URLs completas na aba Sources do modelo.
