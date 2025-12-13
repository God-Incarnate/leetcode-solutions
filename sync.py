import os
import pathlib
from datetime import datetime
import requests
import json

# ---------- Config ----------
DIFFICULTY_FOLDER = {
    "Easy": "JAVA-EASY",
    "Medium": "JAVA-MEDIUM",
    "Hard": "JAVA-HARD",
}
TARGET_LANG = "java"

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRFTOKEN = os.getenv("CSRFTOKEN")
USERNAME = os.getenv("LEETCODE_USERNAME")

if not (LEETCODE_SESSION and CSRFTOKEN and USERNAME):
    raise Exception("Missing LEETCODE_SESSION, CSRFTOKEN, or LEETCODE_USERNAME in environment variables.")

headers = {
    "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRFTOKEN}",
    "x-csrftoken": CSRFTOKEN,
    "Referer": "https://leetcode.com",
    "Content-Type": "application/json",
}

# GraphQL query to get recent accepted submissions
query = """
query recentAcSubmissions($username: String!) {
  recentAcSubmissions(username: $username) {
    title
    titleSlug
    lang
    code
    difficulty
  }
}
"""

variables = {"username": USERNAME}

resp = requests.post(
    "https://leetcode.com/graphql",
    json={"query": query, "variables": variables},
    headers=headers
)

data = resp.json()
subs = data.get("data", {}).get("recentAcSubmissions", [])

updated = 0
stats = {"Easy": 0, "Medium": 0, "Hard": 0}
recent_java = []

# ---------- Process Submissions ----------
for s in subs:
    if s["lang"].lower() != TARGET_LANG:
        continue

    title = s["title"]
    slug = s["titleSlug"]
    code = s["code"]
    difficulty = s.get("difficulty", "Easy")

    folder = DIFFICULTY_FOLDER.get(difficulty)
    if not folder:
        continue

    base = pathlib.Path(folder)
    base.mkdir(exist_ok=True)

    path = base / f"{title}.md"

    content = (
        f"# {title}\n\n"
        f"**Difficulty:** {difficulty}  \n"
        f"**Language:** Java  \n"
        f"**Link:** https://leetcode.com/problems/{slug}/\n\n"
        f"---\n\n"
        f"## 🧠 Solution (Java)\n\n"
        f"```java\n"
        f"{code}\n"
        f"```\n"
    )

    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        updated += 1

    stats[difficulty] += 1

    recent_java.append({
        "title": title,
        "difficulty": difficulty,
        "link": f"https://leetcode.com/problems/{slug}/"
    })

# ---------- Update README ----------
readme = pathlib.Path("README.md")
if readme.exists():
    text = readme.read_text(encoding="utf-8")

    stats_block = (
        f"- **Java Problems Solved:** {sum(stats.values())}\n"
        f"- **Easy:** {stats['Easy']}\n"
        f"- **Medium:** {stats['Medium']}\n"
        f"- **Hard:** {stats['Hard']}\n"
        f"- **Last Updated (UTC):** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    recent_block = "\n".join(
        f"- [{r['title']}]({r['link']}) — *{r['difficulty']}*"
        for r in reversed(recent_java[-5:])
    ) or "*No recent Java submissions.*"

    def replace_block(txt, start, end, content):
        return txt.split(start)[0] + start + "\n\n" + content + "\n\n" + txt.split(end)[1]

    text = replace_block(text, "<!-- LEETCODE_STATS:START -->", "<!-- LEETCODE_STATS:END -->", stats_block)
    text = replace_block(text, "<!-- LEETCODE_RECENT_SUBMISSIONS:START -->", "<!-- LEETCODE_RECENT_SUBMISSIONS:END -->", recent_block)

    readme.write_text(text, encoding="utf-8")

print(f"Updated {updated} Java problem files")
