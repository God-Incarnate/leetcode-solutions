from leetcode_api import LeetCode
import os, pathlib
from datetime import datetime

# ---------- Login ----------
username = os.getenv("LEETCODE_USERNAME")
password = os.getenv("LEETCODE_PASSWORD")
lc = LeetCode(username, password)

# ---------- Fetch Accepted Submissions ----------
subs = lc.get_accepted()

# ---------- Folder Mapping ----------
DIFFICULTY_FOLDER = {
    "Easy": "JAVA-EASY",
    "Medium": "JAVA-MEDIUM",
    "Hard": "JAVA-HARD",
}

LANGUAGE_TARGET = "java"
LANG_CODE_BLOCK = "java"

updated = 0
java_count = {"Easy": 0, "Medium": 0, "Hard": 0}

for s in subs:
    lang = s["lang"]
    if lang != LANGUAGE_TARGET:
        continue   # skip non-Java submissions

    title = s["title"]
    slug = s["title_slug"]
    code = s["code"]
    difficulty = s.get("difficulty", "Easy")

    folder_name = DIFFICULTY_FOLDER.get(difficulty)
    if not folder_name:
        continue

    folder = pathlib.Path(folder_name)
    folder.mkdir(exist_ok=True)

    filename = f"{title}.md"
    path = folder / filename

    content = f"""# {title}

**Difficulty:** {difficulty}  
**Language:** Java  
**Link:** https://leetcode.com/problems/{slug}/

---

## 🧠 Solution (Java)

```{LANG_CODE_BLOCK}
{code}
