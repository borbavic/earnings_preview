# Rubrica do scorecard de reunião

Todas as notas vão de **-2 a +2**, na mesma escala do sentimento base da ficha. Assim a nota da
reunião e o sentimento da ação podem ser subtraídos diretamente.

Regra geral: **nenhuma nota sem evidência.** Cada nota diferente de zero precisa citar uma frase
literal ou um número das notas da reunião. Sem evidência, a nota é 0 e o campo fica "sem sinal".

## 1. Impacto na tese (pilar por pilar)

| Nota | Significado |
|---|---|
| +2 | Evidência nova e concreta (número, prazo) que confirma o pilar além do que esperávamos |
| +1 | Confirma, mas com evidência qualitativa ou já conhecida |
| 0 | Não discutido ou sem sinal |
| -1 | Evidência qualitativa contra o pilar, ou resposta evasiva em tema central |
| -2 | Evidência concreta contra o pilar, ou gatilho do caso bear acionado |

**Score de tese** = média dos pilares ponderada pelos pesos da ficha (pilares sem sinal saem do
denominador; se nenhum pilar tiver sinal, o score é "n/d").

**Veredito de tese:**
- Fortalece: score ≥ +0,75 e nenhum pilar em -2
- Inalterada: entre -0,75 e +0,75 e nenhum pilar em -2
- Enfraquece: score ≤ -0,75
- **Em risco**: qualquer pilar em -2 ou gatilho do caso bear acionado (sobrepõe o resto)

## 2. Dimensões da reunião

| Dimensão | Peso | +2 | 0 | -2 |
|---|---|---|---|---|
| Fundamentos (demanda, preço, margem) vs. consenso | 40% | Sinais claramente acima do consenso | Em linha | Claramente abaixo |
| Guidance / KPIs | 25% | Reafirmou com mais confiança ou sinalizou alta | Reafirmou sem mudança | Evitou reafirmar ou sinalizou corte |
| Mudança de tom vs. última interação | 20% | Mais específico e mais confiante | Igual | Mais vago, mais hedging, desvios |
| Credibilidade / consistência | 15% | Números batem com o que já disseram e com dados de terceiros | — | Contradições ou números que não fecham |

**Sentimento da reunião** = média ponderada das quatro dimensões.

Calibração: gestão em conferência sell-side tende a soar otimista em quase todos os casos. Por isso o
tom é medido **em relação à última interação**, nunca em termos absolutos. Uma reunião "positiva"
que repete o mesmo discurso vale 0, não +1.

## 3. Informação incremental (0 a 3, fora da média)

0 = só o discurso de sempre · 1 = um detalhe novo · 2 = vários dados novos · 3 = muda nossa visão de
um número do modelo.

## 4. Gap de sentimento (a métrica principal)

**Gap = Sentimento da reunião − Sentimento base da ação**

| Gap | Leitura | Ação sugerida |
|---|---|---|
| ≥ +1,0 | A reunião foi bem melhor do que o preço desconta | Discutir aumento / revisar estimativas para cima |
| +0,5 a +1,0 | Melhor do que o preço desconta | Revisar modelo |
| -0,5 a +0,5 | Em linha com o que o preço já desconta | Nenhuma |
| -1,0 a -0,5 | Pior do que o preço desconta | Revisar modelo / checar caso bear |
| ≤ -1,0 | Bem pior do que o preço desconta | Discutir redução com o PM |

Por que o gap e não o sentimento absoluto: uma reunião boa numa ação já esticada (base +1,5) não é
sinal de compra; uma reunião neutra numa ação muito descontada (base -1,5) pode ser. O valor está na
diferença entre o que ouvimos e o que o preço já reflete.

Ressalvas:
- Uma reunião é uma amostra. Gap grande com informação incremental 0 ou 1 pede confirmação antes de
  qualquer ação.
- Se a linha de base tiver mais de 7 dias, sinalizar como possivelmente desatualizada.

## 5. Convicção

Variação da convicção depois da reunião: ↑ / = / ↓, com uma frase de justificativa.
