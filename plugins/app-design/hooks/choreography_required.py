#!/usr/bin/env python3
"""Hook PreToolUse (Write) : aucune NOUVELLE page sans sa chorégraphie minimale.

Une page est reconnue d'après son chemin (vues Blade, pages Next.js / Nuxt /
Astro / Svelte, fichiers .html). Elle ne peut être créée que si
<docs>/<nom>.md existe et contient les rubriques obligatoires. Modifier une
page existante reste libre.

Réglages facultatifs dans .claude/choreography.json du projet :
    {"docs": "docs/choreographie", "ignore": ["sitemap", "articles-flux"]}
"""
import json
import os
import re
import sys

RUBRIQUES = ["## Moment unique", "## Réponses aux gestes", "## Mouvement réduit", "## Ce qui ne bouge pas"]
DOSSIERS_IGNORES = re.compile(r"(^|/)(node_modules|vendor|dist|build|public/build|storage|tests?|coverage|\.git|\.next|\.nuxt)(/|$)")
VUES_TECHNIQUES = re.compile(r"^resources/views/(components|layouts|partials|mail|emails|vendor|errors)/")


def nom_de_page(relatif: str):
    if DOSSIERS_IGNORES.search(relatif):
        return None
    if relatif.startswith("resources/views/") and relatif.endswith(".blade.php"):
        if VUES_TECHNIQUES.match(relatif):
            return None
        nom = relatif[len("resources/views/"):-len(".blade.php")].replace("/", "-")
        return nom[len("pages-"):] if nom.startswith("pages-") else nom
    m = re.match(r"^(?:src/)?app/(.*?)/?page\.(tsx|jsx|ts|js)$", relatif)
    if m:
        return re.sub(r"[()\[\]]", "", m.group(1)).strip("/").replace("/", "-") or "index"
    m = re.match(r"^(?:src/)?pages/(.+)\.(tsx|jsx|vue|svelte|astro)$", relatif)
    if m and not m.group(1).startswith(("_", "api/")):
        return m.group(1).replace("/", "-")
    if relatif.endswith(".html"):
        return os.path.splitext(os.path.basename(relatif))[0]
    return None


def main() -> int:
    entree = json.load(sys.stdin)
    chemin = (entree.get("tool_input") or {}).get("file_path") or ""
    if not chemin or os.path.exists(chemin):
        return 0  # modifier une page existante n'est pas en créer une

    racine = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    relatif = os.path.relpath(chemin, racine)
    if relatif.startswith(".."):
        return 0

    reglages = {}
    fichier_reglages = os.path.join(racine, ".claude", "choreography.json")
    if os.path.exists(fichier_reglages):
        with open(fichier_reglages, encoding="utf-8") as f:
            reglages = json.load(f)

    nom = nom_de_page(relatif)
    if not nom or nom in reglages.get("ignore", []) or nom.startswith("_"):
        return 0

    docs = reglages.get("docs", "docs/choreographie")
    fiche = os.path.join(racine, docs, f"{nom}.md")

    if not os.path.isfile(fiche):
        print(
            f"Création de « {relatif} » refusée : la chorégraphie minimale de cette page n'est pas définie.\n"
            f"Lance d'abord l'agent « choregraphe » pour écrire {docs}/{nom}.md, puis recrée la page.",
            file=sys.stderr,
        )
        return 2

    with open(fiche, encoding="utf-8") as f:
        texte = f.read()
    manquantes = [r for r in RUBRIQUES if r not in texte]
    if manquantes:
        print(
            f"Création de « {relatif} » refusée : {docs}/{nom}.md est incomplète "
            f"(rubriques manquantes : {', '.join(manquantes)}). Complète-la avec l'agent « choregraphe ».",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
