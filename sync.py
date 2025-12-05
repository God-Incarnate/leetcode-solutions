from leetcode_api import LeetCode
import os, json, pathlib

username = os.getenv("LC_USERNAME")
password = os.getenv("LC_PASSWORD")

# Login
lc = LeetCode(username, password)
submissions = lc.get_accepted()  # fetch accepted problems

base = pathlib.Path("solutions")
base.mkdir(exist_ok=True)

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
