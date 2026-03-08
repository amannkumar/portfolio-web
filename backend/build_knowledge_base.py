import os
import json
from dotenv import load_dotenv

load_dotenv()

# ── Import scrapers ────────────────────────────────────────────────────────────
from scrapers.github_scraper import (
    fetch_user_profile,
    fetch_repos,
    fetch_recent_commits,
    build_document as build_github_docs,
)
from scrapers.leetcode_scraper import (
    fetch_leetcode_profile,
    fetch_recent_ac_submissions,
    build_document as build_leetcode_doc,
)
from scrapers.resume_scraper import scrape_all_pdfs

GITHUB_USERNAME  = os.getenv("GITHUB_USERNAME", "amannkumar")
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME", "amannkumar")

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json")


def scrape_github() -> list[dict]:
    print("\n── GitHub ────────────────────────────────────────────────")
    profile        = fetch_user_profile(GITHUB_USERNAME)
    repos          = fetch_repos(GITHUB_USERNAME, max_repos=30)
    recent_commits = fetch_recent_commits(GITHUB_USERNAME)
    print(f"  profile: ✓  |  repos: {len(repos)}  |  commits: {len(recent_commits)}")

    docs = build_github_docs(GITHUB_USERNAME, profile, repos, recent_commits)
    return [{"source": d.metadata["source_type"], "content": d.page_content, "metadata": d.metadata}
            for d in docs]


def scrape_leetcode() -> list[dict]:
    print("\n── LeetCode ──────────────────────────────────────────────")
    data        = fetch_leetcode_profile(LEETCODE_USERNAME)
    recent_subs = fetch_recent_ac_submissions(LEETCODE_USERNAME, limit=20)
    print(f"  profile: ✓  |  recent AC subs: {len(recent_subs)}")

    doc = build_leetcode_doc(LEETCODE_USERNAME, data, recent_subs)
    return [{"source": doc.metadata["source_type"], "content": doc.page_content, "metadata": doc.metadata}]

def scrape_pdfs() -> list[dict]:
    print("\n── PDFs ──────────────────────────────────────────────────")
    docs = scrape_all_pdfs()
    print(f"  total PDF chunks: {len(docs)}")
    return [
        {"source": d.metadata["source_type"], "content": d.page_content, "metadata": d.metadata}
        for d in docs
    ]


def build():
    print("Building knowledge base...")
    chunks: list[dict] = []

    try:
        chunks.extend(scrape_github())
    except Exception as e:
        print(f"  ✗ GitHub scrape failed: {e}")

    try:
        chunks.extend(scrape_leetcode())
    except Exception as e:
        print(f"  ✗ LeetCode scrape failed: {e}")

    try:
        chunks.extend(scrape_pdfs())
    except Exception as e:
        print(f"  ✗ PDF scrape failed: {e}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Saved {len(chunks)} chunk(s) → {OUTPUT_PATH}")
    total_chars = sum(len(c["content"]) for c in chunks)
    print(f"  Total content size: ~{total_chars:,} chars  (~{total_chars // 4:,} tokens)")


if __name__ == "__main__":
    build()
