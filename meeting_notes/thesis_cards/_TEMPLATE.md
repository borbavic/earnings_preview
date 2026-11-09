# {TICKER} — Ficha de tese e sentimento

Uma ficha por empresa. Ela é o "gabarito" contra o qual cada reunião é pontuada.
Atualizar a **Parte B** (sentimento da ação) até 48h antes de cada reunião: a linha de base velha
distorce o gap. Copiar este arquivo como `thesis_cards/{TICKER}.md`.

- Empresa: {nome}
- Posição: {Long / Short / Sem posição / Watchlist} · Tamanho: {% NAV}
- Analista: {nome} · Última revisão da tese: {AAAA-MM-DD}
- Linha de base de sentimento atualizada em: {AAAA-MM-DD} (preço de referência: {US$ x})

---

## Parte A — Nossa tese

**Tese em uma frase:** {por que temos (ou não) a posição}

**Valuation:** preço-alvo {US$ x} ({múltiplo} × {métrica} {ano}), upside {x%}. Bear {US$ x} / Bull {US$ x}.

### Pilares da tese (3 a 5)

Cada pilar tem um KPI verificável e o sinal que confirma ou que contradiz o pilar. A reunião é pontuada
pilar por pilar.

| # | Pilar | Peso | KPI / evidência observável | Confirma se… | Contradiz se… | Nós vs. consenso |
|---|---|---|---|---|---|---|
| P1 | {ex.: demanda de X sustenta crescimento >Y% em 2027} | 35% | {ex.: lead time, backlog} | {…} | {…} | {Consenso / Diferenciado} |
| P2 | {…} | 25% | {…} | {…} | {…} | {…} |
| P3 | {…} | 20% | {…} | {…} | {…} | {…} |
| P4 | {…} | 20% | {…} | {…} | {…} | {…} |

### Caso bear (o que nos tiraria da posição)
- {gatilho 1, com número}
- {gatilho 2}

### Nossos números vs. consenso
| Métrica | Nós | Consenso | Diferença |
|---|---|---|---|
| Receita {ano} | | | |
| Margem bruta {ano} | | | |
| EPS {ano} | | | |
| {KPI-chave} | | | |

### Perguntas para a próxima reunião (em ordem de prioridade)
1. {pergunta ligada ao P1}
2. {…}
3. {pergunta que testa o caso bear}

### Tom da gestão na última interação (referência para medir mudança)
{data, contexto, 2 ou 3 frases literais. Gestão em conferência quase sempre soa otimista, então o
sinal útil é a mudança de tom em relação a esta referência, não o tom absoluto.}

---

## Parte B — Sentimento atual da ação (linha de base)

Escala de -2 a +2: -2 muito pessimista/descontado · 0 neutro · +2 muito otimista/esticado.
Cada linha precisa de fonte e data. O dado pode estar desatualizado: registre quando foi coletado.

| Componente | Peso | Dado | Fonte / data | Score (-2 a +2) |
|---|---|---|---|---|
| Momento de preço (1m / 3m / YTD vs. SOX ou índice relevante) | 20% | | | |
| Valuation vs. histórico 5a e pares (percentil do P/L ou EV/EBITDA NTM) | 20% | | | |
| Revisões de estimativa (EPS NTM, 3m) | 20% | | | |
| Sell-side (% Buy, dispersão dos alvos) | 15% | | | |
| Posicionamento (short interest, crowding de HFs) | 15% | | | |
| Narrativa (tema dominante no sell-side, X e imprensa) | 10% | | | |
| **Sentimento base (média ponderada)** | | | | **{x,x}** |

**O que o preço desconta hoje (uma frase):** {ex.: "o mercado precifica crescimento de X% em 2027 e
margem bruta de Y%"}
