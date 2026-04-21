# Manufacturing Cost Calculator

## What it does

Given a **target** product and a **catalog** of products (each with an optional buy price and a recipe: ordered list of inputs), the program prints the **minimum dollars-and-cents cost** to obtain the target. For every product you may **buy** at its list price or **build** by paying the sum of the minimum costs of its inputs (recursively). Internal math uses **integer cents**; stdout prints **`dollars.cc`** (e.g. `61.00`).

## How to run

From this directory:

**cmd**

```cmd
type test_1.txt | python main.py
```

Use `test_1.txt` … `test_5.txt`. If `python` fails, try `py`.

**Expected outputs (reference)**

| File        | Approx. expected |
|------------|------------------|
| `test_1.txt` | `25800.00` (car) |
| `test_2.txt` | `10.00` (sandwich) |
| `test_3.txt` | `61.00` (teddy bear) |
| `test_4.txt` | `100000000.00` |
| `test_5.txt` | `3.50` (depends on catalog; buy vs build) |


## Quick debug checklist

- Wrong answer but plausible: re-check **buy vs build** on paper for the target and its dependencies.
- Garbage product names in `PRODUCTS`: almost always **last-input / next-row** boundary in `_split_last_input_segment`.
- `0.00`: target missing from catalog or effectively unbuildable and unbuyable.

---

## Files

| File        | Role |
|------------|------|
| `main.py`  | All logic: parse + DP/memo + stdout |
| `test_*.txt` | Sample stdin for the assignment |
