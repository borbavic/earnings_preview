"""
Bottom-up 2030 revenue framework for OpenAI and Anthropic.

Single source of truth for the assumptions used in the markdown framework
(docs/framework_receita_2030.md) and in the Excel model (build_xlsx.py).

Four lenses that must reconcile:
  1. Demand side (bottom-up by segment)  -> users x penetration x spend x share
  2. Supply side (compute)               -> GW x inference share x utilisation x tokens/GW x $/M tokens
  3. Momentum (run-rate path)            -> 2026 exit run-rate x deceleration schedule
  4. Wallet / base-rate checks           -> share of labour cost, software spend, ad market

Units: money in USD billions unless stated; people in millions; tokens in quadrillions (1e15).
Scenarios: bear / base / bull. Anchors are 2026 observed data points (sources in the docs).

Run:  python revenue_2030_model.py   -> prints all tables as markdown
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

SCEN = ["bear", "base", "bull"]
YEARS_2026_TO_2030 = 4.33  # Aug-2026 run-rate to Dec-2030


@dataclass
class A:
    """One assumption line: bear/base/bull values + unit + anchor text."""
    key: str
    label: str
    bear: float
    base: float
    bull: float
    unit: str
    anchor: str
    group: str = ""

    def v(self, s: str) -> float:
        return getattr(self, s)


# ---------------------------------------------------------------------------
# ASSUMPTIONS (2030 unless stated). Anchors = 2026 observed data points.
# ---------------------------------------------------------------------------
ASSUMPTIONS: List[A] = [
    # ---- Global knowledge-worker pool (shared by both companies) ----
    A("kw_dev", "Developers / data-AI engineers (M)", 34, 38, 44, "M people",
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
    A("pen_dev", "Paid-AI penetration - developers", 0.68, 0.80, 0.90, "%",
      "2026: ~10-12M paid (GitHub Copilot 4.7M, Cursor, Claude Code, Codex) of ~30M = ~35-40%", "Penetration"),
    A("pen_pro", "Paid-AI penetration - professionals", 0.32, 0.45, 0.55, "%",
      "2026: ~35-40M paid seats globally (M365 Copilot 20M, ChatGPT biz 9M, Claude, Gemini) = ~4% of all KW, ~10% of pros", "Penetration"),
    A("pen_gen", "Paid-AI penetration - general KW", 0.14, 0.25, 0.38, "%",
      "seat-type products ($20-30/mo); Copilot bundling drives this", "Penetration"),
    # ---- Spend per PAID seat as % of salary (seat fee + usage/tokens) ----
    A("ratio_dev", "AI spend / salary - developers", 0.07, 0.13, 0.16, "%",
      "2026: Claude Code enterprise avg $150-250/mo = $1.8-3k/yr = 2-4% of global-blend salary; heavy agent users >$1k/mo", "Spend"),
    A("ratio_pro", "AI spend / salary - professionals", 0.015, 0.03, 0.045, "%",
      "2026: M365 Copilot $360/yr; ChatGPT Enterprise ~$600-900/yr incl. usage; Atlanta Fed avg AI spend/employee $2,068 (all AI)", "Spend"),
    A("ratio_gen", "AI spend / salary - general KW", 0.007, 0.012, 0.02, "%",
      "2026: Copilot $360/yr; ChatGPT Business $25-30/seat", "Spend"),
    # ---- Lab share of paid-seat spend (direct + model-layer share inside 3rd-party tools) ----
    A("sh_dev_ant", "Anthropic share - developer spend", 0.35, 0.42, 0.48, "%",
      "2026: Claude Code $8B ARR (May-26) + Claude inside Cursor/Copilot; Menlo Ventures: Anthropic ~54% of coding model spend (2025)", "Share"),
    A("sh_dev_oai", "OpenAI share - developer spend", 0.18, 0.25, 0.32, "%",
      "Codex 2M+ weekly users (Mar-26); GPT-5.x in Cursor/Copilot", "Share"),
    A("sh_pro_ant", "Anthropic share - professional seats", 0.13, 0.20, 0.24, "%",
      "Claude Enterprise/Team/Cowork + Bedrock/Vertex/Foundry; MSFT/Google own the seat bundles", "Share"),
    A("sh_pro_oai", "OpenAI share - professional seats", 0.25, 0.30, 0.35, "%",
      "2026: 7M enterprise seats, 9M paying business users, >1M business customers", "Share"),
    A("sh_gen_ant", "Anthropic share - general seats", 0.06, 0.08, 0.12, "%",
      "mostly model-layer share of Copilot-type bundles", "Share"),
    A("sh_gen_oai", "OpenAI share - general seats", 0.20, 0.25, 0.30, "%",
      "ChatGPT Business/Edu; Copilot uses OpenAI models (rev share)", "Share"),
    # ---- Machine / agent API pool (workloads not tied to a human seat) ----
    A("auto_pool", "Labour cost pool of AI-automatable digital tasks ($T)", 7, 8, 10, "$T",
      "global labour comp ~$58T (2025); knowledge-work comp $35-50T; ~15-20% is task-automatable (support, back-office, docs, content, SDR, IT ops)", "Machine"),
    A("auto_share", "Share of that pool automated by AI agents in 2030", 0.06, 0.10, 0.14, "%",
      "2026: customer-service and coding agents are the only scaled cases", "Machine"),
    A("auto_capture", "Vendor capture ($ AI spend per $ labour displaced)", 0.20, 0.25, 0.30, "%",
      "Claude Code $2-3k/yr vs $20-40k of dev output = ~10%; SaaS captures 10-30% of value", "Machine"),
    A("sh_auto_ant", "Anthropic share - machine API", 0.30, 0.38, 0.40, "%",
      "Menlo Ventures 2025: Anthropic ~32-40% of enterprise LLM API spend, OpenAI ~25%", "Machine"),
    A("sh_auto_oai", "OpenAI share - machine API", 0.20, 0.25, 0.28, "%",
      "API ~15-20% of OpenAI revenue (2026); 15B tokens/min (Mar-26)", "Machine"),
    # ---- Consumer: OpenAI ----
    A("oai_mau", "ChatGPT MAU 2030 (M)", 1500, 2000, 2500, "M people",
      "1B MAU (Jun-26), ~1B WAU (Jul-26); internet users ~5.6B->6B; Meta DAP 3.58B", "Consumer OAI"),
    A("oai_conv", "Paid conversion (subs / MAU)", 0.045, 0.06, 0.09, "%",
      ">50M consumer subs / ~1B = ~5% (Aug-26); India Go free promo dilutes", "Consumer OAI"),
    A("oai_arpu", "Paid ARPU ($/month, blended)", 15, 18, 24, "$/mo",
      "Go $8 (US)/Rs399 (India), Plus $20, Pro $200 (~0.5M subs); blended est. $25-30 in 2026, skewing down with EM mix", "Consumer OAI"),
    A("oai_ad_arpu", "Ads ARPU per FREE user ($/yr)", 15, 30, 55, "$/yr",
      "Meta ARPP 2025 $58 global (US&C ~$250+); Google Search ~$60-70/user; OpenAI plan $100B ads by 2030 = ~$50/free user; ads $1B run-rate <200 days after Feb-26 launch", "Consumer OAI"),
    A("oai_gmv", "Commerce GMV routed via ChatGPT ($B)", 100, 400, 1000, "$B",
      "Instant Checkout (Sep-25); global e-commerce ~$7T by 2030", "Consumer OAI"),
    A("oai_take", "Commerce take rate", 0.02, 0.025, 0.03, "%",
      "affiliate/checkout take rates 2-4%", "Consumer OAI"),
    # ---- Consumer: Anthropic ----
    A("ant_mau", "Claude consumer MAU 2030 (M)", 150, 250, 400, "M people",
      "2026 est. 30-140M (third-party, unreliable); consumer ~5-10% of revenue", "Consumer ANT"),
    A("ant_conv", "Paid conversion (subs / MAU)", 0.08, 0.10, 0.13, "%",
      "professional skew; Max tiers", "Consumer ANT"),
    A("ant_arpu", "Paid ARPU ($/month, blended)", 26, 32, 40, "$/mo",
      "Pro $20, Max $100/$200", "Consumer ANT"),
    # ---- Other ----
    A("oai_other", "OpenAI other (devices, licensing, gov, media) ($B)", 4, 10, 20, "$B",
      "io hardware, Sora, sovereign deals, MSFT rev share", "Other"),
    A("ant_other", "Anthropic other (gov/sovereign, licensing, reseller minimums) ($B)", 4, 8, 15, "$B",
      "defense/gov, Amazon/Alexa, Apple", "Other"),
    # ---- Supply side (compute) ----
    A("oai_gw", "OpenAI GW online (avg 2030)", 15, 22, 30, "GW",
      "1.9GW end-25; 30GW target by 2030; 8GW+ of 10GW Stargate secured; Oracle 4.5GW from 2027; Nvidia 10GW, AMD 6GW, Broadcom 10GW LOIs", "Supply"),
    A("ant_gw", "Anthropic GW online (avg 2030)", 10, 16, 22, "GW",
      "~5GW end-26, ~10GW 2027 (press); Google/Broadcom 3.5GW TPU from 2027; AWS up to 5GW Trainium; Australia 2.16GW (2027)", "Supply"),
    A("inf_share", "Inference share of GW", 0.55, 0.62, 0.72, "%",
      "2025-26 fleets ~40-50% training/research; shifts to inference as revenue scales", "Supply"),
    A("util", "Inference fleet utilisation", 0.60, 0.68, 0.78, "%",
      "peak/off-peak; batch jobs fill valleys", "Supply"),
    A("tok_per_gw", "Tokens per GW-year at 100% util (quadrillion)", 16, 20, 32, "1e15 tokens",
      "OpenAI 2026: ~15-20 quadrillion tok/yr on ~1.5-2GW inference => ~10 at actual util; Google 38 quadrillion/yr (3.2q/mo, May-26); GB200 frontier config 75-85q/GW (vendor claim), Rubin 2-4x GB300", "Supply"),
    A("price_tok", "Realised blended price ($/M tokens, 2030)", 1.2, 1.6, 2.6, "$/M",
      "2026 realised: OpenAI ~$2-2.5/M (subs incl.), Anthropic ~$5/M (API-heavy); list Opus $4/$20, GPT $2/$10; ~10x/yr deflation per unit capability offset by mix", "Supply"),
    # ---- Deck as presented (revenue per GW of INFERENCE capacity) ----
    A("deck_gw", "Deck: total GW per company (2030)", 25, 25, 25, "GW",
      "deck assumption; OpenAI targets 30GW by 2030, Anthropic ~10GW in 2027", "Deck"),
    A("deck_inf_share", "Deck: share of capacity allocated to inference", 0.50, 0.525, 0.55, "%",
      "deck assumption: 50-55% inference, rest training/research", "Deck"),
    A("deck_rgw_inf", "Deck: revenue per GW of inference ($B/yr)", 28, 30, 32, "$B",
      "deck assumption ($30B); realised today: OpenAI 2025 ~$20B, Anthropic 2026E ~$34B (see below)", "Deck"),
    A("oai_gw_2025", "OpenAI GW available end-2025 (realised anchor)", 1.9, 1.9, 1.9, "GW",
      "OpenAI: 0.2GW (2023) -> 1.9GW (2025)", "Deck"),
    A("oai_rr_2025", "OpenAI run-rate end-2025 ($B, realised anchor)", 20, 20, 20, "$B",
      ">$20B ARR (Nov-25)", "Deck"),
    A("ant_gw_2026", "Anthropic GW available end-2026 (realised anchor)", 5, 5, 5, "GW",
      "~5GW end-2026 (press)", "Deck"),
    A("inf_share_today", "Inference share of capacity today (for realised $/GW-inference)", 0.50, 0.525, 0.55, "%",
      "same 50-55% assumption applied to 2025-26 fleets", "Deck"),
    # ---- Momentum path (run-rate, $B) ----
    A("oai_rr26", "OpenAI exit-2026 run-rate ($B)", 46, 50, 55, "$B",
      ">$40B run-rate Aug-26 (+35% QTD)", "Momentum"),
    A("ant_rr26", "Anthropic exit-2026 run-rate ($B)", 80, 90, 100, "$B",
      "$65B run-rate end-Jul-26; $47B mid-May; $30B Apr; $14B Feb; $9B Dec-25", "Momentum"),
    A("oai_g27", "OpenAI growth 2027", 0.45, 0.75, 0.95, "%", "company plan implies ~60-80%/yr", "Momentum"),
    A("oai_g28", "OpenAI growth 2028", 0.30, 0.60, 0.75, "%", "", "Momentum"),
    A("oai_g29", "OpenAI growth 2029", 0.20, 0.45, 0.55, "%", "", "Momentum"),
    A("oai_g30", "OpenAI growth 2030", 0.12, 0.35, 0.40, "%", "", "Momentum"),
    A("ant_g27", "Anthropic growth 2027", 0.40, 0.70, 1.00, "%", "internal p50 May-27 run-rate $138B (third-party cite)", "Momentum"),
    A("ant_g28", "Anthropic growth 2028", 0.22, 0.45, 0.60, "%", "IPO case: $190-200B revenue 2028 (Reuters, Aug-26)", "Momentum"),
    A("ant_g29", "Anthropic growth 2029", 0.12, 0.30, 0.40, "%", "", "Momentum"),
    A("ant_g30", "Anthropic growth 2030", 0.06, 0.20, 0.30, "%", "", "Momentum"),
]

AS: Dict[str, A] = {a.key: a for a in ASSUMPTIONS}

# 2026 run-rate mix estimates ($B, Aug-2026) used for the 2026->2030 bridge. Our estimates.
MIX_2026 = {
    "oai": {"Developers / coding agents": 4.0, "Professional seats": 8.0, "General KW seats": 2.0,
            "Machine / agent API": 6.0, "Consumer subscriptions": 17.0, "Consumer ads": 1.0,
            "Commerce / agentic transactions": 0.5, "Other": 1.5},
    "ant": {"Developers / coding agents": 25.0, "Professional seats": 10.0, "General KW seats": 1.0,
            "Machine / agent API": 20.0, "Consumer subscriptions": 6.0, "Consumer ads": 0.0,
            "Commerce / agentic transactions": 0.0, "Other": 3.0},
}

SEGMENTS = ["Developers / coding agents", "Professional seats", "General KW seats", "Machine / agent API",
            "Consumer subscriptions", "Consumer ads", "Commerce / agentic transactions", "Other"]
ENTERPRISE_SEGMENTS = SEGMENTS[:4]


def g(key: str, s: str) -> float:
    return AS[key].v(s)


# ---------------------------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------------------------
def spend_per_seat(tier: str, s: str) -> float:
    """$ per paid seat-year."""
    return g(f"sal_{tier}", s) * g(f"ratio_{tier}", s) * 1000.0


def seat_pool(tier: str, s: str) -> float:
    """Global paid-seat AI spend pool for a tier ($B). M people * % * $k/yr * % = $B."""
    return g(f"kw_{tier}", s) * g(f"pen_{tier}", s) * g(f"sal_{tier}", s) * g(f"ratio_{tier}", s)


def machine_pool(s: str) -> float:
    """Global machine/agent API pool ($B). $T * % * % * 1000."""
    return g("auto_pool", s) * g("auto_share", s) * g("auto_capture", s) * 1000.0


def enterprise_pool(s: str) -> float:
    return sum(seat_pool(t, s) for t in ("dev", "pro", "gen")) + machine_pool(s)


def company(co: str, s: str) -> Dict[str, float]:
    """Segment revenue ($B) for co in {'oai','ant'} and scenario s."""
    r: Dict[str, float] = {}
    r["Developers / coding agents"] = seat_pool("dev", s) * g(f"sh_dev_{co}", s)
    r["Professional seats"] = seat_pool("pro", s) * g(f"sh_pro_{co}", s)
    r["General KW seats"] = seat_pool("gen", s) * g(f"sh_gen_{co}", s)
    r["Machine / agent API"] = machine_pool(s) * g(f"sh_auto_{co}", s)
    mau = g(f"{co}_mau", s)
    conv = g(f"{co}_conv", s)
    r["Consumer subscriptions"] = mau * conv * g(f"{co}_arpu", s) * 12 / 1000.0
    if co == "oai":
        r["Consumer ads"] = mau * (1 - conv) * g("oai_ad_arpu", s) / 1000.0
        r["Commerce / agentic transactions"] = g("oai_gmv", s) * g("oai_take", s)
    else:
        r["Consumer ads"] = 0.0
        r["Commerce / agentic transactions"] = 0.0
    r["Other"] = g(f"{co}_other", s)
    r["TOTAL"] = sum(r[k] for k in SEGMENTS)
    return r


def rev_per_gw_inf(s: str) -> float:
    """$B revenue per GW of INFERENCE capacity: tokens/GW (1e15) x $/M x utilisation."""
    return g("tok_per_gw", s) * g("price_tok", s) * g("util", s)


def deck_check(s: str) -> Dict[str, float]:
    """The deck's arithmetic: total GW x inference share x $/GW-inference, and how it compares."""
    rev = g("deck_gw", s) * g("deck_inf_share", s) * g("deck_rgw_inf", s)
    oai_real = g("oai_rr_2025", s) / (g("oai_gw_2025", s) * g("inf_share_today", s))
    ant_real = g("ant_rr26", s) / (g("ant_gw_2026", s) * g("inf_share_today", s))
    return {
        "Deck revenue = GW x inf share x $/GW-inf ($B)": rev,
        "Deck implied $/GW of TOTAL capacity ($B)": g("deck_inf_share", s) * g("deck_rgw_inf", s),
        "Model $/GW-inference 2030 ($B)": rev_per_gw_inf(s),
        "Deck $/GW-inf vs model": g("deck_rgw_inf", s) / rev_per_gw_inf(s),
        "Realised OpenAI 2025 $/GW-inf ($B)": oai_real,
        "Realised Anthropic 2026E $/GW-inf ($B)": ant_real,
        "Deck $/GW-inf vs OpenAI 2025": g("deck_rgw_inf", s) / oai_real,
        "Deck $/GW-inf vs Anthropic 2026E": g("deck_rgw_inf", s) / ant_real,
    }


