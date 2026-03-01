import os
import json
import base64
import requests
from dotenv import load_dotenv
from langchain_core.documents import Document
from datetime import datetime, timezone

load_dotenv()

USERNAME = os.getenv("GITHUB_USERNAME", "amannkumar")
TOKEN    = os.getenv("GITHUB_TOKEN", GIHUB_API_KEY)

# ── Endpoints ──────────────────────────────────────────────────────────────────
API_BASE = "https://api.github.com"

def _headers() -> dict:
    h = {
        "Accept":               "application/vnd.github+json",
        "User-Agent":           "portfolio-scraper",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


# ── Fetchers ──────────────────────────────────────────────────────────────────

def fetch_user_profile(username: str) -> dict:
    """Fetch basic user info (bio, company, location, followers, etc.)."""
    r = requests.get(f"{API_BASE}/users/{username}", headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_repos(username: str, max_repos: int = 30) -> list[dict]:
    """Fetch non-forked repos sorted by most recently pushed."""
    r = requests.get(
        f"{API_BASE}/users/{username}/repos",
        headers=_headers(),
        params={"sort": "pushed", "direction": "desc", "per_page": max_repos, "type": "owner"},
        timeout=30,
    )
    r.raise_for_status()
    return [repo for repo in r.json() if not repo.get("fork")]


def fetch_readme(username: str, repo_name: str, max_chars: int = 600) -> str:
    """Fetch the decoded README for a repo, truncated to max_chars."""
    r = requests.get(
        f"{API_BASE}/repos/{username}/{repo_name}/readme",
        headers=_headers(),
        timeout=15,
    )
    if r.status_code == 404:
        return ""
    r.raise_for_status()
    data    = r.json()
    content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
    return content[:max_chars].strip()


def fetch_recent_commits(username: str, max_pages: int = 3) -> list[dict]:
    """
    Fetch recent PushEvents from the public events feed (up to max_pages × 100).
    Falls back to searching commits across repos if the events feed is empty,
    which happens when the account has no recent public activity in the feed window.
    """
    commits = []

    # ── Strategy 1: public events feed ────────────────────────
    for page in range(1, max_pages + 1):
        r = requests.get(
            f"{API_BASE}/users/{username}/events/public",
            headers=_headers(),
            params={"per_page": 100, "page": page},
            timeout=30,
        )
        r.raise_for_status()
        events = r.json()
        if not events:
            break
        for event in events:
            if event.get("type") != "PushEvent":
                continue
            repo_name = event.get("repo", {}).get("name", "")
            created   = event.get("created_at", "")
            for c in event.get("payload", {}).get("commits", []):
                msg = c.get("message", "").split("\n")[0]
                commits.append({
                    "repo":    repo_name,
                    "message": msg,
                    "date":    created[:10],
                })

    if commits:
        return commits

    # ── Strategy 2: fallback — search commits via repo API ────
    # Events feed only covers the last ~90 days and can be empty
    # for accounts that push infrequently. This searches each repo's
    # default branch for the 5 most recent commits.
    print("  ⚠ Events feed empty — falling back to per-repo commit search ...")
    repos = fetch_repos(username, max_repos=10)
    for repo in repos:
        repo_name    = repo.get("full_name", "")
        default_branch = repo.get("default_branch", "main")
        r = requests.get(
            f"{API_BASE}/repos/{repo_name}/commits",
            headers=_headers(),
            params={"sha": default_branch, "per_page": 5, "author": username},
            timeout=30,
        )
        if r.status_code != 200:
            continue
        for c in r.json():
            commit  = c.get("commit", {})
            msg     = commit.get("message", "").split("\n")[0]
            date    = (commit.get("author") or {}).get("date", "")[:10]
            commits.append({
                "repo":    repo_name,
                "message": msg,
                "date":    date,
            })

    # Sort by date descending
    commits.sort(key=lambda x: x["date"], reverse=True)
    return commits


# ── Document builder ──────────────────────────────────────────────────────────

def build_document(
    username:       str,
    user_profile:   dict,
    repos:          list[dict],
    recent_commits: list[dict],
) -> list[Document]:
    """
    Returns a list of Documents:
      [0] overall profile + stats + recent commits
      [1..N] one Document per repo (good for RAG chunking)
    """
    docs = []

    # ── Doc 0: User profile overview ──────────────────────────
    lines = []
    lines.append(f"GitHub Profile Summary for @{username}")
    lines.append("")
    lines.append("Profile:")
    for k in ["name", "bio", "company", "location", "blog", "email",
              "twitter_username", "public_repos", "followers", "following"]:
        v = user_profile.get(k)
        if v not in (None, "", 0):
            lines.append(f"  - {k}: {v}")

    lines.append("")
    lines.append(f"Total public repos (non-fork): {len(repos)}")

    # Top languages across all repos
    lang_counts: dict[str, int] = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    if lang_counts:
        sorted_langs = sorted(lang_counts, key=lang_counts.get, reverse=True)
        lines.append(f"Languages used: {', '.join(sorted_langs)}")

    # Recent commits
    if recent_commits:
        lines.append("")
        lines.append(f"Recent Commits (last {len(recent_commits)}):")
        for c in recent_commits[:20]:
            lines.append(f"  - [{c['date']}] {c['repo']}: {c['message']}")

    docs.append(Document(
        page_content="\n".join(lines),
        metadata={
            "source":      f"https://github.com/{username}",
            "source_type": "github_profile",
            "username":    username,
        },
    ))

    # ── Docs 1..N: One doc per repo ───────────────────────────
    for repo in repos:
        name        = repo.get("name", "")
        description = repo.get("description") or ""
        language    = repo.get("language") or "N/A"
        stars       = repo.get("stargazers_count", 0)
        forks       = repo.get("forks_count", 0)
        topics      = repo.get("topics") or []
        pushed_at   = (repo.get("pushed_at") or "")[:10]
        html_url    = repo.get("html_url", "")

        readme = fetch_readme(username, name)

        repo_lines = []
        repo_lines.append(f"GitHub Repository: {name}")
        repo_lines.append(f"  URL:         {html_url}")
        repo_lines.append(f"  Description: {description}")
        repo_lines.append(f"  Language:    {language}")
        repo_lines.append(f"  Stars:       {stars}  |  Forks: {forks}")
        repo_lines.append(f"  Last pushed: {pushed_at}")
        if topics:
            repo_lines.append(f"  Topics:      {', '.join(topics)}")
        if readme:
            repo_lines.append("")
            repo_lines.append("  README (excerpt):")
            for line in readme.splitlines():
                repo_lines.append(f"    {line}")

        docs.append(Document(
            page_content="\n".join(repo_lines),
            metadata={
                "source":      html_url,
                "source_type": "github_repo",
                "username":    username,
                "repo":        name,
                "language":    language,
                "stars":       stars,
            },
        ))

    return docs


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Fetching GitHub profile for @{USERNAME} ...")
    user_profile = fetch_user_profile(USERNAME)

    print("Fetching repositories ...")
    repos = fetch_repos(USERNAME, max_repos=30)
    print(f"  → {len(repos)} non-fork repos")

    print("Fetching recent commits ...")
    recent_commits = fetch_recent_commits(USERNAME)
    print(f"  → {len(recent_commits)} commit(s) found")

    docs = build_document(USERNAME, user_profile, repos, recent_commits)

    os.makedirs("../data/json_files", exist_ok=True)
    os.makedirs("../data/text_files", exist_ok=True)

    # Raw JSON
    raw = {
        "user_profile":   user_profile,
        "repos":          repos,
        "recent_commits": recent_commits,
    }
    with open("../data/json_files/github_profile.json", "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

    # Human-readable RAG text (all docs concatenated)
    with open("../data/text_files/github_profile.txt", "w", encoding="utf-8") as f:
        for i, doc in enumerate(docs):
            if i > 0:
                f.write("\n\n" + "─" * 60 + "\n\n")
            f.write(doc.page_content)

    print(f"\nSaved → ../data/json_files/github_profile.json  and  ../data/text_files/github_profile.txt")
    print(f"Total documents: {len(docs)}  (1 profile + {len(docs)-1} repos)")
    print("\n── Profile document preview ──────────────────────────────────")
    print(docs[0].page_content)