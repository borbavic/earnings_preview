"""
Builds AI_labs_revenue_2030_bottomup.xlsx with live formulas from the assumptions in
revenue_2030_model.py (Base = MBI vBTG v3 by construction). Run, then recalculate with
LibreOffice (recalc.py) and cross-check with verify_xlsx.py.

Sheets: Summary | Inputs | OpenAI | Anthropic | Deck_check | Sensitivity | v3_series | Sources
Convention: blue = hardcoded input, black = formula, green = link to another sheet,
yellow fill = cells the user is meant to edit (Custom scenario column, targets).
"""
from __future__ import annotations

import os
from typing import Callable, Dict, List

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from revenue_2030_model import (ASSUMPTIONS, MIX_2026, SEGMENTS, V3, YEARS_2026_TO_2030,
                                solve_machine_share)

V3_SERIES_KEYS = [("rev", "calendar revenue ($B)"), ("exit_arr", "exit run-rate ARR ($B)"), ("gw_ye", "year-end capacity (GW)"),
                  ("gw_avg_total", "average in-year total capacity (GW)"), ("gw_avg_inf", "average in-year inference capacity (GW)"),
                  ("inf_share_ye", "inference share, year-end"), ("inf_share_avg", "inference share of average capacity"),
                  ("yield_inf", "revenue per average inference GW-year ($B)"), ("inf_cost_per_gw", "inference compute cost per GW-year ($B)"),
                  ("gross_margin", "gross margin"), ("ebit", "EBIT ($B)"), ("total_compute", "total compute cost ($B)")]

FONT = "Arial"
F_BLUE = Font(name=FONT, color="0000FF")
F_BLACK = Font(name=FONT, color="000000")
F_GREEN = Font(name=FONT, color="008000")
F_BOLD = Font(name=FONT, bold=True)
F_TITLE = Font(name=FONT, bold=True, size=14)
F_HEAD = Font(name=FONT, bold=True, color="FFFFFF")
F_NOTE = Font(name=FONT, italic=True, color="595959", size=9)
FILL_HEAD = PatternFill("solid", fgColor="1F3864")
FILL_GROUP = PatternFill("solid", fgColor="D9E1F2")
FILL_YELLOW = PatternFill("solid", fgColor="FFFF00")
FILL_TOTAL = PatternFill("solid", fgColor="E2EFDA")
FILL_OK = PatternFill("solid", fgColor="C6EFCE")

UNIT_FMT = {
    "%": "0.00%", "M people": "#,##0", "$k/yr": "#,##0", "$B": "#,##0.000;(#,##0.000);-", "$T": "0.0",
    "$/mo": "$#,##0.0", "$/yr": "$#,##0", "GW": "0.000", "1e15 tokens": "0.0",
}
B = "#,##0.0;(#,##0.0);-"
B3 = "#,##0.000;(#,##0.000);-"
P = "0.0%"
CO_TO_IN = {"C": "D", "D": "E", "E": "F", "F": "G"}   # company-sheet scenario column -> Inputs column

ROW: Dict[str, int] = {}