def rev_per_gw_total(s: str) -> float:
    """$B revenue per GW of TOTAL capacity: 1e15 tokens * $/1e6 = $1e9."""
    return g("tok_per_gw", s) * g("price_tok", s) * g("util", s) * g("inf_share", s)


def supply(co: str, s: str) -> Dict[str, float]:
    gw = g(f"{co}_gw", s)
    per_gw_inf = g("tok_per_gw", s) * g("price_tok", s) * g("util", s)
    per_gw = rev_per_gw_total(s)
    demand = company(co, s)["TOTAL"]
    return {
        "GW online (avg 2030)": gw,
        "Rev / GW inference ($B)": per_gw_inf,
        "Rev / GW total ($B)": per_gw,
        "Supply-side revenue capacity ($B)": gw * per_gw,
        "Demand-side revenue ($B)": demand,
        "GW needed for demand at this $/GW": demand / per_gw,
        "$/GW needed for demand at this GW": demand / gw,
        "$/GW-inference needed at this GW and inf share": demand / (gw * g("inf_share", s)),
    }


def momentum(co: str, s: str) -> Dict[str, float]:
    rr = g(f"{co}_rr26", s)
    out = {"Exit-2026 run-rate": rr}
    for y in (27, 28, 29, 30):
        rr = rr * (1 + g(f"{co}_g{y}", s))
        out[f"Exit-20{y} run-rate"] = rr
    return out


