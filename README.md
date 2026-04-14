# Gelber Group Take Home — Manufacturing Cost

## What it does

Given a **target** product and a **catalog** of products (each with an optional buy price and a recipe: ordered list of inputs), the program prints the **minimum dollars-and-cents cost** to obtain the target. For every product you may **buy** at its list price or **build** by paying the sum of minimum costs of its inputs (recursively). Internal math uses **integer cents**; stdout prints **`dollars.cc`** (e.g. `61.00`).

## How to run

From this directory:

**PowerShell**

```powershell
Get-Content test_1.txt | python main.py
```

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

## Dependencies

- Python 3.x  
- Standard library only: `sys`, `re`

---

## How to study this codebase

Read in this order — each layer builds on the last.

### 1. Core economics (`min_cost`)

Open `min_cost` in `main.py`. That is the whole optimization:

- **Memoization** (`MEMO`): each product’s minimum cost is computed once per run.
- **Unknown product**: treated as infinitely expensive (`10**18`) so recipes that reference missing items don’t silently look cheap.
- **No inputs (`size` 0 in data → empty `inputs`)**: you must **buy**; `null` / unpurchasable price → infinite cost.
- **Has inputs**: cost = **min**(purchase price if not `null`, **sum** of `min_cost` over each input name).

There is no separate “quantity × input” in the parsed structure: each listed input contributes **one** `min_cost` term in the sum (matches the assignment’s row format).

**Study tip:** Trace `min_cost("teddy bear")` on paper after you’ve parsed `test_3.txt` into `PRODUCTS` — compare buy vs build at each node.

### 2. Money (`parse_cents`)

Prices become **integer cents**. `"null"` → `-1` (meaning “not for sale” / must build if inputs exist). This keeps floating-point out of comparisons.

### 3. Splitting target vs catalog (`split_target_and_catalog`)

The first line of stdin mixes **target** (at most **two words**) and the start of the **catalog** with **no** comma/semicolon in the target part. The code finds the **rightmost** space where:

- the left part has ≤ 2 words and no `,` / `;`, and  
- the right part begins like a product row: `name,price_or_null,count,`.

**Study tip:** Try malformed first lines mentally — why “rightmost” space matters when product names can be long.

### 4. Catalog scan (`parse_catalog`)

- **Normalize**: `re.sub(r"\s+", " ", …)` so wrapped PDF-style line breaks don’t break parsing.
- **Per product**: read `name`, `price`, `input_count`, then:
  - for `count - 1` inputs: split on **`;`**
  - **last input**: everything after the last `;` until the **next product row** starts — not necessarily at the next `;` (because the last segment can contain commas inside names).

So the subtle part is **only** the boundary between the last input of product A and the **first field (name)** of product B.

### 5. Last input boundary (`_split_last_input_segment`)

This function takes the **tail** after the last `;` (or the whole input list when count is 1) and returns `(last_input_string, offset_where_next_product_starts)`.

It uses:

- **`PAIR`**: when the tail looks like `word1 word2,price,count,` — the last input is `word1`; `word2` starts the next product (handles things like `yarn bear,100,...`).
- Else **`HEADER`** matches at **row boundaries** (start of tail, or after space/semicolon) to find candidate **next product** headers, with guards for:
  - duplicate-word product names (`car car`, …) via `_dup_word_pair`
  - false headers inside a long last-input phrase (e.g. `sewing thread faux…` — rejecting spurious `thread …` headers)
- Among valid next-row starts with index **> 0**, take **`min`** (nearest next header), not `max` — otherwise you attach the wrong row to the previous product’s last input.

**Study tip:** Copy a messy tail from `test_3.txt` into a scratch string after normalization and step through `_split_last_input_segment` by hand once; that’s the fastest way to “get” the parser.

### 6. Entry point (`main`)

Clears global `PRODUCTS` and `MEMO`, parses stdin, runs `min_cost(target)`, prints `dollars.cc` or `0.00` if the cost is still “infinite” (guard for missing/unbuildable targets).

---

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
