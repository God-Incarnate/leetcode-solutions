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

# GraphQL query to get recent accepted submissions (max 20)
query = """
query submissionList($username: String!, $limit: Int!) {
  submissionList(username: $username, limit: $limit) {
    submissions {
      title
      titleSlug
      lang
      statusDisplay
      difficulty
      code
    }
  }
}
"""

variables = {"username": USERNAME, "limit": 50}  # adjust limit if needed

resp = requests.post(
    "https://leetcode.com/graphql",
    json={"query": query, "variables": variables},
    headers=headers
)

data = resp.json()
subs = data.get("data", {}).get("submissionList", {}).get("submissions", [])

if not subs:
    print("⚠️ Fetched 0 accepted submissions from LeetCode.")

updated = 0
stats = {"Easy": 0, "Medium": 0, "Hard": 0}
recent_java = []

# ---------- Process Submissions ----------
for s in subs:
    if s["lang"].lower() != TARGET_LANG:
        continue
    if s["statusDisplay"] != "Accepted":
        continue

    title = s["title"]
    slug = s["titleSlug"]
    code = s.get("code", "")
    difficulty = s.get("difficulty", "Easy")

    folder = DIFFICULTY_FOLDER.get(difficulty)
    if not folder:
        continue

    base = pathlib.Path(folder)
    base.mkdir(exist_ok=True)

    # Make filename safe
    filename = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)
    path = base / f"{filename}.md"

    content = f"""# {title}
    **Difficulty:** {difficulty}  
    **Language:** Java  
    **Link:** https://leetcode.com/problems/{slug}/
    ---
    
    ## 🧠 Solution (Java)
    
    ```java
    {code}
    ```
    """
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        updated += 1
    
    stats[difficulty] += 1
    
    recent_java.append({
        "title": title,
        "difficulty": difficulty,
        "link": f"https://leetcode.com/problems/{slug}/"
    })