def bridge(co: str, s: str = "base") -> List[List[str]]:
    rows = []
    r30 = company(co, s)
    tot26 = sum(MIX_2026[co].values())
    for seg in SEGMENTS:
        v26 = MIX_2026[co][seg]
        v30 = r30[seg]
        mult = v30 / v26 if v26 else float("nan")
        cagr = mult ** (1 / YEARS_2026_TO_2030) - 1 if v26 else float("nan")
        rows.append([seg, fmt(v26), fmt(v30), f"{mult:.1f}x" if v26 else "n/a", f"{cagr*100:.0f}%" if v26 else "n/a"])
    mult = r30["TOTAL"] / tot26
    rows.append(["TOTAL", fmt(tot26), fmt(r30["TOTAL"]), f"{mult:.1f}x", f"{(mult ** (1 / YEARS_2026_TO_2030) - 1)*100:.0f}%"])
    return rows


def what_you_need(co: str, target: float, s: str = "base") -> Dict[str, str]:
    """Implied metrics if 2030 revenue = target ($B), holding base-case structure."""
    r = company(co, s)
    non_ent = r["TOTAL"] - sum(r[k] for k in ENTERPRISE_SEGMENTS)
    ent = sum(r[k] for k in ENTERPRISE_SEGMENTS)
    uplift = (target - non_ent) / ent
    gw = g(f"{co}_gw", s)
    out = {}
    out["Implied $/GW total at base GW"] = f"${target/gw:.1f}B/GW ({gw:.0f} GW)"
    out["Implied $/GW-inference at base GW and base inference share"] = f"${target/(gw*g('inf_share', s)):.1f}B per inference GW ({gw:.0f} GW x {g('inf_share', s):.0%})"
    out["Implied GW at deck economics"] = f"{target/(g('deck_rgw_inf', s)*g('deck_inf_share', s)):.1f} GW (${g('deck_rgw_inf', s):.0f}B/GW-inf x {g('deck_inf_share', s):.1%})"
    out["Implied GW at base $/GW"] = f"{target/rev_per_gw_total(s):.1f} GW (${rev_per_gw_total(s):.1f}B/GW total)"
    out["Required uplift on enterprise engines vs base"] = f"{uplift:.2f}x"
    # single-driver equivalents (each alone, others at base)
    dev_ratio = g("ratio_dev", s) * (1 + (uplift - 1) * ent / r["Developers / coding agents"])
    out["...if only developer spend/salary moves"] = f"{dev_ratio*100:.0f}% of salary (${g('sal_dev', s)*dev_ratio:.1f}k/dev/yr) vs base {g('ratio_dev', s)*100:.0f}%"
    auto_share = g("auto_share", s) * (1 + (uplift - 1) * ent / r["Machine / agent API"])
    out["...if only machine-API automation share moves"] = f"{auto_share*100:.0f}% of pool vs base {g('auto_share', s)*100:.0f}%"
    pro_pen = g("pen_pro", s) * (1 + (uplift - 1) * ent / r["Professional seats"])
    out["...if only professional-seat penetration moves"] = f"{min(pro_pen,9.99)*100:.0f}% vs base {g('pen_pro', s)*100:.0f}%" + (" (impossible >100%)" if pro_pen > 1 else "")
    out["Target as % of global enterprise AI pool (base)"] = f"{target/enterprise_pool(s)*100:.0f}% of ${enterprise_pool(s):,.0f}B"
    out["Target as % of global labour comp (~$65T 2030)"] = f"{target/65000*100:.2f}%"
    out["Target as % of global software spend (~$2.4T 2030)"] = f"{target/2400*100:.0f}%"
    return out


