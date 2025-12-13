from leetcode_api import LeetCode
import os, pathlib
from datetime import datetime

# ---------- Login ----------
username = os.getenv("LEETCODE_USERNAME")
password = os.getenv("LEETCODE_PASSWORD")
lc = LeetCode(username, password)

# ---------- Fetch Accepted Submissions ----------
subs = lc.get_accepted()

# ---------- Config ----------
DIFFICULTY_FOLDER = {
    "Easy": "JAVA-EASY",
    "Medium": "JAVA-MEDIUM",
    "Hard": "JAVA-HARD",
}

TARGET_LANG = "java"

updated = 0
stats = {"Easy": 0, "Medium": 0, "Hard": 0}

# Keep recent Java submissions (latest first)
recent_java = []

# ---------- Process Submissions ----------
for s in subs:
    if s["lang"] != TARGET_LANG:
        continue

    title = s["title"]
    slug = s["title_slug"]
    code = s["code"]
    difficulty = s.get("difficulty", "Easy")

    folder = DIFFICULTY_FOLDER.get(difficulty)
    if not folder:
        continue

    base = pathlib.Path(folder)
    base.mkdir(exist_ok=True)

    path = base / f"{title}.md"

    content = f"""# {title}

**Difficulty:** {difficulty}  
**Language:** Java  
**Link:** https://leetcode.com/problems/{slug}/

---

## 🧠 Solution (Java)

```java
{code}
