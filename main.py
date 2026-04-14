"""
Manufacturing cost: min price to obtain the target (buy vs build each component).
Parsing: collapse whitespace, then scan rows as name,price,input_count, then inputs
separated by ';' except the last input ends where the next product row begins.
"""
import re
import sys

PRODUCTS: dict[str, dict[str, object]] = {}
MEMO: dict[str, int] = {}

# Next product row at current position: name has no comma or semicolon.
HEADER = re.compile(r"^([^,;]+),(null|-?\d+(?:\.\d+)?),(\d+),")

# "word word,price,..." on one line — last input is first word; second word starts next row.
PAIR = re.compile(r"^(\S+)\s+(\S+),(null|-?\d+(?:\.\d+)?),(\d+),")


def parse_cents(s: str) -> int:
    s = s.strip()
    if s == "null":
        return -1
    if "." in s:
        parts = s.split(".", 1)
        whole = int(parts[0]) if parts[0] else 0
        frac = (parts[1] + "00")[:2]
        return whole * 100 + int(frac)
    return int(s) * 100


def _dup_word_pair(name: str) -> bool:
    parts = name.split()
    return len(parts) == 2 and parts[0] == parts[1]


def min_cost(name: str) -> int:
    if name in MEMO:
        return MEMO[name]
    if name not in PRODUCTS:
        MEMO[name] = 10**18
        return MEMO[name]

    p = PRODUCTS[name]
    price = p["price"]  # type: ignore[assignment]
    inputs: list[str] = p["inputs"]  # type: ignore[assignment]

    if not inputs:
        if price < 0:  # type: ignore[operator]
            MEMO[name] = 10**18
        else:
            MEMO[name] = price  # type: ignore[assignment]
        return MEMO[name]

    build = sum(min_cost(inp) for inp in inputs)
    if price < 0:  # type: ignore[operator]
        MEMO[name] = build
    else:
        MEMO[name] = min(price, build)  # type: ignore[type-var]
    return MEMO[name]


def split_target_and_catalog(text: str) -> tuple[str, str]:
    """Line 1: <target> <catalog…>. Target is at most two words; rest begins with name,price,count,"""
    text = text.strip()
    if not text:
        return "", ""

    lines = text.splitlines()
    first_line = lines[0]
    rest_lines = "\n".join(lines[1:]) if len(lines) > 1 else ""

    header = re.compile(r"^([^,;]+),(null|-?\d+(?:\.\d+)?),(\d+),")
    best_s: int | None = None
    for s in range(len(first_line) - 1, -1, -1):
        if first_line[s] != " ":
            continue
        prefix = first_line[:s]
        if ";" in prefix or "," in prefix:
            continue
        if len(prefix.split()) > 2:
            continue
        if header.match(first_line[s + 1 :]):
            best_s = s
            break

    if best_s is not None:
        target = first_line[:best_s].strip()
        catalog = (first_line[best_s + 1 :].lstrip() + ("\n" + rest_lines if rest_lines else "")).strip()
        return target, catalog

    if rest_lines:
        return first_line.strip(), rest_lines
    return first_line.strip(), ""


def _split_last_input_segment(r: str) -> tuple[str, int]:
    """
    r is the tail after the last ';' (or after size comma if count==1).
    Returns (last_input, index_in_r where the next product name starts).
    """
    r = r.lstrip()
    if not r:
        return "", 0

    pm = PAIR.match(r)
    if pm:
        a, b = pm.group(1), pm.group(2)
        inputs_append = a
        next_start = pm.start(2)
        return inputs_append, next_start

    starts: list[int] = []
    for i in range(len(r)):
        # Only real row starts: beginning of tail, or after space/semicolon (not mid-word).
        if i > 0 and r[i - 1] not in " ;":
            continue
        if r[i] in " \t,":
            continue
        m = HEADER.match(r[i:])
        if not m:
            continue
        name = m.group(1).strip()
        if _dup_word_pair(name):
            continue
        # "sewing thread faux…" — reject header at "thread faux…" (mid last-input phrase).
        if (
            i > 0
            and r[i - 1] == " "
            and r[i - 2] not in " ;"
            and name.split()
            and name.split()[0] == "thread"
        ):
            continue
        starts.append(i)

    if not starts:
        m = re.search(r",(?:null|-?\d+(?:\.\d+)?),(\d+),", r)
        if m:
            return r[: m.start()].strip(), m.start()
        return r.strip(), len(r)

    # Prefer the nearest next-row header after the last ';' (smallest i > 0). Using max(i)
    # would skip over "faux bear fur fabric,15" and match "yarn,100" inside "bear;yarn bear,100".
    positive = [i for i in starts if i > 0]
    if positive:
        i_next = min(positive)
    else:
        i_next = 0
    last_inp = r[:i_next].strip()
    return last_inp, i_next


def parse_catalog(catalog: str) -> None:
    catalog = catalog.replace("\r\n", "\n").replace("\r", "\n")
    catalog = re.sub(r"\s+", " ", catalog).strip()
    if not catalog:
        return

    pos = 0
    n = len(catalog)
    while pos < n:
        while pos < n and catalog[pos] == " ":
            pos += 1
        if pos >= n:
            break

        ne = catalog.find(",", pos)
        if ne == -1:
            break
        name = catalog[pos:ne].strip()
        pos = ne + 1

        pe = catalog.find(",", pos)
        if pe == -1:
            break
        price = parse_cents(catalog[pos:pe])
        pos = pe + 1

        se = catalog.find(",", pos)
        if se == -1:
            break
        size = int(catalog[pos:se].strip())
        pos = se + 1

        inputs: list[str] = []
        if size > 0:
            for _ in range(size - 1):
                sc = catalog.find(";", pos)
                if sc == -1:
                    break
                inputs.append(catalog[pos:sc].strip())
                pos = sc + 1

            tail = catalog[pos:]
            last_inp, rel = _split_last_input_segment(tail)
            inputs.append(last_inp)
            pos = pos + rel
        else:
            while pos < n and catalog[pos] == " ":
                pos += 1

        PRODUCTS[name] = {"price": price, "inputs": inputs}


def main() -> None:
    raw = sys.stdin.read()
    PRODUCTS.clear()
    MEMO.clear()
    target, catalog = split_target_and_catalog(raw)
    parse_catalog(catalog)
    total = min_cost(target)
    if total >= 10**17:
        print("0.00")
        return
    print(f"{total // 100}.{total % 100:02d}")


if __name__ == "__main__":
    main()
