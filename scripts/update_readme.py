import os
import requests
from pathlib import Path

TOKEN = os.environ["TOKEN"]

# Top-level categories
CATEGORIES = {
    "Elin",
    "ProjectZomboid",
    "Rimworld",
    "SkyrimSpecialEdition",
    "Starbound",
    "Starsector",
    "Stellaris",
}

# Repos to exclude completely
EXCLUDED_REPOS = {
    ".github",
    "github-actions",
}

ORG = "darkbordermanmodding"


def fetch_repositories():
    """Fetch all repositories from the org, excluding EXCLUDED_REPOS"""
    repos = []
    page = 1

    while True:
        resp = requests.get(
            f"https://api.github.com/orgs/{ORG}/repos",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Accept": "application/vnd.github+json",
            },
            params={"per_page": 100, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1

    return [r for r in repos if r["name"] not in EXCLUDED_REPOS]


def categorize_repositories(repos):
    """
    Categorize repos by matching category name in repo name.
    Returns dict: {category_name: [repo1, repo2, ...]}
    """
    categorized = {cat: [] for cat in CATEGORIES}
    uncategorized = []

    for repo in repos:
        matched = False
        name_lower = repo["name"].lower()
        for cat in CATEGORIES:
            if cat.lower() in name_lower:
                categorized[cat].append(repo)
                matched = True
                break
        if not matched:
            uncategorized.append(repo)

    return categorized, uncategorized


def generate_markdown(categorized, uncategorized):
    """Generate README.md content"""
    lines = ["# Mods made by me", ""]

    for cat, repos in categorized.items():
        if not repos:
            continue
        lines.append(f"* {cat}")
        for repo in sorted(repos, key=lambda r: r["name"].lower()):
            lines.append(f"  * {repo['name']} ([source]({repo['html_url']}))")
        lines.append("")  # blank line after each category

    if uncategorized:
        lines.append("# Others")
        for repo in sorted(uncategorized, key=lambda r: r["name"].lower()):
            lines.append(f"  * {repo['name']} ([source]({repo['html_url']}))")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    repos = fetch_repositories()
    categorized, uncategorized = categorize_repositories(repos)
    content = generate_markdown(categorized, uncategorized)

    readme_path = Path("profile/README.md")
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(content, encoding="utf-8")
