# AI labs 2030 revenue framework (OpenAI, Anthropic)

Bottom-up framework to ground the 2030 revenue numbers used in the AI-capex / revenue-per-GW deck.
**The Base column is tied to the MBI vBTG v3 models** (`OpenAI_breakeven_model_MBI_vBTG_v3.xlsx`,
`Anthropic_model_MBI_vBTG_v3.xlsx`, kept in `trabalho/equityresearch/raw/empresas/ai labs`, not in this repo):
2030 revenue, average GW, inference share, revenue per inference GW-year, inference cost per GW-year,
2026E anchors and the 2027-30 run-rate path are identical to v3; bear and bull are sensitised around it.

| File | What it is |
|---|---|
| `docs/framework_receita_2030.md` | The framework (PT-BR): conclusion, driver trees, 2026 anchors, scenarios, GW reconciliation, what the v3 base needs, slide storyboard, sources |
| `model/AI_labs_revenue_2030_bottomup.xlsx` | Live-formula model. Edit the yellow **Custom** column on `Inputs`; everything else recalculates. `Summary` has a reconciliation block to v3 (all differences must be zero) |
| `model/v3_reference.json` | The v3 values the Base is tied to, with their cell references (extracted from the recalculated v3 files) |
| `model/revenue_2030_model.py` | Same assumptions and math in Python; prints all tables (`python3 revenue_2030_model.py`); includes calibration helpers |
| `model/build_xlsx.py` | Rebuilds the workbook from the Python assumptions |
| `model/verify_xlsx.py` | Cross-checks the recalculated workbook against the Python model and against v3 |

Workbook tabs: `Summary` (both companies, three lenses, deck check, reconciliation to v3) · `Inputs` (bear/base/bull/custom with anchors; the two machine-API shares in Base are solved formulas so the bottom-up equals v3; group `2026E anchors` feeds the yearly block) · `OpenAI` · `Anthropic` (pools → segments → total → supply check → momentum → **year-by-year evolution 2026E-2030E of the main inputs, with a scenario dropdown** → what-you-need-to-believe) · `Deck_check` (25 GW × inference share × $/GW-inference vs v3) · `Sensitivity` (9 two-way grids) · `v3_series` (the v3 yearly series 2026E-2030E the Base rows read) · `Sources`.

Year-by-year block: 2026E = anchors, 2030E = the selected scenario's column, 2027-29 interpolated along the scenario's calendar-revenue path (levels geometric, rates linear); enterprise shares carry an explicit tie-out factor k so the yearly total equals the path (Base = v3 every year); in Base the supply rows (GW, inference share, yield, cost, gross margin) are the v3 yearly values. `verify_xlsx.py` checks the block in Base and, with `RECALC_PY=<path to recalc.py>`, also re-runs it with the dropdown set to Bull.

Rebuild after changing assumptions in the Python file (or after a new v3: re-extract `v3_reference.json` from recalculated copies of the v3 files):

```bash
cd ai_labs_2030/model
python3 build_xlsx.py
python3 <xlsx-skill>/scripts/recalc.py AI_labs_revenue_2030_bottomup.xlsx 300   # LibreOffice recalculation
python3 verify_xlsx.py
```
