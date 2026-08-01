#!/usr/bin/env python3
"""
Applique les data-i18n à tous les textes manquants dans l'app.
Parcourt les clés FR et cherche le texte correspondant dans le HTML
pour le remplacer par une version avec data-i18n.
"""
import re
import json

SRC = "/home/amara/Amara/projets/strammara.fr/apps/claude-setup/index.html"
TRANS = "/home/amara/Amara/projets/strammara.fr/apps/claude-setup/translations.js"

with open(TRANS, 'r') as f:
    trans_js = f.read()

# Extraire toutes les clés FR
fr_keys = {}
# Parse plus robuste - capture les valeurs entre quotes simples
block_pattern = re.compile(r'(\w+):\s*\{', re.DOTALL)

# Chercher le bloc FR en comptant les accolades
idx = 0
fr_start = trans_js.find("fr: {")
if fr_start > 0:
    depth = 0
    brace_start = trans_js.find("{", fr_start)
    i = brace_start
    while i < len(trans_js):
        if trans_js[i] == '{': depth += 1
        elif trans_js[i] == '}': depth -= 1
        if depth == 0: break
        i += 1
    fr_block = trans_js[brace_start:i+1]
    
    # Extraire les paires clé:valeur avec regex
    for m in re.finditer(r"(\w+):\s*'((?:[^'\\]|\\.)*)'", fr_block):
        fr_keys[m.group(1)] = m.group(2)

print(f"Clés FR trouvées: {len(fr_keys)}")

with open(SRC, 'r') as f:
    html = f.read()

# Récupérer les clés déjà présentes
existing = set(re.findall(r'data-i18n="(\w+)"', html))
print(f"data-i18n déjà présents: {len(existing)}")

# Pour chaque clé FR pas encore dans le HTML, chercher le texte et le remplacer
# On trie les clés par longueur de texte décroissante pour éviter les remplacements partiels
missing = [(k, v) for k, v in fr_keys.items() if k not in existing]
missing.sort(key=lambda x: -len(x[1]))

count = 0
for key, fr_text in missing:
    if not fr_text or len(fr_text) < 3:
        continue
    
    # Échapper les caractères spéciaux pour la regex
    # On cherche le texte FR exact dans le HTML
    escaped = re.escape(fr_text)
    
    # Remplacer le texte par data-i18n si on le trouve dans un élément textuel
    # On évite les attributs, les balises déjà modifiées, etc.
    pattern_to_find = r'(?<!data-i18n="[^"]*)(?<!>)(>)([^<]*?)' + escaped + r'([^<]*?)(?=<|$)'
    
    # Version plus simple: chercher le texte exact dans le HTML et le remplacer
    # en ajoutant data-i18n="key" quelque part autour
    # On cherche: ">TEXTE<" ou >= more stuff TEXTE< etc.
    
    # Approche: pour les textes dans des balises simples
    # On remplace : >TEXTE< par ><span data-i18n="key">TEXTE</span><
    # Mais seulement si TEXTE est vraiment le contenu exact d'une balise
    
    # Version simple: on cherche chaque occurrence et on décide
    new_html = html
    occurences = []
    
    # Stratégie: trouver les endroits où le texte apparaît comme contenu de balise
    parts = html.split('>')
    replacements = []
    
    for pi, part in enumerate(parts):
        if pi == 0: continue
        # Chaque part est ce qui vient après un >
        # Le début de part est un attribut si <tag, ou du texte si pas de <
        
        # Chercher le texte FR dans cette partie (avant le prochain <)
        bracket_pos = part.find('<')
        text_part = part[:bracket_pos] if bracket_pos >= 0 else part
        
        if fr_text in text_part:
            # Vérifier qu'on n'est pas déjà dans un data-i18n
            prev_bracket = html[0:html.index('>' + part)].rfind('<') if '>' + part in html else -1
            prev_section = html[html.rfind('<', 0, html.index('>' + part)):html.index('>' + part)] if html.index('>' + part) > 0 else ""
            
            if 'data-i18n="' + key + '"' not in html:
                # Remplacer dans cette partie
                start = text_part.index(fr_text)
                end = start + len(fr_text)
                
                new_text_part = (text_part[:start] + 
                                '<span data-i18n="' + key + '">' + 
                                fr_text + 
                                '</span>' + 
                                text_part[end:])
                
                new_part = part[:bracket_pos].replace(text_part, new_text_part) + part[bracket_pos:] if bracket_pos >= 0 else part.replace(text_part, new_text_part)
                parts[pi] = new_part
                count += 1
                break  # Une seule occurrence par clé
    
    html = '>'.join(parts)

print(f"Nouvelles traductions ajoutées: {count}")
print(f"Total data-i18n: {len(existing) + count}")

with open(SRC, 'w') as f:
    f.write(html)

print("✅ Fichier mis à jour")