def style_header(ws, row: int, cols: int):
    for c in range(1, cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = F_HEAD
        cell.fill = FILL_HEAD
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def set_widths(ws, widths: List[float]):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def inp(key: str, co_col: str) -> str:
    return f"Inputs!${CO_TO_IN[co_col]}${ROW[key]}"


def inp_base(key: str) -> str:
    return f"Inputs!$E${ROW[key]}"


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
def build_inputs(wb: Workbook):
    ws = wb.active
    ws.title = "Inputs"
    ws["A1"] = "Inputs - 2030 assumptions (bear / base / bull) + Custom scenario. BASE = MBI vBTG v3 models."
    ws["A1"].font = F_TITLE
    ws["A2"] = ("Legend: blue = hardcoded input; black = formula (the two SOLVED machine-API shares); yellow Custom column (G) is the one to edit "
                "- it defaults to Base. The 'v3 reference' group holds the v3 cells the Base is tied to (used by the reconciliation on Summary).")
    ws["A2"].font = F_NOTE
    headers = ["Key", "Assumption (2030 unless stated)", "Unit", "Bear", "Base", "Bull", "Custom (edit)", "Anchor / source (v3 cell where applicable)"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=4, column=i, value=h)
    style_header(ws, 4, len(headers))
    r = 5
    group = None
    for a in ASSUMPTIONS:
        if a.group != group:
            group = a.group
            ws.cell(row=r, column=1, value=group).font = F_BOLD
            for c in range(1, 9):
                ws.cell(row=r, column=c).fill = FILL_GROUP
            r += 1
        ws.cell(row=r, column=1, value=a.key).font = F_NOTE
        ws.cell(row=r, column=2, value=a.label).font = F_BLACK
        ws.cell(row=r, column=3, value=a.unit).font = F_BLACK
        fmt = UNIT_FMT.get(a.unit, "#,##0.00")
        base_val = solve_machine_share(a.key.split("_")[-1]) if a.solved else a.base
        for col, val in zip(("D", "E", "F", "G"), (a.bear, base_val, a.bull, base_val)):
            cell = ws[f"{col}{r}"]
            cell.value = val   # solved Base cells are overwritten with a formula in patch_solved_inputs()
            cell.font = F_BLUE
            cell.number_format = fmt
        ws[f"G{r}"].fill = FILL_YELLOW
        ws.cell(row=r, column=8, value=a.anchor).font = F_NOTE
        ROW[a.key] = r
        r += 1
    ws.freeze_panes = "D5"
    set_widths(ws, [16, 60, 11, 11, 12, 11, 13, 120])
    return ws


def patch_solved_inputs(wb: Workbook, R: Dict[str, Dict[str, int]]):
    """Base machine-API share = (v3 revenue - other Base segments) / machine pool, as a live formula."""
    ws = wb["Inputs"]
    for co, sheet in (("oai", "OpenAI"), ("ant", "Anthropic")):
        rr = R[sheet]
        others = "+".join(f"{sheet}!$D${rr[k]}" for k in ("seg_dev", "seg_pro", "seg_gen", "seg_subs", "seg_ads", "seg_comm", "seg_other"))
        cell = ws[f"E{ROW['sh_auto_' + co]}"]
        cell.value = f"=IF({sheet}!$D${rr['pool_mach']}=0,0,({inp_base('v3_' + co + '_rev_2030')}-({others}))/{sheet}!$D${rr['pool_mach']})"
        cell.font = F_BLACK
        cell.number_format = "0.00%"


# ---------------------------------------------------------------------------
# v3 yearly series
# ---------------------------------------------------------------------------
def build_v3_series(wb: Workbook) -> Dict[str, Dict[str, int]]:
    ws = wb.create_sheet("v3_series")
    ws["A1"] = "v3 yearly series 2026E-2030E (Model tab of the MBI vBTG v3 files). The Base year-by-year supply rows on OpenAI / Anthropic read these."
    ws["A1"].font = F_TITLE
    for i, h in enumerate(["Line", "2026E", "2027E", "2028E", "2029E", "2030E", "v3 cells"], start=1):
        ws.cell(row=3, column=i, value=h)
    style_header(ws, 3, 7)
    r = 4
    V3S: Dict[str, Dict[str, int]] = {}
    for co, name in (("oai", "OpenAI"), ("ant", "Anthropic")):
        V3S[co] = {}
        ws.cell(row=r, column=1, value=f"{name} - {V3[co]['_file']}").font = F_BOLD
        for c in range(1, 8):
            ws.cell(row=r, column=c).fill = FILL_GROUP
        r += 1
        for key, label in V3_SERIES_KEYS:
            ser = V3[co][f"series_{key}"]
            ws.cell(row=r, column=1, value=f"{name}: {label}")
            for j, v in enumerate(ser["values"], start=2):
                cell = ws.cell(row=r, column=j, value=v)
                cell.font = F_BLUE
                cell.number_format = "0.00%" if ("share" in key or "margin" in key) else ("0.000" if "gw" in key else B3)
            ws.cell(row=r, column=7, value=ser["cells"]).font = F_NOTE
            V3S[co][key] = r
            r += 1
        r += 1
    set_widths(ws, [62, 12, 12, 12, 12, 12, 26])
    return V3S


# ---------------------------------------------------------------------------
# Company sheets
# ---------------------------------------------------------------------------
def build_company(wb: Workbook, co: str, name: str, V3S: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    ws = wb.create_sheet(name)
    R: Dict[str, int] = {}
    ws["A1"] = f"{name} - 2030 revenue, bottom-up ($B unless stated). Base column = MBI vBTG v3."
    ws["A1"].font = F_TITLE
    ws["A2"] = "Green = link to Inputs; black = formula; blue = hardcoded (2026E mix split, targets, constants)."
    ws["A2"].font = F_NOTE
    headers = ["Line", "Unit", "Bear", "Base", "Bull", "Custom", "Formula / note"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=4, column=i, value=h)
    style_header(ws, 4, len(headers))
    r = 5

    def group(title: str):
        nonlocal r
        ws.cell(row=r, column=1, value=title).font = F_BOLD
        for c in range(1, 8):
            ws.cell(row=r, column=c).fill = FILL_GROUP
        r += 1

    def line(key: str, label: str, unit: str, fn: Callable[[str], str], fmt: str, note: str = "",
             font: Font = F_BLACK, total: bool = False):
        nonlocal r
        ws.cell(row=r, column=1, value=label).font = F_BOLD if total else F_BLACK
        ws.cell(row=r, column=2, value=unit).font = F_BLACK
        for col in ("C", "D", "E", "F"):
            cell = ws[f"{col}{r}"]
            cell.value = fn(col)
            cell.font = Font(name=FONT, bold=True, color=font.color) if total else font
            cell.number_format = fmt
            if total:
                cell.fill = FILL_TOTAL
        ws.cell(row=r, column=7, value=note).font = F_NOTE
        R[key] = r
        r += 1

    group("Global pools (all vendors) - shared with the other company")
    line("sps_dev", "Spend per paid seat - developers", "$/yr", lambda c: f"={inp('sal_dev', c)}*{inp('ratio_dev', c)}*1000", "$#,##0", "salary x AI spend ratio", F_GREEN)
    line("sps_pro", "Spend per paid seat - professionals", "$/yr", lambda c: f"={inp('sal_pro', c)}*{inp('ratio_pro', c)}*1000", "$#,##0", "", F_GREEN)
    line("sps_gen", "Spend per paid seat - general KW", "$/yr", lambda c: f"={inp('sal_gen', c)}*{inp('ratio_gen', c)}*1000", "$#,##0", "", F_GREEN)
    line("seats_dev", "Paid developer seats", "M", lambda c: f"={inp('kw_dev', c)}*{inp('pen_dev', c)}", "#,##0.0", "workers x penetration", F_GREEN)
    line("seats_pro", "Paid professional seats", "M", lambda c: f"={inp('kw_pro', c)}*{inp('pen_pro', c)}", "#,##0.0", "", F_GREEN)
    line("seats_gen", "Paid general KW seats", "M", lambda c: f"={inp('kw_gen', c)}*{inp('pen_gen', c)}", "#,##0.0", "", F_GREEN)
    line("pool_dev", "Developer AI spend pool", "$B", lambda c: f"={c}{R['seats_dev']}*{c}{R['sps_dev']}/1000", B, "seats (M) x $/seat / 1000")
    line("pool_pro", "Professional AI spend pool", "$B", lambda c: f"={c}{R['seats_pro']}*{c}{R['sps_pro']}/1000", B, "")
    line("pool_gen", "General KW AI spend pool", "$B", lambda c: f"={c}{R['seats_gen']}*{c}{R['sps_gen']}/1000", B, "")
    line("pool_mach", "Machine / agent API pool", "$B", lambda c: f"={inp('auto_pool', c)}*{inp('auto_share', c)}*{inp('auto_capture', c)}*1000", B, "labour pool ($T) x automated share x vendor capture", F_GREEN)
    line("pool_tot", "Total enterprise AI pool (all vendors)", "$B", lambda c: f"=SUM({c}{R['pool_dev']}:{c}{R['pool_mach']})", B, "", total=True)
    r += 1

    group(f"{name} revenue 2030 by segment")
    line("seg_dev", SEGMENTS[0], "$B", lambda c: f"={c}{R['pool_dev']}*{inp('sh_dev_' + co, c)}", B, "pool x company share", F_GREEN)
    line("seg_pro", SEGMENTS[1], "$B", lambda c: f"={c}{R['pool_pro']}*{inp('sh_pro_' + co, c)}", B, "", F_GREEN)
    line("seg_gen", SEGMENTS[2], "$B", lambda c: f"={c}{R['pool_gen']}*{inp('sh_gen_' + co, c)}", B, "", F_GREEN)
    line("seg_mach", SEGMENTS[3], "$B", lambda c: f"={c}{R['pool_mach']}*{inp('sh_auto_' + co, c)}", B, "Base share is SOLVED on Inputs so that the total equals v3", F_GREEN)
    line("seg_subs", SEGMENTS[4], "$B", lambda c: f"={inp(co + '_mau', c)}*{inp(co + '_conv', c)}*{inp(co + '_arpu', c)}*12/1000", B, "MAU x paid conversion x ARPU x 12", F_GREEN)
    if co == "oai":
        line("seg_ads", SEGMENTS[5], "$B", lambda c: f"={inp('oai_mau', c)}*(1-{inp('oai_conv', c)})*{inp('oai_ad_arpu', c)}/1000", B, "free MAU x ads ARPU", F_GREEN)
        line("seg_comm", SEGMENTS[6], "$B", lambda c: f"={inp('oai_gmv', c)}*{inp('oai_take', c)}", B, "GMV x take rate", F_GREEN)
    else:
        line("seg_ads", SEGMENTS[5], "$B", lambda c: "=0", B, "Anthropic: no ads (stated policy) - hardcoded 0", F_BLUE)
        line("seg_comm", SEGMENTS[6], "$B", lambda c: "=0", B, "not modelled - hardcoded 0", F_BLUE)
    line("seg_other", SEGMENTS[7], "$B", lambda c: f"={inp(co + '_other', c)}", B, "", F_GREEN)
    line("total", "TOTAL REVENUE 2030", "$B", lambda c: f"=SUM({c}{R['seg_dev']}:{c}{R['seg_other']})", B3, "Base = v3 calendar revenue 2030 by construction", total=True)
    line("ent", "Enterprise subtotal (4 engines)", "$B", lambda c: f"=SUM({c}{R['seg_dev']}:{c}{R['seg_mach']})", B, "")
    line("cons", "Consumer subtotal", "$B", lambda c: f"=SUM({c}{R['seg_subs']}:{c}{R['seg_comm']})", B, "")
    line("ent_pct", "Enterprise share of revenue", "%", lambda c: f"=IF({c}{R['total']}=0,0,{c}{R['ent']}/{c}{R['total']})", P, "")
    r += 1

    group("Supply-side check (compute) - v3 mechanics: revenue = average inference GW x yield per inference GW-year")
    line("gw", "Average in-year total capacity 2030", "GW", lambda c: f"={inp(co + '_gw_avg', c)}", "0.000", "", F_GREEN)
    line("sh", "Inference share of average capacity", "%", lambda c: f"={inp(co + '_inf_share_avg', c)}", "0.00%", "", F_GREEN)
    line("gw_inf", "Average inference capacity", "GW", lambda c: f"={c}{R['gw']}*{c}{R['sh']}", "0.000", "GW x share")
    line("yield", "Revenue per average inference GW-year (yield)", "$B/GW", lambda c: f"={inp(co + '_yield_inf', c)}", B3, "", F_GREEN)
    line("rgw_tot", "Revenue per average total GW-year", "$B/GW", lambda c: f"={c}{R['yield']}*{c}{R['sh']}", B3, "yield x inference share")
    line("sup_cap", "Supply-side revenue = inference GW x yield", "$B", lambda c: f"={c}{R['gw_inf']}*{c}{R['yield']}", B3, "", total=True)
    line("dem", "Demand-side revenue (bottom-up)", "$B", lambda c: f"={c}{R['total']}", B3, "")
    line("dem_sup", "Demand / supply", "x", lambda c: f"=IF({c}{R['sup_cap']}=0,0,{c}{R['dem']}/{c}{R['sup_cap']})", "0.000x", "Base = 1.000x")
    line("yield_need", "Yield needed for the bottom-up at this GW and share", "$B/GW", lambda c: f"=IF({c}{R['gw_inf']}=0,0,{c}{R['dem']}/{c}{R['gw_inf']})", B3, "")
    line("cost_gw", "Inference compute cost per GW-year", "$B/GW", lambda c: f"={inp(co + '_cost_inf_gw', c)}", B3, "", F_GREEN)
    line("cogs", "Cost of revenue = inference GW x cost + other CoR", "$B", lambda c: f"={c}{R['gw_inf']}*{c}{R['cost_gw']}+{inp(co + '_other_cor', c)}*{c}{R['sup_cap']}", B3, "other CoR % on Inputs (v3: 3%)", F_GREEN)
    line("gm", "Gross margin (on supply-side revenue)", "%", lambda c: f"=IF({c}{R['sup_cap']}=0,0,1-{c}{R['cogs']}/{c}{R['sup_cap']})", "0.00%", "Base = v3 gross margin 2030")
    line("price", "Memo: implied realised price at memo tokens/GW and utilisation", "$/M tok", lambda c: f"=IF({inp('tok_per_gw', c)}*{inp('util', c)}=0,0,{c}{R['yield']}/({inp('tok_per_gw', c)}*{inp('util', c)}))", "$0.00", "yield / (tokens per GW-yr x utilisation)", F_GREEN)
    r += 1

    group("Momentum path (exit run-rate; calendar revenue = average of consecutive exit run-rates, as in v3)")
    line("rr26", "Exit-2026 run-rate", "$B", lambda c: f"={inp(co + '_rr26', c)}", B3, "", F_GREEN)
    prev = "rr26"
    for y in (27, 28, 29, 30):
        key = f"rr{y}"
        line(key, f"Exit-20{y} run-rate", "$B", (lambda c, p=prev, yy=y: f"={c}{R[p]}*(1+{inp(co + '_g' + str(yy), c)})"), B3, f"x (1 + growth 20{y})", F_GREEN)
        line(f"cal{y}", f"Calendar revenue 20{y}", "$B", (lambda c, p=prev, k=key: f"=({c}{R[p]}+{c}{R[k]})/2"), B3, "average of opening and closing run-rate")
        prev = key
    line("bu_vs_mom", "Bottom-up 2030 / momentum calendar 2030", "x", lambda c: f"=IF({c}{R['cal30']}=0,0,{c}{R['total']}/{c}{R['cal30']})", "0.000x", "Base = 1.000x")
    r += 1

    # ---------------- Year-by-year evolution 2026E-2030E (replaces the 2026->2030 bridge) ----------------
    ws.cell(row=r, column=1, value="Year-by-year evolution of the main inputs, 2026E-2030E   |   scenario shown:").font = F_BOLD
    for c in range(1, 9):
        ws.cell(row=r, column=c).fill = FILL_GROUP
    sel = ws.cell(row=r, column=3, value="Base")
    sel.font = F_BLUE
    sel.fill = FILL_YELLOW
    dv = DataValidation(type="list", formula1='"Bear,Base,Bull,Custom"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(sel)
    ws.cell(row=r, column=4, value=f"=MATCH($C${r},$C$4:$F$4,0)").font = F_NOTE
    ws.cell(row=r, column=5, value="<- Bear / Base / Bull / Custom (dropdown)").font = F_NOTE
    R["y_sel"] = r
    SEL, M = f"$C${r}", f"$D${r}"
    r += 1
    ws.cell(row=r, column=1, value=("2026E = anchors on Inputs (group '2026E anchors'); 2030E = the selected scenario's column above; 2027-29 interpolated along the "
                                    "scenario's calendar-revenue path (levels geometric, rates linear). Enterprise shares carry a tie-out factor k so the yearly total "
                                    "equals the path (Base = v3). In Base the supply rows are the v3 yearly values (tab v3_series).")).font = F_NOTE
    r += 1
    for i, h in enumerate(["Line", "2026E", "2027E", "2028E", "2029E", "2030E", "CAGR 26-30 / delta", "Formula / note"], start=1):
        ws.cell(row=r, column=i, value=h)
    style_header(ws, r, 8)
    R["y_hdr"] = r
    r += 1
    YC = ["B", "C", "D", "E", "F"]

    def idx_sheet(key):   # 2030E = the selected scenario's column of a line above on this sheet
        return f"=INDEX($C${R[key]}:$F${R[key]},1,{M})"

    def idx_inp(key):     # 2030E = the selected scenario's column on Inputs
        return f"=INDEX(Inputs!$D${ROW[key]}:$G${ROW[key]},1,{M})"

    def a26(key):
        return f"=Inputs!$E${ROW[key]}"

    def geo(col, row):
        return f"=IF($B{row}=0,0,$B{row}*($F{row}/$B{row})^{col}${R['y_p']})"

    def lin(col, row):
        return f"=$B{row}+($F{row}-$B{row})*{col}${R['y_p']}"

    def override(fn, v3row):  # Base -> v3 yearly value, else interpolation
        return lambda col, row: f'=IF({SEL}="Base",v3_series!{col}{v3row},{fn(col, row)[1:]})'

    def ygroup(title):
        nonlocal r
        ws.cell(row=r, column=1, value=title).font = F_BOLD
        for c in range(1, 9):
            ws.cell(row=r, column=c).fill = FILL_GROUP
        r += 1

    def yline(key, label, fn, fmt, note="", fb=None, ff=None, growth="cagr", font=F_BLACK, total=False):
        nonlocal r
        row = r
        ws.cell(row=row, column=1, value=label).font = F_BOLD if total else F_BLACK
        for col in YC:
            cell = ws[f"{col}{row}"]
            if col == "B" and fb is not None:
                cell.value = fb
            elif col == "F" and ff is not None:
                cell.value = ff
            else:
                cell.value = fn(col, row) if fn is not None else None
            cell.font = Font(name=FONT, bold=True, color=font.color) if total else font
            cell.number_format = fmt
            if total:
                cell.fill = FILL_TOTAL
        if growth == "cagr":
            gc = ws[f"G{row}"]
            gc.value = f'=IF(OR($B{row}<=0,$F{row}<=0),"",($F{row}/$B{row})^(1/4)-1)'
            gc.number_format = P
        elif growth == "delta":
            gc = ws[f"G{row}"]
            gc.value = f"=$F{row}-$B{row}"
            gc.number_format = "+0.0%;-0.0%;0.0%"
        ws.cell(row=row, column=8, value=note).font = F_NOTE
        R[key] = row
        r += 1
        return row

    YR = {"C": "27", "D": "28", "E": "29"}
    yline("y_cal", "Calendar revenue path ($B)", lambda col, row: f"=INDEX($C${R['cal' + YR[col]]}:$F${R['cal' + YR[col]]},1,{M})", B3,
          "2026E = v3 calendar revenue (all scenarios); 2027-30 = momentum block of the selected scenario (Base = v3)",
          fb=f"=Inputs!$E${ROW['v3_' + co + '_rev_2026']}", ff=idx_sheet("cal30"), font=F_GREEN, total=True)
    yline("y_p", "Progress along the path (p)", lambda col, row: f"=IF(LN($F${R['y_cal']}/$B${R['y_cal']})=0,0,LN({col}${R['y_cal']}/$B${R['y_cal']})/LN($F${R['y_cal']}/$B${R['y_cal']}))",
          "0.000", "p = ln(rev_y / rev_26) / ln(rev_30 / rev_26): 0 in 2026E, 1 in 2030E", fb=0, ff=1, growth=None)
    pending_rev = []
    for t, lab in (("dev", "Developers"), ("pro", "Professionals"), ("gen", "General KW")):
        ygroup(f"{lab}: seats x spend = pool; x share x k = revenue")
        yline(f"y_seats_{t}", f"{lab}: paid seats, global (M)", geo, "#,##0.0", "anchor 2026E; 2030E = workers x penetration (scenario); geometric in between", fb=a26(f"a26_seats_{t}"), ff=idx_sheet(f"seats_{t}"), font=F_GREEN)
        yline(f"y_sps_{t}", f"{lab}: spend per paid seat ($/yr)", geo, "$#,##0", "anchor 2026E; 2030E = salary x AI spend ratio (scenario)", fb=a26(f"a26_sps_{t}"), ff=idx_sheet(f"sps_{t}"), font=F_GREEN)
        yline(f"y_pool_{t}", f"{lab}: global pool ($B)", lambda col, row, t=t: f"={col}{R['y_seats_' + t]}*{col}{R['y_sps_' + t]}/1000", B, "seats x spend / 1000")
        yline(f"y_sh_{t}", f"{lab}: company share (before tie-out)", lin, "0.0%", "anchor 2026E; 2030E = Inputs share (scenario); linear in between", fb=a26(f"a26_sh_{t}_{co}"), ff=idx_inp(f"sh_{t}_{co}"), growth="delta", font=F_GREEN)
        rr_ = yline(f"y_rev_{t}", f"{lab}: revenue ($B)", None, B, "pool x share x tie-out factor k")
        pending_rev.append((rr_, R[f"y_pool_{t}"], R[f"y_sh_{t}"]))
    ygroup("Machine / agent API")
    yline("y_pool_mach", "Machine API: global pool ($B)", geo, B, "anchor 2026E; 2030E = labour pool x automated share x capture (scenario)", fb=a26("a26_pool_mach"), ff=idx_sheet("pool_mach"), font=F_GREEN)
    yline("y_sh_auto", "Machine API: company share (before tie-out)", lin, "0.0%", "anchor 2026E; 2030E = Inputs share (Base: solved)", fb=a26(f"a26_sh_auto_{co}"), ff=idx_inp(f"sh_auto_{co}"), growth="delta", font=F_GREEN)
    rr_ = yline("y_rev_mach", "Machine API: revenue ($B)", None, B, "pool x share x tie-out factor k")
    pending_rev.append((rr_, R["y_pool_mach"], R["y_sh_auto"]))
    ygroup("Consumer")
    yline("y_mau", "Consumer: MAU (M)", geo, "#,##0", "anchor 2026E; 2030E = Inputs MAU (scenario)", fb=a26(f"a26_{co}_mau"), ff=idx_inp(f"{co}_mau"), font=F_GREEN)
    yline("y_conv", "Consumer: paid conversion", lin, "0.00%", "", fb=a26(f"a26_{co}_conv"), ff=idx_inp(f"{co}_conv"), growth="delta", font=F_GREEN)
    yline("y_arpu", "Consumer: paid ARPU ($/mo)", geo, "$#,##0.0", "", fb=a26(f"a26_{co}_arpu"), ff=idx_inp(f"{co}_arpu"), font=F_GREEN)
    yline("y_subs", "Consumer: subscriptions ($B)", lambda col, row: f"={col}{R['y_mau']}*{col}{R['y_conv']}*{col}{R['y_arpu']}*12/1000", B, "MAU x conversion x ARPU x 12")
    yline("y_free", "Consumer: free MAU (M)", lambda col, row: f"={col}{R['y_mau']}*(1-{col}{R['y_conv']})", "#,##0", "")
    if co == "oai":
        yline("y_adarpu", "Consumer: ads ARPU per free user ($/yr)", geo, "$#,##0.00", "anchor 2026E (~$1B ads / free MAU); 2030E = Inputs (scenario)", fb=a26("a26_oai_ad_arpu"), ff=idx_inp("oai_ad_arpu"), font=F_GREEN)
        yline("y_ads", "Consumer: ads ($B)", lambda col, row: f"={col}{R['y_free']}*{col}{R['y_adarpu']}/1000", B, "free MAU x ads ARPU")
        yline("y_gmv", "Consumer: commerce GMV ($B)", geo, B, "", fb=a26("a26_oai_gmv"), ff=idx_inp("oai_gmv"), font=F_GREEN)
        yline("y_take", "Consumer: take rate", lin, "0.00%", "", fb=a26("a26_oai_take"), ff=idx_inp("oai_take"), growth="delta", font=F_GREEN)
        yline("y_comm", "Consumer: commerce ($B)", lambda col, row: f"={col}{R['y_gmv']}*{col}{R['y_take']}", B, "GMV x take rate")
    else:
        yline("y_adarpu", "Consumer: ads ARPU per free user ($/yr)", lambda col, row: 0, "$#,##0.00", "Anthropic: no ads", growth=None, font=F_BLUE)
        yline("y_ads", "Consumer: ads ($B)", lambda col, row: 0, B, "", growth=None, font=F_BLUE)
        yline("y_gmv", "Consumer: commerce GMV ($B)", lambda col, row: 0, B, "not modelled", growth=None, font=F_BLUE)
        yline("y_take", "Consumer: take rate", lambda col, row: 0, "0.00%", "", growth=None, font=F_BLUE)
        yline("y_comm", "Consumer: commerce ($B)", lambda col, row: 0, B, "", growth=None, font=F_BLUE)
    yline("y_other", "Other revenue ($B)", lin, B, "anchor 2026E; 2030E = Inputs (scenario); linear", fb=a26(f"a26_{co}_other"), ff=idx_inp(f"{co}_other"), font=F_GREEN)
    ygroup("Tie-out to the calendar-revenue path")
    yline("y_cons", "Consumer subtotal ($B)", lambda col, row: f"={col}{R['y_subs']}+{col}{R['y_ads']}+{col}{R['y_comm']}", B, "")
    yline("y_ent_raw", "Enterprise before tie-out ($B)", lambda col, row: "=" + "+".join(f"{col}{R['y_pool_' + t]}*{col}{R['y_sh_' + t]}" for t in ("dev", "pro", "gen")) + f"+{col}{R['y_pool_mach']}*{col}{R['y_sh_auto']}", B, "sum of pool x share")
    yline("y_k", "Tie-out factor k on enterprise shares", lambda col, row: f"=IF({col}{R['y_ent_raw']}=0,1,({col}{R['y_cal']}-{col}{R['y_cons']}-{col}{R['y_other']})/{col}{R['y_ent_raw']})", "0.000",
          "(calendar revenue - consumer - other) / enterprise before tie-out; 1.000 in 2026E and 2030E by construction", growth=None)
    yline("y_ent", "Enterprise after tie-out ($B)", lambda col, row: f"={col}{R['y_ent_raw']}*{col}{R['y_k']}", B, "")
    yline("y_total", "Total bottom-up ($B)", lambda col, row: f"={col}{R['y_ent']}+{col}{R['y_cons']}+{col}{R['y_other']}", B3, "equals the calendar revenue path by construction", total=True)
    yline("y_chk", "Check: total - calendar path", lambda col, row: f"={col}{R['y_total']}-{col}{R['y_cal']}", "0.000000;(0.000000);-", "must be zero", growth=None)
    for rev_row, pool_row, sh_row in pending_rev:
        for col in YC:
            ws[f"{col}{rev_row}"].value = f"={col}{pool_row}*{col}{sh_row}*{col}${R['y_k']}"
    ygroup("Supply side by year (Base = v3 yearly values; other scenarios interpolate from the 2026E v3 value to the scenario 2030E)")
    S = V3S[co]
    yline("y_gw", "Supply: average total capacity (GW)", override(geo, S["gw_avg_total"]), "0.000", "2026E = v3", fb=f"=v3_series!B{S['gw_avg_total']}", ff=idx_inp(f"{co}_gw_avg"), font=F_GREEN)
    yline("y_shinf", "Supply: inference share of average capacity", override(lin, S["inf_share_avg"]), "0.00%", "2026E = v3", fb=f"=v3_series!B{S['inf_share_avg']}", ff=idx_inp(f"{co}_inf_share_avg"), growth="delta", font=F_GREEN)
    yline("y_gwinf", "Supply: average inference capacity (GW)", lambda col, row: f"={col}{R['y_gw']}*{col}{R['y_shinf']}", "0.000", "GW x share")
    yline("y_yield", "Supply: revenue per average inference GW-year ($B)", override(geo, S["yield_inf"]), B3, "2026E = v3", fb=f"=v3_series!B{S['yield_inf']}", ff=idx_inp(f"{co}_yield_inf"), font=F_GREEN)
    yline("y_suprev", "Supply: revenue = inference GW x yield ($B)", lambda col, row: f"={col}{R['y_gwinf']}*{col}{R['y_yield']}", B3, "Base = v3 calendar revenue")
    yline("y_cost", "Supply: inference compute cost per GW-year ($B)", override(lin, S["inf_cost_per_gw"]), B3, "2026E = v3", fb=f"=v3_series!B{S['inf_cost_per_gw']}", ff=idx_inp(f"{co}_cost_inf_gw"), font=F_GREEN)
    gm_calc = lambda col, row: f'=IF({SEL}="Base",v3_series!{col}{S["gross_margin"]},IF({col}{R["y_suprev"]}=0,0,1-({col}{R["y_gwinf"]}*{col}{R["y_cost"]}+INDEX(Inputs!$D${ROW[co + "_other_cor"]}:$G${ROW[co + "_other_cor"]},1,{M})*{col}{R["y_suprev"]})/{col}{R["y_suprev"]}))'
    yline("y_gm", "Supply: gross margin", gm_calc, "0.0%", "Base = v3 gross margin; else 1 - (inference GW x cost + other CoR) / revenue", growth="delta")
    yline("y_supvs", "Supply revenue / bottom-up total", lambda col, row: f"=IF({col}{R['y_total']}=0,0,{col}{R['y_suprev']}/{col}{R['y_total']})", "0.000x", "1.000x in Base", growth=None)
    ygroup("Momentum by year")
    yline("y_rr", "Momentum: exit run-rate ($B)", lambda col, row: f"=INDEX($C${R['rr' + YR[col]]}:$F${R['rr' + YR[col]]},1,{M})", B3, "momentum block, selected scenario",
          fb=f"=INDEX($C${R['rr26']}:$F${R['rr26']},1,{M})", ff=idx_sheet("rr30"), font=F_GREEN)
    r += 1

    group("What you need to believe (targets vs Base structure)")
    ws.cell(row=r, column=1, value="Target revenue 2030 ($B)").font = F_BOLD
    ws.cell(row=r, column=2, value="input")
    for col, v in (("C", 280), ("D", 394)):
        cell = ws[f"{col}{r}"]
        cell.value = v
        cell.font = F_BLUE
        cell.fill = FILL_YELLOW
        cell.number_format = B
    ws.cell(row=r, column=7, value="defaults: $280B = OpenAI's own 2030 plan (Bloomberg); $394B = deck 25 GW x 52.5% x $30B (both editable)").font = F_NOTE
    R["tgt"] = r
    r += 1

    def wline(label: str, const, fn: Callable[[str], str], fmt: str, note: str = ""):
        nonlocal r
        ws.cell(row=r, column=1, value=label)
        if const is not None:
            ws.cell(row=r, column=2, value=const).font = F_BLUE
        for col in ("C", "D"):
            cell = ws[f"{col}{r}"]
            cell.value = fn(col)
            cell.number_format = fmt
        ws.cell(row=r, column=7, value=note).font = F_NOTE
        r += 1
        return r - 1

    t = R["tgt"]
    wline("Target vs Base (v3) revenue", None, lambda c: f"=IF($D${R['total']}=0,0,{c}${t}/$D${R['total']})", "0.00x", "")
    wline("Implied yield per inference GW at Base GW and share", None, lambda c: f"=IF($D${R['gw_inf']}=0,0,{c}${t}/$D${R['gw_inf']})", B, "target / Base average inference GW")
    wline("Implied average GW at Base yield and share", None, lambda c: f"=IF($D${R['yield']}*$D${R['sh']}=0,0,{c}${t}/($D${R['yield']}*$D${R['sh']}))", "0.0", "")
    wline("Implied GW at deck economics ($/GW-inf x inference share, Inputs Base)", None, lambda c: f"={c}${t}/({inp_base('deck_rgw_inf')}*{inp_base('deck_inf_share')})", "0.0", "target / ($30B x 52.5%)")
    up = wline("Required uplift on enterprise engines vs Base", None, lambda c: f"=({c}${t}-($D${R['total']}-$D${R['ent']}))/$D${R['ent']}", "0.00x", "consumer + other held at Base")
    wline("...if only developer spend/salary moves", None, lambda c: f"={inp_base('ratio_dev')}*(1+({c}{up}-1)*$D${R['ent']}/$D${R['seg_dev']})", P, "vs Base ratio on Inputs")
    wline("...if only machine-API automated share moves", None, lambda c: f"={inp_base('auto_share')}*(1+({c}{up}-1)*$D${R['ent']}/$D${R['seg_mach']})", P, "")
    wline("Target as % of global enterprise AI pool (Base)", None, lambda c: f"={c}${t}/$D${R['pool_tot']}", P, "")
    wline("Target as % of global labour compensation ($B) =", 65000, lambda c: f"={c}${t}/$B{r}", "0.00%", "~$58T 2025 growing to ~$65T")
    wline("Target as % of global software spend ($B) =", 2400, lambda c: f"={c}${t}/$B{r}", P, "Gartner $1.47T 2026 -> ~$2.4T 2030")

    ws.freeze_panes = "C5"
    set_widths(ws, [58, 10, 13, 13, 13, 13, 70, 40])
    return R


# ---------------------------------------------------------------------------
# Deck check
# ---------------------------------------------------------------------------
def build_deck_check(wb: Workbook) -> Dict[str, int]:
    ws = wb.create_sheet("Deck_check")
    R: Dict[str, int] = {}
    ws["A1"] = "Deck check: revenue = total GW x share of capacity in inference x revenue per GW of inference, vs the v3 models"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Deck inputs live on Inputs (group 'Deck'); v3 values come from the 'v3 reference' group."
    ws["A2"].font = F_NOTE
    headers = ["Line", "Unit", "Bear", "Base", "Bull", "Custom", "Formula / note"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=4, column=i, value=h)
    style_header(ws, 4, len(headers))
    r = 5

    def line(key, label, unit, fn, fmt, note="", font=F_BLACK, total=False):
        nonlocal r
        ws.cell(row=r, column=1, value=label).font = F_BOLD if total else F_BLACK
        ws.cell(row=r, column=2, value=unit)
        for col in ("C", "D", "E", "F"):
            cell = ws[f"{col}{r}"]
            cell.value = fn(col)
            cell.font = Font(name=FONT, bold=True, color=font.color) if total else font
            cell.number_format = fmt
            if total:
                cell.fill = FILL_TOTAL
        ws.cell(row=r, column=7, value=note).font = F_NOTE
        R[key] = r
        r += 1

    line("gw", "Deck: total GW per company", "GW", lambda c: f"={inp('deck_gw', c)}", "0.0", "", F_GREEN)
    line("sh", "Deck: share of capacity in inference", "%", lambda c: f"={inp('deck_inf_share', c)}", "0.0%", "", F_GREEN)
    line("rgwi", "Deck: revenue per GW of inference", "$B/GW", lambda c: f"={inp('deck_rgw_inf', c)}", B, "", F_GREEN)
    line("rev", "Deck revenue = GW x share x $/GW-inference", "$B", lambda c: f"={c}{R['gw']}*{c}{R['sh']}*{c}{R['rgwi']}", B, "", total=True)
    line("rgwt", "Deck implied $/GW of TOTAL capacity", "$B/GW", lambda c: f"={c}{R['sh']}*{c}{R['rgwi']}", B, "share x $/GW-inference")
    r += 1
    for co, name in (("oai", "OpenAI"), ("ant", "Anthropic")):
        line(f"{co}_v3_gw", f"v3 {name}: average in-year total GW 2030", "GW", lambda c, co=co: f"={inp('v3_' + co + '_gw_avg_total_2030', c)}", "0.000", "", F_GREEN)
        line(f"{co}_v3_sh", f"v3 {name}: inference share of average capacity", "%", lambda c, co=co: f"={inp('v3_' + co + '_inf_share_avg_2030', c)}", "0.00%", "", F_GREEN)
        line(f"{co}_v3_y", f"v3 {name}: revenue per average inference GW-year", "$B/GW", lambda c, co=co: f"={inp('v3_' + co + '_yield_inf_2030', c)}", B3, "", F_GREEN)
        line(f"{co}_v3_rev", f"v3 {name}: calendar revenue 2030", "$B", lambda c, co=co: f"={inp('v3_' + co + '_rev_2030', c)}", B3, "", F_GREEN)
        line(f"{co}_vs_y", f"Deck yield vs v3 {name} yield", "x", lambda c, co=co: f"=IF({c}{R[co + '_v3_y']}=0,0,{c}{R['rgwi']}/{c}{R[co + '_v3_y']})", "0.00x", "")
        line(f"{co}_vs_rev", f"Deck revenue vs v3 {name} revenue", "x", lambda c, co=co: f"=IF({c}{R[co + '_v3_rev']}=0,0,{c}{R['rev']}/{c}{R[co + '_v3_rev']})", "0.00x", "")
        line(f"{co}_vs_y26", f"Deck yield vs v3 {name} 2026E yield", "x", lambda c, co=co: f"=IF({inp('v3_' + co + '_yield_inf_2026', c)}=0,0,{c}{R['rgwi']}/{inp('v3_' + co + '_yield_inf_2026', c)})", "0.00x", "2026E revenue per average inference GW-year", F_GREEN)
        r += 1
    line("gm8", "Gross margin on inference at $8B cost per GW-yr (deck yield)", "%", lambda c: f"=IF({c}{R['rgwi']}=0,0,1-8/{c}{R['rgwi']})", "0%", "owned / custom-silicon compute")
    line("gm12", "Gross margin on inference at $12B cost per GW-yr (deck yield)", "%", lambda c: f"=IF({c}{R['rgwi']}=0,0,1-12/{c}{R['rgwi']})", "0%", "v3 Anthropic applied cost; OpenAI $11.7B")
    line("gm13", "Gross margin on inference at $13.3B cost per GW-yr (deck yield)", "%", lambda c: f"=IF({c}{R['rgwi']}=0,0,1-13.3/{c}{R['rgwi']})", "0%", "rented at Oracle-OpenAI pricing")
    ws.freeze_panes = "C5"
    set_widths(ws, [62, 10, 12, 12, 12, 12, 55])
    return R


# ---------------------------------------------------------------------------
# Sensitivity
# ---------------------------------------------------------------------------
def build_sensitivity(wb: Workbook):
    ws = wb.create_sheet("Sensitivity")
    ws["A1"] = "Two-way sensitivities (constants read the Base column of Inputs; headers in blue are editable)"
    ws["A1"].font = F_TITLE
    r = 3

    def grid(title, row_label, col_label, row_vals, col_vals, fn, row_fmt, col_fmt, cell_fmt):
        nonlocal r
        ws.cell(row=r, column=1, value=title).font = F_BOLD
        r += 1
        ws.cell(row=r, column=1, value=f"{row_label} \\ {col_label}").font = F_NOTE
        for j, cv in enumerate(col_vals, start=2):
            cell = ws.cell(row=r, column=j, value=cv)
            cell.font = F_BLUE
            cell.number_format = col_fmt
        hdr = r
        r += 1
        for rv in row_vals:
            cell = ws.cell(row=r, column=1, value=rv)
            cell.font = F_BLUE
            cell.number_format = row_fmt
            for j in range(2, 2 + len(col_vals)):
                cl = get_column_letter(j)
                c = ws.cell(row=r, column=j, value=fn(f"$A{r}", f"{cl}${hdr}"))
                c.number_format = cell_fmt
            r += 1
        r += 1

    grid("Revenue ($B) = average total GW x inference share (v3 Anthropic Base, Inputs) x yield per inference GW", "avg GW", "$B/GW-inference",
         [15, 20, 22.5, 25, 30], [22, 26, 30, 31, 35, 40],
         lambda rc, cc: f"={rc}*{inp_base('ant_inf_share_avg')}*{cc}", '0.0" GW"', '"$"0"B/GW-inf"', "#,##0")
    grid("Revenue ($B) at 22.5 average GW = inference share x yield per inference GW", "inference share", "$B/GW-inference",
         [0.45, 0.50, 0.54, 0.60, 0.65], [22, 26, 30, 31, 35, 40],
         lambda rc, cc: f"=22.5*{rc}*{cc}", "0%", '"$"0"B/GW-inf"', "#,##0")
    grid("Yield per inference GW ($B) = tokens/GW-yr (1e15) x realised $/M tokens x utilisation (Base memo)",
         "q tokens/GW-yr", "$/M tokens", [12, 16, 20, 24, 28, 32], [1.2, 1.6, 2.0, 2.3, 2.6, 3.0],
         lambda rc, cc: f"={rc}*{cc}*{inp_base('util')}", '0"q"', '"$"0.0"/M"', "#,##0.0")
    grid("OpenAI ads revenue ($B) = free MAU (M) x ads ARPU ($/yr)", "free MAU (M)", "$/free user/yr",
         [1400, 1900, 2300], [20, 30, 40, 50, 60], lambda rc, cc: f"={rc}*{cc}/1000", "#,##0", '"$"0', "#,##0")
    grid("OpenAI consumer subscriptions ($B) = MAU (M) x paid conversion x Base ARPU x 12", "MAU (M)", "paid conversion",
         [1500, 2000, 2500], [0.045, 0.065, 0.08, 0.10], lambda rc, cc: f"={rc}*{cc}*{inp_base('oai_arpu')}*12/1000", "#,##0", "0.0%", "#,##0")
    grid("Anthropic developer engine ($B) = paid devs (Base: workers x penetration) x spend ($k/dev/yr) x Anthropic share",
         "$k/dev/yr", "Anthropic share", [6, 9, 12, 15, 18], [0.35, 0.40, 0.45, 0.50],
         lambda rc, cc: f"={inp_base('kw_dev')}*{inp_base('pen_dev')}*{rc}*{cc}", '"$"0"k"', "0%", "#,##0")
    grid("Professional-seat global pool ($B) = professionals (Base) x penetration x $/seat", "penetration", "$/seat/yr",
         [0.40, 0.50, 0.60], [1800, 2700, 3600, 4500], lambda rc, cc: f"={inp_base('kw_pro')}*{rc}*{cc}/1000", "0%", '"$"#,##0', "#,##0")
    grid("Machine / agent API global pool ($B) = labour pool (Base, $T) x automated share x vendor capture", "automated share", "vendor capture",
         [0.08, 0.125, 0.16, 0.20], [0.20, 0.25, 0.30, 0.35], lambda rc, cc: f"={inp_base('auto_pool')}*1000*{rc}*{cc}", "0.0%", "0%", "#,##0")
    grid("Gross margin on inference = 1 - (compute cost per GW-yr / yield per inference GW), before other CoR", "$B yield/GW-inf", "$B cost/GW-yr",
         [22, 30.9, 35, 40, 50], [8, 10, 11.7, 12, 13.3], lambda rc, cc: f"=1-{cc}/{rc}", '"$"0.0"B"', '"$"0.0"B"', "0%")
    set_widths(ws, [36, 12, 12, 12, 12, 12, 12])


# ---------------------------------------------------------------------------
# Summary + Sources
# ---------------------------------------------------------------------------
def build_summary(wb: Workbook, R: Dict[str, Dict[str, int]]):
    ws = wb.create_sheet("Summary", 0)
    ws["A1"] = "OpenAI & Anthropic - 2030 revenue framework (bottom-up vs compute vs momentum). Base = MBI vBTG v3."
    ws["A1"].font = F_TITLE
    ws["A2"] = "All cells are links (green) or formulas. Edit assumptions on Inputs (Custom column)."
    ws["A2"].font = F_NOTE
    headers = ["Metric ($B unless stated)", "Bear", "Base", "Bull", "Custom"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=4, column=i, value=h)
    style_header(ws, 4, len(headers))
    r = 5
    rows = [
        ("OpenAI - bottom-up revenue 2030", "OpenAI", "total", B3),
        ("OpenAI - supply-side revenue 2030 (avg inference GW x yield)", "OpenAI", "sup_cap", B3),
        ("OpenAI - momentum calendar revenue 2030", "OpenAI", "cal30", B3),
        ("OpenAI - yield needed for the bottom-up ($B per inference GW)", "OpenAI", "yield_need", B),
        ("Anthropic - bottom-up revenue 2030", "Anthropic", "total", B3),
        ("Anthropic - supply-side revenue 2030 (avg inference GW x yield)", "Anthropic", "sup_cap", B3),
        ("Anthropic - momentum calendar revenue 2030", "Anthropic", "cal30", B3),
        ("Anthropic - yield needed for the bottom-up ($B per inference GW)", "Anthropic", "yield_need", B),
    ]
    R_SUM: Dict[str, int] = {}
    for label, sheet, key, fmt in rows:
        ws.cell(row=r, column=1, value=label)
        for j, col in enumerate(("C", "D", "E", "F"), start=2):
            cell = ws.cell(row=r, column=j, value=f"={sheet}!{col}{R[sheet][key]}")
            cell.font = F_GREEN
            cell.number_format = fmt
        R_SUM[f"{sheet}_{key}"] = r
        r += 1
    ws.cell(row=r, column=1, value="Combined bottom-up revenue 2030").font = F_BOLD
    for j, col in enumerate(("B", "C", "D", "E"), start=2):
        cell = ws.cell(row=r, column=j, value=f"={col}{R_SUM['OpenAI_total']}+{col}{R_SUM['Anthropic_total']}")
        cell.number_format = B3
        cell.fill = FILL_TOTAL
        cell.font = F_BOLD
    R_SUM["combined"] = r
    r += 1
    for label, key, fmt in (("Deck check: 25 GW x inference share x $/GW-inference (per company)", "rev", B),
                            ("Deck yield vs v3 OpenAI yield", "oai_vs_y", "0.00x"),
                            ("Deck yield vs v3 Anthropic yield", "ant_vs_y", "0.00x")):
        ws.cell(row=r, column=1, value=label)
        for j, col in enumerate(("C", "D", "E", "F"), start=2):
            cell = ws.cell(row=r, column=j, value=f"=Deck_check!{col}{R['Deck_check'][key]}")
            cell.font = F_GREEN
            cell.number_format = fmt
        r += 1
    r += 1

    # Reconciliation to v3 (Base column only)
    ws.cell(row=r, column=1, value="Reconciliation of the Base column to the v3 models (must be zero)").font = F_BOLD
    for c in range(1, 6):
        ws.cell(row=r, column=c).fill = FILL_GROUP
    r += 1
    for i, h in enumerate(["Line", "Model Base", "v3", "Difference", ""], start=1):
        ws.cell(row=r, column=i, value=h).font = F_BOLD
    r += 1
    recon = [
        ("2030 revenue - bottom-up", "total", "rev_2030", B3),
        ("2030 revenue - supply side", "sup_cap", "rev_2030", B3),
        ("2030 revenue - momentum (calendar)", "cal30", "rev_2030", B3),
        ("2030 exit run-rate", "rr30", "exit_arr_2030", B3),
        ("Average total GW 2030", "gw", "gw_avg_total_2030", "0.000"),
        ("Inference share of average capacity", "sh", "inf_share_avg_2030", "0.00%"),
        ("Average inference GW 2030", "gw_inf", "gw_avg_inf_2030", "0.000"),
        ("Revenue per average inference GW-year", "yield", "yield_inf_2030", B3),
        ("Revenue per average total GW-year", "rgw_tot", "rev_per_total_gw_2030", B3),
        ("Gross margin 2030", "gm", "gross_margin_2030", "0.00%"),
    ]
    R_SUM["recon_first"] = r
    for co, sheet in (("oai", "OpenAI"), ("ant", "Anthropic")):
        for label, key, v3key, fmt in recon:
            ws.cell(row=r, column=1, value=f"{sheet}: {label}")
            a = ws.cell(row=r, column=2, value=f"={sheet}!D{R[sheet][key]}")
            a.font = F_GREEN
            a.number_format = fmt
            b = ws.cell(row=r, column=3, value=f"={inp_base('v3_' + co + '_' + v3key)}")
            b.font = F_GREEN
            b.number_format = fmt
            d = ws.cell(row=r, column=4, value=f"=B{r}-C{r}")
            d.number_format = "0.000000;(0.000000);-"
            d.fill = FILL_OK
            r += 1
    R_SUM["recon_last"] = r - 1
    r += 1
    ws.cell(row=r, column=1, value="Reference points (2026)").font = F_BOLD
    r += 1
    refs = [
        ("OpenAI run-rate Aug-2026", 40, "press reports; enterprise >50% of mix"),
        ("Anthropic run-rate end-Jul-2026", 65, "Bloomberg/Axios 17-Aug-2026"),
        ("OpenAI company plan 2030", 280, ">$280B (Bloomberg 20-Feb-2026); later reports up to ~$350B"),
        ("Anthropic company plan 2028", 195, "$190-200B (Reuters 14-Aug-2026)"),
        ("Superforecaster median, OpenAI+Anthropic combined 2030 run-rate", 300, "Forecasting Research Institute; 34% prob. >$400B"),
        ("Bain: AI revenue needed by 2030 (whole industry)", 2000, "Bain Global Technology Report 2025"),
    ]
    for label, v, note in refs:
        ws.cell(row=r, column=1, value=label)
        c = ws.cell(row=r, column=2, value=v)
        c.font = F_BLUE
        c.number_format = "#,##0"
        ws.cell(row=r, column=3, value=note).font = F_NOTE
        r += 1
    set_widths(ws, [66, 16, 16, 16, 14])
    return R_SUM


SOURCES = [
    ("BASE CASE: OpenAI breakeven model (MBI vBTG v3) - 2030 calendar revenue $338.1B, avg 20.24 GW, 54.1% inference, $30.89B per inference GW-year, $11.70B inference cost/GW-yr, GM 59.1%, EBIT 0", "v3", "OpenAI_breakeven_model_MBI_vBTG_v3.xlsx (Model!I100, I29, I26, I101, I62, I119, I128) - file kept in trabalho/equityresearch/raw/empresas/ai labs, not in the repo", ""),
    ("BASE CASE: Anthropic model (MBI vBTG v3) - 2030 calendar revenue $425.6B, avg 22.5 GW, 54.1% inference, $34.96B per inference GW-year, $12B inference cost/GW-yr, GM 62.7%, EBIT $48.0B", "v3", "Anthropic_model_MBI_vBTG_v3.xlsx (Model!I89, I29, I26, I88, I62, I107, I116) - same folder", ""),
    ("v3 2026E anchors: OpenAI calendar $36.5B / exit ARR $60B / 4.05 GW; Anthropic calendar $57B / exit ARR $100B / 5 GW", "v3", "v3 Model!E100/E105/E7 and E89/E90/E7", ""),
    ("OpenAI annualised revenue run-rate >$40B; enterprise >50% of mix", "Aug-2026", "press (enterprisedna.co / valueaddvc.com summaries of company statements)", "https://enterprisedna.co/resources/news/openai-enterprise-revenue-overtakes-consumer-40-billion-arr-2026/"),
    ("ChatGPT ~1B MAU (Jun-26), ~1B WAU (Jul-26); >50M consumer subs; 9M paying business users; 7M enterprise seats", "Jul/Aug-2026", "demandsage / secondtalent (secondary)", "https://www.demandsage.com/chatgpt-statistics/"),
    ("OpenAI forecasts 2030 revenue >$280B; consumer/enterprise ~50/50 by 2030", "20-Feb-2026", "Bloomberg", "https://www.bloomberg.com/news/articles/2026-02-20/openai-forecasts-its-revenue-will-top-280-billion-in-2030"),
    ("OpenAI ads plan: $2.5B 2026, $11B 2027, $25B 2028, $53B 2029, $100B 2030", "09-Apr-2026", "Axios", "https://axios.com/2026/04/09/openai-100-billion-in-ad-revenue"),
    ("ChatGPT ads: launched 9-Feb-2026 (US Free + Go); $1B run-rate in <200 days; ~$60 CPM", "2026", "press (secondary)", "https://explainx.ai/blog/openai-advertise-in-chatgpt-ads-launch-july-2026"),
    ("OpenAI API 15B tokens/min; Codex 2M+ weekly users", "Mar-2026", "OpenAI", "https://openai.com/index/a-business-that-scales-with-the-value-of-intelligence/"),
    ("OpenAI compute: 0.2GW (2023) -> 1.9GW (2025) while run-rate $2B -> $20B (~$10B/GW)", "2025", "MBI Deep Dives citing OpenAI", "https://www.mbi-deepdives.com/oai-breakeven/"),
    ("OpenAI 30GW target by 2030; compute spend ~$600B -> ~$750B through 2030", "2026", "WSJ / DCD (secondary)", "https://www.datacenterdynamics.com/en/news/openai-cuts-projected-compute-spend-to-600bn-by-2030-report/"),
    ("Oracle-OpenAI $300B / 5 yrs / 4.5GW (~$13.3B per GW-year)", "Jul/Sep-2025", "The Register", "https://www.theregister.com/2025/07/22/openai_oracle_gpus/"),
    ("Anthropic run-rate $65B (end-Jul-26); $47B mid-May; $9B end-2025", "17-Aug-2026", "Bloomberg / TechCrunch / Axios", "https://techcrunch.com/2026/08/17/anthropics-annualized-revenue-surges-to-65b/"),
    ("Anthropic run-rate >$30B; >1,000 customers >$1M/yr; multi-GW TPU capacity from 2027", "Apr-2026", "Anthropic", "https://www.anthropic.com/news/google-broadcom-partnership-compute"),
    ("Anthropic IPO case: $190-200B revenue in 2028", "14-Aug-2026", "Reuters", "https://www.usnews.com/news/top-news/articles/2026-08-14/exclusive-anthropic-ipo-valuation-hinges-on-190-200-billion-2028-revenue-forecast-sources-say"),
    ("Claude Code $8B ARR (May-26); >50% enterprise", "May-2026", "press (secondary)", "https://aibusinessweekly.net/p/claude-code-statistics"),
    ("Claude Code cost: avg ~$6/dev/day; 90% of users <$12/day; enterprise avg $150-250/dev/month", "2026", "Anthropic docs / morphllm", "https://code.claude.com/docs/en/costs"),
    ("Claude pricing: Pro $20, Max $100/$200, Team $25 std / $125 premium, Enterprise ~$20/seat + usage", "Sep-2026", "Anthropic", "https://claude.com/pricing"),
    ("ChatGPT Go $8/mo US, Rs399 India (free promo to Dec-26); Plus $20; Pro $200", "2026", "OpenAI", "https://openai.com/index/introducing-chatgpt-go/"),
    ("Meta FY2025 revenue $200.1B; DAP 3.58B; Q4-25 ARPP $16.56 (~$58/yr)", "28-Jan-2026", "Meta IR", "https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Fourth-Quarter-and-Full-Year-2025-Results/default.aspx"),
    ("Google Search & other ads revenue 2025: $175.8B", "Feb-2026", "Alphabet Q4-25 release", "https://s206.q4cdn.com/479360582/files/doc_financials/2025/q4/2025q4-alphabet-earnings-release.pdf"),
    ("Google processes 3.2 quadrillion tokens/month (7x YoY)", "May-2026", "Google I/O 2026", "https://blog.google/innovation-and-ai/sundar-pichai-io-2026/"),
    ("M365 Copilot 20M paid seats (Q3 FY26) at $30/seat; 450M M365 commercial seats; GitHub Copilot 4.7M paid", "Jan-Apr 2026", "Microsoft earnings via Directions on Microsoft (secondary)", "https://www.directionsonmicrosoft.com/microsoft-claims-15-million-paid-m365-copilot-seats/"),
    ("Cursor $2B+ ARR", "2026", "secondtalent (secondary)", "https://www.secondtalent.com/resources/cursor-vs-github-copilot/"),
    ("Enterprise LLM API spend share: Anthropic ~32-40%, OpenAI ~25-27%; coding ~54% Anthropic", "2025-26", "Menlo Ventures (via secondary)", "https://medium.com/@david.j.sea/anthropic-just-passed-openai-in-revenue-here-is-why-it-matters-e3dd9bb04069"),
    ("AI spend per employee 2026: avg $2,068 (+50% YoY); top decile >$2,800; median <$200", "06-May-2026", "Atlanta Fed", "https://www.atlantafed.org/research-and-data/publications/policy-hub-macroblog/2026/05/06/how-much-firms-spending-on-ai-and-what-will-happen-to-headcounts"),
    ("Gartner: IT spend 2026 $6.37T (+14.2%); software $1.468T (+15.5%); AI spending $2.59T (+47%)", "Jul-2026", "Gartner", "https://www.gartner.com/en/newsroom/press-releases/2026-07-27-gartner-forecasts-worldwide-it-spending-to-grow-14-point-2-percent-in-2026-totaling-6-point-37-trillion"),
    ("Knowledge workers ~1B+ globally (Gartner); 1.25B information workers (Forrester 2018); global labour comp ~$58T", "various", "Forrester / Gartner / Substrate gist (secondary)", "https://go.forrester.com/blogs/the-global-information-worker-population-swells-to-1-25-billion-in-2018/"),
    ("Bain: AI needs $2T annual revenue by 2030; $800B shortfall; ~200GW global AI compute by 2030", "Sep-2025", "Bain & Company", "https://www.bain.com/about/media-center/press-releases/20252/$2-trillion-in-new-revenue-needed-to-fund-ais-scaling-trend---bain--companys-6th-annual-global-technology-report/"),
    ("1GW AI data center TCO: ~$38B upfront capex + ~$0.9B/yr opex (servers ~60% of annualised cost)", "2026", "Epoch AI", "https://epoch.ai/data-insights/ai-datacenter-cost-breakdown"),
    ("Frontier API list prices Sep-2026: Claude Opus 5.5 $4/$20, GPT-6 Sol $2/$10, Gemini 3.8 Flash $0.75/$3.75 per M tokens", "Sep-2026", "benchlm / developersdigest (secondary)", "https://benchlm.ai/llm-pricing"),
    ("Superforecasters: OpenAI+Anthropic combined 2030 run-rate median $300B; 34% prob >$400B; 18% prob <$100B", "2026", "Forecasting Research Institute", "https://forecastingresearch.substack.com/p/will-the-ai-boom-continue-forecasting"),
]


def build_sources(wb: Workbook):
    ws = wb.create_sheet("Sources")
    ws["A1"] = "Data anchors and sources (as of 24-Sep-2026; several are press summaries of company disclosures - flagged 'secondary')"
    ws["A1"].font = F_TITLE
    headers = ["Data point", "Date", "Source", "URL"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=3, column=i, value=h)
    style_header(ws, 3, len(headers))
    for i, (dp, dt, src, url) in enumerate(SOURCES, start=4):
        ws.cell(row=i, column=1, value=dp)
        ws.cell(row=i, column=2, value=dt)
        ws.cell(row=i, column=3, value=src)
        if url:
            c = ws.cell(row=i, column=4, value=url)
            c.hyperlink = url
            c.font = Font(name=FONT, color="0563C1", underline="single")
    set_widths(ws, [110, 12, 70, 80])


def main(out: str):
    wb = Workbook()
    build_inputs(wb)
    V3S = build_v3_series(wb)
    R = {"OpenAI": build_company(wb, "oai", "OpenAI", V3S), "Anthropic": build_company(wb, "ant", "Anthropic", V3S)}
    patch_solved_inputs(wb, R)
    R["Deck_check"] = build_deck_check(wb)
    build_sensitivity(wb)
    build_sources(wb)
    build_summary(wb, R)
    order = ["Summary", "Inputs", "OpenAI", "Anthropic", "Deck_check", "Sensitivity", "v3_series", "Sources"]
    wb._sheets = [wb[n] for n in order]
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is not None and (cell.font is None or cell.font.name != FONT):
                    f = cell.font
                    cell.font = Font(name=FONT, bold=f.bold, italic=f.italic, color=f.color, size=f.size, underline=f.underline)
    wb.save(out)
    print("saved", out)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    main(os.path.join(here, "AI_labs_revenue_2030_bottomup.xlsx"))
