import os
import pathlib
from datetime import datetime
import requests

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

# ---------- Fetch all accepted submissions ----------
all_subs = []
skip = 0
limit = 50  # Number of submissions per request

while True:
    query = """
    query userStatus($username: String!, $skip: Int!, $first: Int!) {
      submissionList(username: $username, limit: $first, offset: $skip) {
        title
        titleSlug
        lang
        code
        status
        difficulty
      }
    }
    """
    variables = {"username": USERNAME, "skip": skip, "first": limit}
    resp = requests.post(
        "https://leetcode.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers
    )
    data = resp.json()
    subs = data.get("data", {}).get("submissionList", [])
    if not subs:
        break
    # Keep only accepted submissions
    accepted = [s for s in subs if s.get("status") == "Accepted"]
    all_subs.extend(accepted)
    skip += limit

print(f"Fetched {len(all_subs)} accepted submissions from LeetCode.")

updated = 0
stats = {"Easy": 0, "Medium": 0, "Hard": 0}
recent_java = []

# ---------- Process Submissions ----------
for s in all_subs:
    lang = s["lang"].lower()
    if lang != TARGET_LANG:
        continue

    title = s["title"]
    slug = s["titleSlug"]
    code = s.get("code", "")
    difficulty = s.get("difficulty", "Easy").capitalize()

    folder = DIFFICULTY_FOLDER.get(difficulty)
    if not folder:
        print(f"Skipping {title}, unknown difficulty: {difficulty}")
        continue

    base = pathlib.Path(folder)
    base.mkdir(exist_ok=True)

    # Slug-safe filename
    filename = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)
    path = base / f"{filename}.md"

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
        if start in txt and end in txt:
            return txt.split(start)[0] + start + "\n\n" + content + "\n\n" + txt.split(end)[1]
        else:
            print(f"Warning: Tags {start} or {end} not found in README")
            return txt

    text = replace_block(text, "<!-- LEETCODE_STATS:START -->", "<!-- LEETCODE_STATS:END -->", stats_block)
    text = replace_block(text, "<!-- LEETCODE_RECENT_SUBMISSIONS:START -->", "<!-- LEETCODE_RECENT_SUBMISSIONS:END -->", recent_block)

    readme.write_text(text, encoding="utf-8")

print(f"Updated {updated} Java problem files")
