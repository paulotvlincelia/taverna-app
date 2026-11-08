#!/usr/bin/env python3
"""Recalcula o contraste WCAG 2.x dos pares declarados no DESIGN.md (5.1) a partir de tokens.json.

Uso: python3 measure_contrast.py   (lê tokens.json e grava contrast.json na mesma pasta)
Sai com código 1 se algum par ficar abaixo do limiar. Cores opacas apenas.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
PAIRS = [  # (frente, fundo, limiar)
    ("text", "canvas", 4.5), ("text", "outgoing", 4.5),
    ("textSecondary", "surface", 4.5), ("textSecondary", "outgoing", 4.5),
    ("textSecondary", "surfaceMuted", 4.5), ("onPrimary", "primary", 4.5),
    ("primary", "canvas", 4.5), ("accent", "surface", 4.5), ("accent", "outgoing", 4.5),
    ("accent", "innerLight", 3.0), ("warning", "surface", 4.5), ("danger", "surface", 4.5),
    ("success", "surface", 4.5), ("onPrimary", "success", 3.0), ("border", "surface", 3.0),
    ("border", "canvas", 3.0), ("focus", "canvas", 3.0),
]

def lum(hex_):
    h = hex_.lstrip("#")
    def ch(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(h[i:i + 2]) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)

tokens = json.loads((HERE / "tokens.json").read_text(encoding="utf-8"))
color = tokens["color"]
results, failed = [], False
for fg, bg, minimum in PAIRS:
    for theme in ("light", "dark"):
        value = ratio(color[fg][theme], color[bg][theme])
        ok = value >= minimum
        failed |= not ok
        results.append({"pair": f"{fg}/{bg}", "theme": theme, "foreground": color[fg][theme],
                        "background": color[bg][theme], "ratio": round(value, 4),
                        "minimum": minimum, "pass": ok})

report = {"tokensVersion": tokens.get("version"), "method": "WCAG 2.x relative luminance, opaque sRGB",
          "pairs": len(PAIRS), "results": results}
(HERE / "contrast.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
for r in results:
    print(f"{r['pair']:<28} {r['theme']:<5} {r['ratio']:>6.2f}  {'OK' if r['pass'] else 'FALHA'}")
sys.exit(1 if failed else 0)
