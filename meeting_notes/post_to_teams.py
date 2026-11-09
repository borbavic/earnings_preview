#!/usr/bin/env python3
"""Calcula o scorecard de uma reunião e publica o resumo no Teams.

Entrada: um arquivo JSON de debrief (ver records/_example_debrief.json).
O script calcula score de tese, sentimento da reunião, gap e veredito a partir das
notas individuais (para que nenhuma conta dependa do LLM), grava o registro em
Markdown ao lado do JSON e, se pedido, publica um Adaptive Card no canal do Teams.

Uso:
    python3 post_to_teams.py records/2026-12-02_NVDA.json             # calcula e grava o .md
    python3 post_to_teams.py records/2026-12-02_NVDA.json --print-card # mostra o payload
    TEAMS_WEBHOOK_URL=... python3 post_to_teams.py records/....json --post

TEAMS_WEBHOOK_URL é a URL do fluxo "Post to a channel when a webhook request is received"
(Teams → canal → ... → Workflows). Não commitar a URL: ela funciona como senha.
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

SCALE = (-2, 2)


def wavg(items):
    """Média ponderada ignorando itens sem sinal (score None)."""
    valid = [i for i in items if i.get("score") is not None]
    total_w = sum(i["weight"] for i in valid)
    if not valid or total_w == 0:
        return None
    return sum(i["score"] * i["weight"] for i in valid) / total_w


def validate(d):
    errors = []
    for group in ("pillars", "dimensions"):
        for i in d.get(group, []):
            s = i.get("score")
            if s is not None and not SCALE[0] <= s <= SCALE[1]:
                errors.append(f"{group}/{i.get('id', i.get('name'))}: score {s} fora de -2..+2")
            if s not in (None, 0) and not i.get("evidence"):
                errors.append(f"{group}/{i.get('id', i.get('name'))}: nota {s} sem evidência")
    b = d.get("baseline_sentiment")
    if b is None or not SCALE[0] <= b <= SCALE[1]:
        errors.append("baseline_sentiment ausente ou fora de -2..+2 (preencher a Parte B da ficha)")
    return errors


def thesis_verdict(score, pillars, bear_trigger):
    if bear_trigger or any(p.get("score") == -2 for p in pillars):
        return "Em risco"
    if score is None:
        return "Sem sinal"
    if score >= 0.75:
        return "Fortalece"
    if score <= -0.75:
        return "Enfraquece"
    return "Inalterada"


def gap_reading(gap):
    if gap >= 1.0:
        return "Bem melhor do que o preço desconta", "Discutir aumento / revisar estimativas para cima"
    if gap >= 0.5:
        return "Melhor do que o preço desconta", "Revisar modelo"
    if gap > -0.5:
        return "Em linha com o que o preço desconta", "Nenhuma"
    if gap > -1.0:
        return "Pior do que o preço desconta", "Revisar modelo / checar caso bear"
    return "Bem pior do que o preço desconta", "Discutir redução com o PM"


def compute(d):
    d["thesis_score"] = wavg(d["pillars"])
    d["thesis_verdict"] = thesis_verdict(d["thesis_score"], d["pillars"], d.get("bear_trigger_hit"))
    d["meeting_sentiment"] = wavg(d["dimensions"])
    if d["meeting_sentiment"] is None:
        d["gap"] = None
        d["gap_reading"], d["suggested_action"] = "Sem sinal", "Nenhuma"
    else:
        d["gap"] = round(d["meeting_sentiment"] - d["baseline_sentiment"], 2)
        d["gap_reading"], d["suggested_action"] = gap_reading(d["gap"])
        if d["gap"] and abs(d["gap"]) >= 0.5 and d.get("incremental_info", 0) <= 1:
            d["suggested_action"] += " (confirmar antes: pouca informação nova)"
    return d


def fmt(x):
    return "n/d" if x is None else f"{x:+.2f}"


def verdict_icon(v):
    return {"Fortalece": "🟢", "Inalterada": "⚪", "Enfraquece": "🟠", "Em risco": "🔴"}.get(v, "⚪")


def to_markdown(d):
    L = [
        f"# {d['ticker']} — {d['event']} — {d['date']}",
        "",
        f"Participantes: {d['participants']} · Formato: {d['format']}",
        f"Notas completas: {d.get('notes_url', 'n/d')}",
        "",
        "## Resumo",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Veredito de tese | {verdict_icon(d['thesis_verdict'])} {d['thesis_verdict']} ({fmt(d['thesis_score'])}) |",
        f"| Sentimento da reunião | {fmt(d['meeting_sentiment'])} |",
        f"| Sentimento base da ação | {fmt(d['baseline_sentiment'])} (em {d['baseline_date']}) |",
        f"| **Gap** | **{fmt(d['gap'])}** — {d['gap_reading']} |",
        f"| Informação incremental | {d.get('incremental_info', 'n/d')}/3 |",
        f"| Convicção | {d.get('conviction', '=')} — {d.get('conviction_note', '')} |",
        f"| Ação sugerida | {d['suggested_action']} |",
        "",
        "## Highlights",
        "",
    ]
    L += [f"- **[{h['tag']}]** {h['text']}" for h in d["highlights"]]
    L += ["", "## Tese, pilar por pilar", "", "| Pilar | Peso | Nota | Evidência |", "|---|---|---|---|"]
    L += [f"| {p['id']} {p['name']} | {p['weight']:.0%} | {fmt(p['score'])} | {p.get('evidence') or 'sem sinal'} |"
          for p in d["pillars"]]
    L += ["", "## Dimensões da reunião", "", "| Dimensão | Peso | Nota | Evidência |", "|---|---|---|---|"]
    L += [f"| {x['name']} | {x['weight']:.0%} | {fmt(x['score'])} | {x.get('evidence') or 'sem sinal'} |"
          for x in d["dimensions"]]
    L += ["", "## Red flags", ""] + ([f"- {r}" for r in d.get("red_flags", [])] or ["- nenhuma"])
    L += ["", "## Impacto no modelo / follow-ups", ""] + [f"- {f}" for f in d.get("follow_ups", [])]
    return "\n".join(L) + "\n"


def to_card(d):
    facts = [
        {"title": "Tese", "value": f"{verdict_icon(d['thesis_verdict'])} {d['thesis_verdict']} ({fmt(d['thesis_score'])})"},
        {"title": "Reunião vs. ação", "value": f"{fmt(d['meeting_sentiment'])} vs. {fmt(d['baseline_sentiment'])} → gap {fmt(d['gap'])}"},
        {"title": "Leitura", "value": d["gap_reading"]},
        {"title": "Info nova", "value": f"{d.get('incremental_info', 'n/d')}/3"},
        {"title": "Convicção", "value": f"{d.get('conviction', '=')} {d.get('conviction_note', '')}"},
        {"title": "Ação", "value": d["suggested_action"]},
    ]
    body = [
        {"type": "TextBlock", "size": "Large", "weight": "Bolder", "wrap": True,
         "text": f"{verdict_icon(d['thesis_verdict'])} {d['ticker']} | {d['event']} | {d['date']}"},
        {"type": "TextBlock", "isSubtle": True, "spacing": "None", "wrap": True,
         "text": f"{d['participants']} · {d['format']}"},
        {"type": "FactSet", "facts": facts},
        {"type": "TextBlock", "weight": "Bolder", "text": "Highlights", "spacing": "Medium"},
        {"type": "TextBlock", "wrap": True,
         "text": "\n".join(f"- **[{h['tag']}]** {h['text']}" for h in d["highlights"])},
        {"type": "TextBlock", "weight": "Bolder", "text": "Scorecard por pilar", "spacing": "Medium"},
        {"type": "FactSet", "facts": [{"title": f"{p['id']} {p['name']}", "value": fmt(p["score"])} for p in d["pillars"]]},
    ]
    if d.get("red_flags"):
        body += [{"type": "TextBlock", "weight": "Bolder", "color": "Attention", "text": "Red flags", "spacing": "Medium"},
                 {"type": "TextBlock", "wrap": True, "text": "\n".join(f"- {r}" for r in d["red_flags"])}]
    if d.get("follow_ups"):
        body += [{"type": "TextBlock", "weight": "Bolder", "text": "Follow-ups", "spacing": "Medium"},
                 {"type": "TextBlock", "wrap": True, "text": "\n".join(f"- {f}" for f in d["follow_ups"])}]
    card = {"$schema": "http://adaptivecards.io/schemas/adaptive-card.json", "type": "AdaptiveCard",
            "version": "1.4", "msteams": {"width": "Full"}, "body": body}
    if d.get("notes_url"):
        card["actions"] = [{"type": "Action.OpenUrl", "title": "Notas completas", "url": d["notes_url"]}]
    return {"type": "message", "attachments": [
        {"contentType": "application/vnd.microsoft.card.adaptive", "contentUrl": None, "content": card}]}


def post(payload, url):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("debrief", type=Path)
    ap.add_argument("--print-card", action="store_true")
    ap.add_argument("--post", action="store_true")
    a = ap.parse_args()

    d = json.loads(a.debrief.read_text())
    errors = validate(d)
    if errors:
        sys.exit("Debrief inválido:\n- " + "\n- ".join(errors))
    d = compute(d)

    md_path = a.debrief.with_suffix(".md")
    md_path.write_text(to_markdown(d))
    print(f"Registro gravado em {md_path}")
    print(f"Tese: {d['thesis_verdict']} ({fmt(d['thesis_score'])}) | Reunião {fmt(d['meeting_sentiment'])} "
          f"vs. base {fmt(d['baseline_sentiment'])} → gap {fmt(d['gap'])} | {d['suggested_action']}")

    payload = to_card(d)
    if a.print_card:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    if a.post:
        url = os.environ.get("TEAMS_WEBHOOK_URL")
        if not url:
            sys.exit("TEAMS_WEBHOOK_URL não definido")
        print(f"Teams respondeu HTTP {post(payload, url)}")


if __name__ == "__main__":
    main()
