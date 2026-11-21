Smart AgriCare - Backend
========================

Notes:
- Unknown/low-confidence Kindwise outputs are normalized to `Suspected Leaf Disease` with `Low` confidence and safe, generic recommendations.

Run locally:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Tests:
```bash
pytest -q
```
ope t