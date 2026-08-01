#!/usr/bin/env python3
"""
Script de vérification et guide pour l'ajout des data-i18n dans l'app.
Ce script parse le fichier index.html et identifie les textes statiques
qui ne sont pas encore couverts par des data-i18n, en les comparant
aux traductions connues.
"""
import re
import os

SRC = "/home/amara/Amara/projets/strammara.fr/apps/claude-setup/index.html"
TRANS = "/home/amara/Amara/projets/strammara.fr/apps/claude-setup/translations.js"

# Lire les traductions FR pour avoir les textes source
with open(TRANS, 'r') as f:
    trans_js = f.read()

# Extraire les clés et valeurs FR via regex simple
fr_keys = {}
pattern = re.compile(r"(\w+):\s*'([^']*)'", re.DOTALL)

# Chercher le bloc FR
fr_match = re.search(r"fr:\s*\{([^}]+)\}", trans_js, re.DOTALL)
if fr_match:
    fr_block = fr_match.group(1)
    for m in re.finditer(r"(\w+):\s*'((?:[^'\\]|\\.)*)'", fr_block):
        fr_keys[m.group(1)] = m.group(2)

print(f"Clés FR trouvées: {len(fr_keys)}")

# Lire le HTML
with open(SRC, 'r') as f:
    html = f.read()

# Extraire les textes déjà couverts par data-i18n
existing_i18n = set(re.findall(r'data-i18n="(\w+)"', html))
print(f"data-i18n déjà présents: {len(existing_i18n)}")
print(f"\nClés manquantes (avec leur texte FR):")
for k, v in sorted(fr_keys.items()):
    if k not in existing_i18n:
        # Couper le texte pour lisibilité
        show = v[:80] + '...' if len(v) > 80 else v
        print(f"  {k}: {show}")

print(f"\nTotal clés manquantes: {len(fr_keys) - len(existing_i18n)}")
