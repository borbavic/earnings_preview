# AI labs 2030 revenue framework (OpenAI, Anthropic)

Bottom-up framework to ground the 2030 revenue numbers used in the AI-capex / revenue-per-GW deck.

| File | What it is |
|---|---|
| `docs/framework_receita_2030.md` | The framework (PT-BR): conclusion, driver trees, 2026 anchors, scenarios, GW reconciliation, slide storyboard, sources |
| `model/AI_labs_revenue_2030_bottomup.xlsx` | Live-formula model. Edit the yellow **Custom** column on `Inputs`; everything else recalculates |
| `model/revenue_2030_model.py` | Same assumptions and math in Python; prints all tables (`python3 revenue_2030_model.py`) |
| `model/build_xlsx.py` | Rebuilds the workbook from the Python assumptions |
| `model/verify_xlsx.py` | Cross-checks the recalculated workbook against the Python model |

Workbook tabs: `Summary` (both companies, four lenses) · `Inputs` (bear/base/bull/custom with 2026 anchors) · `OpenAI` · `Anthropic` (pools → segments → total → supply check → momentum → 2026-2030 bridge → what-you-need-to-believe) · `Deck_check` (GW × inference share × $/GW-inference vs model and realised anchors) · `Sensitivity` (9 two-way grids) · `Sources`.

Rebuild after changing assumptions in the Python file:

```bash
cd ai_labs_2030/model
python3 build_xlsx.py
python3 <xlsx-skill>/scripts/recalc.py AI_labs_revenue_2030_bottomup.xlsx 300   # LibreOffice recalculation
python3 verify_xlsx.py
```