# ---------------------------------------------------------------------------
# REPORTING
# ---------------------------------------------------------------------------
def fmt(x: float, unit: str = "") -> str:
    if unit == "%":
        return f"{x*100:.1f}%"
    if abs(x) >= 100:
        return f"{x:,.0f}"
    if abs(x) >= 10:
        return f"{x:,.1f}"
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
    dsh = g("deck_inf_share", s)
    out[f"Revenue ($B) = total GW x inference share ({dsh:.1%}) x $/GW-inference"] = grid(
        [10, 15, 20, 25, 30], [15, 20, 25, 30, 35, 40], lambda gw, pg: gw * dsh * pg,
        lambda r: f"{r} GW", lambda c: f"${c}B/GW-inf", lambda v: f"{v:,.0f}")
    dgw = g("deck_gw", s)
    out[f"Revenue ($B) at {dgw:.0f} GW = inference share x $/GW-inference"] = grid(
        [0.45, 0.50, 0.55, 0.60, 0.65], [15, 20, 25, 30, 35, 40], lambda sh, pg: dgw * sh * pg,
        lambda r: f"{r:.0%} inference", lambda c: f"${c}B/GW-inf", lambda v: f"{v:,.0f}")
    ku = g("util", s)
    out[f"$/GW-inference = tokens/GW-yr x realised price x utilisation ({ku:.0%})"] = grid(
        [12, 16, 20, 24, 28, 32], [0.8, 1.2, 1.6, 2.0, 2.4, 3.0], lambda t, p: t * p * ku,
        lambda r: f"{r}q tok/GW", lambda c: f"${c}/M", lambda v: f"{v:,.1f}")
    out["OpenAI ads revenue ($B) = free MAU x ad ARPU"] = grid(
        [1400, 1900, 2300], [15, 30, 45, 60, 80], lambda m, a: m * a / 1000,
        lambda r: f"{r/1000:.1f}B free", lambda c: f"${c}/yr", lambda v: f"{v:,.0f}")
    out["OpenAI consumer subs ($B) = MAU x conversion x $18/mo"] = grid(
        [1500, 2000, 2500], [0.04, 0.06, 0.08, 0.10], lambda m, c: m * c * g("oai_arpu", s) * 12 / 1000,
        lambda r: f"{r/1000:.1f}B MAU", lambda c: f"{c:.0%} paid", lambda v: f"{v:,.0f}")
    devs = g("kw_dev", s) * g("pen_dev", s)
    out[f"Anthropic developer engine ($B) = {devs:.0f}M paid devs x spend x share"] = grid(
        [4, 6, 9, 12, 15], [0.30, 0.36, 0.42, 0.48], lambda sp, sh: devs * sp * sh,
        lambda r: f"${r}k/dev/yr", lambda c: f"{c:.0%} share", lambda v: f"{v:,.0f}")
    out[f"Professional-seat global pool ($B) = {g('kw_pro', s):.0f}M x penetration x spend"] = grid(
        [0.30, 0.45, 0.60], [900, 1800, 2700, 3600], lambda pen, sp: g("kw_pro", s) * pen * sp / 1000,
        lambda r: f"{r:.0%} penetration", lambda c: f"${c}/seat", lambda v: f"{v:,.0f}")
    out["Machine/agent API global pool ($B) = $8T x automated share x capture"] = grid(
        [0.05, 0.10, 0.15, 0.20], [0.15, 0.20, 0.25, 0.30, 0.35], lambda a, c: 8000 * a * c,
        lambda r: f"{r:.0%} automated", lambda c: f"{c:.0%} capture", lambda v: f"{v:,.0f}")
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
    dc = {s: deck_check(s) for s in SCEN}
    parts.append("## Deck check: revenue = total GW x inference share x $/GW-inference\n" + md_table(
        ["Metric", "Bear", "Base", "Bull"], [[k] + [fmt(dc[s][k]) for s in SCEN] for k in dc["base"].keys()]))
    for co, name in [("oai", "OpenAI"), ("ant", "Anthropic")]:
        res = {s: company(co, s) for s in SCEN}
        rows = [[seg] + [fmt(res[s][seg]) for s in SCEN] for seg in SEGMENTS + ["TOTAL"]]
        parts.append(f"## {name} 2030 revenue by segment ($B)\n" + md_table(["Segment", "Bear", "Base", "Bull"], rows))
        sup = {s: supply(co, s) for s in SCEN}
        rows = [[k] + [fmt(sup[s][k]) for s in SCEN] for k in sup["base"].keys()]
        parts.append(f"## {name} supply-side check\n" + md_table(["Metric", "Bear", "Base", "Bull"], rows))
        mom = {s: momentum(co, s) for s in SCEN}
        rows = [[k] + [fmt(mom[s][k]) for s in SCEN] for k in mom["base"].keys()]
        parts.append(f"## {name} momentum path (run-rate, $B)\n" + md_table(["Year", "Bear", "Base", "Bull"], rows))
        parts.append(f"## {name} bridge 2026 run-rate -> 2030 base ($B)\n" + md_table(
            ["Segment", "2026 RR (est.)", "2030 base", "Multiple", "CAGR"], bridge(co)))
        for tgt in (350, 400):
            w = what_you_need(co, tgt)
            parts.append(f"## {name}: what ${tgt}B in 2030 implies\n" + md_table(["Metric", "Value"], [[k, v] for k, v in w.items()]))
    for title, tbl in sensitivities().items():
        parts.append(f"## Sensitivity: {title}\n" + tbl)
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# CALIBRATION HELPER (align the Base column to an external model, e.g. the v3 OpenAI/Anthropic model)
# ---------------------------------------------------------------------------
def implied_inputs_for_targets(co: str, targets: Dict[str, float], s: str = "base") -> Dict[str, str]:
    """Given target 2030 revenue by segment ($B) for company co, return the Base input values that
    reproduce them with the global pools unchanged. Segments not in `targets` are left as they are.
    Keys of `targets` are SEGMENTS labels or 'TOTAL' (TOTAL scales the four enterprise shares uniformly)."""
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
            # hold MAU and ARPU, solve conversion
            conv = tgt * 1000 / (g(f"{co}_mau", s) * g(f"{co}_arpu", s) * 12)
            out[f"{co}_conv"] = f"{conv:.4f}  (was {g(f'{co}_conv', s):.4f}; MAU/ARPU held)"
        elif seg == "Consumer ads" and co == "oai":
            arpu = tgt * 1000 / (g("oai_mau", s) * (1 - g("oai_conv", s)))
            out["oai_ad_arpu"] = f"{arpu:.2f}  (was {g('oai_ad_arpu', s):.2f}; free MAU held)"
        elif seg == "Commerce / agentic transactions" and co == "oai":
            out["oai_gmv"] = f"{tgt / g('oai_take', s):.1f}  (was {g('oai_gmv', s):.1f}; take rate held)"
        elif seg == "Other":
            out[f"{co}_other"] = f"{tgt:.2f}  (was {g(f'{co}_other', s):.2f})"
    return out


def implied_supply_inputs(gw: float, inf_share: float, rev: float, util: float = None, s: str = "base") -> Dict[str, str]:
    """Given an external model's GW, inference share and revenue, return the $/GW-inference and the
    tokens/GW x price combination (at Base utilisation unless given) that reproduce it."""
    util = g("util", s) if util is None else util
    rgw_inf = rev / (gw * inf_share)
    tok_price = rgw_inf / util  # tokens/GW (1e15) x $/M
    return {"rev_per_gw_inference": f"{rgw_inf:.2f} $B/GW-inf",
            "rev_per_gw_total": f"{rgw_inf * inf_share:.2f} $B/GW",
            "tokens_x_price (q x $/M) at util": f"{tok_price:.2f} at util {util:.0%}",
            "price if tokens/GW = base": f"{tok_price / g('tok_per_gw', s):.2f} $/M at {g('tok_per_gw', s):.0f}q",
            "tokens/GW if price = base": f"{tok_price / g('price_tok', s):.1f}q at ${g('price_tok', s):.2f}/M"}


if __name__ == "__main__":
    print(report())
