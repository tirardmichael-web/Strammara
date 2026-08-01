#!/usr/bin/env python3
"""
Vérifie quels textes visibles du HTML n'ont PAS de data-i18n et dont la clé
existe dans translations.js. Compare le HTML avec la liste des clés FR.
Si des textes sont encore sans data-i18n mais que la clé existe, il les signale.
"""
import re, sys

SRC = "/home/amara/Amara/projets/strammara.fr/apps/claude-setup/index.html"
TRANS = "/home/amara/Amara/projets/strammara.fr/apps/claude-setup/translations.js"

with open(TRANS,'r') as f: tjs = f.read()

# Extraire bloc FR
s = tjs.find("fr: {")
e = tjs.find("pt:", s)
fr_block = tjs[s:e]

# Toutes les clés FR
fr_keys = {}
for m in re.finditer(r"(\w+):\s*'((?:[^'\\]|\\.)*)'", fr_block):
    fr_keys[m.group(1)] = m.group(2)
print(f"Clés FR dans traductions: {len(fr_keys)}")

with open(SRC,'r') as f: html = f.read()

# data-i18n déjà présents
existing = set(re.findall(r'data-i18n="(\w+)"', html))
print(f"data-i18n dans HTML: {len(existing)}")
print(f"Clés FR non utilisées dans HTML:")
unused = [k for k in fr_keys if k not in existing]
for k in unused:
    v = fr_keys[k]
    if len(v) > 70: v = v[:67]+"..."
    print(f"  {k}: {v}")

print(f"\nTotal clés FR non utilisées: {len(unused)}")
