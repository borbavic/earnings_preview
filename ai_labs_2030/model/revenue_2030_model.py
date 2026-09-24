"""
Bottom-up 2030 revenue framework for OpenAI and Anthropic, calibrated to the
MBI vBTG v3 models (OpenAI_breakeven_model_MBI_vBTG_v3.xlsx, Anthropic_model_MBI_vBTG_v3.xlsx).

Single source of truth for the assumptions used in the markdown framework
(docs/framework_receita_2030.md) and in the Excel model (build_xlsx.py).

BASE = v3 by construction:
  * total 2030 revenue, average in-year GW, average inference share, revenue per average
    inference GW-year ("yield"), inference compute cost per GW-year, 2026E revenue / exit ARR
    and the 2027-30 run-rate path are taken from v3 (see v3_reference.json, with cell refs);
  * the bottom-up reproduces the v3 revenue exactly because the company's share of the
    machine/agent-API pool is SOLVED as the residual (all other segments are explicit choices).
BEAR / BULL are sensitised around that base.

Four lenses that must reconcile:
  1. Demand side (bottom-up by segment)  -> users x penetration x spend x share
  2. Supply side (compute)               -> avg GW x inference share x yield per inference GW-year
  3. Momentum (run-rate path)            -> exit-2026 run-rate x growth; calendar = avg of exit run-rates
  4. Wallet / base-rate checks           -> share of labour cost, software spend, ad market

Units: money in USD billions unless stated; people in millions; tokens in quadrillions (1e15).
Run:  python revenue_2030_model.py   -> prints all tables as markdown
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List

SCEN = ["bear", "base", "bull"]
YEARS_2026_TO_2030 = 4  # 2026E calendar -> 2030E calendar

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = json.load(open(os.path.join(HERE, "v3_reference.json")))


def v3(co: str, key: str) -> float:
    return V3[co][key]["value"]


def v3cell(co: str, key: str) -> str:
    return f"{V3[co]['_file']} {V3[co][key]['cell']}"


@dataclass
class A:
    """One assumption line: bear/base/bull values + unit + anchor text.
    solved=True: the Base value is not an input but is solved so that the bottom-up equals v3."""
    key: str
    label: str
    bear: float
    base: float
    bull: float
    unit: str
    anchor: str
    group: str = ""
    solved: bool = False

    def v(self, s: str) -> float:
        return getattr(self, s)


def _g(co: str, y: int) -> float:
    """v3 exit-ARR growth for year y (27..30)."""
    return v3(co, f"exit_arr_20{y}") / v3(co, f"exit_arr_20{y-1}") - 1


# ---------------------------------------------------------------------------
# ASSUMPTIONS (2030 unless stated). Anchors = 2026 observed data points / v3 cells.
# ---------------------------------------------------------------------------
ASSUMPTIONS: List[A] = [
    # ---- Global knowledge-worker pool (shared by both companies) ----
    A("kw_dev", "Developers / data-AI engineers (M)", 36, 42, 46, "M people",
      "~30M professional devs 2026 (SlashData/Evans est.); AI-native builders expand the pool", "Pool"),
    A("kw_pro", "Professional / high-intensity knowledge workers (M)", 205, 220, 240, "M people",
      "finance, legal, consulting, research, marketing, sales, product; ~20% of ~1.05B KW", "Pool"),
    A("kw_gen", "General knowledge workers (M)", 770, 790, 815, "M people",
      "~1B+ knowledge workers globally (Gartner >1B; Forrester 1.25B info workers); residual", "Pool"),
    A("sal_dev", "Avg salary - developers ($k/yr, global blend)", 72, 75, 80, "$k/yr",
      "US ~$150k, India ~$15k; global blend ~$75k", "Pool"),
    A("sal_pro", "Avg salary - professionals ($k/yr, global blend)", 57, 60, 65, "$k/yr",
      "global blend; US-only ~$100-120k", "Pool"),
    A("sal_gen", "Avg salary - general KW ($k/yr, global blend)", 29, 30, 32, "$k/yr",
      "global blend incl. EM", "Pool"),
    # ---- Penetration of PAID AI seats in 2030 ----
    A("pen_dev", "Paid-AI penetration - developers", 0.70, 0.85, 0.92, "%",
      "2026: ~10-12M paid (GitHub Copilot 4.7M, Cursor, Claude Code, Codex) of ~30M = ~35-40%", "Penetration"),
    A("pen_pro", "Paid-AI penetration - professionals", 0.35, 0.50, 0.60, "%",
      "2026: ~35-40M paid seats globally (M365 Copilot 20M, ChatGPT biz 9M, Claude, Gemini) = ~4% of all KW, ~10% of pros", "Penetration"),
    A("pen_gen", "Paid-AI penetration - general KW", 0.15, 0.30, 0.40, "%",
      "seat-type products ($20-30/mo); Copilot bundling drives this", "Penetration"),
    # ---- Spend per PAID seat as % of salary (seat fee + usage/tokens) ----
    A("ratio_dev", "AI spend / salary - developers", 0.08, 0.168, 0.20, "%",
      "Base $12.6k/dev/yr is what the v3 revenue needs; 2026: Claude Code enterprise avg $150-250/mo = $1.8-3k/yr; heavy agent users >$1k/mo", "Spend"),
    A("ratio_pro", "AI spend / salary - professionals", 0.02, 0.045, 0.06, "%",
      "Base $2.7k/seat; 2026: M365 Copilot $360/yr; ChatGPT Enterprise ~$600-900/yr incl. usage; Atlanta Fed avg AI spend/employee $2,068 (all AI)", "Spend"),
    A("ratio_gen", "AI spend / salary - general KW", 0.008, 0.014, 0.02, "%",
      "Base $420/seat; 2026: Copilot $360/yr; ChatGPT Business $25-30/seat", "Spend"),
    # ---- Lab share of paid-seat spend (direct + model-layer share inside 3rd-party tools) ----
    A("sh_dev_ant", "Anthropic share - developer spend", 0.36, 205 / (42 * 0.85 * 75 * 0.168), 0.48, "%",
      "Base = $205B of a $450B pool; 2026: Claude Code $8B ARR (May-26) + Claude inside Cursor/Copilot; Menlo: Anthropic ~54% of coding model spend", "Share"),
    A("sh_dev_oai", "OpenAI share - developer spend", 0.14, 78 / (42 * 0.85 * 75 * 0.168), 0.24, "%",
      "Base = $78B; Codex 2M+ weekly users (Mar-26); GPT-5.x in Cursor/Copilot", "Share"),
    A("sh_pro_ant", "Anthropic share - professional seats", 0.13, 55 / (220 * 0.50 * 60 * 0.045), 0.24, "%",
      "Base = $55B of a $297B pool; Claude Enterprise/Team/Cowork + Bedrock/Vertex/Foundry", "Share"),
    A("sh_pro_oai", "OpenAI share - professional seats", 0.20, 68 / (220 * 0.50 * 60 * 0.045), 0.30, "%",
      "Base = $68B; 2026: 7M enterprise seats, 9M paying business users, >1M business customers", "Share"),
    A("sh_gen_ant", "Anthropic share - general seats", 0.05, 8 / (790 * 0.30 * 30 * 0.014), 0.12, "%",
      "Base = $8B of a $100B pool; mostly model-layer share of Copilot-type bundles", "Share"),
    A("sh_gen_oai", "OpenAI share - general seats", 0.14, 18 / (790 * 0.30 * 30 * 0.014), 0.25, "%",
      "Base = $18B; ChatGPT Business/Edu; Copilot uses OpenAI models (rev share)", "Share"),
    # ---- Machine / agent API pool (workloads not tied to a human seat) ----
    A("auto_pool", "Labour cost pool of AI-automatable digital tasks ($T)", 7, 8, 10, "$T",
      "global labour comp ~$58T (2025); knowledge-work comp $35-50T; ~15-20% is task-automatable", "Machine"),
    A("auto_share", "Share of that pool automated by AI agents in 2030", 0.07, 0.125, 0.16, "%",
      "2026: customer-service and coding agents are the only scaled cases", "Machine"),
    A("auto_capture", "Vendor capture ($ AI spend per $ labour displaced)", 0.20, 0.30, 0.34, "%",
      "Claude Code $2-3k/yr vs $20-40k of dev output = ~10%; SaaS captures 10-30% of value", "Machine"),
    A("sh_auto_ant", "Anthropic share - machine API (BASE SOLVED so total = v3)", 0.30, 0.0, 0.45, "%",
      "Base is a formula: (v3 2030 revenue - all other Anthropic segments) / machine pool. 2026 anchor: Menlo, Anthropic ~32-40% of enterprise LLM API spend", "Machine", solved=True),
    A("sh_auto_oai", "OpenAI share - machine API (BASE SOLVED so total = v3)", 0.12, 0.0, 0.24, "%",
      "Base is a formula: (v3 2030 revenue - all other OpenAI segments) / machine pool. 2026 anchor: API ~15-20% of OpenAI revenue; Menlo ~25% of API spend", "Machine", solved=True),
    # ---- Consumer: OpenAI ----
    A("oai_mau", "ChatGPT MAU 2030 (M)", 1500, 2000, 2500, "M people",
      "1B MAU (Jun-26), ~1B WAU (Jul-26); internet users ~5.6B->6B; Meta DAP 3.58B", "Consumer OAI"),
    A("oai_conv", "Paid conversion (subs / MAU)", 0.045, 0.065, 0.09, "%",
      ">50M consumer subs / ~1B = ~5% (Aug-26); India Go free promo dilutes", "Consumer OAI"),
    A("oai_arpu", "Paid ARPU ($/month, blended)", 15, 20.5, 24, "$/mo",
      "Go $8 (US)/Rs399 (India), Plus $20, Pro $200 (~0.5M subs); blended est. $25-30 in 2026, skewing down with EM mix", "Consumer OAI"),
    A("oai_ad_arpu", "Ads ARPU per FREE user ($/yr)", 15, 40, 60, "$/yr",
      "Base $40 = ~50% of Meta's 2030 ARPP (~$80); Meta ARPP 2025 $58 global; Google Search ~$60-70/user; OpenAI plan $100B ads by 2030 = ~$50/free user; ads $1B run-rate <200 days after Feb-26 launch", "Consumer OAI"),
    A("oai_gmv", "Commerce GMV routed via ChatGPT ($B)", 100, 480, 1000, "$B",
      "Instant Checkout (Sep-25); global e-commerce ~$7T by 2030", "Consumer OAI"),
    A("oai_take", "Commerce take rate", 0.02, 0.025, 0.03, "%",
      "affiliate/checkout take rates 2-4%", "Consumer OAI"),
    # ---- Consumer: Anthropic ----
    A("ant_mau", "Claude consumer MAU 2030 (M)", 150, 250, 400, "M people",
      "2026 est. 30-140M (third-party, unreliable); consumer ~5-10% of revenue", "Consumer ANT"),
    A("ant_conv", "Paid conversion (subs / MAU)", 0.08, 0.12, 0.14, "%",
      "professional skew; Max tiers", "Consumer ANT"),
    A("ant_arpu", "Paid ARPU ($/month, blended)", 26, 40, 45, "$/mo",
      "Pro $20, Max $100/$200", "Consumer ANT"),
    # ---- Other ----
    A("oai_other", "OpenAI other (devices, licensing, gov, media) ($B)", 4, 8, 20, "$B",
      "io hardware, Sora, sovereign deals, MSFT rev share", "Other"),
    A("ant_other", "Anthropic other (gov/sovereign, licensing, reseller minimums) ($B)", 4, 12, 20, "$B",
      "defense/gov, Amazon/Alexa, Apple", "Other"),
    # ---- Supply side: OpenAI (Base = v3) ----
    A("oai_gw_avg", "OpenAI average in-year total capacity 2030 (GW)", 14, v3("oai", "gw_avg_total_2030"), 27.5, "GW",
      f"Base = v3 {v3cell('oai', 'gw_avg_total_2030')} (year-end 22.1 GW after the 26.4% budget haircut on the 30 GW path); bull = full stated path avg(25,30)", "Supply OAI"),
    A("oai_inf_share_avg", "OpenAI inference share of average capacity 2030", 0.48, v3("oai", "inf_share_avg_2030"), 0.60, "%",
      f"Base = v3 avg inference GW / avg total GW ({v3cell('oai', 'gw_avg_inf_2030')} / I29); year-end allocation 55% inference / 33% training / 12% alignment", "Supply OAI"),
    A("oai_yield_inf", "OpenAI revenue per average inference GW-year 2030 ($B)", 22, v3("oai", "yield_inf_2030"), 40, "$B",
      f"Base = v3 {v3cell('oai', 'yield_inf_2030')} (breakeven yield); 2026E $27.1B (E101); exit-ARR yield 2026E $32.9B", "Supply OAI"),
    A("oai_cost_inf_gw", "OpenAI inference compute cost per GW-year 2030 ($B)", 13.3, v3("oai", "inf_cost_per_gw_2030"), 10, "$B",
      f"Base = v3 {v3cell('oai', 'inf_cost_per_gw_2030')} (blend of Azure $12B, Oracle $13.3B, AWS $8-10B, owned chips ~$10.5B)", "Supply OAI"),
    A("oai_other_cor", "OpenAI other cost of revenue, % of revenue 2030", 0.04, 0.03, 0.025, "%",
      "v3 Model!I71 = 3.0% (payments, app-store fees, support, non-compute hosting)", "Supply OAI"),
    # ---- Supply side: Anthropic (Base = v3) ----
    A("ant_gw_avg", "Anthropic average in-year total capacity 2030 (GW)", 15, v3("ant", "gw_avg_total_2030"), 25, "GW",
      f"Base = v3 {v3cell('ant', 'gw_avg_total_2030')} (stated path 20 -> 25 GW year-end, no haircut)", "Supply ANT"),
    A("ant_inf_share_avg", "Anthropic inference share of average capacity 2030", 0.48, v3("ant", "inf_share_avg_2030"), 0.60, "%",
      f"Base = v3 avg inference GW / avg total GW ({v3cell('ant', 'gw_avg_inf_2030')} / I29); year-end allocation 55% / 33% / 12%", "Supply ANT"),
    A("ant_yield_inf", "Anthropic revenue per average inference GW-year 2030 ($B)", 25, v3("ant", "yield_inf_2030"), 45, "$B",
      f"Base = v3 {v3cell('ant', 'yield_inf_2030')}: 2026E $40.2B then -6%/yr 2027-29 and -5.3% in 2030; v3 breakeven yield memo $30.1B (I94)", "Supply ANT"),
    A("ant_cost_inf_gw", "Anthropic inference compute cost per GW-year 2030 ($B)", 13.3, v3("ant", "inf_cost_per_gw_2030"), 10, "$B",
      f"Base = v3 {v3cell('ant', 'inf_cost_per_gw_2030')} (held at $12B from 2027; blended stack ~$10B)", "Supply ANT"),
    A("ant_other_cor", "Anthropic other cost of revenue, % of revenue 2030", 0.04, 0.03, 0.025, "%",
      "v3 Model!I71 = 3.0%", "Supply ANT"),
    # ---- Supply side: shared decomposition memo ----
    A("tok_per_gw", "Tokens per GW-year at 100% util (quadrillion) - decomposition memo", 16, 20, 32, "1e15 tokens",
      "OpenAI 2026: ~15-20 quadrillion tok/yr on ~1.5-2GW inference; Google 38 quadrillion/yr (3.2q/mo, May-26); Rubin 2-4x GB300", "Supply shared"),
    A("util", "Inference fleet utilisation - decomposition memo", 0.60, 0.68, 0.78, "%",
      "peak/off-peak; batch jobs fill valleys. Implied realised $/M tokens = yield / (tokens x util)", "Supply shared"),
    # ---- Deck as presented ----
    A("deck_gw", "Deck: total GW per company (2030)", 25, 25, 25, "GW",
      "deck assumption; v3 uses avg in-year 20.2 GW (OpenAI, after haircut) and 22.5 GW (Anthropic)", "Deck"),
    A("deck_inf_share", "Deck: share of capacity allocated to inference", 0.50, 0.525, 0.55, "%",
      "deck assumption 50-55%; v3 year-end 55%, in-year average 54.1%", "Deck"),
    A("deck_rgw_inf", "Deck: revenue per GW of inference ($B/yr)", 28, 30, 32, "$B",
      "deck assumption $30B; v3: OpenAI breakeven yield $30.9B, Anthropic $35.0B (breakeven memo $30.1B)", "Deck"),
    # ---- Momentum path (exit run-rate, $B; Base = v3) ----
    A("oai_rr26", "OpenAI exit-2026 run-rate ($B)", 50, v3("oai", "exit_arr_2026"), 65, "$B",
      f"Base = v3 {v3cell('oai', 'exit_arr_2026')}; >$40B run-rate Aug-26 (+35% QTD)", "Momentum"),
    A("ant_rr26", "Anthropic exit-2026 run-rate ($B)", 85, v3("ant", "exit_arr_2026"), 110, "$B",
      f"Base = v3 {v3cell('ant', 'exit_arr_2026')}; $65B run-rate end-Jul-26", "Momentum"),
    A("oai_g27", "OpenAI exit run-rate growth 2027", 0.45, _g("oai", 27), 1.40, "%", "Base = v3 exit ARR path (Model!E105:I105)", "Momentum"),
    A("oai_g28", "OpenAI exit run-rate growth 2028", 0.30, _g("oai", 28), 0.75, "%", "", "Momentum"),
    A("oai_g29", "OpenAI exit run-rate growth 2029", 0.20, _g("oai", 29), 0.45, "%", "", "Momentum"),
    A("oai_g30", "OpenAI exit run-rate growth 2030", 0.12, _g("oai", 30), 0.30, "%", "", "Momentum"),
    A("ant_g27", "Anthropic exit run-rate growth 2027", 0.40, _g("ant", 27), 1.10, "%", "Base = v3 exit ARR path (Model!E90:I90)", "Momentum"),
    A("ant_g28", "Anthropic exit run-rate growth 2028", 0.22, _g("ant", 28), 0.60, "%", "", "Momentum"),
    A("ant_g29", "Anthropic exit run-rate growth 2029", 0.12, _g("ant", 29), 0.35, "%", "", "Momentum"),
    A("ant_g30", "Anthropic exit run-rate growth 2030", 0.06, _g("ant", 30), 0.28, "%", "", "Momentum"),
]

# v3 reference lines (same value in all three columns; used by the reconciliation block)
V3_REF_KEYS = [
    ("rev_2030", "calendar revenue 2030 ($B)"), ("rev_2026", "calendar revenue 2026E ($B)"),
    ("exit_arr_2030", "exit run-rate ARR 2030 ($B)"), ("exit_arr_2026", "exit run-rate ARR 2026E ($B)"),
    ("gw_avg_total_2030", "average in-year total capacity 2030 (GW)"), ("gw_ye_2030", "year-end capacity 2030 (GW)"),
    ("gw_avg_inf_2030", "average in-year inference capacity 2030 (GW)"),
    ("inf_share_avg_2030", "inference share of average capacity 2030"), ("inf_share_ye_2030", "inference share, year-end 2030"),
    ("yield_inf_2030", "revenue per average inference GW-year 2030 ($B)"), ("rev_per_total_gw_2030", "revenue per average total GW-year 2030 ($B)"),
    ("inf_cost_per_gw_2030", "inference compute cost per GW-year 2030 ($B)"), ("gross_margin_2030", "gross margin 2030"),
    ("ebit_2030", "EBIT 2030 ($B)"), ("total_compute_2030", "total compute cost 2030 ($B)"), ("yield_inf_2026", "revenue per average inference GW-year 2026E ($B)"),
]
for _co, _name in (("oai", "OpenAI"), ("ant", "Anthropic")):
    for _key, _label in V3_REF_KEYS:
        _val = v3(_co, _key)
        _unit = "%" if ("share" in _key or "margin" in _key) else ("GW" if _key.startswith("gw_") else "$B")
        ASSUMPTIONS.append(A(f"v3_{_co}_{_key}", f"v3 {_name}: {_label}", _val, _val, _val, _unit, v3cell(_co, _key), "v3 reference"))

AS: Dict[str, A] = {a.key: a for a in ASSUMPTIONS}

SEGMENTS = ["Developers / coding agents", "Professional seats", "General KW seats", "Machine / agent API",
            "Consumer subscriptions", "Consumer ads", "Commerce / agentic transactions", "Other"]
ENTERPRISE_SEGMENTS = SEGMENTS[:4]

# 2026E calendar revenue mix ($B): totals = v3 (36.5 / 57.0); the segment split is our estimate.
MIX_2026 = {
    "oai": {"Developers / coding agents": 3.5, "Professional seats": 7.5, "General KW seats": 1.8,
            "Machine / agent API": 5.5, "Consumer subscriptions": 15.5, "Consumer ads": 1.0,
            "Commerce / agentic transactions": 0.4, "Other": 1.3},
    "ant": {"Developers / coding agents": 22.0, "Professional seats": 8.5, "General KW seats": 0.8,
            "Machine / agent API": 17.5, "Consumer subscriptions": 5.5, "Consumer ads": 0.0,
            "Commerce / agentic transactions": 0.0, "Other": 2.7},
}
assert abs(sum(MIX_2026["oai"].values()) - v3("oai", "rev_2026")) < 1e-9
assert abs(sum(MIX_2026["ant"].values()) - v3("ant", "rev_2026")) < 1e-9


# ---------------------------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------------------------
def spend_per_seat(tier: str, s: str) -> float:
    return g(f"sal_{tier}", s) * g(f"ratio_{tier}", s) * 1000.0


def seat_pool(tier: str, s: str) -> float:
    """Global paid-seat AI spend pool for a tier ($B). M people * % * $k/yr * % = $B."""
    return g(f"kw_{tier}", s) * g(f"pen_{tier}", s) * g(f"sal_{tier}", s) * g(f"ratio_{tier}", s)


def machine_pool(s: str) -> float:
    return g("auto_pool", s) * g("auto_share", s) * g("auto_capture", s) * 1000.0


def enterprise_pool(s: str) -> float:
    return sum(seat_pool(t, s) for t in ("dev", "pro", "gen")) + machine_pool(s)


def _non_machine(co: str, s: str) -> Dict[str, float]:
    r: Dict[str, float] = {}
    r["Developers / coding agents"] = seat_pool("dev", s) * g(f"sh_dev_{co}", s)
    r["Professional seats"] = seat_pool("pro", s) * g(f"sh_pro_{co}", s)
    r["General KW seats"] = seat_pool("gen", s) * g(f"sh_gen_{co}", s)
    mau, conv = g(f"{co}_mau", s), g(f"{co}_conv", s)
    r["Consumer subscriptions"] = mau * conv * g(f"{co}_arpu", s) * 12 / 1000.0
    if co == "oai":
        r["Consumer ads"] = mau * (1 - conv) * g("oai_ad_arpu", s) / 1000.0
        r["Commerce / agentic transactions"] = g("oai_gmv", s) * g("oai_take", s)
    else:
        r["Consumer ads"] = 0.0
        r["Commerce / agentic transactions"] = 0.0
    r["Other"] = g(f"{co}_other", s)
    return r


def solve_machine_share(co: str) -> float:
    """Base share of the machine pool that makes the bottom-up total equal to v3 2030 revenue."""
    others = sum(_non_machine(co, "base").values())
    return (v3(co, "rev_2030") - others) / machine_pool("base")


def g(key: str, s: str) -> float:
    a = AS[key]
    if s == "base" and a.solved:
        return solve_machine_share(key.split("_")[-1])
    return a.v(s)


def company(co: str, s: str) -> Dict[str, float]:
    r = _non_machine(co, s)
    r["Machine / agent API"] = machine_pool(s) * g(f"sh_auto_{co}", s)
    r = {k: r[k] for k in SEGMENTS}
    r["TOTAL"] = sum(r[k] for k in SEGMENTS)
    return r


def supply(co: str, s: str) -> Dict[str, float]:
    gw, sh, y = g(f"{co}_gw_avg", s), g(f"{co}_inf_share_avg", s), g(f"{co}_yield_inf", s)
    inf_gw = gw * sh
    rev_sup = inf_gw * y
    demand = company(co, s)["TOTAL"]
    cogs = inf_gw * g(f"{co}_cost_inf_gw", s) + g(f"{co}_other_cor", s) * rev_sup
    return {
        "Average in-year total capacity (GW)": gw,
        "Inference share of average capacity": sh,
        "Average inference capacity (GW)": inf_gw,
        "Revenue per average inference GW-year ($B)": y,
        "Revenue per average total GW-year ($B)": y * sh,
        "Supply-side revenue = inf GW x yield ($B)": rev_sup,
        "Demand-side revenue (bottom-up, $B)": demand,
        "Demand / supply": demand / rev_sup,
        "Yield needed for bottom-up at this GW and share ($B)": demand / inf_gw,
        "Inference compute cost per GW-year ($B)": g(f"{co}_cost_inf_gw", s),
        "Cost of revenue = inf GW x cost + other CoR ($B)": cogs,
        "Gross margin (supply-side revenue)": 1 - cogs / rev_sup,
        "Implied realised price ($/M tokens) at memo tokens/GW and util": y / (g("tok_per_gw", s) * g("util", s)),
    }


def momentum(co: str, s: str) -> Dict[str, float]:
    rr = g(f"{co}_rr26", s)
    out = {"Exit-2026 run-rate": rr}
    prev = rr
    for y in (27, 28, 29, 30):
        cur = prev * (1 + g(f"{co}_g{y}", s))
        out[f"Exit-20{y} run-rate"] = cur
        out[f"Calendar revenue 20{y} (avg of exit run-rates)"] = (prev + cur) / 2
        prev = cur
    return out


def deck_check(s: str) -> Dict[str, float]:
    rev = g("deck_gw", s) * g("deck_inf_share", s) * g("deck_rgw_inf", s)
    return {
        "Deck revenue = GW x inf share x $/GW-inf ($B)": rev,
        "Deck implied $/GW of TOTAL capacity ($B)": g("deck_inf_share", s) * g("deck_rgw_inf", s),
        "v3 OpenAI 2030 revenue ($B)": v3("oai", "rev_2030"),
        "v3 Anthropic 2030 revenue ($B)": v3("ant", "rev_2030"),
        "Deck yield vs v3 OpenAI yield": g("deck_rgw_inf", s) / v3("oai", "yield_inf_2030"),
        "Deck yield vs v3 Anthropic yield": g("deck_rgw_inf", s) / v3("ant", "yield_inf_2030"),
        "Deck yield vs OpenAI 2026E yield (v3)": g("deck_rgw_inf", s) / v3("oai", "yield_inf_2026"),
        "Deck yield vs Anthropic 2026E yield (v3)": g("deck_rgw_inf", s) / v3("ant", "yield_inf_2026"),
    }


def bridge(co: str, s: str = "base") -> List[List[str]]:
    rows = []
    r30 = company(co, s)
    tot26 = sum(MIX_2026[co].values())
    for seg in SEGMENTS:
        v26, v30 = MIX_2026[co][seg], r30[seg]
        if v26:
            mult = v30 / v26
            rows.append([seg, fmt(v26), fmt(v30), f"{mult:.1f}x", f"{(mult ** (1 / YEARS_2026_TO_2030) - 1)*100:.0f}%"])
        else:
            rows.append([seg, fmt(v26), fmt(v30), "n/a", "n/a"])
    mult = r30["TOTAL"] / tot26
    rows.append(["TOTAL", fmt(tot26), fmt(r30["TOTAL"]), f"{mult:.1f}x", f"{(mult ** (1 / YEARS_2026_TO_2030) - 1)*100:.0f}%"])
    return rows


def what_you_need(co: str, target: float, s: str = "base") -> Dict[str, str]:
    r = company(co, s)
    non_ent = r["TOTAL"] - sum(r[k] for k in ENTERPRISE_SEGMENTS)
    ent = sum(r[k] for k in ENTERPRISE_SEGMENTS)
    uplift = (target - non_ent) / ent
    gw, sh = g(f"{co}_gw_avg", s), g(f"{co}_inf_share_avg", s)
    out = {}
    out["Target vs Base (v3) revenue"] = f"{target / r['TOTAL']:.2f}x"
    out["Implied yield per inference GW at Base GW and share"] = f"${target/(gw*sh):.1f}B ({gw:.1f} GW x {sh:.1%})"
    out["Implied average GW at Base yield and share"] = f"{target/(g(f'{co}_yield_inf', s)*sh):.1f} GW"
    out["Implied GW at deck economics"] = f"{target/(g('deck_rgw_inf', s)*g('deck_inf_share', s)):.1f} GW (${g('deck_rgw_inf', s):.0f}B x {g('deck_inf_share', s):.1%})"
    out["Required uplift on enterprise engines vs Base"] = f"{uplift:.2f}x"
    dev_ratio = g("ratio_dev", s) * (1 + (uplift - 1) * ent / r["Developers / coding agents"])
    out["...if only developer spend/salary moves"] = (f"{dev_ratio*100:.0f}% of salary (${g('sal_dev', s)*dev_ratio:.1f}k/dev/yr) vs base {g('ratio_dev', s)*100:.1f}%"
                                                      if dev_ratio > 0 else "n/a: this driver alone cannot get there (would be <0)")
    auto_share = g("auto_share", s) * (1 + (uplift - 1) * ent / r["Machine / agent API"])
    out["...if only machine-API automation share moves"] = (f"{auto_share*100:.1f}% of pool vs base {g('auto_share', s)*100:.1f}%"
                                                            if auto_share > 0 else "n/a: this driver alone cannot get there (would be <0)")
    out["Target as % of global enterprise AI pool (base)"] = f"{target/enterprise_pool(s)*100:.0f}% of ${enterprise_pool(s):,.0f}B"
    out["Target as % of global labour comp (~$65T 2030)"] = f"{target/65000*100:.2f}%"
    out["Target as % of global software spend (~$2.4T 2030)"] = f"{target/2400*100:.0f}%"
    return out


def reconciliation(co: str) -> List[List[str]]:
    """Model Base vs v3 for the lines that must be identical."""
    c, sp, mo = company(co, "base"), supply(co, "base"), momentum(co, "base")
    rows = [
        ["2030 revenue - bottom-up", c["TOTAL"], v3(co, "rev_2030")],
        ["2030 revenue - supply side", sp["Supply-side revenue = inf GW x yield ($B)"], v3(co, "rev_2030")],
        ["2030 revenue - momentum (calendar)", mo["Calendar revenue 2030 (avg of exit run-rates)"], v3(co, "rev_2030")],
        ["2030 exit run-rate", mo["Exit-2030 run-rate"], v3(co, "exit_arr_2030")],
        ["Average total GW 2030", sp["Average in-year total capacity (GW)"], v3(co, "gw_avg_total_2030")],
        ["Inference share of average capacity", sp["Inference share of average capacity"], v3(co, "inf_share_avg_2030")],
        ["Average inference GW", sp["Average inference capacity (GW)"], v3(co, "gw_avg_inf_2030")],
        ["Revenue per average inference GW-year", sp["Revenue per average inference GW-year ($B)"], v3(co, "yield_inf_2030")],
        ["Revenue per average total GW-year", sp["Revenue per average total GW-year ($B)"], v3(co, "rev_per_total_gw_2030")],
        ["Gross margin 2030", sp["Gross margin (supply-side revenue)"], v3(co, "gross_margin_2030")],
    ]
    return [[a, f"{b:.4f}", f"{d:.4f}", f"{b-d:+.6f}"] for a, b, d in rows]


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def fmt(x: float, unit: str = "") -> str:
    if unit == "%":
        return f"{x*100:.1f}%"
    if abs(x) >= 100:
        return f"{x:,.0f}"
    if abs(x) < 1:
        return f"{x:,.3f}"
    return f"{x:,.1f}"


def md_table(headers: List[str], rows: List[List[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def grid(row_vals, col_vals, f, row_fmt, col_fmt, cell_fmt, corner="") -> str:
    headers = [corner] + [col_fmt(c) for c in col_vals]
    rows = [[row_fmt(r)] + [cell_fmt(f(r, c)) for c in col_vals] for r in row_vals]
    return md_table(headers, rows)


def sensitivities() -> Dict[str, str]:
    s = "base"
    out = {}
    sh = 0.541
    out[f"Revenue ($B) = average total GW x inference share ({sh:.1%}) x yield per inference GW"] = grid(
        [15, 20, 22.5, 25, 30], [22, 26, 30, 31, 35, 40], lambda gw, y: gw * sh * y,
        lambda r: f"{r} GW", lambda c: f"${c}B/GW-inf", lambda v: f"{v:,.0f}")
    out["Revenue ($B) at 22.5 average GW = inference share x yield per inference GW"] = grid(
        [0.45, 0.50, 0.54, 0.60, 0.65], [22, 26, 30, 31, 35, 40], lambda a, y: 22.5 * a * y,
        lambda r: f"{r:.0%} inference", lambda c: f"${c}B/GW-inf", lambda v: f"{v:,.0f}")
    ku = g("util", s)
    out[f"Yield per inference GW ($B) = tokens/GW-yr x realised price x utilisation ({ku:.0%})"] = grid(
        [12, 16, 20, 24, 28, 32], [1.2, 1.6, 2.0, 2.3, 2.6, 3.0], lambda t, p: t * p * ku,
        lambda r: f"{r}q tok/GW", lambda c: f"${c}/M", lambda v: f"{v:,.1f}")
    out["OpenAI ads revenue ($B) = free MAU x ad ARPU"] = grid(
        [1400, 1900, 2300], [20, 30, 40, 50, 60], lambda m, a: m * a / 1000,
        lambda r: f"{r/1000:.1f}B free", lambda c: f"${c}/yr", lambda v: f"{v:,.0f}")
    out[f"OpenAI consumer subs ($B) = MAU x conversion x ${g('oai_arpu', s)}/mo"] = grid(
        [1500, 2000, 2500], [0.045, 0.065, 0.08, 0.10], lambda m, c: m * c * g("oai_arpu", s) * 12 / 1000,
        lambda r: f"{r/1000:.1f}B MAU", lambda c: f"{c:.1%} paid", lambda v: f"{v:,.0f}")
    devs = g("kw_dev", s) * g("pen_dev", s)
    out[f"Anthropic developer engine ($B) = {devs:.1f}M paid devs x spend x share"] = grid(
        [6, 9, 12, 15, 18], [0.35, 0.40, 0.45, 0.50], lambda sp, shr: devs * sp * shr,
        lambda r: f"${r}k/dev/yr", lambda c: f"{c:.0%} share", lambda v: f"{v:,.0f}")
    out[f"Professional-seat global pool ($B) = {g('kw_pro', s):.0f}M x penetration x spend"] = grid(
        [0.40, 0.50, 0.60], [1800, 2700, 3600, 4500], lambda pen, sp: g("kw_pro", s) * pen * sp / 1000,
        lambda r: f"{r:.0%} penetration", lambda c: f"${c}/seat", lambda v: f"{v:,.0f}")
    out["Machine/agent API global pool ($B) = $8T x automated share x capture"] = grid(
        [0.08, 0.125, 0.16, 0.20], [0.20, 0.25, 0.30, 0.35], lambda a, c: 8000 * a * c,
        lambda r: f"{r:.1%} automated", lambda c: f"{c:.0%} capture", lambda v: f"{v:,.0f}")
    out["Gross margin on inference = 1 - cost per GW-yr / yield per inference GW (before other CoR)"] = grid(
        [22, 30.9, 35, 40, 50], [8, 10, 11.7, 12, 13.3], lambda y, c: 1 - c / y,
        lambda r: f"${r}B yield", lambda c: f"${c}B cost", lambda v: f"{v*100:.0f}%")
    return out


def report() -> str:
    parts = []
    parts.append("## Spend per paid seat 2030 ($/yr)\n" + md_table(
        ["Tier", "Bear", "Base", "Bull", "2026 anchor"],
        [["Developers"] + [f"{spend_per_seat('dev', s):,.0f}" for s in SCEN] + ["$1.8-3k (Claude Code ent. avg)"],
         ["Professionals"] + [f"{spend_per_seat('pro', s):,.0f}" for s in SCEN] + ["$360 Copilot / $600-900 ChatGPT Ent."],
         ["General KW"] + [f"{spend_per_seat('gen', s):,.0f}" for s in SCEN] + ["$360 Copilot"]]))
    rows = [[lab] + [fmt(seat_pool(t, s)) for s in SCEN] for t, lab in
            [("dev", "Developers"), ("pro", "Professionals"), ("gen", "General KW")]]
    rows.append(["Machine / agent API"] + [fmt(machine_pool(s)) for s in SCEN])
    rows.append(["TOTAL enterprise pool"] + [fmt(enterprise_pool(s)) for s in SCEN])
    parts.append("## Global enterprise AI spend pools 2030 ($B, all vendors)\n" + md_table(["Pool", "Bear", "Base", "Bull"], rows))
    parts.append("## Solved base shares of the machine pool\n" + md_table(
        ["Company", "Share"], [["OpenAI", f"{solve_machine_share('oai'):.4%}"], ["Anthropic", f"{solve_machine_share('ant'):.4%}"]]))
    dc = {s: deck_check(s) for s in SCEN}
    parts.append("## Deck check vs v3\n" + md_table(["Metric", "Bear", "Base", "Bull"], [[k] + [fmt(dc[s][k]) for s in SCEN] for k in dc["base"].keys()]))
    for co, name in [("oai", "OpenAI"), ("ant", "Anthropic")]:
        res = {s: company(co, s) for s in SCEN}
        rows = [[seg] + [fmt(res[s][seg]) for s in SCEN] for seg in SEGMENTS + ["TOTAL"]]
        parts.append(f"## {name} 2030 revenue by segment ($B)\n" + md_table(["Segment", "Bear", "Base", "Bull"], rows))
        sup = {s: supply(co, s) for s in SCEN}
        parts.append(f"## {name} supply-side check\n" + md_table(["Metric", "Bear", "Base", "Bull"], [[k] + [fmt(sup[s][k]) for s in SCEN] for k in sup["base"].keys()]))
        mo = {s: momentum(co, s) for s in SCEN}
        parts.append(f"## {name} momentum path ($B)\n" + md_table(["Line", "Bear", "Base", "Bull"], [[k] + [fmt(mo[s][k]) for s in SCEN] for k in mo["base"].keys()]))
        parts.append(f"## {name} bridge 2026E -> 2030 base ($B)\n" + md_table(["Segment", "2026E", "2030 base", "Multiple", "CAGR"], bridge(co)))
        parts.append(f"## {name} reconciliation to v3 (Base)\n" + md_table(["Line", "Model base", "v3", "Diff"], reconciliation(co)))
        for tgt in (280, 394):
            parts.append(f"## {name}: what ${tgt}B in 2030 implies\n" + md_table(["Metric", "Value"], [[k, v] for k, v in what_you_need(co, tgt).items()]))
    for title, tbl in sensitivities().items():
        parts.append(f"## Sensitivity: {title}\n" + tbl)
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# CALIBRATION HELPERS
# ---------------------------------------------------------------------------
def implied_inputs_for_targets(co: str, targets: Dict[str, float], s: str = "base") -> Dict[str, str]:
    """Given target 2030 revenue by segment ($B), return the input values that reproduce them with the
    global pools unchanged (keys: SEGMENTS labels or 'TOTAL' for a uniform enterprise-share scaling)."""
    out: Dict[str, str] = {}
    cur = company(co, s)
    if "TOTAL" in targets:
        non_ent = sum(cur[k] for k in SEGMENTS if k not in ENTERPRISE_SEGMENTS)
        ent = sum(cur[k] for k in ENTERPRISE_SEGMENTS)
        f = (targets["TOTAL"] - non_ent) / ent
        for key in (f"sh_dev_{co}", f"sh_pro_{co}", f"sh_gen_{co}", f"sh_auto_{co}"):
            out[key] = f"{g(key, s) * f:.4f}  (was {g(key, s):.4f}; x{f:.3f})"
    pools = {"Developers / coding agents": (seat_pool("dev", s), f"sh_dev_{co}"),
             "Professional seats": (seat_pool("pro", s), f"sh_pro_{co}"),
             "General KW seats": (seat_pool("gen", s), f"sh_gen_{co}"),
             "Machine / agent API": (machine_pool(s), f"sh_auto_{co}")}
    for seg, tgt in targets.items():
        if seg in pools:
            pool, key = pools[seg]
            out[key] = f"{tgt / pool:.4f}  (was {g(key, s):.4f}; pool {pool:,.0f})"
        elif seg == "Consumer subscriptions":
            conv = tgt * 1000 / (g(f"{co}_mau", s) * g(f"{co}_arpu", s) * 12)
            out[f"{co}_conv"] = f"{conv:.4f}  (was {g(f'{co}_conv', s):.4f}; MAU/ARPU held)"
        elif seg == "Consumer ads" and co == "oai":
            out["oai_ad_arpu"] = f"{tgt * 1000 / (g('oai_mau', s) * (1 - g('oai_conv', s))):.2f}  (free MAU held)"
        elif seg == "Commerce / agentic transactions" and co == "oai":
            out["oai_gmv"] = f"{tgt / g('oai_take', s):.1f}  (take rate held)"
        elif seg == "Other":
            out[f"{co}_other"] = f"{tgt:.2f}"
    return out


def implied_supply_inputs(gw: float, inf_share: float, rev: float, util: float = None, s: str = "base") -> Dict[str, str]:
    util = g("util", s) if util is None else util
    y = rev / (gw * inf_share)
    tp = y / util
    return {"yield per inference GW-year": f"{y:.2f} $B", "revenue per total GW-year": f"{y * inf_share:.2f} $B",
            "tokens x price (q x $/M) at util": f"{tp:.2f} at util {util:.0%}",
            "price if tokens/GW = memo": f"{tp / g('tok_per_gw', s):.2f} $/M at {g('tok_per_gw', s):.0f}q"}


if __name__ == "__main__":
    print(report())
