import re
from decimal import Decimal
from itertools import combinations

_TOKEN = re.compile(
    r"(?<![\w.,])("
    r"\d{1,3}(?:[\u00a0\u202f ]\d{3})+(?:,\d+)?"
    r"|\d{1,3}(?:\.\d{3})+(?:,\d+)?"
    r"|\d+(?:[.,]\d+)?"
    r")(?![\w])(\s?%)?"
)
_HEDGE = re.compile(r"(hơn|gần|khoảng|xấp xỉ|trên|dưới|tầm|~)\s*$", re.IGNORECASE)
_MAX_SUBSET_ROWS = 10
_MAX_PAIR_ROWS = 50


def _to_float(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        return float(value)
    return None


def _numeric_columns(rows):
    if not rows:
        return {}
    cols = {}
    for key in rows[0].keys():
        values = [_to_float(r.get(key)) for r in rows]
        if all(v is not None for v in values):
            cols[key] = values
    return cols


def _build_candidates(rows):
    cols = _numeric_columns(rows)
    n = len(rows)
    general = set()
    percent = set()

    general.add(float(n))
    for k in range(0, n + 1):
        general.add(float(k))

    for values in cols.values():
        if not values:
            continue
        total = sum(values)
        general.update(values)
        general.update([total, total / len(values), max(values), min(values)])
        sorted_vals = sorted(values)
        mid = len(sorted_vals) // 2
        median = sorted_vals[mid] if len(sorted_vals) % 2 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
        general.add(median)

        percent.update(values)
        if all(abs(v) <= 1 for v in values):
            percent.update(v * 100 for v in values)

        if total:
            if n <= _MAX_SUBSET_ROWS:
                for size in range(1, n + 1):
                    for combo in combinations(values, size):
                        subtotal = sum(combo)
                        general.add(subtotal)
                        percent.add(subtotal / total * 100)
            else:
                for v in values:
                    percent.add(v / total * 100)

        if n <= _MAX_PAIR_ROWS:
            for a, b in combinations(values, 2):
                general.add(abs(a - b))
                if b:
                    general.add(a / b)
                    percent.add((a - b) / abs(b) * 100)
                    percent.add(a / b * 100)
                if a:
                    general.add(b / a)
                    percent.add((b - a) / abs(a) * 100)
                    percent.add(b / a * 100)

    col_names = list(cols.keys())
    if n <= _MAX_PAIR_ROWS:
        for i in range(n):
            for x, y in combinations(col_names, 2):
                a, b = cols[x][i], cols[y][i]
                general.add(abs(a - b))
                if b:
                    general.add(a / b)
                    percent.add(a / b * 100)
                if a:
                    general.add(b / a)
                    percent.add(b / a * 100)

    return general, percent


def _interpretations(raw):
    text = raw.replace("\u00a0", " ").replace("\u202f", " ")
    interps = []
    if re.fullmatch(r"\d{1,3}(?: \d{3})+(?:,\d+)?", text):
        merged = text.replace(" ", "").replace(",", ".")
        interps.append([float(merged)])
        interps.append([float(p) for p in re.split(r"[ ]", text.replace(",", "."))])
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", text):
        interps.append([float(text.replace(".", "").replace(",", "."))])
        if text.count(".") == 1 and "," not in text:
            interps.append([float(text)])
    elif re.fullmatch(r"\d+,\d+", text):
        interps.append([float(text.replace(",", "."))])
        if re.fullmatch(r"\d{1,3},\d{3}", text):
            interps.append([float(text.replace(",", ""))])
    else:
        interps.append([float(text)])
    decimals = 0
    m = re.search(r"[.,](\d+)$", text)
    if m and not re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", text):
        decimals = len(m.group(1))
    return interps, decimals


def _matches(value, decimals, pool, hedge, is_percent):
    for c in pool:
        if is_percent:
            tol = 0.5 * 10 ** -decimals + 0.06
        else:
            rel = 0.10 if hedge else 0.005
            tol = max(10 ** -decimals, rel * abs(c))
        if abs(value - c) <= tol:
            return True
    return False


def find_unverified_numbers(insight, rows):
    if not insight:
        return []
    cleaned = insight.replace("**", "").replace("*", "")
    general, percent = _build_candidates(rows or [])
    unverified = []

    for match in _TOKEN.finditer(cleaned):
        raw = match.group(1)
        is_percent = match.group(2) is not None
        interps, decimals = _interpretations(raw)
        hedge = bool(_HEDGE.search(cleaned[max(0, match.start() - 14):match.start()]))

        def verified(vals):
            for v in vals:
                if v == 0:
                    continue
                pool = percent if is_percent else general
                if not _matches(v, decimals, pool, hedge, is_percent):
                    return False
            return True

        if any(verified(vals) for vals in interps):
            continue

        primary = interps[0][0]
        if primary == int(primary) and abs(primary) <= 10:
            continue
        if primary == int(primary) and 1900 <= primary <= 2100:
            continue

        unverified.append(raw + ("%" if is_percent else ""))

    seen = []
    for token in unverified:
        if token not in seen:
            seen.append(token)
    return seen[:5]