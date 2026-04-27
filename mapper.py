import sys
import re

current_url = ""

for line in sys.stdin:
    line = line.strip()

    if line.startswith("URL:"):
        current_url = line.replace("URL:", "").strip()
        continue

    if not current_url or len(line) < 3:
        continue

    words = re.findall(r"[a-zA-Z]+", line.lower())

    for word in words:
        if len(word) > 2:
            print(f"{word}\t{current_url}")
