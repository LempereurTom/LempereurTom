"""Met à jour la section « Derniers dépôts publics » du README de profil.

Lit les dépôts publics de l'utilisateur via l'API GitHub et réécrit le
tableau entre les marqueurs <!-- PROJETS:START --> et <!-- PROJETS:END -->.
Les dépôts privés n'apparaissent jamais.
"""
import json
import os
import re
import urllib.request

USER = os.environ.get("GH_USER", "LempereurTom")
LIMIT = 6
README = "README.md"
# Dépôts à ne jamais afficher dans la liste automatique
EXCLUDE = {"portfolio-custom"}

req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&sort=pushed",
    headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-updater"},
)
token = os.environ.get("GITHUB_TOKEN")
if token:
    req.add_header("Authorization", f"Bearer {token}")

with urllib.request.urlopen(req) as resp:
    repos = json.load(resp)

repos = [
    r for r in repos
    if not r["fork"] and not r["archived"] and not r["private"]
    and r["name"].lower() != USER.lower()
    and r["name"] not in EXCLUDE
]
repos.sort(key=lambda r: r["pushed_at"], reverse=True)


def cell(text):
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


rows = ["| Projet | Description | Langage | Mis à jour |", "|---|---|---|---|"]
for r in repos[:LIMIT]:
    link = f"**[{cell(r['name'])}]({r['html_url']})**"
    if r.get("homepage"):
        link += f" · [site]({r['homepage']})"
    rows.append(
        f"| {link} | {cell(r['description'])} | {cell(r['language'])} | {r['pushed_at'][:10]} |"
    )
table = "\n".join(rows) if repos else "_Aucun dépôt public pour l'instant._"

with open(README, encoding="utf-8") as f:
    content = f.read()

new = re.sub(
    r"(<!-- PROJETS:START -->).*?(<!-- PROJETS:END -->)",
    lambda m: f"{m.group(1)}\n{table}\n{m.group(2)}",
    content,
    flags=re.S,
)

if new != content:
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print("README mis à jour")
else:
    print("Rien à changer")
