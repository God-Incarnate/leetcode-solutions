from leetcode_api import LeetCode
import os, pathlib
from datetime import datetime

# --- Login ---
username = os.getenv("LEETCODE_USERNAME")
password = os.getenv("LEETCODE_PASSWORD")
lc = LeetCode(username, password)

# --- Fetch Accepted Submissions ---
submissions = lc.get_accepted()

# --- Prepare Solutions Folder ---
base = pathlib.Path("solutions")
base.mkdir(exist_ok=True)

# --- Write Solutions ---
for sub in submissions:
    title = sub["title_slug"]
    code = sub["code"]
    lang = sub["lang"]

    ext = {
        "python3": ".py",
        "java": ".java",
        "cpp": ".cpp",
        "javascript": ".js",
        "sql": ".sql",
    }.get(lang, ".txt")

    path = base / f"{title}{ext}"

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

# --- Prepare Stats for README ---
total_solved = len(submissions)
recent = submissions[-5:]  # last 5 submissions
recent_list = "\n".join([f"- {s['title_slug']} ({s['lang']})" for s in reversed(recent)])

stats_content = f"- **Total Problems Solved:** {total_solved}\n"
stats_content += f"- **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

# --- Update README Placeholders ---
readme_path = pathlib.Path("README.md")
if readme_path.exists():
    readme_text = readme_path.read_text(encoding="utf-8")

    # Update LEETCODE_STATS
    start_tag = "<!-- LEETCODE_STATS:START -->"
    end_tag = "<!-- LEETCODE_STATS:END -->"
    readme_text = readme_text.split(start_tag)[0] + start_tag + "\n" + stats_content + "\n" + readme_text.split(end_tag)[1]

    # Update LEETCODE_RECENT_SUBMISSIONS
    start_tag2 = "<!-- LEETCODE_RECENT_SUBMISSIONS:START -->"
    end_tag2 = "<!-- LEETCODE_RECENT_SUBMISSIONS:END -->"
    readme_text = readme_text.split(start_tag2)[0] + start_tag2 + "\n" + recent_list + "\n" + readme_text.split(end_tag2)[1]

    # Write back updated README
    readme_path.write_text(readme_text, encoding="utf-8")
