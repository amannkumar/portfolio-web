import os
import json
import requests
from dotenv import load_dotenv
from langchain_core.documents import Document
from datetime import datetime

load_dotenv()

USERNAME = os.getenv("LEETCODE_USERNAME", "amannkumar")

GRAPHQL_URL = "https://leetcode.com/graphql/"
# alfa-leetcode-api is a free public wrapper that already handles LeetCode auth
# useing this to get recent submissions
ALFA_BASE   = "https://alfa-leetcode-api.onrender.com"

GRAPHQL_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent":   "Mozilla/5.0",
    "Referer":      "https://leetcode.com",
}
PROFILE_QUERY = """
query userProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      ranking
      realName
    }
    submitStats {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
      totalSubmissionNum {
        difficulty
        count
        submissions
      }
    }
    badges {
      id
      displayName
      icon
    }
    activeBadge {
      displayName
      icon
    }
    submissionCalendar
  }
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    totalParticipants
    topPercentage
  }
}
"""

def fetch_leetcode_profile(username: str) -> dict:
    """Fetch profile & contest data via the public LeetCode GraphQL API."""
    payload = {"query": PROFILE_QUERY, "variables": {"username": username}}
    r = requests.post(GRAPHQL_URL, headers=GRAPHQL_HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]

def fetch_recent_ac_submissions(username: str, limit: int = 20) -> list[dict]:
    """
    Fetch recent accepted submissions via alfa-leetcode-api — no LEETCODE_SESSION
    cookie needed. The direct LeetCode GraphQL endpoint (recentAcSubmissions)
    returns HTTP 400 for unauthenticated requests; this wrapper fixes that.

    Endpoint: GET /{username}/acSubmission?limit={limit}
    Returns items like:
      {"title": "Two Sum", "titleSlug": "two-sum", "timestamp": "1700000000", "lang": "python3"}
    """
    url = f"{ALFA_BASE}/{username}/acSubmission"
    r = requests.get(url, params={"limit": limit}, timeout=30)
    r.raise_for_status()
    data = r.json()
    # alfa-leetcode-api wraps submissions under "submission" key
    return data.get("submission", []) if isinstance(data, dict) else data

def format_timestamp(ts) -> str:
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return str(ts)
    

def build_document(username: str, data: dict, recent_subs: list[dict]) -> Document:
    mu      = data.get("matchedUser") or {}
    profile = mu.get("profile") or {}
    stats   = mu.get("submitStats") or {}
    ac      = stats.get("acSubmissionNum") or []
    contest = data.get("userContestRanking") or {}

    lines = []
    lines.append(f"LeetCode Profile Summary for @{username}")
    lines.append("")
    lines.append("Profile:")

    lines.append("Profile:")
    for k in ["realName","ranking"]:
        v = profile.get(k)
        if v not in (None, "", []):
            lines.append(f"  - {k}: {v}")
    
    lines.append("")
    lines.append("Solved / Submission Stats:")
    for row in ac:
        lines.append(
            f"  - {row['difficulty']}: solved={row['count']}, "
            f"submissions={row['submissions']}"
        )
    
    if contest:
        lines.append("")
        lines.append("Contest Rankings:")
        for k in ["rating", "globalRanking", "attendedContestsCount",
                  "topPercentage", "totalParticipants"]:
            if contest.get(k) is not None:
                lines.append(f"  - {k}: {contest[k]}")

    if mu.get("badges"):
        lines.append("")
        lines.append("Badges:")
        for b in mu["badges"]:
            lines.append(f"  - {b.get('displayName')}")
    
    lines.append("")
    if recent_subs:
        lines.append(f"Recent Accepted Submissions (last {len(recent_subs)}):")
        for sub in recent_subs:
            date  = format_timestamp(sub.get("timestamp"))
            title = sub.get("title", "Unknown")
            lang  = sub.get("lang", "?")
            slug  = sub.get("titleSlug", "")
            url   = f"https://leetcode.com/problems/{slug}/"
            lines.append(f"  - [{date}] {title} ({lang})  →  {url}")
    else:
        lines.append("Recent Accepted Submissions: none returned")

    cal = mu.get("submissionCalendar")
    if cal:
        lines.append("")
        lines.append("Submission calendar (raw JSON string):")
        lines.append(cal)

    return Document(
        page_content="\n".join(lines),
        metadata={
            "source":      f"https://leetcode.com/u/{username}/",
            "source_type": "leetcode_profile",
            "username":    username,
        },
    )

if __name__ == "__main__":
    profile_data = fetch_leetcode_profile(USERNAME)

    recent_subs = fetch_recent_ac_submissions(USERNAME, limit=20)
    print(f"  → {len(recent_subs)} submission(s) returned")

    doc = build_document(USERNAME, profile_data, recent_subs)

    os.makedirs("../data/json_files", exist_ok=True)
    os.makedirs("../data/text_files", exist_ok=True)

    combined = {**profile_data, "recentAcSubmissions": recent_subs}
    with open("../data/json_files/leetcode_profile.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    with open("../data/text_files/leetcode_profile.txt", "w", encoding="utf-8") as f:
        f.write(doc.page_content)