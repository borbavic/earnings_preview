"""Cross-checks the recalculated workbook against revenue_2030_model.py (run after recalc)."""
import os
import sys

from openpyxl import load_workbook

from revenue_2030_model import SCEN, SEGMENTS, company, momentum, supply

here = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "AI_labs_revenue_2030_bottomup.xlsx")
wb = load_workbook(path, data_only=True)
cols = {"bear": "C", "base": "D", "bull": "E", "custom": "F"}
bad = 0
for co, sheet in (("oai", "OpenAI"), ("ant", "Anthropic")):
    ws = wb[sheet]
    # find rows by label in column A
    rows = {}
    for rr in range(1, ws.max_row + 1):
        v = ws.cell(row=rr, column=1).value
        if v and v not in rows:  # first occurrence (segment names repeat in the bridge block)
            rows[v] = rr
    for s in SCEN + ["custom"]:
        py = company(co, "base" if s == "custom" else s)
        for seg in SEGMENTS + ["TOTAL"]:
            label = "TOTAL REVENUE 2030" if seg == "TOTAL" else seg
            xl = ws[f"{cols[s]}{rows[label]}"].value
            if xl is None or abs(xl - py[seg]) > 1e-6 * max(1, abs(py[seg])):
                bad += 1
                print(f"MISMATCH {sheet} {s} {seg}: xlsx={xl} py={py[seg]}")
        sp = supply(co, "base" if s == "custom" else s)
        xl = ws[f"{cols[s]}{rows['Supply-side revenue capacity']}"].value
        if abs(xl - sp["Supply-side revenue capacity ($B)"]) > 1e-6:
            bad += 1
            print(f"MISMATCH {sheet} {s} supply: xlsx={xl} py={sp}")
        mo = momentum(co, "base" if s == "custom" else s)
        xl = ws[f"{cols[s]}{rows['Exit-2030 run-rate']}"].value
        if abs(xl - mo["Exit-2030 run-rate"]) > 1e-6:
            bad += 1
            print(f"MISMATCH {sheet} {s} momentum: xlsx={xl} py={mo}")
    tot_row = rows["TOTAL REVENUE 2030"]
    print(f"{sheet}: base total xlsx={ws['D' + str(tot_row)].value:.1f}  py={company(co, 'base')['TOTAL']:.1f}")
# summary sheet spot check
ws = wb["Summary"]
print("Summary row 5 (OpenAI bottom-up):", [ws.cell(row=5, column=c).value for c in range(2, 6)])
print("Summary row 9 (Anthropic bottom-up):", [ws.cell(row=9, column=c).value for c in range(2, 6)])
print("Summary combined:", [ws.cell(row=13, column=c).value for c in range(2, 6)])
# sensitivity spot check: first grid cell B5 should be 10*8 = 80
ws = wb["Sensitivity"]
print("Sensitivity B5 (10GW x $8B/GW):", ws["B5"].value)
print("MISMATCHES:", bad)
sys.exit(1 if bad else 0)
